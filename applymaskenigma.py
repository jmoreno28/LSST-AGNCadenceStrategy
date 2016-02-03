#!/usr/bin/env python

import argparse as argparse
import numpy as np
import scipy.stats as spstats
import sys
import socket
HOST = socket.gethostname()
print 'HOST: %s'%(str(HOST))
import os
import time
import pdb

from python.plotPSD import plotPSDTask
from python.makeMockLC import makeMockLCTask
from python.plotSuppliedLC import plotSuppliedLCTask
from python.fitCARMA import fitCARMATask

parser = argparse.ArgumentParser()
parser.add_argument("pwd", help = "Path to Working Directory")
parser.add_argument("cf", help = "Configuration File")
parser.add_argument("-o", "--old", help = "DateTime of run to be used")
parser.add_argument("-v", "--verbose", help = "Verbose T/F")
parser.add_argument("-p", "--prob", help = "Probability of retaining a point in lc", default = 0.5)
args = parser.parse_args()


#adjustable params before runtime
#provide stepsize of uniformly sampled mock lightcurve to mask with LSST cadence pattern 
stepsize = 30.0
sim_cadence = '/Users/Jackster/Research/masks/enigma_1189.txt'
#mocklc = "y.dat"
mocklc = "Regular.lc"
folder = "enigma_1189strdcadence"

#------------------------
#function to convert fractional day to mins
def MJDfracday2mins(MJD):
	mjn = np.floor(MJD)
	fracday = MJD-mjn
	min = fracday*24*60
	return min, mjn
	
#function to compute timesteps, units = minutes
def timesteps(min, mjn, stepsize):
	day2min = 24.0*60.0
	timestep = np.zeros(len(mjn)-1)
	for i in range(0, len(min)-1):
		timestep[i] = (min[i+1]-min[i]) + (mjn[i+1]-mjn[i])*day2min
	#functions as index values for mask	
	rawsteps = timestep/stepsize
	n_steps = np.unique(np.rint(rawsteps)) 

	for i in range (0,len(mjn)-1):
		if (mjn[i] == mjn[i+1]):
			mjn[i+1] = mjn[i+1]+1
	mjn[:]=mjn[:]-mjn[0]
	mask = mjn[:]*24*2
	mask = mask.astype(int)
	return mask
		

#function to make/apply mask	
def apply(mask, mock):
	#expecting mock with 4 columns (cadence, weights, flux, fluxerr)
	mock[:,1] = 0.0
	#print mask#, mask2
	mock[mask,1] = 1.0
	mock = mock[0:mask[-1]+1,:]
	return mock#, mock2
	
def details(x):
    sum1=0
    sum2=0
    for i in range(0, len(x)): 
        sum1 = sum1+x[i][1]
        sum2 = sum2+(x[i][2]*x[i][1])
    mean1 = sum2/sum1
    numC = len(x[0:])
    numObs = sum1
    median_flux = mean1
    return numC, numObs, median_flux
    
    
class Prepender(object):
    def __init__(self,
                 file_path,
                ):
        # Read in the existing file, so we can write it back later
        with open(file_path, mode='r') as f:
            self.__write_queue = f.readlines()

        self.__open_file = open(file_path, mode='w')

    def write_line(self, line):
        self.__write_queue.insert(0,
                                  "%s\n" % line,
                                 )
    def write_lines(self,  numC, numObs, median_flux,lines):
        lines.reverse()
        for line in lines:
            self.write_line(line)

    def close(self):
        self.__exit__(None, None, None)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.__write_queue:
            self.__open_file.writelines(self.__write_queue)
        self.__open_file.close()


#------------------------


if args.old:
	try:
		TestFile = open(args.pwd + args.cf.split('.')[0] + '_' + args.old + '.lc', 'r')
		TestFile.close()
	except:
		print args.pwd + args.cf.split('.')[0] + '_' + args.old + '_LC.dat not found!'
		sys.exit(1)
	Stamp = args.old
else:
	TimeStr = time.strftime("%m%d%Y") + time.strftime("%H%M%S")
	Stamp = TimeStr
plotPSDTask(args.pwd, args.cf, Stamp).run()
makeMockLCTask(args.pwd, args.cf, Stamp).run()

cmd = 'cp %s%s %sRegular.lc'%(args.pwd, args.cf.split('.')[0] + '_' + Stamp + '.lc', args.pwd)
os.system(cmd)

RegularFile = 'Regular.lc'
MissingFile = 'Missing.lc'
IrregularFile = 'Irregular.lc'
Regular = np.loadtxt(args.pwd + RegularFile, skiprows = 7)
numCadences_Regular = Regular.shape[0]

sim = np.loadtxt(sim_cadence)
mock = np.loadtxt(args.pwd + RegularFile, skiprows = 7)
MJD = sim[:,1]
min, mjn = MJDfracday2mins(MJD)
mask = timesteps(min, mjn,stepsize)


#---------------old format------ uncomment and it will created masked mocklc with name y.dat

newmock = apply(mask,mock)

#if not os.path.exists(folder):
#	os.mkdir(folder)
#np.savetxt('./'+folder+'/y.dat', newmock)



#with Prepender('./'+ folder + '/' + mocklc) as f:
    # Or, use write_lines instead - that maintains order.
    
#    numC, numObs, median_flux = details(newmock)
#    f.write_lines(numC, numObs, median_flux,
#        ['numCadences: '+ str(numC),
#         'numObservations: '+ str(numObs),
#         'meanFlux: '+ str(median_flux),
#        ]
#    )
#---------------old format------



numCadences_Regular, numCadences_Missing, median_flux = details(newmock)    
numCadences_Irregular0, numCadences_Irregular, median_flux_irr = details(newmock) 


Missing = open(args.pwd + MissingFile, 'w')
line = "#ConfigFileHash: %s\n"%('e338349c2ce27cd3daa690704386d14c6299d410efe52e3df9c5e1ca75c8347d32782aa7e289514b95cc8901ad3a88b87cb56e1925392968d4471fb480e1e37a')
Missing.write(line)
line = "#SuppliedLCHash: %s\n"%('')
Missing.write(line)
line = "#numCadences: %d\n"%(numCadences_Regular)
Missing.write(line)
line = "#numObservations: %d\n"%(numCadences_Missing)
Missing.write(line)
line = "#meanFlux: %+17.16e\n"%(0.0)
Missing.write(line)
line = "#LnLike: %+17.16e\n"%(0.0)
Missing.write(line)
line = "#cadence mask t x y yerr\n"
Missing.write(line)
    
Irregular = open(args.pwd + IrregularFile, 'w')
line = "#ConfigFileHash: %s\n"%('e338349c2ce27cd3daa690704386d14c6299d410efe52e3df9c5e1ca75c8347d32782aa7e289514b95cc8901ad3a88b87cb56e1925392968d4471fb480e1e37a')
Irregular.write(line)
line = "#SuppliedLCHash: %s\n"%('')
Irregular.write(line)
line = "#numCadences: %d\n"%(numCadences_Irregular)
Irregular.write(line)
line = "#numObservations: %d\n"%(numCadences_Irregular)
Irregular.write(line)
line = "#meanFlux: %+17.16e\n"%(median_flux_irr)
Irregular.write(line)
line = "#LnLike: %+17.16e\n"%(0.0)
Irregular.write(line)
line = "#cadence mask t x y yerr\n"
Irregular.write(line)

#irregular file is being written
IrregularCounter = 0
for i in xrange(len(newmock)):
	if newmock[i,1] == 1:
		line = "%d %1.0f %+17.16e %+17.16e %+17.16e %+17.16e\n"%(IrregularCounter, Regular[i,1], Regular[i,2], Regular[i,3], Regular[i,4], Regular[i,5])
		Irregular.write(line)
		IrregularCounter += 1
		line = "%d %1.0f %+17.16e %+17.16e %+17.16e %+17.16e\n"%(int(Regular[i,0]), Regular[i,1], Regular[i,2], Regular[i,3], Regular[i,4], Regular[i,5])
	else:
		line = "%d %1.0f %+17.16e %+17.16e %+17.16e %+17.16e\n"%(int(Regular[i,0]), 0.0, Regular[i,2], 0.0, 0.0, 1.3407807929942596e+154)
	Missing.write(line)

Missing.close()
Irregular.close()

#running C-ARMA routine on all files
try:
	TestFile = open(args.pwd + 'Irregular_MMDDYYYYHHMMSS.log', 'r')
	TestFile.close()
except IOError:
	plotSuppliedLCTask(args.pwd, 'Irregular.ini', 'MMDDYYYYHHMMSS').run()
try:
	TestFile = open(args.pwd + 'Irregular_MMDDYYYYHHMMSS_CARMAResult.dat', 'r')
except IOError:
	fitCARMATask(args.pwd, 'Irregular.ini', 'MMDDYYYYHHMMSS').run()

try:
	TestFile = open(args.pwd + 'Missing_MMDDYYYYHHMMSS.log', 'r')
	TestFile.close()
except IOError:
	plotSuppliedLCTask(args.pwd, 'Missing.ini', 'MMDDYYYYHHMMSS').run()
try:
	TestFile = open(args.pwd + 'Missing_MMDDYYYYHHMMSS_CARMAResult.dat', 'r')
except IOError:
	fitCARMATask(args.pwd, 'Missing.ini', 'MMDDYYYYHHMMSS').run()

try:
	TestFile = open(args.pwd + 'Regular_MMDDYYYYHHMMSS.log', 'r')
	TestFile.close()
except IOError:
	plotSuppliedLCTask(args.pwd, 'Regular.ini', 'MMDDYYYYHHMMSS').run()
try:
	TestFile = open(args.pwd + 'Regular_MMDDYYYYHHMMSS_CARMAResult.dat', 'r')
except IOError:
	fitCARMATask(args.pwd, 'Regular.ini', 'MMDDYYYYHHMMSS').run()


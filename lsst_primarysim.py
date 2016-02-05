import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import stats
import sys





connection = None

try:            
	connection = sqlite3.connect("enigma_1189_sqlite.db")
	cursor = connection.cursor()
	
	
#	bin fieldIDs to find deep drilling field
	cursor.execute("select distinct fieldID, count(fieldID)  from summary where filter = 'g' or filter = 'r' group by fieldID order by fieldID")

	#Only use in conjunction with binning execute statement
	data = cursor.fetchall()
	data = np.array(data)
	ddfs = np.argmax(data[:,1])
	print ddfs, data[ddfs]
	#plt.plot(data[:,0],data[:,1])
	#plt.savefig('nvisits_enigma.png')

#	check out only g and r bands
	cursor.execute("select fieldID,expMJD,night,lst,visitExpTime from summary where filter = 'g' or filter = 'r'  order by fieldID")


	#count rows = 249383
	data = cursor.fetchall()
	data = np.array(data)
	

	
	w1 = np.where((data[:,0] == 1000))[0]
	w2 = np.where((data[:,0] == ddfs+1))[0]


	#print(data[:,0].shape)
	data_std = data[w1,:]
	data_ddf= data[w2,:]
	np.savetxt('gandrbands_enigma1189std.txt',data_std)
	np.savetxt('gandrbands_enigma1189ddf.txt',data_ddf)
	
#	checkout all rows- all bands
	cursor.execute("select fieldID,expMJD,night,lst,visitExpTime from summary order by fieldID")
	data = cursor.fetchall()
	data = np.array(data)
	w1 = np.where((data[:,0] == 1000))[0]
	w2 = np.where((data[:,0] == ddfs+1))[0]
	#ddfs = np.argmax(data)
	#print ddfs, data[ddfs]

	#print(data[:,0].shape)
	data_std = data[w1,:]
	data_ddf= data[w2,:]
	np.savetxt('allbands_enigma1189std.txt',data_std)
	np.savetxt('allbands_enigma1189ddf.txt',data_ddf)
    
        
    
except sqlite3.Error, e:
    
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    
    if connection:
        connection.close()





import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import stats



connection = sqlite3.connect("enigma_1189_sqlite.db")
cursor = connection.cursor()
cursor.execute("select fieldID,expMJD,night,lst from summary where filter = 'g' order by fieldID")
#count rows = 249383
data = cursor.fetchall()
data = np.array(data)
w1 = np.where((data[:,0] == 1000))[0]
w2 = np.where((data[:,0] == 1003))[0]
w3 = np.where((data[:,0] == 3000))[0]
print(len(w1),len(w2),len(w3))
# save file?
print(data[:,0].shape)
data_med = data[w1,:]
visits1 = np.arange(1, len(data_med)+1,1)
#print (visits.shape,data_med[:,1].shape)
np.savetxt('avgcadence.txt',data_med)
data_l = np.zeros(shape=data_med.shape)
data_l = data[w3,:]
visits2 = np.arange(1, len(data_l)+1,1)
#l, h = data[:,0],data[:,0]
#bins = np.arange(l, h, 1)
#(n, bins, patches)  = plt.hist(data[:,0], h)

#(count, ll, binsize,extrapoints) = scipy.stats.histogram(data[:,0], h)
plt.plot(data_med[:,1],visits1, 'k.')
plt.plot(data_l[:,1],visits2, 'b.')
plt.ylabel('number of visits')
plt.xlabel('MJD')
#plt.show()
plt.savefig('example_cadences.png')




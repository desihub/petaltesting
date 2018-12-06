import os
import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd 
from scipy import interpolate
import argparse

fvc_data_dir = '/home/msdos/data/sti2/'#'/Users/parkerf/Research/DESI/PetalTesting/IllTesting/data/'

parser = argparse.ArgumentParser()
parser.add_argument('--focus', '-f', 
					help='list focus values in order of image taken',
					nargs = '*')

args = parser.parse_args()
focus = np.array(args.focus,dtype = float)
print(focus)
num_files = len(focus)
bashCommand = "ls -tr %s/*.pos | tail -n%d > temp.txt" % (fvc_data_dir, num_files)
os.system(bashCommand)

with open('temp.txt') as f:
	pos_files = f.readlines()
pos_files = [x.strip() for x in pos_files]
print(pos_files)

MEAN_FWHM = []
for pos in pos_files:
	data = pd.DataFrame(np.loadtxt(str(pos)), columns = ['X','Y','MAG','ID','FWHM'])
	good_idx = np.where(data['FWHM']>0)
	fwhm = np.mean(data['FWHM'][good_idx[0]])
	print(np.mean(data['FWHM']))
	print(np.max(data['FWHM']))
	print(np.median(data['FWHM']))
	MEAN_FWHM.append(fwhm)

f = interpolate.interp1d(focus, MEAN_FWHM)
xnew = np.linspace(min(focus), max(focus), num_files*10)
ynew = f(xnew)

plt.figure(figsize = (8,6))
plt.plot(focus, MEAN_FWHM, 'kx', label = 'Mean FWHM')
plt.plot(xnew, ynew, '-', label = 'Interpolation')
plt.axvline(xnew[np.argmin(ynew)])

plt.xlabel("Focus")
plt.ylabel("FWHM")
plt.legend()

print("Measured Focus: %.2f" % focus[np.argmin(MEAN_FWHM)])
print("Calculated Focus: %.2f" % xnew[np.argmin(ynew)])

plt.show()

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import sys,os
sys.path.append('/home/msdos/focalplane/plate_control/trunk/petal')
import petalcomm
import petal
import pandas as pd
import datetime
import time, datetime
import pickle
import csv
from scipy import interpolate
import json
import argparse

import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
# nominal hole location data

plt.ion()

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--wait", help="Determines amount of time between measuring temperature",action='store',dest='wait',default=None)
parser.add_argument('petal',type=int,help="Petal Number")
parser.add_argument('pc',type=int,help="Petal Controller Number")
results = parser.parse_args()

class PlotPetalBoxTemps():
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.file_path = '/home/msdos/focalplane/pos_utility/'
        self.temp_log_path = os.getcwd()#'/home/msdos/test_util/temp_logs/'
 
        self.wait = int(results.wait)
        if self.wait is None:
            self.wait = 60

        print("Temperature will be read every %d seconds"%self.wait)

        self.temp_log = open(self.temp_log_path+'/temp_log_%s.txt'%str(self.start_time),'w')
        self.hole_coords = np.genfromtxt(self.file_path+'hole_coords.csv', delimiter = ',', usecols = (3,4), skip_header = 40)
        self.nons = [38, 331, 438, 460, 478, 479, 480, 481, 497, 498, 499, 500, 513, 514, 515, 516, 527, 528, 529, 530, 531, 535, 536, 537, 538, 539, 540]
        self.gifs = [541, 542]
        self.fifs = [11, 75, 150, 239, 321, 439, 482, 496, 517, 534]
        try:
            self.petal = str(results.petal).zfill(2)
            self.comm = petalcomm.PetalComm(int(str(results.pc)))
        except:
            print('Must be run with two arguments: petal # and petalbox #')
            sys.exit()

        self.init_temps=[-40, -35, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125]
        self.adc=[3972.291151, 3927.370935, 3869.451327, 3795.92674, 3704.600096, 3593.238247, 3460.369957, 
                  3305.419031, 3129.278263, 2933.684449, 2721.964441, 2500.36307, 2273.125056, 2048, 1829.510403, 
                  1621.972457, 1428.638708, 1251.753073, 1091.966263, 949.5873406, 823.911807, 713.9506234, 618.034474, 
                  535.4993046, 464.1503813, 402.5825068, 348.8588418, 302.7049454, 263.3419356, 229.9160146, 201.3532376, 
                  176.832823, 155.6819655, 137.3646468]

        self.f2 = interpolate.interp1d(self.adc, self.init_temps, kind = 'cubic')

    def get_temps(self):
        measure_time = datetime.datetime.now()
        temp_dict = self.comm.pbget('posfid_temps')
        print(measure_time)
        ids=[]
        temps=[]
        for id,val in temp_dict.items():
            _ids=list(val.keys())
            _temps=list(self.f2([t for t in val.values()]))
            ids=ids+_ids
            temps=temps+_temps
        self.ids = ids
        self.temps=temps
        self.temp_log.write(str(measure_time)+'\n')
        for t in temps:
            self.temp_log.write(str(t)+', ')
        self.temp_log.write('\n')

    def plot_hole_info(self):
        for i in range(len(self.hole_coords)):
            x = self.hole_coords[i][0]
            y = self.hole_coords[i][1]

            if i not in self.nons:
                self.ax.plot(x, y, color = 'lightgrey', marker='o', zorder = -1)
                if i in self.fifs:
                    text = 'F' + str(i)
                    col = 'blue'
                elif i in self.gifs:
                    text = 'G' + str(i)
                    col = 'purple'
                else:
                    text = i
                    col = 'black'
                self.ax.text(x-.1, y + 0.3, text, color = col, fontsize=6)

    def initial_plot(self):

        self.fig=plt.figure(figsize = (10,5))
        self.ax=self.fig.add_axes(self.fig.add_axes([0,0,1,1]))
        self.plot_hole_info()
        self.hole=1
        self.ax.scatter(self.hole_coords[self.hole][0], self.hole_coords[self.hole][1], marker= '*', s=200, color = 'gold')

        # Google sheet
        url = 'https://docs.google.com/spreadsheets/d/1lJ9GjhUUsK2SIvXeerpGW7664OFKQWAlPqpgxgevvl8/edit#gid=0'
        credentials = self.file_path+'google_access_account.json'
        scope = ['https://spreadsheets.google.com/feeds', 'https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(url).sheet1
        df  = get_as_dataframe(sheet, parse_dates=True, usecols=[0,1,2,3,4,6,8,14], skiprows=20, header=0)
        pdf=df
        pdf=pdf.loc[pdf['PETAL_ID'] == int(self.petal)]

        self.dev_list=pdf['CAN_ID'].tolist()
        #self.dev_list = [str(i) for i in dev_list]
        self.hole_list=pdf['DEVICE_LOC'].tolist()
        self.dev_id_loc=dict(zip(self.dev_list,self.hole_list))

        holes = []
        idx = []
        for i,e in enumerate(self.ids):
            try:
                holes.append(self.dev_id_loc[e])
                idx.append(i)
            except:
                print('failed: ',e)
                self.nons.append(e)
                pass
        temps = np.array(self.temps)[np.array(idx)]
        new_ids = np.array(self.ids)[np.array(idx)]

        #print(holes[0:5]) 
        x = []
        y = []
        idx2 = []
        for i,e in enumerate(holes):
            try:
                x.append(self.hole_coords[int(e)][0])
                y.append(self.hole_coords[int(e)][1])
                idx2.append(i)
            except:
                print('failed: ',new_ids[i])
                self.nons.append(new_ids[i])
                pass
        temps = temps[np.array(idx2)]
        x = np.array(x)
        y = np.array(y)

        sc = self.ax.scatter(x,y,s=120,c=temps)
        self.cbar = plt.colorbar(sc)
        plt.show()


    def updated_plot(self):
        #Update data (with the new _and_ the old points)
        self.ax.scatter(self.hole_coords[self.hole][0], self.hole_coords[self.hole][1], marker= '*', s=200, color = 'gold')
        holes = []
        idx = []
        for i,e in enumerate(self.ids):
            try:
                holes.append(self.dev_id_loc[e])
                idx.append(i)
            except:
                print('failed: ',e)
                pass
        temps = np.array(self.temps)[np.array(idx)]
        new_ids = np.array(self.ids)[np.array(idx)]

        #print(holes[0:5]) 
        x = []
        y = []
        idx2 = []
        for i,e in enumerate(holes):
            try:
                x.append(self.hole_coords[int(e)][0])
                y.append(self.hole_coords[int(e)][1])
                idx2.append(i)
            except:
                print('failed: ',new_ids[i])
                pass
        temps = temps[np.array(idx2)]
        x = np.array(x)
        y = np.array(y)

        self.ax.scatter(x,y,s=120,c=temps)
        self.cbar.set_clim(vmin=min(temps),vmax=max(temps))
        self.cbar.draw_all()
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def __call__(self):
        self.get_temps()
        self.initial_plot()
        time.sleep(self.wait)
        while True:
           try:
               self.get_temps()
               self.updated_plot()
               time.sleep(self.wait)
           except KeyboardInterrupt:
               print('interrupted!')

if __name__ == '__main__':
    P = PlotPetalBoxTemps()
    P()

    




        

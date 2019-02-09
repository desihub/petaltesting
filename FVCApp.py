import os, sys, time
from DOSlib.proxies import FVC
import tkinter as tk
import tkinter
import numpy as np

import petalcomm
import petal

import tkinter.filedialog
import tkinter.messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import matplotlib.pyplot as plt 
from matplotlib.pyplot import cm

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys,os
from gspread_dataframe import get_as_dataframe

from configobj import ConfigObj
import configparser
pos_settings_path = ('/home/msdos/focalplane/fp_settings/fid_settings/')

BADFILEDIR = os.getcwd()+'/bad_locs/'



class FVCApp(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, bg = 'white')

        #try:
        #    self.petal = sys.argv[1].zfill(2)
        #    self.bad_file = BADFILEDIR + 'petal' + self.petal
        #    self.bad_ids = np.genfromtxt(self.bad_file)
        #except:
        #    print('Must be run with two arguments: petal # and petalbox #')
        #    sys.exit()

        #data frame initialization
        self.url = 'https://docs.google.com/spreadsheets/d/1lJ9GjhUUsK2SIvXeerpGW7664OFKQWAlPqpgxgevvl8/edit#gid=0'
        self.credentials = 'google_access_account.json'
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_url(self.url).sheet1
        self.df  = get_as_dataframe(self.sheet, parse_dates=True, usecols=[0,1,2,3,4,6,8,14], skiprows=20, header=0)
        self.map = self.df.to_records(index=False)

        self.FVC = FVC('petal2')
        self.exptime = None
        self.num_spots = None
        self.loc = None
        self.file_name = None
         
        self.createWidgets()

        self.plot_color=iter(cm.rainbow(np.linspace(0,1,10)))

    def createWidgets(self):
        window = tk.Frame(root, bg = 'white')
        window.pack(side='top', fill='both')
        print_window = tk.Frame(root, bg = 'white')
        print_window.pack(side='top', fill='both')
        plot_window = tk.Frame(root, bg = 'white')
        plot_window.pack(side='bottom', fill='both')

        #set exptime
        self.exptime_entry = tk.Entry(window, width = 8, justify = 'right')
        self.exptime_entry.grid(column=0, row=0)
        self.exptime_button = tk.Button(window, width = 10, text = 'SET EXPTIME', command=lambda: self.set_exptime())
        self.exptime_button.grid(column=0,row=1)

        #set num targets
        self.numtargets_entry = tk.Entry(window, width = 8, justify = 'right')
        self.numtargets_entry.grid(column=1, row=0)
        self.numtargets_button = tk.Button(window, width = 10, text = 'NUM TARGETS', command=lambda: self.set_numtargets())
        self.numtargets_button.grid(column=1, row=1)

        #calibrate bias dark
        self.darkbias_button = tk.Button(window, text = 'DARK BIAS', command=lambda: self.calibrate_dark_bias())
        self.darkbias_button.grid(column=3, row=0)

        #calibrate 
        self.calibrate_button = tk.Button(window, text = 'CALIBRATE IMG', command=lambda: self.calibrate_image())
        self.calibrate_button.grid(column=3, row=1)

        #locate
        self.locate_button = tk.Button(window, text = 'LOCATE', command=lambda: self.locate())
        self.locate_button.grid(column=4, row=0)

        #plot the positions
        self.plot_button = tk.Button(window, text = 'PLOT', command=lambda: self.plot_loc())
        self.plot_button.grid(column=4, row=1)

        #Plot options
        self.plot_var = tk.IntVar(window)
        self.plot_together= tk.Radiobutton(window, text = 'PLOT SEQ', bg = 'thistle', width = 10, variable = self.plot_var, value = 1).grid(column=5, row=0)
        self.plot_refresh= tk.Radiobutton(window, text = 'PLOT REFRESH', bg = 'thistle', width = 10, variable = self.plot_var, value = 2).grid(column=5, row=1)

        #print locate
        self.print_loc_button = tk.Button(window, text = 'PRINT LOC', command=lambda: self.print_loc())
        self.print_loc_button.grid(column=6, row=0)

        #take image
        self.take_image_button = tk.Button(window, text = 'TAKE EXP', command=lambda: self.take_exp())
        self.take_image_button.grid(column=6, row=1)

        window.grid_columnconfigure(7, minsize=50)

        import tkinter.ttk
        tkinter.ttk.Separator(window, orient=tk.VERTICAL).grid(column = 7, row=0, rowspan=2, sticky='ns')

        #Connect to Petal
        self.petal_num_entry = tk.Entry(window, width = 8, justify = 'right')
        self.petal_num_entry.grid(column=8, row=0)
        self.petal_num_button = tk.Button(window, text = 'Petal', command=lambda: self.set_petal())
        self.petal_num_button.grid(column=8, row=1)
        self.pc_num_entry = tk.Entry(window,  width = 8, justify = 'right')
        self.pc_num_entry.grid(column=9, row=0)
        self.pc_num_button = tk.Button(window, text = 'PC#', command=lambda: self.set_pc())
        self.pc_num_button.grid(column=9, row=1)
        self.petal_connect = tk.Button(window, text = 'CONNECT TO PETAL', command=lambda: self.connect_to_petal())
        self.petal_connect.grid(column=10, row=0)

        #Turn on Fiducials
        self.fid_type = tk.IntVar(window)
        self.fid_metrology= tk.Radiobutton(window, text = 'METRLGY (10)', bg = 'thistle', width = 10, variable = self.fid_type, value = 1).grid(column=10, row=1)
        self.fid_test= tk.Radiobutton(window, text = 'TEST (100)', bg = 'thistle', width = 10, variable = self.fid_type, value = 2).grid(column=11, row=0)
        self.fid_xytest= tk.Radiobutton(window, text = 'XY TEST', bg = 'thistle', width = 10, variable = self.fid_type, value = 3).grid(column=11, row=1)
        self.fids_on = tk.Button(window, text = 'FIDS ON', command=lambda: self.turn_on_fids())
        self.fids_on.grid(column=12, row=0)
        self.fids_off = tk.Button(window, text = 'FIDS OFF', command=lambda: self.turn_off_fids())
        self.fids_off.grid(column=12, row=1)

        #quit
        self.quit_button = tk.Button(window, text = 'QUIT', command=lambda: self.quit())
        self.quit_button.grid(column=13, row=0)


        #Plot options
        self.plot_var = tk.IntVar(window)
        self.plot_together= tk.Radiobutton(window, text = 'PLOT SEQ', bg = 'thistle', width = 10, variable = self.plot_var, value = 1).grid(column=5, row=0)
        self.plot_refresh= tk.Radiobutton(window, text = 'PLOT REFRESH', bg = 'thistle', width = 10, variable = self.plot_var, value = 2).grid(column=5, row=1)
        
        scrollbar = tk.Scrollbar(print_window)
        scrollbar.pack(side='right', fill='y')

        self.logdisp = tk.Listbox(print_window,  yscrollcommand=scrollbar.set, height = 8, background='white')
        self.logdisp.pack(fill = 'both')
        scrollbar.configure(command = self.logdisp.yview)

        self.plot_loc()

    def print_info(self):
        exptime = self.FVC.get('exptime') 
        num_spots = self.num_spots
        
        file_name = self.FVC.get('image_name')
        
        line = 'Exptime: %s, Num Spots: %s, Filename: %s' % (str(exptime), str(num_spots), file_name)
        self.logdisp.insert(0, line) 

    def set_exptime(self):
        self.exptime = float(self.exptime_entry.get())
        self.FVC.set(exptime = self.exptime)
        self.print_info()

    def set_numtargets(self):
        self.num_spots = int(self.numtargets_entry.get())
        self.FVC.make_targets(num_spots=self.num_spots) 
        self.print_info()

    def calibrate_dark_bias(self):
        self.FVC.calibrate_bias(dark_flag=False)
        self.print_info()

    def calibrate_image(self):
        self.FVC.calibrate_image()
        self.print_info()

    def locate(self):
        self.loc = self.FVC.locate(send_centroids=True)
        self.print_info()

    def take_exp(self):
        self.FVC.take_exposure()
        self.print_info()

    def quit(self):
        print("Bye bye!")
        sys.exit()
 
    def print_loc(self):
        self.logdisp.insert(0, self.loc)

    def plot_loc(self):
        #plot bad ones
        #for line in self.bad_ids:
        #   if line['type'] == 'broken':
        #       plt.plot(line[])

        if self.loc is None:
            self.fig=plt.figure(figsize = (14,7))
            self.ax=self.fig.add_axes(self.fig.add_axes([0,0,1,1]))
            self.canvas = FigureCanvasTkAgg(self.fig, master=root)
            self.canvas.get_tk_widget().pack(side='bottom')
            self.toolbarFrame = tk.Frame(master=root)
            self.toolbarFrame.pack(side='bottom')
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)

        else:
            c=next(self.plot_color)
            if self.plot_var.get() == 1:
                for num, info in self.loc.items():
                    self.ax.plot(info['x'], info['y'],'x',c=c)
                self.fig.canvas.draw()
            elif self.plot_var.get() == 2:
                try:
                    self.canvas.get_tk_widget().destroy()
                except:
                    pass
                self.fig = plt.figure(figsize = (14,7))
                self.ax=self.fig.add_axes(self.fig.add_axes([0,0,1,1]))
                for num, info in self.loc.items():
                    self.ax.plot(info['x'], info['y'], 'x',c=c)
                self.canvas = FigureCanvasTkAgg(self.fig, master=root)
                self.canvas.get_tk_widget().pack()
            else:
                print("Select a printing option")
                

        self.canvas.draw()

    def set_petal(self):
        self.petal_num = int(self.petal_num_entry.get())

    def set_pc(self):
        self.pc_num = int(self.pc_num_entry.get())

    def connect_to_petal(self):
        self.comm = petalcomm.PetalComm(self.pc_num)
        line = 'Connected to Petal %d with PC# %d' % (self.petal_num, self.pc_num)
        self.logdisp.insert(0, line) 

        #Get FIF CANIDS
        this_data = self.map[self.map['PETAL_ID'] == float(self.petal_num)]
        fif_list = this_data[(this_data['DEVICE_TYPE'] == 'FIF')|(this_data['DEVICE_TYPE'] == 'GIF')]
        self.fid_dict = {'can10':{},'can11':{},'can12':{},'can13':{},'can14':{},'can15':{},'can16':{},'can17':{},'can22':{},'can23':{}}
        for fif in fif_list:
            self.fid_dict['can'+str(int(fif['BUS_ID']))][int(fif['CAN_ID'])] = fif['DEVICE_ID']
        line = "Using this list of fiducials: ", self.fid_dict
        self.logdisp.insert(0,line)

    def turn_on_fids(self):
        commands = {'can10':{},'can11':{},'can12':{},'can13':{},'can14':{},'can15':{},'can16':{},'can17':{},'can22':{},'can23':{}}
        if self.fid_type.get() == 1: #Metrology
            for busid, info in self.fid_dict.items():
                for canid, deviceid in info.items():
                    commands[busid][canid] = 10
            self.comm.pbset('fiducials', commands)
            line = "Fiducials are turned ON with a duy of 10%"
            self.logdisp.insert(0,line)
        elif self.fid_type.get() == 2: #Test
            for busid, info in self.fid_dict.items():
                for canid, deviceid in info.items():
                    commands[busid][canid] = 100
            self.comm.pbset('fiducials', commands)
            line = "Fiducials are turned ON with a duy of 100%"
            self.logdisp.insert(0,line)
        elif self.fid_type.get() == 3: #XY Test
            for busid, info in self.fid_dict.items():
                for canid, deviceid in info.items():
                    name = pos_settings_path+'unit_%s.conf'%deviceid
                    config = ConfigObj(name)
                    duty = int(config['DUTY_DEFAULT_ON'])
                    commands[busid][canid] = duty
            self.comm.pbset('fiducials', commands)
            line = "Fiducials are turned ON with the duty from their .conf files: ", commands
            self.logdisp.insert(0,line)


    def turn_off_fids(self):
        commands = {'can10':{},'can11':{},'can12':{},'can13':{},'can14':{},'can15':{},'can16':{},'can17':{},'can22':{},'can23':{}}
        for busid, info in self.fid_dict.items():
            for canid, deviceid in info.items():
                commands[busid][canid] = 0
        self.comm.pbset('fiducials', commands)
        line = "Fiducials are turned OFF", commands
        self.logdisp.insert(0,line)

if __name__=="__main__":
    root=tk.Tk()
    root.title("FVC App")
    app=FVCApp(master=root)
    app.mainloop()





       

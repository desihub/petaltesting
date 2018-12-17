import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter.ttk import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from tkinter import messagebox
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys,os
sys.path.append('/home/msdos/focalplane/plate_control/trunk/petal')
import petalcomm
import petal
from gspread_dataframe import get_as_dataframe
import pandas as pd
from numpy import genfromtxt
import datetime
import time
import pickle
import csv

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master, bg = 'white')

        #data frame initialization
        self.url = 'https://docs.google.com/spreadsheets/d/1lJ9GjhUUsK2SIvXeerpGW7664OFKQWAlPqpgxgevvl8/edit#gid=0'
        self.credentials = 'google_access_account.json'
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_url(self.url).sheet1
        self.df  = get_as_dataframe(self.sheet, parse_dates=True, usecols=[0,1,2,3,4,6,8,14], skiprows=20, header=0)
        self.map = self.df.to_records(index=False)

        self.petal = None
        self.canbus = None
        self.deviceloc = None
        self.canid = None
        self.fif_only = False

    def createWidgets(self):
        window = tk.Frame(root, bg = 'white')
        window.pack(side='top', fill='both')

        logarea = tk.Frame(root, bg = 'white')
        logarea.pack(side='bottom', fill='both')
        scrollbar = tk.Scrollbar(logarea)
        scrollbar.pack(side='right', fill='y')

        self.logdisp = tk.Listbox(logarea,  yscrollcommand=scrollbar.set, height = 8, background='white')
        self.logdisp.pack(fill = 'both')
        scrollbar.configure(command = self.logdisp.yview)

        self.petal_entry = tk.Entry(window, justify = 'right')
        self.petal_entry.grid(column=0, row=0)
        self.petal_button = tk.Button(window, text = 'PETAL', command=lambda: self.set_petal()).pack()
        self.petal_button.grid(column=1, row=0)

        self.canbus_entry = tk.Entry(window, justify = 'right')
        self.canbus_entry.grid(column=0, row=1)
        self.canbus_button = tk.Button(window, text = 'CAN BUS (as #)', command=lambda: self.set_canbus()).pack()
        self.canbus_button.grid(column=1, row=1)

        self.loc_entry = tk.Entry(window, justify = 'right')
        self.loc_entry.grid(column=0, row=2)
        self.loc_button = tk.Button(window, text = 'DEVICE LOC', command=lambda: self.set_deviceloc()).pack()
        self.loc_button.grid(column=1, row=2)

        self.canid_entry = tk.Entry(window, justify = 'right')
        self.canid_entry.grid(column=0, row=3)
        self.canid_button = tk.Button(window, text = 'PETAL', command=lambda: self.set_canid()).pack()
        self.canid_button.grid(column=1, row=3)

        self.fif_button = tk.Button(window, text = 'FIF ONLY', command=lambda: self.set_fif()).pack()

        self.get_info_button = tk.Button(window, text = 'GET INFO', command=lambda: self.get_info()).pack()

    def set_petal(self):
        self.petal = self.petal_entry.get()

    def set_canbus(self):
        self.canbus = self.canbus_entry.get()

    def set_deviceloc(self):
        self.deviceloc = self.loc_entry.get()

    def set_canid(self):
        self.canid = self.canid_entry.get()

    def set_fif(self):
        self.fif_only = True

    def get_info(self):
        if self.petal == None:
            petal = 'All'
        else:
            petal = int(self.petal)
        if self.canbus == None:
            canbus = 'All'
        else:
            canbus = int(self.canbus)

        if self.deviceloc == None:
            deviceloc = 'All'
        else:
            deviceloc = int(self.deviceloc)

        if self.deviceid == None:
            deviceid = 'All'
        else:
            deviceid = int(self.deviceid)

        if self.fif_only == False:
            msg = "Printing Device Information for devices on:\n Petal: %s\n CAN Bus: %d\nDevice Loc: %d\nDevice ID: %d"%(petal, canbus, deviceloc, deviceid)
        else:
            msg = "Printing All FIFs for:\n Petal %d\nCAN Bus:%d"%(petal, canbus)
        self.logdisp.insert(0, msg)

        if self.petal is not None:
            this_data = self.map[self.map['PETAL_ID'] == self.petal]
        else:
            this_data = self.map

        if self.canbus is not None:
            this_data = this_data[this_data['BUS_ID'] == self.canbus]
        else:
            pass

        if self.deviceloc is not None:
            try:
                this_data = this_data[this_data['DEVICE_LOC'] == self.deviceloc]
            except:
                raise ValueError("This device location doesn't exist on this Petal/CAN Bus")
        else:
            pass

        if self.canid is not None:
            try:
                this_data = this_data[this_data['DEVICE_ID'] == self.canid]
            except:
                raise ValueError("This CanID cannot be found with the current selections")
        else:
            pass

        if self.fif_only == True:
            try:
                this_data = this_data[(this_data['DEVICE_TYPE'] == 'FIF') | (this_data['DEVICE_TYPE'] == 'GIF')]
            except:
                raise ValueError("There are no Fiducials with your current selection")
        else:
            pass

        self.logdisp.insert(0,this_data.dtype.names)
        for info in this_data:
            self.logdisp.insert(0,info)

if __name__=="__main__":
    root=tk.Tk()
    root.title("PosFidSpec ID Map")
    app=Application(master=root)
    app.mainloop()



        



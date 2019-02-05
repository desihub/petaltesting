import os, sys, time
from DOSlib.proxies import FVC
import tkinter as tk
import tkinter

import tkinter.filedialog
import tkinter.messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import matplotlib.pyplot as plt 

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

        self.FVC = FVC('petal2')
        self.exptime = None
        self.num_spots = None
        self.loc = None
        self.file_name = None
         
        self.createWidgets()

    def createWidgets(self):
        window = tk.Frame(root, bg = 'white')
        window.pack(side='top', fill='both')
        print_window = tk.Frame(root, bg = 'white')
        print_window.pack(side='top', fill='both')
        plot_window = tk.Frame(root, bg = 'white')
        plot_window.pack(side='bottom', fill='both')

        #set exptime
        self.exptime_entry = tk.Entry(window, justify = 'right')
        self.exptime_entry.grid(column=0, row=0)
        self.exptime_button = tk.Button(window, text = 'EXPTIME', command=lambda: self.set_exptime())
        self.exptime_button.grid(column=0,row=1)

        #set num targets
        self.numtargets_entry = tk.Entry(window, justify = 'right')
        self.numtargets_entry.grid(column=1, row=0)
        self.numtargets_button = tk.Button(window, text = 'NUM TARGETS', command=lambda: self.set_numtargets())
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

        #print locate
        self.print_loc_button = tk.Button(window, text = 'PRINT LOC', command=lambda: self.print_loc())
        self.print_loc_button.grid(column=5, row=0)

        #print locate
        self.take_image_button = tk.Button(window, text = 'TAKE EXP', command=lambda: self.take_exp())
        self.take_image_button.grid(column=5, row=1)

        #quit
        self.quit_button = tk.Button(window, text = 'QUIT', command=lambda: self.quit())
        self.quit_button.grid(column=6, row=0)

        #plot the positions
        self.plot_button = tk.Button(window, text = 'PLOT', command=lambda: self.plot_loc())
        self.plot_button.grid(column=4, row=1)
        
        scrollbar = tk.Scrollbar(print_window)
        scrollbar.pack(side='right', fill='y')

        self.logdisp = tk.Listbox(print_window,  yscrollcommand=scrollbar.set, height = 8, background='white')
        self.logdisp.pack(fill = 'both')
        scrollbar.configure(command = self.logdisp.yview)

        self.print_info()

        fig=plt.figure(figsize = (14,7))
        self.ax=fig.add_axes(fig.add_axes([0,0,1,1]))

        self.canvas = FigureCanvasTkAgg(fig, master= root)
        self.canvas.get_tk_widget().pack(side='bottom')

        self.toolbarFrame = tk.Frame(master=root)
        self.toolbarFrame.pack(side='bottom') 
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)

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
            print('No locations right now')
        else:
            for num, info in self.loc.items():
                plt.plot(info['x'], info['y'], 'x')

        self.canvas.draw()

if __name__=="__main__":
    root=tk.Tk()
    root.title("FVC App")
    app=FVCApp(master=root)
    app.mainloop()





       

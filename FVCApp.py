import os, sys, time
from DOSlib.proxies import FVC
import tkinter

import tkinter.filedialog
import tkinter.messagebox

import matplotlib.pyplot as plt 

BADFILEDIR = os.get_cwd()+'/bad_locs/'



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
        self.loc = None
         
        self.createWidgets()

    def createWidgets(self):
        window = tk.Frame(root, bg = 'white')
        window.pack(side='top', fill='both')
        plot_window = tk.Frame(root, bg = 'white')
        plot_window.pack(side='bottom', fill='both')

        #set exptime
        self.exptime_entry = tk.Entry(window, justify = 'right')
        self.exptime_entry.grid(column=0, row=0)
        self.exptime_button = tk.Button(window, text = 'EXPTIME', command=lambda: self.set_exptime())
        self.exptime_button.grid(column=1, row=0)

        #set num targets
        self.numtargets_entry = tk.Entry(window, justify = 'right')
        self.numtargets_entry.grid(column=0, row=0)
        self.numtargets_button = tk.Button(window, text = 'NUM TARGETS', command=lambda: self.set_numtargets())
        self.numtargets_button.grid(column=1, row=0)

        #calibrate bias dark
        self.darkbias_button = tk.Button(window, text = 'DARK BIAS', command=lambda: self.calibrate_dark_bias())
        self.darkbias_button.grid(column=1, row=0)

        #calibrate 
        self.calibrate_button = tk.Button(window, text = 'CALIBRATE IMG', command=lambda: self.calibrate_image())
        self.calibrate_button.grid(column=1, row=0)

        #locate
        self.locate_button = tk.Button(window, text = 'LOCATE', command=lambda: self.locate())
        self.locate_button.grid(column=1, row=0)

        #plot the positions
        self.plot_button = tk.Button(window, text = 'LOCATE', command=lambda: self.plot_loc())
        self.plot_button.grid(column=1, row=0)

        fig=plt.figure(figsize = (14,7))
        self.ax=fig.add_axes(fig.add_axes([0,0,1,1]))

        self.canvas = FigureCanvasTkAgg(fig, master= root)
        self.canvas.get_tk_widget().pack(side='bottom')

        self.plot_loc()
        fig.canvas.callbacks.connect('button_press_event', self.callback)


    def get_bad_loc(self):


    def set_exptime(self):
        self.FVC.set(exptime = self.exptime_entry)

    def set_numtargets(self):
        self.FVC.make_targets(num_spots = self.numtargets_entry) 

    def calibrate_dark_bias(self):
        self.FVC.calibrate_bias(dark_flag=False)

    def calibrate_image(self):
        self.FVC.calibrate_image()

    def locate(self):
        self.loc = self.FVC.locate(send_centroids=True)

    def plot_loc(self):
        #plot bad ones
        #for line in self.bad_ids:
        #   if line['type'] == 'broken':
        #       plt.plot(line[])

        if self.loc is None:
            print('No locations right now')
        else:
            for num, info in self.loc.items():
                plt.scatter(info['x'], info['y'], 'x')


if __name__=="__main__":
    root=tk.Tk()
    root.title("FVC App")
    app=FVCApp(master=root)
    app.mainloop()





       
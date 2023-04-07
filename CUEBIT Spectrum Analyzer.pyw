#CUEBIT Spectrum Analyzer
#Author: Richard Mattish
#Last Updated: 04/07/2023

#Function:  This program provides a graphical user interface for importing
#           and analyzing EBIT data files to identify isotopes present in the
#           spectrum as well as the exporting of results


#Imports necessary packages
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
from tkinter import *
from tkinter import ttk
from scipy.signal import find_peaks
from scipy.stats import mode
import sys
import os
import platform
import time
from tkinter import filedialog
from PIL import ImageTk, Image
import cv2
import threading
import webbrowser
from mendeleev.fetch import fetch_table
import pandas as pd


#Defines location of the Desktop as well as font and text size for use in the software
desktop = os.path.expanduser("~\Desktop")
desktop = desktop.replace(os.sep, '/')
font1 = ('Helvetica', 16)
font2 = ('Helvetica', 14)
font3 = ('Helvetica', 18)
font4 = ('Helvetica', 12)
textSize = 20
first = True

colors = [[0.368417,0.506779,0.709798],[0.880722,0.611041,0.142051],[0.560181,0.691569,0.194885],\
          [0.922526,0.385626,0.209179],[0.528488,0.470624,0.701351],[0.772079,0.431554,0.102387]]

#Opens a url in a new tab in the default webbrowser
def callback(url):
    webbrowser.open_new_tab(url)

#Sorts all columns of a matrix by a single column
def orderMatrix(matrix, column):
    i = 0
    a = len(matrix)
    orderedMatrix = []
    while i < len(matrix):
        j = 0
        smallest = True
        while j < len(matrix) and smallest == True:
            if matrix[i][column] <= matrix[j][column]:
                smallest = True
                j = j + 1
            else:
                smallest = False
        if smallest == True:
            orderedMatrix.append(matrix.pop(i))
            i = 0
        else:
            i = i + 1
    return orderedMatrix

#Enables multi-threading so that function will not freeze main GUI
def multiThreading(function):
    t1=threading.Thread(target=function)
    t1.setDaemon(True)      #This is so the thread will terminate when the main program is terminated
    t1.start()

def startProgram(root=None):
    instance = CSA()
    instance.makeGui(root)

class CSA:
    def __init__(self):
        #Loads elemental information from periodic table
        multiThreading(self.load_Ptable)

        #Defines global variables
        self.canvas = None
        self.fig = None
        self.ax = None
        self.toolbar = None
        self.filename = None
        self.work_dir = None
        self.header = None
        self.B = []
        self.I = []

        #Charge to mass ratio of a proton
        self.a = 1.6022E-19/1.6605E-27 

        self.R = None
        self.graph = False
        self.shift_is_held = False
        self.labels = []
        self.count = None
        self.calibrate_run = 0
        self.modes = []
        self.graphType = 0
        self.calibrate = False
        self.calibration_elements = []
        self.energy = None
        print('successfully initialized')

        #Loads the variables V and R from the variables file, and creates the file if none exists
        try:
            f = open('variables', 'r')
            variables = f.readlines()
            f.close()
            self.V = float(variables[0].split('=')[1])
            self.R = float(variables[1].split('=')[1])
            self.energy = int(variables[2].split('=')[1])
            carbon = int(variables[3].split('=')[1])
            nitrogen = int(variables[4].split('=')[1])
            oxygen = int(variables[5].split('=')[1])
            neon = int(variables[6].split('=')[1])
            argon = int(variables[7].split('=')[1])
            krypton = int(variables[8].split('=')[1])
            self.calibration_elements = [carbon, nitrogen, oxygen, neon, argon, krypton]
            self.work_dir = str(variables[9].split('=')[1])
        except:
            self.V = 3330
            self.R = 0.35
            self.energy = 4500
            self.calibration_elements = [1, 1, 1, 0, 1, 0]
            self.work_dir = desktop
            f = open("variables",'w')
            f.write('V='+str(self.V)+'\n'+'R='+str(self.R)+'\n'+'energy='+str(self.energy)+'\n')
            f.write('carbon=1\nnitrogen=1\noxygen=1\nneon=0\nargon=1\nkrypton=0\n')
            f.write(f'work_dir={self.work_dir}')
            f.close()


        
    def load_Ptable(self):
        self.ptable = fetch_table('elements')
        self.isotopes = fetch_table('isotopes', index_col='id')
        cols = ['atomic_number', 'symbol']
        self.ptable = self.ptable[cols]
        cols = ['atomic_number', 'mass', 'abundance']
        self.isotopes = self.isotopes[cols]

        merged = pd.merge(self.ptable, self.isotopes, how='outer', on='atomic_number')
        self.isotopes = merged[merged['mass'].notnull()]


    #Opens About Window with description of software
    def About(self):
        name = "CUEBIT Spectrum Analyzer"
        version = 'Version: 2.2.6'
        date = 'Date: 04/07/2023'
        support = 'Support: '
        url = 'https://github.com/rhmatti/CUEBIT-Spectrum-Analyzer'
        copyrightMessage ='Copyright © 2023 Richard Mattish All Rights Reserved.'
        t = Toplevel(self.root)
        t.wm_title("About")
        t.geometry("400x300")
        t.resizable(False, False)
        t.configure(background='white')
        if platform.system() == 'Windows':
            try:
                t.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        l1 = Label(t, text = name, bg='white', fg='blue', font=font2)
        l1.place(relx = 0.15, rely = 0.14, anchor = W)
        l2 = Label(t, text = version, bg='white', font=font4)
        l2.place(relx = 0.15, rely = 0.25, anchor = W)
        l3 = Label(t, text = date, bg='white', font=font4)
        l3.place(relx = 0.15, rely = 0.35, anchor = W)
        l4 = Label(t, text = support, bg = 'white', font=font4)
        l4.place(relx = 0.15, rely = 0.45, anchor = W)
        l5 = Label(t, text = 'https://github.com/rhmatti/\nCUEBIT-Spectrum-Analyzer', bg = 'white', fg = 'blue', font=font4)
        l5.place(relx = 0.31, rely=0.48, anchor = W)
        l5.bind("<Button-1>", lambda e:
        callback(url))
        messageVar = Message(t, text = copyrightMessage, bg='white', font = font4, width = 600)
        messageVar.place(relx = 0.5, rely = 1, anchor = S)

    def Instructions(self):
        instructions = Toplevel(self.root)
        instructions.geometry('1280x720')
        instructions.wm_title("User Instructions")
        instructions.configure(bg='white')
        if platform.system() == 'Windows':
            try:
                instructions.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        v = Scrollbar(instructions, orient = 'vertical')
        t = Text(instructions, font = font4, bg='white', width = 100, height = 100, wrap = NONE, yscrollcommand = v.set)
        t.insert(END, "*********************************************************************************************************************\n")
        t.insert(END, "Program: EBIT Ion Beam Analyzer\n")
        t.insert(END, "Author: Richard Mattish\n")
        t.insert(END, "Last Updated: 06/10/2021\n\n")
        t.insert(END, "Function:  This program provides a graphical user interface for quickly importing\n")
        t.insert(END, "\tEBIT data files and comparing them to several of the most common elements and gases,\n")
        t.insert(END, "\tas well as the option to define your own isotope.\n")
        t.insert(END, "*********************************************************************************************************************\n\n\n\n")
        t.insert(END, "User Instructions\n-------------------------\n")
        t.insert(END, "1. Open the file \"EBIT Ion Beam Analyzer.pyw\"\n\n")
        t.insert(END, "2. Select the \"Import\" option from the drop-down File menu (File>Import) or use the shortcut <Ctrl+I>\n\n")
        t.insert(END, "3. Using the navigation window, navigate to an output file generated from the DREEBIT software and import it\n\n")
        t.insert(END, "4. Perform a calibration of the offset/fudge-factor V\n\n")
        t.insert(END, "\ta. Automatic Calibration:\n")
        t.insert(END, "\t\t1) Select \"Calibrate\" from the drop-down File menu (File>Calibrate)\n")
        t.insert(END, "\t\t2) A separate progress window will open. Allow calibration to complete before closing\n")
        t.insert(END, "\t\t3) Once the calibration is marked complete, you may close the window\n")
        t.insert(END, "\t\t4) The offset V has been calibrated!\n\n")
        t.insert(END, "\t\tNote:\tThis method is quicker than manual calibration, but I do not guarantee it is always accurate.\n")
        t.insert(END, "\t\t\tAlways evaluate it's accuracy yourself afterwards using the Analysis menu's various options!\n\n")
        t.insert(END, "\tb. Manual Calibration:\n")
        t.insert(END, "\t\t1) Select \"Settings\" from the drop-down File menu (File>Settings)\n")
        t.insert(END, "\t\t2) Enter a new value for V in the appropriate box\n")
        t.insert(END, "\t\t3) Select \"Update and Close\"\n")
        t.insert(END, "\t\t4) Access various comparisons from the drop-down Analysis menu\n")
        t.insert(END, "\t\t5) Visually compare/evaluate that setting for V using the graphs\n")
        t.insert(END, "\t\t6) Repeat steps 1-5 as needed until a good value for V has been found\n\n")
        t.insert(END, "5. Perform a spectral analysis\n\n")
        t.insert(END, "\ta. Automatic Analysis:\n")
        t.insert(END, "\t\t1) Select \"Auto-Anayze\" from the drop-down Analysis menu (Analysis>Auto-Analylze) or use the shortcut <Ctrl+R>\n")
        t.insert(END, "\t\t2) A separate window will open with the results of the analysis\n")
        t.insert(END, "\t\t3) The results are binned as follows:\n")
        t.insert(END, "\t\t\tVery Likely.....2/3 or more of charge states match peaks\t(matches >= 2/3)\n")
        t.insert(END, "\t\t\tPossible........Between 1/3 and 2/3 of charge states match peaks\t(1/3 < matches < 2/3)\n")
        t.insert(END, "\t\t\tUnlikely........Less than 1/3 of charge states match peaks\t(0 < matches < 1/3)\n")
        t.insert(END, "\t\t\tNone............No charge states match peaks\t(matches = 0)\n")
        t.insert(END, "\t\t4) To save these results, click anywhere within the results window and use the <Ctrl+S> command\n\n")
        t.insert(END, "\t\tNote:\tThis method is very useful for quickly obtaining a list of possible isotopes present in the spectrum.\n")
        t.insert(END, "\t\t\tHowever, it will inevitably include possible isotopes which are not present. Use it as a way to\n")
        t.insert(END, "\t\t\tnarrow down the list of possible candidates, and evaluate the ones it gives further using the\n")
        t.insert(END, "\t\t\t\"Manual Analysis\" instructions to obtain the actual isotopes that are constituents of the beam.\n\n")
        t.insert(END, "\tb. Manual Analysis:\n\n")
        t.insert(END, "\t\t1) Select an isotope from the drop-down Analysis menu\n")
        t.insert(END, "\t\t2) A graph will appear comparing the spectrum to that isotope's charge states\n")
        t.insert(END, "\t\t3) Anything not on a vertical dashed line corresponding to that isotope's charge state should be ignored\n")
        t.insert(END, "\t\t4) If the peaks align well with the charge states, that isotope may be present in the spectrum\n")
        t.insert(END, "\t\t5) Repeat steps 1-4 for additional isotopes of interest\n")
        t.insert(END, "\t\t6) If you want to evaluate an isotope other than the most abundant isotope of the given elements,\n")
        t.insert(END, "\t\tor of an element not listed in the Analysis menu, select the \"Other\" option\n")
        t.insert(END, "\t\t7) Enter the atomic number Z and atomic mass (in amu) for the desired isotope, then select \"Run Comparison\"\n\n")
        t.insert(END, "6. To save the graph on screen, select \"Save\" from the drop-down File menu (File>Save) or use the shortcut <Ctrl+S>\n\n")
        t.insert(END, "7. To open additional files, select \"New Window\" from the File menu\n\n")

        t.pack(side=TOP, fill=X)
        v.config(command=t.yview)
    

    #Opens Settings Window, which allows the user to change the persistent global variables V and R
    def Settings(self):
        t = Toplevel(self.root)
        t.geometry('400x300')
        t.wm_title("Settings")
        if platform.system() == 'Windows':
            try:
                t.iconbitmap("icons/settings.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        t.configure(bg='grey95')
        L0 = Label(t, text = 'Settings', font = font3)
        L0.place(relx=0.5, rely=0.15, anchor = CENTER)
        L1 = Label(t, text = 'V:', font = font2)
        L1.place(relx=0.4, rely=0.3, anchor = E)
        E1 = Entry(t, font = font2, width = 10)
        E1.insert(0,str(self.V))
        E1.place(relx=0.4, rely=0.3, anchor = W)

        L2 = Label(t, text = 'R:', font = font2)
        L2.place(relx=0.4, rely=0.5, anchor = E)
        E2 = Entry(t, font = font2, width = 10)
        E2.insert(0,str(self.R))
        E2.place(relx=0.4, rely=0.5, anchor = W)
        L3 = Label(t, text = 'm', font = font2)
        L3.place(relx=0.64, rely=0.5, anchor = W)
            
        b1 = Button(t, text = 'Update', relief = 'raised', background='lightblue', activebackground='blue', font = font1, width = 10, height = 1,\
                    command = lambda: [self.updateSettings(float(E1.get()),float(E2.get()), self.energy, self.calibration_elements),t.destroy()])
        b1.place(relx=0.75, rely=0.8, anchor = CENTER)

        b2 = Button(t, text = 'Reset', relief = 'raised', background='pink', activebackground='red', font = font1, width = 10, height = 1, command = lambda: [self.updateSettings(3330,0.35, 4500, [1, 1, 1, 0, 1, 0]),t.destroy()])
        b2.place(relx=0.25, rely=0.8, anchor = CENTER)

    #Updates the persistent global variables V and R, as well as store which elements the user has selected for calibration
    def updateSettings(self, E1, E2, E3, E4):
        self.V = E1
        self.R = E2
        self.energy = int(E3)
        self.calibration_elements = E4
        names = ['carbon', 'nitrogen', 'oxygen', 'neon', 'argon', 'krypton']
        f = open("variables",'w')
        f.write('V='+str(self.V)+'\n'+'R='+str(self.R)+'\n'+'energy='+str(self.energy)+'\n')
        for i in range(0,len(self.calibration_elements)):
            f.write(names[i] + '=' + str(self.calibration_elements[i]) + '\n') 
        f.write(f'work_dir={self.work_dir}')
        f.close()

        if self.calibrate:
            print("I should see this")
            self.calibrate = False
            sys.exit()

        if self.graphType == 0:
            print('no graph needs changes')
        elif self.graphType == 1:
            self.massToCharge()
        else:
            self.graphType = self.graphType.split(',')
            Z = int(self.graphType[0])
            A = float(self.graphType[1])
            x_label = self.graphType[2]
            self.elementComparison(Z, A, x_label)
        
    
    #Used to import an EBIT data file into the software
    def askopenfile(self):
        try:
            newfile = filedialog.askopenfilename(initialdir = self.work_dir,title = "Select file",filetypes = (("all files","*.*"),("all files","*.*")))
        except:
            newfile = filedialog.askopenfilename(initialdir = desktop,title = "Select file",filetypes = (("all files","*.*"),("all files","*.*")))
        if newfile == '':
            return
        self.filename = newfile
        folders = newfile.split('/')
        self.work_dir = ''
        for i in range(0,len(folders)-1):
            self.work_dir = f'{self.work_dir}{folders[i]}/'

        self.updateSettings(self.V, self.R, self.energy, self.calibration_elements)
        self.eraseAll()
        self.header = self.parse_header()
        self.getData()

    #Lets user save a copy of the matplotlib graph displayed in the software
    def saveGraph():
        try:
            saveFile = str(filedialog.asksaveasfile(initialdir = desktop,title = "Save file",filetypes = (("Portable Network Graphic","*.png"),("JPEG","*.jpeg")), defaultextension = (("Portable Network Graphic","*.png"),("JPEG","*.jpeg"))))
            print(saveFile)
            saveFile = saveFile.split("'")
            saveFile = saveFile[1]
            print(str(saveFile))
            plt.savefig(saveFile, bbox_inches='tight')
        except:
            pass

    #Opens a window with a periodic table for reference
    def PTable(self):
        ptable = Toplevel(self.root)
        ptable.geometry('1920x1080')
        ptable.configure(bg='white')
        if platform.system() == 'Windows':
            try:
                ptable.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('This functionality not possible when program is accessed remotely')
                message = Label(ptable, text='Cannot view periodic table when program was\n accessed remotely by another program', font=font3, bg = 'white')
                message.place(relx=0.5, rely=0.5, anchor = CENTER)
                return

        ptable.wm_title('Periodic Table')
        load = Image.open('PeriodicTable.png')
        render = ImageTk.PhotoImage(load)
        img = Label(ptable, image=render)
        img.image = render
        img.pack(side="top",fill='both',expand=True)
        
    def _resize_image(self,event):

        new_width = event.width
        new_height = event.height

        self.img_copy.thumbnail((new_width, new_height), )
        self.image = self.img_copy

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image =  self.background_image)

    def quitProgram(self):
        print('quit')
        self.root.quit()
        self.root.destroy()


    """
    Gun Parameters: 
    V_anode: 10994.2 V, V_Cathode: 598.936 V, I_emission: 71.786 mA

    Drift Tubes:
    U_0: 4524.69 V, U_A: 514.731 V, U_B: 445.12 V

    Extraction:
    EXT: 2080.35 V, EL1: 1305.2 V, EL2: 2523.73 V

    Deflectors: 
    X1: 0.1815,-0.176 V; Y1: -23.815,23.782 V
    X2: -0.1595,0.154 V; Y2: -0.066,0.066 V

    Source Pressure:
    4.12097e-09 mbar

    Ar leaked in

    """

    def parse_header(self, filename = None):
        if filename != None:
            self.filename = filename
        inputFile = open(self.filename, "r")
        values = {}
        next_is_pressure = False
        for line in inputFile:
            if 'Timestamp (s)\tMagnetic Field (T)\tFC2 Current (A)' in line:
                break
            if line.startswith("V_anode") or line.startswith("U_0") or line.startswith("EXT"):
                args = line.strip().split(', ')
                for i in range(len(args)):
                    arg_v = args[i].split(' ')
                    name = arg_v[0].replace(':', '')
                    values[name] = float(arg_v[1])
            if next_is_pressure:
                next_is_pressure = False
                args = line.split(' ')
                values['PSRC'] = float(args[0])
            if line.startswith('Source Pressure:'):
                next_is_pressure=True
        inputFile.close()
        return values

    def getData(self, filename = None):
        if filename != None:
            self.filename = filename
        inputFile = open(self.filename, "r")
        start_line = 0
        header = False

        i = 0
        for line in inputFile:
            if not header:
                i = i + 1
                if 'Timestamp (s)\tMagnetic Field (T)\tFC2 Current (A)' in line:
                    header = True
                    start_line = i
                    break

        inputFile.close()

        data = np.genfromtxt(self.filename, delimiter='\t', skip_header=start_line)
        if header == True:
            self.B = data[:,1]*10**3
            self.I = data[:,2]*10**12
        else:
            self.B = data[:,1]
            self.I = data[:,2]
        self.plotData()

    def plotData(self):
        self.graphType = 0

        try:
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            plt.close('all')
        except:
            pass

        try:
            title = os.path.basename(self.filename)
            x_min = np.amin(self.B)
            x_max = np.amax(self.B)
            y_min = np.amin(self.I)
            y_max = np.amax(self.I)
            # creating the Matplotlib figure
            fig, ax = plt.subplots(figsize = (16,9))
            ax.tick_params(which='both', direction='in')
            plt.rcParams.update({'font.size': textSize})
            if len(self.labels) > 0:
                    for label in self.labels:
                        label_x_pos = np.sqrt(label[0]*2*self.V/self.a)*1000/self.R
                        plt.text(label_x_pos, label[1]+.03*y_max, label[2], fontsize = 10, ha='center')
            for label in (ax.get_xticklabels() + ax.get_yticklabels()):
                label.set_fontsize(textSize)
            plt.plot(self.B, self.I, color = colors[0], linestyle = '-', linewidth = 2)
            plt.xlim([x_min,x_max])
            plt.ylim([y_min,1.1*y_max])
            plt.xlabel('Magnetic Field (mT)',fontsize=textSize)
            plt.ylabel('Current (pA)',fontsize=textSize)
            plt.title(title)

            #Setting the default save directory for matplotlib toolbar
            plt.rcParams["savefig.directory"] = desktop
            print(f'Desktop{desktop}')

            # creating the Tkinter canvas containing the Matplotlib figure
            self.canvas = FigureCanvasTkAgg(fig, master = self.root)
            self.canvas.draw()

            # creating the toolbar and placing it
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.root, pack_toolbar=False)
            self.toolbar.update()
            self.toolbar.pack(side=BOTTOM, fill=X)

            # placing the canvas on the Tkinter window
            self.canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
        
        except NameError:
            helpMessage ='Please import a data file first.' 
            messageVar = Message(self.root, text = helpMessage, font = font2, width = 600) 
            messageVar.config(bg='lightgreen')
            messageVar.place(relx = 0, rely = 1, anchor = SW)
    

    #Creates a plot of current vs. mass-to-charge ratio
    def massToCharge(self):
        self.graphType = 1

        try:
            title = os.path.basename(self.filename)
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            plt.close('all')
            mpq = self.a*np.square(self.R*self.B/1000)/(2*self.V)
            x_min = np.amin(mpq)
            x_max = np.amax(mpq)
            y_min = np.amin(self.I)
            y_max = np.amax(self.I)
            fig, ax = plt.subplots(figsize = (16,9))
            ax.tick_params(which='both', direction='in')
            plt.rcParams.update({'font.size': textSize})
            if len(self.labels) > 0:
                    for label in self.labels:
                        plt.text(label[0], label[1]+.03*y_max, label[2], fontsize = 10, ha='center')
            for label in (ax.get_xticklabels() + ax.get_yticklabels()):
                label.set_fontsize(textSize)
            plt.plot(mpq, self.I, color = colors[0], linestyle = '-', linewidth = 2)
            plt.xlim([x_min,x_max])
            plt.ylim([y_min,1.1*y_max])
            plt.xlabel('A/q',fontsize=textSize)
            plt.ylabel('Current (pA)',fontsize=textSize)
            plt.title(title)

            # creating the Tkinter canvas containing the Matplotlib figure
            self.canvas = FigureCanvasTkAgg(fig, master = self.root)
            self.canvas.draw()

            # creating the toolbar and placing it
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.root, pack_toolbar=False)
            self.toolbar.update()
            self.toolbar.pack(side=BOTTOM, fill=X)

            # placing the canvas on the Tkinter window
            self.canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
        
        except NameError:
            helpMessage ='Please import a data file first.' 
            messageVar = Message(self.root, text = helpMessage, font = font2, width = 600) 
            messageVar.config(bg='lightgreen')
            messageVar.place(relx = 0, rely = 1, anchor = SW)

    #Creates a plot of current vs. a given element's/gas's charge states for use in identifying if it is present in the ion beam
    def elementComparison(self, Z, A, x_label):
        self.graphType = str(Z)+','+str(A)+','+x_label

        try:
            title = os.path.basename(self.filename)
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            plt.close('all')
            y_min = np.amin(self.I)
            y_max = np.amax(self.I)
            mpq = self.a*np.square(self.R*self.B/1000)/(2*self.V)
            fig, self.ax = plt.subplots(figsize = (16,9))
            self.ax.tick_params(which='both', direction='in')
            plt.rcParams.update({'font.size': textSize})                
            for label in (self.ax.get_xticklabels() + self.ax.get_yticklabels()):
                label.set_fontsize(textSize)
            for xc in range(1,Z+1):
                plt.axvline(x=xc, color='black', linestyle='--', linewidth = 1)
            plt.plot(A/mpq, self.I, color = colors[0], linestyle = '-', linewidth = 2)
            plt.xlabel(x_label + " Charge State",fontsize=textSize)
            plt.ylabel('Current (pA)',fontsize=textSize)
            plt.title(title)
            plt.xlim([0.5,Z+0.5])
            plt.ylim([y_min,1.1*y_max])
            y_min, y_max = plt.gca().get_ylim()
            if len(self.labels) > 0:
                    for label in self.labels:
                        plt.text(A/label[0], label[1]+0.03*y_max, label[2], fontsize = 10, ha='center')
            # creating the Tkinter canvas containing the Matplotlib figure
            self.canvas = FigureCanvasTkAgg(fig, master = self.root)
            self.canvas.draw()

            # creating the toolbar and placing it
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.root, pack_toolbar=False)
            self.toolbar.update()
            self.toolbar.pack(side=BOTTOM, fill=X)

            # placing the canvas on the Tkinter window
            self.canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
            fig.canvas.mpl_connect('button_press_event', lambda event: self.onclick(event, Z, A))
            fig.canvas.mpl_connect('key_press_event', CSA.onkeypress)
            fig.canvas.mpl_connect('key_release_event', CSA.onkeyrelease)

            clickInstructions = 'Double Click: Add Label\t\tCtrl+Z: Undo\t\tCtr+A: Clear All'

            clickMessage = Message(self.root, text = clickInstructions, font = font4, width = 700)
            clickMessage.config(bg='white', fg='grey')
            clickMessage.place(relx = 0.5, rely = 0.02, anchor = CENTER)
        
        except NameError:
            helpMessage ='Please import a data file first.' 
            messageVar = Message(self.root, text = helpMessage, font = font2, width = 600) 
            messageVar.config(bg='lightgreen')
            messageVar.place(relx = 0, rely = 1, anchor = SW)

    def onclick(self, event, Z, A):
        present = False
        if event.xdata is None:
            return
        if event.dblclick:
            y_min, y_max = plt.gca().get_ylim()
            matches = self.isotopes.loc[self.isotopes['atomic_number']==Z]
            element = matches['symbol'].iloc[0]

            massVector = []
            abundVector = []
            for i in range(0, len(matches)):
                mass = matches['mass'].iloc[i]
                abund = matches['abundance'].iloc[i]
                massVector.append(mass)
                abundVector.append(abund)
            massArray = np.array(massVector)
            abundArray = np.array(abundVector)
            commonMass = massArray[np.argmax(abundArray)]

            q = int(round(event.xdata,0))
            peak_index = find_peaks(self.I, height=0)[0]
            deltas = abs(self.B[peak_index]-(1000/self.R)*np.sqrt(A/q*2*self.V/self.a))
            min_delta_index = np.argmin(deltas)
            peak_I = self.I[peak_index[min_delta_index]]
            if abs(A-commonMass) < 0.5:
                label = [A/int(round(event.xdata,0)), peak_I, element+'$^{'+str(q)+'+}$']
            else:
                label = [A/int(round(event.xdata,0)), peak_I, '$^{'+str(int(A))+'}$'+element+'$^{'+str(q)+'+}$']

            if len(self.labels) > 0:
                self.count = 0
                for entry in self.labels:
                    if label[0]==entry[0]:
                        present = True
                        if label[2]==entry[2]:
                            return
                        else:
                            entries = entry[2].split(',')
                            for i in entries:
                                if label[2]==i:
                                    return
                            charges = []
                            for i in entries:
                                charge = int(i.split('{')[1].split('+')[0])
                                charges.append([charge, i])
                                print(charges)
                            charges.append([q, label[2]])
                            charges = orderMatrix(charges, 0)
                            entry[2]=''
                            for j in charges:
                                if entry[2] != '':
                                    entry[2] = entry[2]+','+j[1]
                                else:
                                    entry[2]=j[1]
                            del self.ax.texts[self.count]
                            plt.text(A/label[0]+0.02, label[1]+0.02*y_max, entry[2], fontsize = 10, ha='center')
                            self.canvas.draw()
                            self.labels.pop(self.count)
                            self.labels.append(entry)
                            return
                    self.count = self.count + 1
            if present == False:
                self.labels.append(label)
                plt.text(A/label[0]+0.02, label[1]+0.02*y_max, label[2], fontsize = 10, ha='center')
            self.canvas.draw()

    def onkeypress(event):
        if event.key == 'shift':
            global shift_is_held
            shift_is_held = True

    def onkeyrelease(event):
        if event.key == 'shift':
            global shift_is_held
            shift_is_held = False

    def undo(self):
        try:
            self.labels.pop()
            del self.ax.texts[len(self.ax.texts)-1]
            self.canvas.draw()
        except IndexError:
            return

    def eraseAll(self):
        try:
            self.labels = []
            self.ax.texts = []
            self.canvas.draw()
        except:
            return

    #Allows the user to manually define an isotope by giving the isotopic mass and atomic number
    def manualEnter(self):
        newIso = Toplevel(self.root)
        newIso.geometry('400x300')
        newIso.wm_title("User-Defined Isotope")
        if platform.system() == 'Windows':
            try:
                newIso.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        L4 = Label(newIso, text = 'Enter the information\n for the desired isotope', font = font3)
        L4.place(relx=0.5, rely=0.15, anchor = CENTER)
        L5 = Label(newIso, text = 'Atomic Number, Z:', font = font2)
        L5.place(relx=0.5, rely=0.4, anchor = E)
        E3 = Entry(newIso, font = font2, width = 10)
        E3.place(relx=0.5, rely=0.4, anchor = W)

        L6 = Label(newIso, text = 'Isotopic Mass, A:', font = font2)
        L6.place(relx=0.5, rely=0.5, anchor = E)
        E4 = Entry(newIso, font = font2, width = 10)
        E4.place(relx=0.5, rely=0.5, anchor = W)
        L7 = Label(newIso, text = 'amu', font = font2)
        L7.place(relx=0.74, rely=0.5, anchor = W)
        b2 = Button(newIso, text = 'Run Comparison', relief = 'raised', activebackground='blue', font = font1, width = 15, height = 2, command = lambda: [self.elementComparison(int(E3.get()), float(E4.get()), "User-Defined Isotope"),newIso.destroy()])
        b2.place(relx=0.5, rely=0.8, anchor = CENTER)


    #Analyzes spectrum and compares to all isotopes present in the json file
    def autoAnalyze(self):
        autoanalysis = Toplevel(self.root)
        autoanalysis.geometry('800x600')
        autoanalysis.wm_title("results for Auto-Analysis")
        autoanalysis.configure(bg='white')
        if platform.system() == 'Windows':
            try:
                autoanalysis.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        v = Scrollbar(autoanalysis, orient = 'vertical')
        t = Text(autoanalysis, font = font4, width = 100, height = 100, wrap = NONE, yscrollcommand = v.set)
        
        results = []

        for Z in range(1,118):
            charge = Z
            matches = self.isotopes.loc[self.isotopes['atomic_number']==Z]
            element = matches['symbol'].iloc[0]
            massVector = []
            abundVector = []

            for i in range(0, len(matches)):
                mass = matches['mass'].iloc[i]
                abund = matches['abundance'].iloc[i]
                massVector.append(mass)
                abundVector.append(abund)

            for i in range(0, len(massVector)):
                mass = massVector[i]
                abundance = abundVector[i]
                if mass > 0:
                    matches, chargeStates = self.crossCheck(element, mass, charge)
                    result = [element, mass, charge, matches, chargeStates, abundance]
                    results.append(result)

        veryLikely = []
        possible = []
        unlikely = []
        none = []
        for result in results:
            if result[3]/result[2] >= 2/3:
                veryLikely.append(result)
            elif result[3]/result[2] >= 1/3:
                possible.append(result)
            elif result[3]/result[2] == 0:
                none.append(result)
            else:
                unlikely.append(result)


        t.insert(END, "Very Likely:\n-------------------------\n")
        for result in veryLikely:
            t.insert(END, f'Isotope: {result[0]}-{int(round(result[1],0))}\n')
            t.insert(END, 'Matches: ')
            for chargeState in result[4]:
                t.insert(END, chargeState + '     ')
            t.insert(END, f'\nAbundance: {round(result[5]*100,1)}%')
            t.insert(END, '\n\n')


        t.insert(END, "\n\nSomewhat Likely:\n-------------------------\n")
        for result in possible:
            t.insert(END, 'Isotope: ' + result[0] + '-' + str(int(round(result[1],0))) + '\n')
            t.insert(END, 'Matches: ')
            for chargeState in result[4]:
                t.insert(END, chargeState + '     ')
            t.insert(END, f'\nAbundance: {round(result[5]*100,1)}%')
            t.insert(END, '\n\n')

        t.insert(END, "\n\nUnlikely:\n-------------------------\n")
        for result in unlikely:
            t.insert(END, 'Isotope: ' + result[0] + '-' + str(int(round(result[1],0))) + '\n')
            t.insert(END, 'Matches: ')
            for chargeState in result[4]:
                t.insert(END, chargeState + '     ')
            t.insert(END, f'\nAbundance: {round(result[5]*100,1)}%')
            t.insert(END, '\n\n')

        t.insert(END, "\n\nNone:\n-------------------------\n")
        for result in none:
            t.insert(END, 'Isotope: ' + result[0] + '-' + str(int(round(result[1],0))))
            t.insert(END, f'\nAbundance: {round(result[5]*100,1)}%\n\n')
                        
        t.pack(side=TOP, fill=X)
        v.config(command=t.yview)

        resultText = t.get("1.0","end-1c")
        autoanalysis.bind("<Control-s>", lambda eff: CSA.saveAutoAnalysisResults(resultText))

    #When called, this functions writes the results of the autoAnalyze function to a text file
    def saveAutoAnalysisResults(resultText):
        fileName = str(filedialog.asksaveasfile(initialdir = desktop,title = "Save",filetypes = (("Text Document","*.txt*"),("Text Document","*.txt*"))))
        fileName = fileName.split("'")
        fileName = fileName[1]
        outputFile = open(fileName + '.txt', "w")
        outputFile.write(resultText)
        outputFile.close()
        os.remove(fileName)

    #Checks to see if there are any charge states that match the spectrum, and if so returns how many and which ones are matches
    def crossCheck(self, element, mass, charge):
        mpq = self.a*np.square(self.R*self.B/1000)/(2*self.V)
        q = mass/mpq
        peak_index = find_peaks(self.I, height=0)
        peak_q = q[peak_index[0]]
        
        chargeStates = []
        present = False
        for i in range(0, len(peak_q)):
            for j in range(1, charge):
                if abs(peak_q[i]-j) < 0.04:
                    name = element + str(j) + '+'
                    if len(chargeStates) > 0:
                        present = False
                        for k in range(0, len(chargeStates)):
                            if chargeStates[k]==name:
                                present = True
                    if not present:
                        chargeStates.append(name)
        matches = len(chargeStates)
                            
                        
        return matches, chargeStates

    #Primarily for debugging purposes
    def checkboxTest(element):
        return

    #Opens a window that allows the user to make various selections and start a calibration
    def calibration(self):
        if self.header != {}:
            self.energy = self.header["U_0"]-self.header["U_A"]
        print(self.calibration_elements)
        options = Toplevel(self.root)
        options.geometry('350x350')
        options.wm_title("Calibration Options")
        options.configure(bg='white')
        if platform.system() == 'Windows':
            try:
                options.iconbitmap("icons/calibration.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        Label(options, text = 'Select elements that you think\n could be present', bg='white', font = font2).place(relx=0.5, rely=0.1, anchor = CENTER)
        
        carbon = IntVar(value=int(self.calibration_elements[0]))
        check1 = Checkbutton(options, text="C", variable=carbon, onvalue = 1, offvalue = 0, bg='white', font = font4, command=lambda:CSA.checkboxTest(carbon))
        check1.place(relx=0.4, rely=0.25, anchor=CENTER)
        
        nitrogen = IntVar(value=int(self.calibration_elements[1]))
        check2 = Checkbutton(options, text="N", variable=nitrogen, bg='white', font = font4, command=lambda:CSA.checkboxTest(nitrogen))
        check2.place(relx=0.4, rely=0.35, anchor=CENTER)
        
        oxygen = IntVar(value=int(self.calibration_elements[2]))
        check3 = Checkbutton(options, text="O", variable=oxygen, bg='white', font = font4, command=lambda:CSA.checkboxTest(oxygen))
        check3.place(relx=0.4, rely=0.45, anchor=CENTER)
        
        neon = IntVar(value=int(self.calibration_elements[3]))
        check4 = Checkbutton(options, text="Ne", variable=neon, bg='white', font = font4, command=lambda:CSA.checkboxTest(neon))
        check4.place(relx=0.6, rely=0.25, anchor=CENTER)
        
        argon = IntVar(value=int(self.calibration_elements[4]))
        check5 = Checkbutton(options, text="Ar", variable=argon, bg='white', font = font4, command=lambda:CSA.checkboxTest(argon))
        check5.place(relx=0.6, rely=0.35, anchor=CENTER)
        
        krypton = IntVar(value=int(self.calibration_elements[5]))
        check6 = Checkbutton(options, text="Kr", variable=krypton, bg='white', font = font4, command=lambda:CSA.checkboxTest(krypton))
        check6.place(relx=0.6, rely=0.45, anchor=CENTER)

        Label(options, text = 'Beam Energy:', bg='white', font = font2).place(relx=0.5, rely=0.6, anchor=E)
        E1 = Entry(options, bg='lightcyan', font = font2, width = 6)
        E1.place(relx=0.5, rely=0.6, anchor=W)
        E1.insert(0,int(self.energy))
        Label(options, text = 'eV/q', bg='white', font=font2).place(relx=0.7, rely=0.6, anchor=W)

        b1 = Button(options, text = 'Run Calibration', relief = 'raised', background='lightblue', activebackground='blue', font = font1, width = 15, height = 2,\
                    command = lambda: [self.updateSettings(self.V, self.R, int(float(E1.get())), [carbon.get(), nitrogen.get(), oxygen.get(), neon.get(), argon.get(), krypton.get()]), multiThreading(self.newCalibrateV), options.destroy()])
        b1.place(relx=0.5, rely=0.8, anchor = CENTER)

    #Aims to select a value for V that maximizes the number of peaks that align with the elements selected by the user
    def newCalibrateV(self):
        self.calibrate = True
        status = Toplevel(self.root)
        status.geometry('350x150')
        status.wm_title("Calibration")
        status.configure(bg='white')
        if platform.system() == 'Windows':
            try:
                status.iconbitmap("icons/calibration.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        L0 = Label(status, text = 'Calibrating...', bg='white', font = font2)
        L0.place(relx=0.5, rely=0.3, anchor = CENTER)
        progress = ttk.Progressbar(status, orient = HORIZONTAL, length = 300)
        progress.place(relx=0.5, rely=0.5, anchor=CENTER)
        progress.config(mode = 'determinate', maximum=100, value = 0)

        t1 = time.time()
        atoms = []
        possible_elements = ['C', 'N', 'O', 'Ne', 'Ar', 'Kr']
        for i in range(0, len(self.calibration_elements)):
            if self.calibration_elements[i] == 1:
                atoms.append(possible_elements[i])
        fudgeArray = np.arange(max(self.energy-2000,1), self.energy+1, dtype=int)
        peak_index = find_peaks(self.I, height=0.5, width=3)
        peak_B = self.B[peak_index[0]]
        #print(peak_B)
        #print(len(peak_B))

        mpqArray = []
        for atom in atoms:
            matches = self.isotopes.loc[self.isotopes['symbol']==atom]
            #print(matches)

            massVector = []
            abundVector = []
            for i in range(0, len(matches)):
                mass = matches['mass'].iloc[i]
                abund = matches['abundance'].iloc[i]
                massVector.append(mass)
                abundVector.append(abund)
            
            massArray = np.array(massVector)
            abundArray = np.array(abundVector)
            mass = massArray[np.argmax(abundArray)]
            charge = matches['atomic_number'].iloc[0]
            #print(f'mass={mass}')
            #print(f'charge={charge}')
            while charge > 0:
                mpqArray.append(mass/charge)
                charge = charge - 1
        mpqArray = np.array(mpqArray)
        matches = []

        if fudgeArray[0]==1:
            interval = int((fudgeArray[len(fudgeArray)-1]-(fudgeArray[0]-1))/20)
        else:
            interval = int((fudgeArray[len(fudgeArray)-1]-(fudgeArray[0]))/20)
        start = fudgeArray[0]
        n = 0
        for fudge in fudgeArray:
            #Steps up progress bar by 4%
            if fudge == start+n*interval:
                progress.step(5)
                n = n + 1

            B_peak_array = (1000/self.R)*np.sqrt((2*fudge*mpqArray)/self.a)
            num_matches = 0
            for B in B_peak_array:
                for peak in peak_B:
                    if abs(B-peak) < 0.2:
                        num_matches = num_matches + 1
            if num_matches > 0:
                matches.append([fudge, num_matches])
        progress.step(5)
        
        matches = np.array(matches)
        print(f'matches={matches}')
        arg_matches = np.where(matches[:,1]==np.amax(matches[:,1]))[0]
        #index = int(len(arg_matches)/2-1)
        #middle_match = arg_matches[index]
        #middle_match_V = matches[middle_match,0]

        mode_match_V = int(mode(np.round(matches[arg_matches,0]/10)*10)[0])
        #print(f'mode={mode_match_V}')
        #print(f'middle={middle_match_V}')
        self.V = mode_match_V
        t2 = time.time()-t1
        print(t2)

        L0.destroy()
        progress.destroy()
        L1 = Label(status, text = 'Calibration Complete', bg='white', font = font2)
        L1.place(relx=0.5, rely=0.3, anchor = CENTER)
        L2 = Label(status, text = 'Setting V='+ str(self.V), bg = 'white', font = font4)
        L2.place(relx=0.5, rely=0.5, anchor = CENTER)
        L3 = Label(status, text = 'New Calibration Routine', bg = 'white', fg = 'green', font = font4)
        L3.place(relx=0.5, rely=0.8, anchor = CENTER)

        self.updateSettings(self.V, self.R, self.energy, self.calibration_elements)
                        
    #Aims to select a value for V that maximizes the number of peaks that align with the elements selected by the user
    def calibrateV(self):
        self.calibrate = True

        status = Toplevel(self.root)
        status.geometry('350x150')
        status.wm_title("Calibration")
        status.configure(bg='white')
        if platform.system() == 'Windows':
            try:
                status.iconbitmap("icons/calibration.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        L0 = Label(status, text = 'Calibrating...', bg='white', font = font2)
        L0.place(relx=0.5, rely=0.3, anchor = CENTER)
        progress = ttk.Progressbar(status, orient = HORIZONTAL, length = 300)
        progress.place(relx=0.5, rely=0.5, anchor=CENTER)
        progress.config(mode = 'determinate', maximum=100, value = 0)

        t1 = time.time()
        atoms = []
        possible_elements = ['C', 'N', 'O', 'Ne', 'Ar', 'Kr']
        for i in range(0, len(self.calibration_elements)):
            if self.calibration_elements[i] == 1:
                atoms.append(possible_elements[i])
        modes = []
        fudgeArray = np.arange(max(self.energy-4000,1), self.energy+1001, dtype=int)
        totalNumMatchesArray = np.zeros(len(fudgeArray),dtype=int)

        for atom in atoms:
            matches = self.isotopes.loc[self.isotopes['symbol']==atom]
            print(matches)

            massVector = []
            abundVector = []
            for i in range(0, len(matches)):
                mass = matches['mass'].iloc[i]
                abund = matches['abundance'].iloc[i]
                massVector.append(mass)
                abundVector.append(abund)
            
            massArray = np.array(massVector)
            abundArray = np.array(abundVector)
            mass = massArray[np.argmax(abundArray)]
            charge = matches['atomic_number'].iloc[0]

            matchVector = []
            chargeStateVector = []
            
            print(fudgeArray)
            for fudge in fudgeArray:
                mpqArray = self.a*np.square(self.R*self.B/1000)/(2*fudge)
                q = mass/mpqArray
                peak_index = find_peaks(self.I, height=0.5, width=3)
                peak_q = q[peak_index[0]]
                if fudgeArray[0]==1:
                    interval = (fudgeArray[len(fudgeArray)-1]-(fudgeArray[0]-1))/5
                else:
                    interval = (fudgeArray[len(fudgeArray)-1]-(fudgeArray[0]))/5
                start = fudgeArray[0]
                #Steps up progress bar by 4%
                if fudge == start+interval or fudge == start+2*interval or fudge == start+3*interval or fudge == start+4*interval:
                    progress.step(20/len(atoms))
                    
                chargeStates = []
                present = False
                for i in range(0, len(peak_q)):
                    for j in range(1, charge):
                        if abs(peak_q[i]-j) < 0.03:
                            name = atom + str(j) + '+'
                            if len(chargeStates) > 0:
                                present = False
                                for k in range(0, len(chargeStates)):
                                    if chargeStates[k]== atom + str(j) + '+':
                                        present = True
                            if not present:
                                chargeStates.append(name)
                chargeStateVector.append(chargeStates)
                matches = len(chargeStates)
                matchVector.append(matches)

            matchArray = np.array(matchVector)
            totalNumMatchesArray = np.add(totalNumMatchesArray,matchArray)
            max_index = np.argmax(matchArray)
            possibleMatches = []
            for i in range(0,len(matchArray)):
                if matchArray[i] == matchArray[max_index]:
                    possibleMatches.append(fudgeArray[i])
            print(atom)
            print(chargeStateVector[max_index])
            print(possibleMatches)
            roundedMatches = []
            for number in possibleMatches:
                roundedNum = round(number/10,0)*10
                roundedMatches.append(roundedNum)
                roundedMatchesArray = np.array(roundedMatches)
            print(mode(roundedMatchesArray)[0])
            print(matchArray[max_index])
            modes.append(mode(roundedMatchesArray)[0][0])
            #Steps up progress bar by 4%
            progress.step(20/len(atoms))
        modeArray = np.array(modes)

        roundedModeV = int(mode(modeArray)[0][0])
        numModeMatches = int(mode(modeArray)[1][0])

        maxMatches = totalNumMatchesArray[np.argmax(totalNumMatchesArray)]
        maxMatchV = fudgeArray[np.where(totalNumMatchesArray==maxMatches)[0]]
        roundedMaxMatchV = int(mode(np.round(maxMatchV/10)*10)[0])

        print('Max Peaks V: ' + str(roundedMaxMatchV))

        print('Mode V='+ str(int(mode(modeArray)[0][0])))
        print('Number of mode matches: ' + str(mode(modeArray)[1][0]))
        print('Total Time: ' + str(time.time()-t1))


        if numModeMatches > 1 and abs(roundedModeV-roundedMaxMatchV) < 20:
            L0.destroy()
            progress.destroy()
            L1 = Label(status, text = 'Calibration Complete', bg='white', font = font2)
            L1.place(relx=0.5, rely=0.3, anchor = CENTER)
            L2 = Label(status, text = 'Setting V='+ str(roundedModeV), bg = 'white', font = font4)
            L2.place(relx=0.5, rely=0.5, anchor = CENTER)
            L3 = Label(status, text = 'High Confidence', bg = 'white', fg = 'green', font = font4)
            L3.place(relx=0.5, rely=0.8, anchor = CENTER)

            self.V = roundedModeV
            print('High Confidence')
            self.updateSettings(self.V, self.R, self.energy, self.calibration_elements)

        elif numModeMatches > 1:
            L0.destroy()
            progress.destroy()
            L1 = Label(status, text = 'Calibration Complete', bg='white', font = font2)
            L1.place(relx=0.5, rely=0.3, anchor = CENTER)
            L2 = Label(status, text = 'Setting V='+ str(roundedModeV), bg = 'white', font = font4)
            L2.place(relx=0.5, rely=0.5, anchor = CENTER)
            L3 = Label(status, text = 'Medium Confidence', bg = 'white', fg = 'yellow', font = font4)
            L3.place(relx=0.5, rely=0.8, anchor = CENTER)

            self.V = roundedModeV
            print('Medium')
            self.updateSettings(self.V, self.R, self.energy, self.calibration_elements)

        elif roundedMaxMatchV < self.energy:
            L0.destroy()
            progress.destroy()
            L1 = Label(status, text = 'Calibration Complete', bg='white', font = font2)
            L1.place(relx=0.5, rely=0.3, anchor = CENTER)
            L2 = Label(status, text = 'Setting V='+ str(roundedMaxMatchV), bg = 'white', font = font4)
            L2.place(relx=0.5, rely=0.5, anchor = CENTER)
            L3 = Label(status, text = 'Medium Confidence', bg = 'white', fg = 'orange', font = font4)
            L3.place(relx=0.5, rely=0.8, anchor = CENTER)

            self.V = roundedMaxMatchV
            print('Medium Confidence')
            self.updateSettings(self.V, self.R, self.energy, self.calibration_elements)

        elif int(modeArray[len(modeArray)-1]) < self.energy:
            L0.destroy()
            progress.destroy()
            L1 = Label(status, text = 'Calibration Complete', bg='white', font = font2)
            L1.place(relx=0.5, rely=0.3, anchor = CENTER)
            L2 = Label(status, text = 'Setting V='+ str(int(modeArray[len(modeArray)-1])), bg = 'white', font = font4)
            L2.place(relx=0.5, rely=0.5, anchor = CENTER)
            L3 = Label(status, text = 'Low Confidence', bg = 'white', fg = 'red', font = font4)
            L3.place(relx=0.5, rely=0.8, anchor = CENTER)

            self.V = int(modeArray[len(modeArray)-1])
            print('V='+str(self.V))
            print('Low Confidence')
            self.updateSettings(self.V, self.R, self.energy, self.calibration_elements)
        
        else:
            L0.destroy()
            progress.destroy()
            L1 = Label(status, text = 'Calibration Complete', bg='white', font = font2)
            L1.place(relx=0.5, rely=0.3, anchor = CENTER)
            L2 = Label(status, text = 'Setting V='+ str(roundedModeV), bg = 'white', font = font4)
            L2.place(relx=0.5, rely=0.5, anchor = CENTER)
            L3 = Label(status, text = 'Low Confidence', bg = 'white', fg = 'red', font = font4)
            L3.place(relx=0.5, rely=0.8, anchor = CENTER)

            self.V = roundedModeV
            print('V='+str(self.V))
            print('Low Confidence')
            self.updateSettings(self.V, self.R, self.energy, self.calibration_elements)        

    #This is the GUI for the software
    def makeGui(self, root=None):
        global first
        if root == None:
            self.root = Tk()
        else:
            self.root = root
        menu = Menu(self.root)
        self.root.config(menu=menu)

        self.root.title("CUEBIT Spectrum Analyzer")
        self.root.geometry("1200x768")
        self.root.configure(bg='white')
        self.root.protocol("WM_DELETE_WINDOW", self.quitProgram)
        if platform.system() == 'Windows':
            try:
                self.root.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')

        #Creates intro message
        introMessage ='Import a data file to begin'
        introMessageVar = Message(self.root, text = introMessage, font = font2, width = 600)
        introMessageVar.config(bg='white', fg='grey')
        introMessageVar.place(relx = 0.5, rely = 0.5, anchor = CENTER)
        introMessageVar.bind('<Button-1>', lambda  eff: self.askopenfile())

        #Creates File menu
        filemenu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Import", command=lambda: self.askopenfile(), accelerator="Ctrl+I")
        filemenu.add_command(label="Save", command=lambda: CSA.saveGraph(), accelerator="Ctrl+S")
        filemenu.add_command(label='Settings', command=lambda: self.Settings())
        filemenu.add_command(label='Calibrate', command=lambda: self.calibration())
        filemenu.add_separator()
        filemenu.add_command(label='New Window', command=lambda: startProgram(Toplevel(self.root)))
        filemenu.add_command(label='Exit', command=lambda: self.quitProgram())

        #Creates Analysis menu
        analysismenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='Analysis', menu=analysismenu)
        analysismenu.add_command(label='Auto-Analyze', command= lambda: self.autoAnalyze(), accelerator="Ctrl+R")
        analysismenu.add_command(label='I vs B', command= lambda: self.plotData())
        analysismenu.add_command(label='A/q', command= lambda: self.massToCharge())
        analysismenu.add_separator()
        analysismenu.add_command(label='Be', command= lambda: self.elementComparison(4, 9, "Beryllium-9"))
        analysismenu.add_command(label='C', command= lambda: self.elementComparison(6, 12, "Carbon-12"))
        analysismenu.add_command(label='N', command= lambda: self.elementComparison(7, 14, "Nitrogen-14"))
        analysismenu.add_command(label='O', command= lambda: self.elementComparison(8, 16, "Oxygen-16"))
        analysismenu.add_command(label='F', command= lambda: self.elementComparison(9, 19, "Fluorine-19"))
        analysismenu.add_command(label='Ne', command= lambda: self.elementComparison(10, 20, "Neon-20"))
        analysismenu.add_command(label='Mg', command= lambda: self.elementComparison(12, 24, "Magnesium-24"))
        analysismenu.add_command(label='Si', command= lambda: self.elementComparison(14, 28, "Silicon-28"))
        analysismenu.add_command(label='P', command= lambda: self.elementComparison(15, 31, "Phosphorus-31"))
        analysismenu.add_command(label='Ar', command= lambda: self.elementComparison(18, 40, "Argon-40"))
        analysismenu.add_command(label='Fe', command= lambda: self.elementComparison(26, 56, "Iron-56"))
        analysismenu.add_command(label='Kr', command= lambda: self.elementComparison(36, 84, "Krypton-84"))
        analysismenu.add_separator()
        analysismenu.add_command(label='OH', command= lambda: self.elementComparison(9, 17, "OH"))
        analysismenu.add_command(label='H2O', command= lambda: self.elementComparison(10, 18, "H$_2$O"))
        analysismenu.add_command(label='CO2', command= lambda: self.elementComparison(20, 44, "CO$_2$"))
        analysismenu.add_separator()
        analysismenu.add_command(label='Other', command= lambda: self.manualEnter())

        #Creates Help menu
        helpmenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='Help', menu=helpmenu)
        helpmenu.add_command(label='Instructions', command= lambda: self.Instructions())
        helpmenu.add_command(label='Periodic Table', command= lambda: self.PTable(), accelerator="Ctrl+P")
        helpmenu.add_command(label='About', command= lambda: self.About())

        #Binds keyboard shortcuts to functions
        self.root.bind_all("<Control-i>", lambda eff: self.askopenfile())
        #self.root.bind("<Control-s>", lambda eff: CSA.saveGraph())
        self.root.bind_all("<Control-r>", lambda eff: self.autoAnalyze())
        self.root.bind_all("<Control-p>", lambda eff: self.PTable())
        self.root.bind("<Control-z>", lambda eff: self.undo())
        self.root.bind("<Control-a>", lambda eff: self.eraseAll())

        #Allows another program to open spectrum analyzer and provide an input file to be read
        if len(sys.argv) > 1 and first:
            print('Program started remotely by another program')
            self.getData(sys.argv[1])
            first = False

        self.root.mainloop()

startProgram()

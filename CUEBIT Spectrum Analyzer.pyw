#EBIT Ion Beam Analyzer
#Author: Richard Mattish
#Last Updated: 06/10/2021

#Function:  This program provides a graphical user interface for quickly importing
#           EBIT data files and comparing them to several of the most common elements
#           and gases, as well as the option to define your own isotope.


#Imports necessary packages
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import style
from matplotlib.figure import Figure
import numpy as np
from tkinter import *
from tkinter import ttk
from scipy.signal import find_peaks
from scipy.stats import mode
import sys
import os
import time
import datetime
from decimal import Decimal
from tkinter import filedialog
from PIL import ImageTk, Image
import json
import threading


#Defines global variables
global canvas
global filename
global B
global I
global a
global R
global graph
global calibrate_run
global modes
global graphType
global calibrate
global calibration_elements
global energy

calibrate_run = 0
modes = []
graphType = 0
calibrate = False


#Defines location of the Desktop as well as font and text size for use in the software
desktop = os.path.expanduser("~\Desktop")
font1 = ('Helvetica', 16)
font2 = ('Helvetica', 14)
font3 = ('Helvetica', 18)
font4 = ('Helvetica', 12)
textSize = 20
graph = False

#Loads the variables V and R from the variables file, and creates the file if none exists
try:
    f = open('variables', 'r')
    variables = f.readlines()
    V = float(variables[0].split('=')[1])
    R = float(variables[1].split('=')[1])
    energy = int(variables[2].split('=')[1])
    carbon = int(variables[3].split('=')[1])
    nitrogen = int(variables[4].split('=')[1])
    oxygen = int(variables[5].split('=')[1])
    neon = int(variables[6].split('=')[1])
    argon = int(variables[7].split('=')[1])
    krypton = int(variables[8].split('=')[1])
    calibration_elements = [carbon, nitrogen, oxygen, neon, argon, krypton]
except:
    V = 3330
    R = 0.35
    energy = 4500
    calibration_elements = [1, 1, 1, 0, 1, 0]
    f = open("variables",'w')
    f.write('V='+str(V)+'\n'+'R='+str(R)+'\n'+'energy='+str(energy)+'\n')
    f.write('carbon=1\nnitrogen=1\noxygen=1\nneon=0\nargon=1\nkrypton=0')
    f.close()
    
#Charge to mass ratio of a proton
a = 1.6022E-19/1.6605E-27 

#Opens About Window with description of software
def About():
    helpMessage ='This program aims to provide easy analysis\n of EBIT charge state spectra. To begin, \nimport a data file using the File menu.'
    copyrightMessage ='Copyright © 2021 Richard Mattish All Rights Reserved.'
    t = Toplevel(root)
    t.wm_title("About")
    t.configure(background='white')
    l = Label(t, text = helpMessage, bg='white', font = font2)
    l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
    messageVar = Message(t, text = copyrightMessage, bg='white', fg='blue', font = font2, width = 600)
    messageVar.place(relx = 0.5, rely = 1, anchor = S)

def Instructions():
    instructions = Toplevel(root)
    instructions.geometry('1280x720')
    instructions.wm_title("User Instructions")
    instructions.configure(bg='white')
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


    t.pack(side=TOP, fill=X)
    v.config(command=t.yview)
    

#Opens Settings Window, which allows the user to change the persistent global variables V and R
def Settings():
    global V
    global R
    global calibration_elements
    t = Toplevel(root)
    t.geometry('400x300')
    t.wm_title("Settings")
    L0 = Label(t, text = 'Settings', font = font3)
    L0.place(relx=0.5, rely=0.15, anchor = CENTER)
    L1 = Label(t, text = 'V:', font = font2)
    L1.place(relx=0.4, rely=0.3, anchor = E)
    E1 = Entry(t, font = font2, width = 10)
    E1.insert(0,str(V))
    E1.place(relx=0.4, rely=0.3, anchor = W)

    L2 = Label(t, text = 'R:', font = font2)
    L2.place(relx=0.4, rely=0.4, anchor = E)
    E2 = Entry(t, font = font2, width = 10)
    E2.insert(0,str(R))
    E2.place(relx=0.4, rely=0.4, anchor = W)
    L3 = Label(t, text = 'm', font = font2)
    L3.place(relx=0.64, rely=0.4, anchor = W)
        
    b1 = Button(t, text = 'Update & Close', relief = 'raised', background='lightblue', activebackground='blue', font = font1, width = 15, height = 2,\
                command = lambda: [updateSettings(float(E1.get()),float(E2.get()), energy, calibration_elements),t.destroy()])
    b1.place(relx=0.5, rely=0.6, anchor = CENTER)

    b2 = Button(t, text = 'Reset', relief = 'raised', background='pink', activebackground='red', font = font1, width = 10, height = 1, command = lambda: [updateSettings(3330,0.35, 4500, [1, 1, 1, 0, 1, 0]),t.destroy()])
    b2.place(relx=0.5, rely=0.9, anchor = CENTER)

#Updates the persistent global variables V and R, as well as store which elements the user has selected for calibration
def updateSettings(E1, E2, E3, E4):
    global V
    global R
    global graphType
    global calibrate
    global energy
    global calibration_elements
    V = E1
    R = E2
    energy = int(E3)
    calibration_elements = E4
    names = ['carbon', 'nitrogen', 'oxygen', 'neon', 'argon', 'krypton']
    f = open("variables",'w')
    f.write('V='+str(V)+'\n'+'R='+str(R)+'\n'+'energy='+str(energy)+'\n')
    for i in range(0,len(calibration_elements)):
        f.write(names[i] + '=' + str(calibration_elements[i]) + '\n') 
    f.close()

    if calibrate:
        print("I should see this")
        calibrate = False
        sys.exit()

    if graphType == 0:
        print('no graph needs changes')
    elif graphType == 1:
        massToCharge()
    else:
        graphType = graphType.split(',')
        Z = int(graphType[0])
        A = float(graphType[1])
        x_label = graphType[2]
        elementComparison(Z, A, x_label)
        
    
#Used to import an EBIT data file into the software
def askopenfile():
    global filename
    filename = filedialog.askopenfilename(initialdir = desktop,title = "Select file",filetypes = (("all files","*.*"),("all files","*.*")))
    plotData()

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
def PTable():
    ptable = Toplevel(root)
    ptable.geometry('1920x1080')
    ptable.configure(bg='white')
    ptable.wm_title('Periodic Table')
    load = Image.open('PeriodicTable.png')
    render = ImageTk.PhotoImage(load)
    img = Label(ptable, image=render)
    img.image = render
    img.pack(side="top",fill='both',expand=True)

def quitProgram():
    print('quit')
    root.quit()
    root.destroy()

def getData():
    global filename
    global B
    global I
    data = np.genfromtxt(filename)
    B = data[:,1]
    I = data[:,2]

#Creates a plot of the raw EBIT data for current vs. B-field
def plotData():
    global B
    global I
    global canvas
    global plt
    global graph
    global filename

    try:
        canvas.get_tk_widget().destroy()
    except:
        pass
    getData()
    x_min = np.amin(B)
    x_max = np.amax(B)

    title = filename.split('/')

    # creating the Matplotlib figure
    plt.close('all')
    fig, ax = plt.subplots(figsize = (16,9))
    ax.tick_params(which='both', direction='in')
    plt.rcParams.update({'font.size': textSize})
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontsize(textSize)
    plt.plot(B, I, color = (0.368417,0.506779,0.709798), linestyle = '-', linewidth = 2)
    plt.xlim([x_min,x_max])
    plt.xlabel('Magnetic Field (mT)',fontsize=textSize)
    plt.ylabel('Current (pA)',fontsize=textSize)
    plt.title(title[len(title)-1])

    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master = root)  
    canvas.draw()
  
    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack(side="top",fill='both',expand=True)

    # creating the Matplotlib toolbar
    if graph == False:
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()
        graph = True
  
    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()

#Creates a plot of current vs. mass-to-charge ratio
def massToCharge():
    global a
    global R
    global B
    global V

    global canvas
    global filename
    global graphType

    graphType = 1

    title = filename.split('/')

    try:
       canvas.get_tk_widget().destroy()
       plt.close('all')
       mpq = a*np.square(R*B/1000)/(2*V)
       x_min = np.amin(mpq)
       x_max = np.amax(mpq)
       fig, ax = plt.subplots(figsize = (16,9))
       ax.tick_params(which='both', direction='in')
       plt.rcParams.update({'font.size': textSize})
       for label in (ax.get_xticklabels() + ax.get_yticklabels()):
           label.set_fontsize(textSize)
       plt.plot(mpq, I, color = (0.368417,0.506779,0.709798), linestyle = '-', linewidth = 2)
       plt.xlim([x_min,x_max])
       plt.xlabel('A/q',fontsize=textSize)
       plt.ylabel('Current (pA)',fontsize=textSize)
       plt.title(title[len(title)-1])

       # creating the Tkinter canvas containing the Matplotlib figure
       canvas = FigureCanvasTkAgg(fig, master = root)
       canvas.draw()

       # placing the canvas on the Tkinter window
       canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
       
    except:
        helpMessage ='Please import a data file first.' 
        messageVar = Message(root, text = helpMessage, font = font2, width = 600) 
        messageVar.config(bg='lightgreen')
        messageVar.place(relx = 0, rely = 1, anchor = SW)

#Creates a plot of current vs. a given element's/gas's charge states for use in identifying if it is present in the ion beam
def elementComparison(Z, A, x_label):
    global a
    global R
    global B
    global V

    global canvas
    global filename
    global graphType

    graphType = str(Z)+','+str(A)+','+x_label

    title = filename.split('/')

    try:
       canvas.get_tk_widget().destroy()
       plt.close('all')
       mpq = a*np.square(R*B/1000)/(2*V)
       fig, ax = plt.subplots(figsize = (16,9))
       ax.tick_params(which='both', direction='in')
       plt.rcParams.update({'font.size': textSize})
       for label in (ax.get_xticklabels() + ax.get_yticklabels()):
           label.set_fontsize(textSize)
       for xc in range(1,Z+1):
           plt.axvline(x=xc, color='black', linestyle='--', linewidth = 1)
       plt.plot(A/mpq, I, color = (0.368417,0.506779,0.709798), linestyle = '-', linewidth = 2)
       plt.xlabel(x_label + " Charge State",fontsize=textSize)
       plt.ylabel('Current (pA)',fontsize=textSize)
       plt.title(title[len(title)-1])
       plt.xlim([0.5,Z+0.5])
       # creating the Tkinter canvas containing the Matplotlib figure
       canvas = FigureCanvasTkAgg(fig, master = root)
       canvas.draw()

       # placing the canvas on the Tkinter window
       canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
       
    except:
        helpMessage ='Please import a data file first.' 
        messageVar = Message(root, text = helpMessage, font = font2, width = 600) 
        messageVar.config(bg='lightgreen')
        messageVar.place(relx = 0, rely = 1, anchor = SW)

#Allows the user to manually define an isotope by giving the isotopic mass and atomic number
def manualEnter():
    newIso = Toplevel(root)
    newIso.geometry('400x300')
    newIso.wm_title("User-Defined Isotope")
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
    b2 = Button(newIso, text = 'Run Comparison', relief = 'raised', activebackground='blue', font = font1, width = 15, height = 2, command = lambda: [elementComparison(int(E3.get()), float(E4.get()), "User-Defined Isotope"),newIso.destroy()])
    b2.place(relx=0.5, rely=0.8, anchor = CENTER)


#Analyzes spectrum and compares to all isotopes present in the json file
def autoAnalyze():
    autoanalysis = Toplevel(root)
    autoanalysis.geometry('800x600')
    autoanalysis.wm_title("results for Auto-Analysis")
    autoanalysis.configure(bg='white')
    v = Scrollbar(autoanalysis, orient = 'vertical')
    t = Text(autoanalysis, font = font4, width = 100, height = 100, wrap = NONE, yscrollcommand = v.set)
    
    results = []
    with open('json_background.py') as f:
        J = json.load(f)
    for a in J['elements']:#finds element in json file and checks if the input is the same
        element=a['name']
        charge=a['charge']
        mass1=a['mass1']
        mass2=a['mass2']
        mass3=a['mass3']
        mass4=a['mass4']
        mass5=a['mass5']

        massVector = [mass1, mass2, mass3, mass4, mass5]

        for mass in massVector:
            if mass > 0:
                matches, chargeStates = crossCheck(element, mass, charge)
                result = [element, mass, charge, matches, chargeStates]
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
        t.insert(END, 'Isotope: ' + result[0] + '-' + str(int(round(result[1],0))) + '\n')
        t.insert(END, 'Matches: ')
        for chargeState in result[4]:
            t.insert(END, chargeState + '     ')
        t.insert(END, '\n\n')


    t.insert(END, "\n\nSomewhat Likely:\n-------------------------\n")
    for result in possible:
        t.insert(END, 'Isotope: ' + result[0] + '-' + str(int(round(result[1],0))) + '\n')
        t.insert(END, 'Matches: ')
        for chargeState in result[4]:
            t.insert(END, chargeState + '     ')
        t.insert(END, '\n\n')

    t.insert(END, "\n\nUnlikely:\n-------------------------\n")
    for result in unlikely:
        t.insert(END, 'Isotope: ' + result[0] + '-' + str(int(round(result[1],0))) + '\n')
        t.insert(END, 'Matches: ')
        for chargeState in result[4]:
            t.insert(END, chargeState + '     ')
        t.insert(END, '\n\n')

    t.insert(END, "\n\nNone:\n-------------------------\n")
    for result in none:
        t.insert(END, 'Isotope: ' + result[0] + '-' + str(int(round(result[1],0))) + '\n\n')
                    
    t.pack(side=TOP, fill=X)
    v.config(command=t.yview)

    resultText = t.get("1.0","end-1c")
    autoanalysis.bind("<Control-s>", lambda eff: saveAutoAnalysisResults(resultText))

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
def crossCheck(element, mass, charge):
    global B
    global I
    global V
    global a
    global R

    mpq = a*np.square(R*B/1000)/(2*V)
    q = mass/mpq
    peak_index = find_peaks(I, height=0)
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
    print('The box value is: '+format(element.get()))

#Opens a window that allows the user to make various selections and start a calibration
def calibration():
    global energy
    global calibration_elements
    #carbon = False
    #nitrogen = False
    #oxygen = False
    options = Toplevel(root)
    options.geometry('350x350')
    options.wm_title("Calibration Options")
    options.configure(bg='white')
    Label(options, text = 'Select elements that you think\n could be present', bg='white', font = font2).place(relx=0.5, rely=0.1, anchor = CENTER)
    
    carbon = IntVar(value=int(calibration_elements[0]))
    check1 = Checkbutton(options, text="C", variable=carbon, onvalue = 1, offvalue = 0, bg='white', font = font4, command=lambda:checkboxTest(carbon))
    check1.place(relx=0.4, rely=0.25, anchor=CENTER)
    
    nitrogen = IntVar(value=int(calibration_elements[1]))
    check2 = Checkbutton(options, text="N", variable=nitrogen, bg='white', font = font4, command=lambda:checkboxTest(nitrogen))
    check2.place(relx=0.4, rely=0.35, anchor=CENTER)
    
    oxygen = IntVar(value=int(calibration_elements[2]))
    check3 = Checkbutton(options, text="O", variable=oxygen, bg='white', font = font4, command=lambda:checkboxTest(oxygen))
    check3.place(relx=0.4, rely=0.45, anchor=CENTER)
    
    neon = IntVar(value=int(calibration_elements[3]))
    check4 = Checkbutton(options, text="Ne", variable=neon, bg='white', font = font4, command=lambda:checkboxTest(neon))
    check4.place(relx=0.6, rely=0.25, anchor=CENTER)
    
    argon = IntVar(value=int(calibration_elements[4]))
    check5 = Checkbutton(options, text="Ar", variable=argon, bg='white', font = font4, command=lambda:checkboxTest(argon))
    check5.place(relx=0.6, rely=0.35, anchor=CENTER)
    
    krypton = IntVar(value=int(calibration_elements[5]))
    check6 = Checkbutton(options, text="Kr", variable=krypton, bg='white', font = font4, command=lambda:checkboxTest(krypton))
    check6.place(relx=0.6, rely=0.45, anchor=CENTER)

    Label(options, text = 'Beam Energy:', bg='white', font = font2).place(relx=0.5, rely=0.6, anchor=E)
    E1 = Entry(options, bg='lightcyan', font = font2, width = 6)
    E1.place(relx=0.5, rely=0.6, anchor=W)
    E1.insert(0,str(energy))
    Label(options, text = 'eV/q', bg='white', font=font2).place(relx=0.7, rely=0.6, anchor=W)

    b1 = Button(options, text = 'Run Calibration', relief = 'raised', background='lightblue', activebackground='blue', font = font1, width = 15, height = 2,\
                command = lambda: [updateSettings(V, R, int(float(E1.get())), [carbon.get(), nitrogen.get(), oxygen.get(), neon.get(), argon.get(), krypton.get()]), multiThreading(), options.destroy()])
    b1.place(relx=0.5, rely=0.8, anchor = CENTER)

    

#Enables multi-threading so that the calibrateV process does not freeze main GUI
def multiThreading():
    t1=threading.Thread(target=calibrateV)
    t1.start()

#Aims to select a value for V that maximizes the number of peaks that align with the elements selected by the user
def calibrateV():
    global B
    global I
    global V
    global a
    global R
    
    global calibrate
    calibrate = True
    global energy
    global calibration_elements

    status = Toplevel(root)
    status.geometry('350x150')
    status.wm_title("Calibration")
    status.configure(bg='white')
    L0 = Label(status, text = 'Calibrating...', bg='white', font = font2)
    L0.place(relx=0.5, rely=0.3, anchor = CENTER)
    progress = ttk.Progressbar(status, orient = HORIZONTAL, length = 300)
    progress.place(relx=0.5, rely=0.5, anchor=CENTER)
    progress.config(mode = 'determinate', maximum=100, value = 0)

    t1 = time.time()
    atoms = []
    possible_elements = ['C', 'N', 'O', 'Ne', 'Ar', 'Kr']
    for i in range(0, len(calibration_elements)):
        if calibration_elements[i] == 1:
            atoms.append(possible_elements[i])
    modes = []
    numMatches = []
    for atom in atoms:
        results = []
        with open('json_background.py') as f:
            J = json.load(f)
        for e in J['elements']:#finds element in json file and checks if the input is the same
            element=e['name']
            if atom == element:
                charge=e['charge']
                mass=e['mass1']
        matchVector = []
        chargeStateVector = []

        fudgeArray = np.arange(max(energy-4000,1), energy+1001, dtype=int)
        
        print(fudgeArray)
        for fudge in fudgeArray:
            mpqArray = a*np.square(R*B/1000)/(2*fudge)
            q = mass/mpqArray
            peak_index = find_peaks(I, height=0)
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
    print('Setting V='+ str(int(mode(modeArray)[0][0])))
    print('Total Time: ' + str(time.time()-t1))
    L0.destroy()
    progress.destroy()
    L1 = Label(status, text = 'Calibration Complete', bg='white', font = font2)
    L1.place(relx=0.5, rely=0.3, anchor = CENTER)
    L2 = Label(status, text = 'Setting V='+ str(int(mode(modeArray)[0][0])), bg = 'white', font = font4)
    L2.place(relx=0.5, rely=0.5, anchor = CENTER)

    V = int(mode(modeArray)[0][0])
    updateSettings(V, R, energy, calibration_elements)





#This is the GUI for the software
root = Tk()
menu = Menu(root)
root.config(menu=menu)

root.title("EBIT Ion Beam Analyzer")
root.geometry("1200x768")
root.configure(bg='white')
root.protocol("WM_DELETE_WINDOW", quitProgram)

#Creates intro message
introMessage ='Import a data file to begin'
introMessageVar = Message(root, text = introMessage, font = font2, width = 600)
introMessageVar.config(bg='white', fg='grey')
introMessageVar.place(relx = 0.5, rely = 0.5, anchor = CENTER)

#Creates File menu
filemenu = Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Import", command=lambda: askopenfile(), accelerator="Ctrl+I")
filemenu.add_command(label="Save", command=lambda: saveGraph(), accelerator="Ctrl+S")
filemenu.add_command(label='Settings', command=lambda: Settings())
filemenu.add_command(label='Calibrate', command=lambda: calibration())
filemenu.add_separator()
filemenu.add_command(label='Exit', command=lambda: quitProgram())

#Creates Analysis menu
analysismenu = Menu(menu, tearoff=0)
menu.add_cascade(label='Analysis', menu=analysismenu)
analysismenu.add_command(label='Auto-Analyze', command= lambda: autoAnalyze(), accelerator="Ctrl+R")
analysismenu.add_command(label='A/q', command= lambda: massToCharge())
analysismenu.add_separator()
analysismenu.add_command(label='C', command= lambda: elementComparison(6, 12, "Carbon-12"))
analysismenu.add_command(label='N', command= lambda: elementComparison(7, 14, "Nitrogen-14"))
analysismenu.add_command(label='O', command= lambda: elementComparison(8, 16, "Oxygen-16"))
analysismenu.add_command(label='F', command= lambda: elementComparison(9, 19, "Fluorine-19"))
analysismenu.add_command(label='Ne', command= lambda: elementComparison(10, 20, "Neon-20"))
analysismenu.add_command(label='Mg', command= lambda: elementComparison(12, 24, "Magnesium-24"))
analysismenu.add_command(label='Si', command= lambda: elementComparison(14, 28, "Silicon-28"))
analysismenu.add_command(label='P', command= lambda: elementComparison(15, 31, "Phosphorus-31"))
analysismenu.add_command(label='Ar', command= lambda: elementComparison(18, 40, "Argon-40"))
analysismenu.add_command(label='Fe', command= lambda: elementComparison(26, 56, "Iron-56"))
analysismenu.add_separator()
analysismenu.add_command(label='OH', command= lambda: elementComparison(9, 17, "OH"))
analysismenu.add_command(label='H2O', command= lambda: elementComparison(10, 18, "H$_2$O"))
analysismenu.add_command(label='CO2', command= lambda: elementComparison(20, 44, "CO$_2$"))
analysismenu.add_separator()
analysismenu.add_command(label='Other', command= lambda: manualEnter())

#Creates Help menu
helpmenu = Menu(menu, tearoff=0)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='Instructions', command= lambda: Instructions())
helpmenu.add_command(label='Periodic Table', command= lambda: PTable(), accelerator="Ctrl+P")
helpmenu.add_command(label='About', command= lambda: About())

#Binds keyboard shortcuts to functions
root.bind_all("<Control-i>", lambda eff: askopenfile())
root.bind("<Control-s>", lambda eff: saveGraph())
root.bind_all("<Control-r>", lambda eff: autoAnalyze())
root.bind_all("<Control-p>", lambda eff: PTable())


root.mainloop()


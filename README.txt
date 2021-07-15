***************************************************************************************
Program: CUEBIT Spectrum Analyzer
Author: Richard Mattish
Last Updated: 06/10/2021

Function:  This program provides a graphical user interface for quickly importing
           EBIT data files and comparing them to several of the most common elements
           and gases, as well as the option to define your own isotope.
***************************************************************************************



Install Instructions
--------------------
1. To run, users must have python version 3.9 or newer installed on their machine.

2. In addition to the base install of python, the following packages are required:
	a. Scipy
		To install: python -m pip install scipy

	b. Numpy
		To install: python -m pip install numpy

	c. Pillow
		To install: python -m pip install pillow

	d. Matplotlib
		To install: python -m pip install matplotlib


User Instructions
--------------------
1. Open the file "CUEBIT Spectrum Analyzer.pyw"

2. Select the "Import" option from the drop-down File menu (File>Import) or use the shortcut <Ctrl+I>

3. Using the navigation window, navigate to an output file generated from the DREEBIT software and import it

4. Perform a calibration of the offset/fudge-factor V

	a. Automatic Calibration:
		1) Select "Calibrate" from the drop-down File menu (File>Calibrate). A separate options window will open
		2) Select all elements that you wish to use for calibration (usually those that you expect to be present in the spectrum)
		3) Enter the beam energy (drift tube voltage) that was set for that data run
		4) Select "Calibrate". A progress bar will appear. Allow calibration to complete before closing
		5) Once the calibration is marked complete, the returned value for V is displayed along with a confidence level
		6) The offset V has been calibrated. You may close the window

		Note: 	This method is quicker than manual calibration, but I do not guarantee it is always accurate.
			Always evaluate it's accuracy yourself afterwards using the Analysis menu's various options, 
			especially for values marked as low confidence!

	b. Manual Calibration:
		1) Select "Settings" from the drop-down File menu (File>Settings)
		2) Enter a new value for V in the appropriate box
		3) Select "Update and Close"
		4) Access various comparisons from the drop-down Analysis menu
		5) Visually compare/evaluate that setting for V using the graphs
		6) Repeat steps 1-5 as needed until a good value for V has been found

5. Perform a spectral analysis

	a. Automatic Analysis:
		1) Select "Auto-Anayze" from the drop-down Analysis menu (Analysis>Auto-Analylze) or use the shortcut <Ctrl+R>
		2) A separate window will open with the results of the analysis
		3) The results are binned as follows:
			Very Likely.....2/3 or more of charge states match peaks 		(matches >= 2/3)
			Possible........Between 1/3 and 2/3 of charge states match peaks 	(1/3 < matches < 2/3)
			Unlikely........Less than 1/3 of charge states match peaks 		(0 < matches < 1/3)
			None............No charge states match peaks 				(matches = 0)
		4) To save these results, click anywhere within the results window and use the <Ctrl+S> command

		Note:	This method is very useful for quickly obtaining a list of possible isotopes present in the spectrum.
			However, it will inevitably include possible isotopes which are not present. Use it as a way to
			narrow down the list of possible candidates, and evaluate the ones it gives further using the 
			"Manual Analysis" instructions to obtain the actual isotopes that are constituents of the beam.

	b. Manual Analysis:
		1) Select an isotope from the drop-down Analysis menu
		2) A graph will appear comparing the spectrum to that isotope's charge states
		3) Anything not on a vertical dashed line corresponding to that isotope's charge state should be ignored
		4) If the peaks align well with the charge states, that isotope may be present in the spectrum
		5) Repeat steps 1-4 for additional isotopes of interest
		6) If you want to evaluate an isotope other than the most abundant isotope of the given elements,
		   or of an element not listed in the Analysis menu, select the "Other" option
		7) Enter the atomic number Z and atomic mass (in amu) for the desired isotope, then select "Run Comparison"

6. To save the graph on screen, select "Save" from the drop-down File menu (File>Save) or use the shortcut <Ctrl+S>
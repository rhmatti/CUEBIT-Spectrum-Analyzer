# CUEBIT Spectrum Analyzer

Installation Instructions
--------------------
1. To run, users must have a version of python 3 installed on their machine.

2. In addition to the base install of python 3, the following packages are required:

	a. Scipy
	
		python -m pip install scipy

	b. Numpy
	
		python -m pip install numpy

	c. Pillow
	
		python -m pip install pillow

	d. Matplotlib
	
		python -m pip install matplotlib
3. Download the code as a .zip file, and extract all contents to the desired directory


User Instructions
--------------------
1. Open the file "CUEBIT Spectrum Analyzer.pyw"

2. Select the "Import" option from the drop-down File menu (File>Import) or use the shortcut `<Ctrl+I>`

3. Using the navigation window, navigate to an output file generated from the DREEBIT software and import it

4. Perform a calibration of the offset/fudge-factor V

	a. Automatic Calibration:
	* Select "Calibrate" from the drop-down File menu (File>Calibrate)
	* A separate progress window will open. Allow calibration to complete before closing
	* Once the calibration is marked complete, you may close the window
	* The offset V has been calibrated

		> Note: This method is quicker than manual calibration, but I do not guarantee it is always accurate. Always evaluate it's accuracy yourself afterwards using the Analysis menu's various options!

	b. Manual Calibration:
	* Select "Settings" from the drop-down File menu (File>Settings)
	* Enter a new value for V in the appropriate box
	* Select "Update and Close"
	* Access various comparisons from the drop-down Analysis menu
	* Visually compare/evaluate that setting for V using the graphs
	* Repeat these steps as needed until a good value for V has been found

5. Perform a spectral analysis

	a. Automatic Analysis:
	* Select "Auto-Anayze" from the drop-down Analysis menu (Analysis>Auto-Analylze) or use the shortcut `<Ctrl+R>`
	* A separate window will open with the results of the analysis
	* The results are binned as follows:

		* Very Likely.....2/3 or more of charge states match peaks 		(matches >= 2/3)
		
		* Possible........Between 1/3 and 2/3 of charge states match peaks 	(1/3 < matches < 2/3)
		
		* Unlikely........Less than 1/3 of charge states match peaks 		(0 < matches < 1/3)
		
		* None............No charge states match peaks 				(matches = 0)
		
	* To save these results, click anywhere within the results window and use the `<Ctrl+S>` command

		> Note: This method is very useful for quickly obtaining a list of possible isotopes present in the spectrum. However, it will inevitably include possible isotopes which are not present. Use it as a way to narrow down the list of possible candidates, and evaluate the ones it gives further using the "Manual Analysis" instructions to obtain the actual isotopes that are constituents of the beam.

	b. Manual Analysis:
	* Select an isotope from the drop-down Analysis menu
	* A graph will appear comparing the spectrum to that isotope's charge states
	* Anything not on a vertical dashed line corresponding to that isotope's charge state should be ignored
	* If the peaks align well with the charge states, that isotope may be present in the spectrum
	* Repeat steps these steps for additional isotopes of interest
	* If you want to evaluate an isotope other than the most abundant isotope of the given elements, or of an element not listed in the Analysis menu, select the "Other" option
	* Enter the atomic number Z and atomic mass (in amu) for the desired isotope, then select "Run Comparison"

6. To save the graph on screen, select "Save" from the drop-down File menu (File>Save) or use the shortcut `<Ctrl+S>`



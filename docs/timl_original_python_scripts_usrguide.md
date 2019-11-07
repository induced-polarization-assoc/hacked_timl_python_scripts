# How to Use Tim’s Scripts to Process Data (Until we have something better anyway...)

Joseph J. Radler, MS

Research Associate

Induced Polarization Associates, LLC, Seattle, WA 

2019.11.04

---

Tim’s scripts use a very rigid, hardcoded directory structure to process data. This needs to be rewritten ASAP.  However, for the time being, we need to be able to process the data we *do* have, and therefore it is important to know how to deploy these really complex scripts to process field and laboratory data to generate the data Art and Kari need. 



## Setting Up Data Directories and Processing the Data for Analysis

The directories have to be used *on Tim Lewis’s account on the Williamson box*! There are a number of options in each script that are scattered about in the code. I would advise against changing *any of them* unless you are certain what function they perform or what the effect will be. 

In a near-future refactor, we will have user-defined configuration files with clearer language and configuration options for the user so the source code itself doesn’t need to be touched at all and they will be called from a single script that is a “plug and play” sort of solution. 

1. Login as `WASSOC\timl`

2. Password: `-p)IhV}m4%y`

3. Open the directory: `C:\Users\timl\Documents\GitHub\induced_polarization\Python Scripts`

4. In order to process raw data output from the `ipDAQ_AG132` software, it must first be parsed and serialized using the `ipProcess.py` script.  This one can take a while. Go into `ipProcess.py` and change `line 39` to set the variable `pklFolder=r'<path to data folder>`.

5. Ensure that the folder specified as `pklFolder` contains the raw text data (output from `ipDAQ_AG132`) in a folder entitled `rawData`. If this step is not carried out, the script will fail instantly. 

6. Run the script in Spyder or PyCharm, making sure to call the script from within the `Python Scripts` directory. This can take up to ten or fifteen minutes in the current implementation depending on the volume of data being converted and serialized into a `pickle` file. 

7. The IPython console should output something that looks like: `Creating <__main__.FileClass object at 0x00000NNNNNNN> from YYMMDD_N.txt.`

8. Once this has completed, the IPython prompt will reappear.

9. Now, `pklCrop.py` needs to be used to “crop” the pickle file for some reason. This requires explicitly using the `pklCropInfo.txt` file in the same directory that contains rows corresponding to:

   `(filedatestr, filenum, startpkt, endpkt)`

   with integer values for each element of the tuple. You will get `out of range` errors if this is not set up correctly. 

10. At this point you can move on to analyze and plot the data. 

## Data Analysis Scripts:

1. Select which script to use:
   1. `ip_survey.py` is used for fieldwork and surveys requiring visualizations on charts of where the largest real-impedances are located on Earth. 
   2. `ipQuickShow.py` will allow you to select the “track” or test run of interest and plot the apparent real-magnitude as a function of packet number. 
   3. `ipScatterEverything` will produce a scatterplot on one channel for 2*ComplexZMag with respect to packet number. 
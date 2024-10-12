# ZTF-SIMPLE
An automated process for converting ZTF time-series data from difference photometry to absolute photometry.

# Introduction
Converting ZTF's difference photometry back to its original absolute photometry is a difficult, time consuming, and all around inconvenient process. This code aims to ease that difficulty, for everything besides querying the Zwicky Forced Photometry Service, of which documentation can be found at these two links:

Single object query documentation: https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_forced_photometry.pdf

Multi-object query documentation: https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_zfps_userguide.pdf

# Requirements
A python interpreter of version greater than or equal to 3.8 is required. ZTF-SIMPLE requires the following modules: os, math, pandas, numpy, astropy, and matplotlib.

# Running ZTF-SIMPLE
ZTF-SIMPLE requires data only found within ZFPS, with ZTF data retrieved from IRSA being unusable, as it lacks several important variables needed to convert the difference photometry back to absolute photometry. 

Upon receiving your objects from ZFPS, they will all be .txt files. It is strongly recommended you rename these files to the name of the object, as folders will be generated for each object using the name of the .txt file. You do NOT need to convert these .txt files to any other format, as ZTF-SIMPLE will handle this itself. Place the .txt files in the same directory that SIMPLE.py can be found in.

In terminal, change directories to the path that SIMPLE.py and your .txt files are in, then input the command 'python3 SIMPLE.py'. This will start the program, and all your files will be processed. It should be noted some files may be missing important data like 'nearestrefmag'. Unfortunately, nothing can be done for this, and the data is unusable. 

SIMPLE.py will generate unique folders for each object, creating CSV files for every photometric band it could identify in the .txt files. Once all objects are processed, SIMPLE.py will ask you in the terminal whether you would like for the program to generate phase-folded figures of the objects just processed. You may answer 'Y' or 'N'. If you answer Y, SIMPLE.py will generate 3 sublots into a png. The top most is the magnitude over modified julian date (mjd), the middle is the periodogram of the data (Lomb-Scargle), and the bottom is the phase-fold itself, with the highest-power period shown. All figures are generated choosing the highest power frequency found by the Lomb-Scargle transformation.

If you enter 'N', SIMPLE.py will quit.

# Contact
If you have any issues, questions, or thoughts about ZTF-SIMPLE, please do not hesitate to reach out to Ms. Yves Wood. cbw236@nau.edu or yves.b.wood@gmail.com are easy ways to get in contact.

# Acknowledging ZTF-SIMPLE
If you found ZTF-SIMPLE useful for your research and intend to publish, please cite it using the 'cite this repository' widget in the repo sidebar.

# reespectroPy
Processing and analysis toolbox for identification of Rare Earth Elements (REE) in reflectance spectroscopy.

## About the data set

In this work, we've built a data set from three libraries to build a collection containing three classes of minerals:



The samples were compiled from the Geological Survey of Canada Open File Report 8619 [GSC OF_8619], Geological Survey of Canada Open File Report 7923 (link), as well as a hand selection the USGS_Speclib_07a. We've built specific file readers to parse the numerical and textual meta data from this different sources.

## What do the classes mean?

- Class 0: minerals that do not contain REE.
- Class 1: minerals that have the capacity to host REEs, but there is no guarentee that each sample will contain REEs.
- Class 2: minerals that contain REEs.

Note: for the minerals in Class 1 and Class 2 that contains REEs, we do not know the concentration or the elemental makeup of this concentration. So that limits what we can do from a characterization perspective. 

Class 1 might need a rethink.

# Visualization

A composite plot of a raw spectrogram with two background corrections applied: the so-called Convex-Hull correction, and an Asymmetric Least Squares fit.

![Example of sample 2399 (Allanite)](/images/2399_allanite.png)

In the QC_plots notebook we have a interactive widget where the user can slide through the entire sample collection, and save any figure using the "Save Figure" button. The button, doesn't not have the most elegant behavior. You must press the button once to save a figure (the figure name will be made up of the `cm_ree_labels` category, the sample ID and the mineral name). You must then press the button a second time to deactivate the saving before moving to a new image. If you don't deselect the Save Figure button, the program will save every figure that you move to. If you have any suggestions on how to improve this behaviour, please let me know.

Colors: throughout this work I've chosen three colours to denote the classes. Black is used to label Class 0 (no REE bearing mineral), Green is labels

Darkness threshold: In the plots, the user can set a darkness threshold, which will turn the plot background gray if no raw reflectance value exceeds this threshold. The idea being that we may want to flag or treat the dark or generally less reflective samples differently. It's hard to see subtle things in the dark! The default value of the cutoff is 0.5, but there is no physical basis for this and should be adjusted. Currently this cutoff is not used for anything other than to decorate the plot. In other words, it's not used to figure or modify the raw data in any way.


![Example of sample 2104 (Polycrase)](/images/2104_polycrase.png)

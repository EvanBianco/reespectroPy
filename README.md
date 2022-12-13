# reespectroPy
Processing and analysis toolbox for identification of Rare Earth Elements (REE) in reflectance spectroscopy.

## About the data set

In this work, we've built a data set from three libraries to build a collection containing three classes of minerals:

The samples were compiled from the [Geological Survey of Canada Open File Report 8619](https://doi.org/10.4095/315690), [Geological Survey of Canada Open File Report 7923](https://doi.org/10.4095/297564), as well as a hand selection the [USGS_Spectral Library version 7](https://pubs.er.usgs.gov/publication/ds1035).

We've built specific file readers to parse the numerical and textual meta data for each of these this different sources.

## What do the classes mean?

- Class 0: minerals that do not contain REEs.
- Class 1: minerals that have the capacity to host REEs, but there is no guarentee that each sample will contain REEs.
- Class 2: minerals that contain REEs.

Note: for the minerals in Class 1 and Class 2 that contains REEs, we do not know the concentration or the elemental makeup of this concentration. So that limits what we can do from a characterization perspective. 

Class 1 might need a rethink. This might not be a fair class for supervised learning.

## Understanding the plots

A composite plot of a raw spectrogram with two background corrections applied: the so-called Convex-Hull correction, and an Asymmetric Least Squares fit.

![Example of sample 2399 (Allanite)](/images/2399_allanite.png)

In the [QC_plots notebook](notebooks/05_QC_plots_and_visualizations.ipynb) we have a interactive widget where the user can slide through the entire sample collection, and save any figure using the "Save Figure" button. Please be advised that this button, doesn't not have the most elegant behavior. You must press the button **once to save a figure** (the figure name will be made up of the `cm_ree_labels` category, the sample ID and the mineral name). You must then **press the button a second time** to deactivate the saving **before** moving to a new image. If you don't deselect the Save Figure button, the program will save every new figure that you navigate to. If you have any suggestions on how to improve this behaviour, please let me know. 

**Colors**: throughout this work I've chosen three colours to denote the classes. Black is used to label Class 0; a mineral that does not bear REEs, Green is Class 1; a mineral that has the capacity to hold REEs in it's mineral structure, but may not nessecarily have any REEs within, and Red is Class 2: a mineral that contains REEs.

**Darkness threshold**: In the plots, we also have designed the ability for the user to denote if a specimen is dark. It might be hard to see subtle details in the dark! Specifically, we change the plot background to gray if the maximum values of the raw reflectance is less than the darkness threshold value (default it 0.5, but this can be adjusted as there is no physical basis for this value). Currently, this cutoff is not used for anything other than to simply decorate the plot. In other words, it's not used to process or modify the data in any way.

![Example of sample 2104 (Polycrase)](/images/2104_polycrase.png)

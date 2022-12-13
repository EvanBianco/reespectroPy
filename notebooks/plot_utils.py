# Plot utils for spectroscopy.
from tokenize import PlainToken
import numpy as np
import matplotlib.pyplot as plt
from pysptools.spectro import convex_hull_removal, SpectrumConvexHullQuotient

def plot(record,
         w=None,
         meta_keys=['cm_ree_labels', 'ID', 'Mineral_Name', 'Formula'],
         low_start=450,
         raw_only=False, 
         hull_curve=True, 
         side_panel=False, 
         ylim='auto', 
         figsize=(15, 6), 
         dark_flag=0.0,
         wv_range=(450, 2500),
         vert_lines=list(np.arange(350, 1000, 100)) + [1500],
         flag_color='orange',
         **kwargs):
    """
    Does a plot of the spectrum.
    Args:
        s (ndarray, Iterable, or pd.DataSeries):
            Input is passed as data for the spectrum.
        w (ndarray, Iterable, or pd.DataSeries):
            Input is passed as the wavelength of the plot
            If w is None it is taken as np.arange(350, 350+len(s)), 
        meta (dict):
            A dictionary of the meta data you want on the side.
            Not implemented.
        low_start (int):
            Chop the signal and hull remove here.
        raw_only (bool):
            Plot the raw curve only (not the hull corrected spectrum)
        side_panel (bool):
            Plot meta data in and info panel to the side.
        ylim (auto or tuple)
            Set the y-limits of the yaxis.
        figsize:
            The width and heigh of the entire canvas (inches)
        dark_flag:
            If the max value of the spectrum is less than this value, consider
            the sample to be "dark", and flag the plot with flag_color
    """
    color_dict = {2: 'red', 1: 'green', 0:'black'}

    if w is None:
        w = list(np.arange(wv_range[0], wv_range[1]).astype(str))
        basis = np.array(w).astype(float)
    else:
        basis = np.array(w).astype(float)

    curve = np.array(record[w])

    # this spectrum seems to take a long time
    crs, xhull, yhull = convex_hull_removal(list(curve), wvl=list(basis))
    ncrs = crs
    #ncrs = (1 - (crs / np.amax(crs)))  # normalized

    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0.1, 0.1, 0.5, 0.8])

    # raw curve
    ax.plot(basis, curve, c=color_dict[record['cm_ree_labels']],
            linestyle='dotted', label='raw', **kwargs)

    # hull curve
    ax.plot(xhull, yhull, c=color_dict[record['cm_ree_labels']], 
            linestyle='dashed', lw=1, label='hull curve', **kwargs)
    # hull correction
    ax.plot(basis, ncrs, c=color_dict[record['cm_ree_labels']], 
            label='hull-corrected', **kwargs)
    ax.set_xlabel('wavelength (nm)')
    ax.legend()

    # Darkness threshold
    if np.amax(curve) <= dark_flag:
        ax.patch.set_alpha(0.25)
        ax.patch.set_facecolor(flag_color)
        
    ax.axhline(dark_flag, linestyle='dashed', color='gray', lw=1)
    ax.text(2600, dark_flag, s='        darkness \n        threshold', color='gray', ha='left', va='center')

    plt.tick_params(axis='y', which='both', labelleft='off', labelright='on')
    ax.grid()

    # Vertical line annotations
    _ = ax.set_xticks(vert_lines)
    ax.set_ylim(0, 1.1)

    if meta_keys is not None:
        label = ''
        longest = max([len(k) for k in meta_keys])
        for k in meta_keys:
            if k.lower() == 'formula':
                item = format_formula(str(record[k]))
            else:
                item = str(record[k])
            label = label + k.replace('_', ' ') + ': ' + ' '*(longest - len(k)) + \
                    item + '\n'
        ax.text(x=1.1, y=1.0, s=label, transform=ax.transAxes, 
                va='top', font='monospace', fontsize=11)

    return fig, ax


def format_formula(str):
    """Make all numbers subscripts in chemical formula"""
    sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return str.translate(sub)

    



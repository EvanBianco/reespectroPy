
#import utils
import camelot as cl
import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull
from scipy.interpolate import interp1d
from scipy import sparse
from scipy.sparse.linalg import spsolve


def get_hull_curve(row):
    """
    Docstring
    """
    s = np.array(row)
    hull_curve = resample_hull_curve(s)
    return hull_curve


def correct_curve(row): #, n_data_cols=2051):
    """
    Docstring
    """
    s = np.array(row).astype(float)
    hull_curve = get_hull_curve(s)
    corrected =  s / hull_curve
    corrected[corrected == np.nan] = 1
    return corrected


def convex_hull(r, w, trim_zeros=True, pad_x=(-500, 5000)):
    """
    Calculates the Convex Hull of a set of points by padding the ends with 
    zeros.
    r = s.data.reflectance
    w = s.data.wavelength
    """
    padded_points = np.pad(np.array(r), 
                           pad_width=1, mode='constant', constant_values=0)
    padded_wavelength = np.pad(np.array(w), pad_width=1, mode='edge')
    spec_points_2d = np.array([padded_wavelength, padded_points])
    points = np.array([[p, q] for p, q in spec_points_2d.T])
    hull = ConvexHull(points)
    hull_x, hull_y = points[hull.vertices, 0], points[hull.vertices, 1]
    if trim_zeros:
        hull_x, hull_y = hull_x[0:-1], hull_y[0:-1]
    hull_points = np.sort([hull_x, hull_y], axis=-0)
    return hull_points


def resample_hull_curve(r):
    """
    Docstring
    """
    w=np.arange(350, 350+len(r))
    hull_points = convex_hull(r, w)
    out_data = chop_zeros(hull_points)
    x, y = out_data[0], out_data[1]
    f = interp1d(x, y, bounds_error=False)
    xnew = np.array(w)
    ynew = f(xnew)
    return ynew


def chop_zeros(hull_points):
    """
    Docstring
    """
    out_data = []
    for y, x in hull_points.T:
        if y != 0.0:
            out_data.append([x, y])
    out_data = np.array(out_data).T
    return out_data


def baseline_als(y, lam=1e7, p=0.98, niter=10):
    """
    Calcuates the asymmetric least squares fit of a signal.

    Reference: Asymmetric Least Squares Smoothing" by P. Eilers and 
    H. Boelens (2005)
    Args:
        y (array): signal
        lam (float): smoothness parameter. Consider varying logarithmically.
        p (float): symmetry parameter. Should be less than and very close
            to 1, e.g. 0.98
    """
    L = len(y)
    D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
    w = np.ones(L)
    for i in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + lam * D.dot(D.transpose())
        z = spsolve(Z, w*y)
        w = p * (y > z) + (1-p) * (y < z)
    return z
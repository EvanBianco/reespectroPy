
#import utils
import camelot as cl
import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull
from scipy.interpolate import interp1d, splrep, splev
from scipy import sparse
from scipy.sparse.linalg import spsolve


TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)

def jarvis_convex_hull(points):
    """Returns the points on the convex hull of points in CCW order.
    from: https://github.com/ctherien/pysptools/blob/master/pysptools/spectro/_jarvis.py
    """
    hull = [min(points)]
    for p in hull:
        q = _next_hull_pt(points, p)
        if q != hull[0]:
            hull.append(q)
    # Here the second update:
    hull.reverse()
    return hull


def _turn(p, q, r):
    """Returns -1, 0, 1 if p,q,r forms a right, straight, or left turn."""
    t = (q[0] - p[0])*(r[1] - p[1]) - (r[0] - p[0])*(q[1] - p[1])
    # Update to make jarvis run with Python 3.3:
    if t < 0: return -1
    if t == 0: return 0
    if t > 0: return 1


def _dist(p, q):
    """Returns the squared Euclidean distance between p and q."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    return dx * dx + dy * dy


def _next_hull_pt(points, p):
    """Returns the next point on the convex hull in CCW from p."""
    q = p
    for r in points:
        t = _turn(p, q, r)
        if t == TURN_RIGHT or t == TURN_NONE and _dist(p, r) > _dist(p, q):
            q = r
    return q


def convex_hull_removal(wvl, sig):
    """
    Remove the convex-hull of the signal by hull quotient.

    https://pysptools.sourceforge.io/_modules/pysptools/spectro/hull_removal.html#convex_hull_removal

    Parameters:
        pixel: `list`
            1D HSI data (p), a pixel.
        wvl: `list`
            Wavelength of each band (p x 1).

    Results: `list`
        Data with convex hull removed (p).

    Reference:
        Clark, R.N. and T.L. Roush (1984) Reflectance Spectroscopy: Quantitative
        Analysis Techniques for Remote Sensing Applications, J. Geophys. Res., 89,
        6329-6340.
    """
    points = list(zip(wvl, sig))
    # close the polygon
    poly = [(points[0][0],0)] + points + [(points[-1][0], 0)]
    hull = jarvis_convex_hull(poly)
    # the last two points are on the x axis, remove it
    x_hull = np.array(hull)[:, 0][:-2]
    y_hull = np.array(hull)[:, 1][:-2]

    if False:
        tck = splrep(x_hull, y_hull, k=1)
        iy_hull = splev(wvl, tck, der=0)

        norm = []
        for ysig, yhull in zip(pixel, iy_hull):
            if yhull != 0:
                norm.append(ysig/yhull)
            else:
                norm.append(1)

    f = interp1d(x_hull, y_hull, bounds_error=False)
    xnew = np.array(wvl)
    ynew = f(xnew)

    return xnew, ynew, x_hull, y_hull
    


def get_continuum_removed_spectrum(x, y, y_hull):
    return (1 - (y_hull - y)) # normalized


def alternate_convex_hull(r, w, trim_zeros=True, pad_x=(-500, 5000)):
    """
    Potentially deprecated??
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
    hull_points = jarvis_convex_hull(r, w)
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
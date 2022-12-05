from configparser import MAX_INTERPOLATION_DEPTH
from distutils.errors import DistutilsPlatformError
import glob
import matplotlib.pyplot as plt
import numpy as np
#from reflectance.spectrum import Spectrum
#import spectrum as spec
import pandas as pd
import matplotlib.pyplot as plt
import camelot as cl
from scipy.spatial import ConvexHull
from scipy.interpolate import interp1d

from docx.api import Document
import codecs

import chardet
from pathlib import Path


def predict_encoding(file_path: Path, n_lines: int=20) -> str:
    '''Predict a file's encoding using chardet'''

    # Open the file as binary data
    with Path(file_path).open('rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']


def get_USGS_data(file, encodings='us-ascii', file_start='splib07a',
                  print_fname=False, instrument='ASDF'):
    """
    Documentation
    """
    encodings = [encodings]
    for i, enc in enumerate(encodings):
        with open(file, encoding=enc, errors='ignore') as f:
            content = f.read()
            content = content.replace('\ufeff', '')            
            # Have we found the right encoding?
            lines = content.split('\n')
            correct_encoding = True
            if correct_encoding:
                if print_fname:
                    print('correct', enc, file.split('/')[-1])    
                header = lines[0].split('\t')
                data = []
                for line in lines[1:]:
                    if len(line) > 0:
                        x = line.strip()
                        data.append([float(x)])
    
    data = np.array(data)
    
    if instrument == 'ASDF':
        w = np.arange(350, 2501)  # wavelengths in nm
    else:
        w = np.arange(len(data))
        
    return header, w, data[:,0] 


def get_USGS_data_header(fname):
    """"
    Get meta data dict from the filename.
    Not implemented
    """
    folder_id, mat_name, sample_id, instr, *_ = fname.split('/')[-1].strip(' .txt').split('_')
    return folder_id, mat_name, sample_id, instr, _


def get_USGS_meta(file, encodings, file_start='splib07a'):
    """"
    Get meta data from separate file than the data file
    if file is the same as the data file.
    NOT IMPLEMENTED
    """
    return None


def get_OF8619_data(file, 
                    encodings=['utf-16le',  'us-ascii', 'ISO-8859-1', 'utf-16be'],
                    print_fname=False):
    """
    Reads a file containing data, returns the header and an array of
    wavelengths and data (2-D array)
    """
    #pred_encoding = predict_encoding(file)
    #print(pred_encoding)
    for j, enc in enumerate(encodings):
        with open(file, encoding=enc, errors='ignore') as f:
            content = f.read()
            content = content.replace('\ufeff', '')
            
            # Have we found the right encoding?
            lines = content.split('\n')
            encoding_test = len(lines[:20]) == 20
            if encoding_test:
                for i, line in enumerate(lines):
                    if line.startswith('Wavelength'):
                        first_idx = i + 1
                        break
                
                correct_encoding = lines[i].startswith('Wavelength')
                if correct_encoding:
                    if print_fname:
                        print('correct', enc, file.split('/')[-1])    
                    header = lines[i].split('\t')
                    data = []
                    for line in lines[first_idx:]:
                        if len(line) > 0:
                            x, y, = line.strip().split('\t')
                            data.append([float(x), float(y)])

    data = np.array(data)
    w, r = data[:,0].astype(int), data[:,1]
    return header, w, r


def get_OF8619_meta(file):
    """
    Returns a dictionary of the meta data
    from a PDF file (file)
    """
    df = cl.read_pdf(file)[0].df
    temp = {k: v for k, v in zip(df.to_dict('series')[0], df.to_dict('series')[1])}
    meta = {}
    for k, v in temp.items():
        new_key = k.replace(' ', '_')
        meta[new_key] = v
    return meta


def get_OF7923_data(file):
    """
    Reads a file containing data, returns the header and an array of
    wavelengths and data (2-D array)
    """
    with open(file, encoding='utf-16le') as f:
        content = f.read()
        content = content.replace('\ufeff', '')

    lines = content.split('\n')
    if lines[0].startswith('Wavelength'):
        header = lines[0].split('\t')
        data = []
        for line in lines[1:]:
            if len(line) > 0:
                x, y, = line.strip().split('\t')
                data.append([float(x), float(y)])
    else:
        header = ['Wavelength', 'Average']
        data = []
        for line in lines:
            if len(line) > 0:
                x, y, = line.strip().split('\t')
                data.append([float(x), float(y)])
    data = np.array(data)
    w, r = data[:,0].astype(int), data[:,1]
    return header, w, r


def get_OF7923_meta(file):
    """
    Docstring
    """
    document = Document(file)
    table = document.tables[0]
    temp = {}
    for i, row in enumerate(table.rows):
        text = [cell.text for cell in row.cells]
        temp[text[0]] = text[1]
    
    text = temp['Mineral Name']
    mineral = text[:-text[::-1].find('(')-1].strip()
    sample_id = text[-text[::-1].find('('):].strip('()')
    temp['Mineral Name'] = mineral
    temp['ID'] = sample_id

    meta = {}
    for k, v in temp.items():
        new_key = k.replace(' ', '_')
        meta[new_key] = v
    return meta


def get_spectrum_df(df, idx, wvls=None, return_meta=False):
    """
    Returns a DataFrame with two columns (Series) corresponding to 
    "wavelengths" and "values", respectively
    Args:
        df (pd.DataFrame or array)
            containing a collection of spectra.
        idx (int)
            the index or row to get
        wvls (Sequence of ints or boolean array)
            which columns to grab from the df. If "None", then will
            choose the last 2151 columns (350-2500)
        return_meta (bool):
            Returns a dictionary of the meta data if True
    Returns:
        a DataFrame with two columns 'wavelengths', 'values
    """
    if not wvls:
        w = 2151
        row = df.iloc[idx, -w:]
        wvls = np.arange(350, 2500)
    else:
        row = df.iloc[idx, wvls]
    print(row)
    np.array([wvls, row.iloc[0].values]).T
    df = pd.DataFrame(df, columns=['wavelength', 'values'])
    return df


def to_filename(path):
    """
    Convert string/pathlib.Path to string.
    Args:
        path (str/pathlib.Path): filename
    Returns:
        str: filename
    """
    try:
        from pathlib import Path
    except ImportError:
        return path

    if isinstance(path, Path):
        return path.absolute().__str__()
    else:
        return path


def find_first_dataline(lines):
    """
    Finds the first row of data where the last header starts with 
    "Wavelength"
    """
    lines = lines.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('Wavelength'):
            first_data_idx = i + 1
    return first_data_idx
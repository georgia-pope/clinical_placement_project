import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import ast
import math
import random
import seaborn as sns

from config import column_dict, N, M, preferences_csv_path, pp_csv_path

"""
N = num rotations
M = max num placements for any individual rotation
M' = total number of placements (at most N*M)
W = num students
Columns: Name, Rotation ranking (N columns with a ranking), M' columns of rankings, 1 column of preference points
"""


def csv_load_and_clean(preferences_csv_path, pp_csv_path, column_dict):
    """
    Load csv and assign each student an index and convert string rankings to 
    numerical rankings (First choice -> 1, Second choice -> 2,...)

    Returns pandas df 
    """
    preferences = pd.read_csv(preferences_csv_path)
    pp = pd.read_csv(pp_csv_path)
    preferences = preferences.merge(pp, left_on = 'Your Name', right_on = 'Your Name')
    preferences = preferences.astype(str)

    preferences.mask(preferences == 'First Choice', 1 , inplace=True )
    preferences.mask(preferences == 'Second Choice', 2 , inplace=True )
    preferences.mask(preferences == 'Third Chice', 3 , inplace=True )
    preferences.mask(preferences == 'Third Choice', 3 , inplace=True )
    preferences.mask(preferences == 'third Chice', 3 , inplace=True )

    preferences.rename(columns=column_dict, inplace=True)
    preferences.sort_values('student', inplace=True)
    preferences[preferences.columns[1:]] = preferences[preferences.columns[1:]].apply(pd.to_numeric)
    return preferences 

def build_r(preferences : pd.DataFrame, N):
    """
    Returns WxN array with list representation of rotation preference where r[0] is first choice rotation index,
    (e.g. [1,2,0] means the second rotation is most preferable, followed by the third and finally the first)
    """
    r = preferences[preferences.columns[1:1 + N]].to_numpy()
    return r

def build_pp(preferences : pd.DataFrame):
    """
    Returns Wx1 array with preference points for each student 
    """
    return preferences['preference_points'].to_numpy()

def build_S(df : pd.DataFrame):
    """
    Returns WxNxM array containing numerical representations of all student preferences
    S_wnm is the ranking for the wth student for the nth rotation for the mth placement within that rotation
    """
    raise NotImplementedError("We are getting to it")
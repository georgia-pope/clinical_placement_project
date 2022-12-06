import numpy as np
N = 3
M = 4
preferences_csv_path = 'spring_22_preferences.csv'
pp_csv_path = 'spring_22_preference_points.csv' # CHANGE THIS!!!
column_dict = {
    'Email Address': 'student', 
    'Rank Rotations [Med-Surg]': '0', 
    'Rank Rotations [Peds]': '1',
    'Rank Rotations [OB]': '2',
    'Rank M/S Rotations [Kaiser Sunset (ICU) | Monday]': '[0,0]',
    'Rank M/S Rotations [Cedars | Monday]': '[0,1]',
    'Rank M/S Rotations [Kaiser Downey (ED) | Thursday]': '[0,2]',
    'Rank Peds Rotations (first 8 weeks) [White Memorial | Thursday]': '[1,0]',
    'Rank Peds Rotations (first 8 weeks) [Valley Presbyterian | Thursday]': '[1,1]',
    'Rank Peds Rotations (first 8 weeks) [CHLA | Friday]': '[1,2]',
    'Rank Peds Rotations (first 8 weeks) [CHLA | Saturday]': '[1,3]',
    'Rank OB Rotations (2nd 8 weeks) [Huntington Memorial | Monday]': '[2,0]',
    'Rank OB Rotations (2nd 8 weeks) [Kaiser Woodland Hills | Thursday]': '[2,1]',
    'Rank OB Rotations (2nd 8 weeks) [Good Samaritan | Thursday]': '[2,2]',
    'Rank OB Rotations (2nd 8 weeks) [Kaiser Downey | Friday]': '[2,3]'
}

restrictions = np.asarray([
    [[(2,0)],                           # Monday Med Surg Kaiser Sunset(0,0)
     [(2,0)],                           # Monday Med Surg Cedars (0,1)
     [(1,0), (1,1), (2,1), (2,2)],      # Thursday Med Surg Kaiser Downey (0,2)
     []],                               # placeholder (0,3)
    [[(0,2)],                           # Thursday Peds White Memorial(1,0)
     [(0,2)],                           # Thursday Peds VPH (1,1)
     [],                                # Friday Peds CHLA (1,2)
     []],                               # Saturday Peds (1,3) 
    [[(0,0),(0,1)],                     # Monday OB Huntington (2,0)
     [(0,2)],                           # Thursday OB Kaiser Woodland Hills(2,1)
     [(0,2)],                           # Thursday OB Good Sam (2,2)
     []]                                # Friday OB Kaiser Downey (2,3) 
], dtype=object)

placement_count_original = np.asarray([
    [10,10,10,0],
    [6,8,8,8],
    [6,8,8,7]
])
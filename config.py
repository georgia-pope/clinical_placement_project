import numpy as np
# some kind of representation of the columns 
    # dictionary that goes from original column name to index representation
# include conflicts

# store somewhere what index goes to what 
N = 2
M = 3
preferences_csv_path = 'fall_clinical_preferences.csv'
pp_csv_path = 'fall_preference_points.csv'
column_dict = {
    'Your Name':'student', 
    'Med Surg Ranking':'0',
    'Psych Ranking':'1',
    'Clinical Site Med Surg - Mondays Cedar Sinai Medical Center': '[0,0]',
    'Clinical Site Med Surg - Fridays Valley Presbyterian Medical Center': '[0,1]',
    'Clinical Site Med Surg - Saturdays PIH Whittier Medical Center': '[0,2]',
    'Clinical Site Psych - Mondays LADMC Ingleside': '[1,0]',
    'Clinical Site Psych - Thursdays Gateways Hospital and Mental Health Center': '[1,1]',
    'Clinical Site Psych - Saturdays Gateways Hospital and Mental Health Center': '[1,2]'
}
restrictions = np.asarray([
    [[(1, 0)], # Monday Med Surg (0,0)
     [], # Friday Med Surg (0,1)
     [(1,2)]], # Saturday Med Surg (0,2)
    [[(0,0)], # Monday Psych (1,0)
     [], # Thursday Psych (1,1)
     [(0,2)]] # Saturday Psych (1,2) 
], dtype=object)

placement_count_original = np.asarray([
    [10,10,10],
    [10,10,10],
])




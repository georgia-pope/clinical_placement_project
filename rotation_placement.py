import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import ast
import math
import random
import seaborn as sns
import copy

from config_spring import column_dict, N, M, preferences_csv_path, pp_csv_path

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
    if preferences_csv_path == 'spring_22_preferences.csv':
        preferences.drop('Timestamp', axis=1, inplace=True)
        preferences = preferences[preferences.columns[:-1]]
        preferences.dropna(inplace=True)
    preferences.rename(columns=column_dict, inplace=True)
    preferences = preferences.merge(pp, left_on = 'student', right_on = 'student', how='left')
    preferences = preferences.astype(str)

    preferences.mask(preferences == 'First Choice', 1 , inplace=True )
    preferences.mask(preferences == 'Second Choice', 2 , inplace=True )
    preferences.mask(preferences == 'Third Chice', 3 , inplace=True )
    preferences.mask(preferences == 'Third Choice', 3 , inplace=True )
    preferences.mask(preferences == 'third Chice', 3 , inplace=True )
    preferences.mask(preferences == '1st choice', 1 , inplace=True )
    preferences.mask(preferences == '2nd choice', 2 , inplace=True )
    preferences.mask(preferences == '3rd choice', 3 , inplace=True )
    preferences.mask(preferences == '4th choice', 4 , inplace=True )
    preferences.mask(preferences == '4th Choice', 4 , inplace=True )

    preferences.sort_values('student', inplace=True)
    if preferences_csv_path == 'spring_22_preferences.csv':
        preferences=preferences.apply(pd.to_numeric)
    else:
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

def build_S(preferences : pd.DataFrame, N : int, M : int):
    """
    Returns WxNxM array containing numerical representations of all student preferences
    S_wnm is the ranking for the wth student for the nth rotation for the mth placement within that rotation
    """
    num_students=preferences.shape[0]
    S = np.ones((num_students,N,M))*(M+5)
    for col in preferences.columns[N+1:-1]: 
        # Converting string to list
        rotation_idx = ast.literal_eval(col)
        S[:,rotation_idx[0],rotation_idx[1]] = preferences[col]
    return S

def G(S,r,pp,N,M):
    S_prime = np.zeros((S.shape[0],N,M))
    def calc_pref_val(preference):
        if preference == 1:
            return 0
        else:
            return (preference - 2)*(-2) -1
    for i in range(S.shape[0]):
        S_prime_i = np.zeros((N,M))
        print(S_prime_i.shape)
        for row in range(N):
            for col in range(M):
                val = 0
                preference = S[i,row,col]
                # First do G()
                val += calc_pref_val(preference)
                    
                # Now add rotation ranking and preference points
                rotation_rank = r[i,row]
                if pp[i] > N:
                    print('WARNING PREFERENCE POINTS WONT BE ALLOCATED CORRECTLY')
                if rotation_rank == 1:
                    val += 2
                    val += allocate_pp(rotation_rank, pp[i])
                elif rotation_rank == 2:
                    val +=1
                    val += allocate_pp(rotation_rank, pp[i])
                elif rotation_rank == 3:
                    val += 0
                    val += allocate_pp(rotation_rank, pp[i])
                else:
                    print('Not a valid rotation rank, talk to Georgia to fix this')
                S_prime_i[row,col] = val
        S_prime[i] = S_prime_i
    return S_prime

def allocate_pp(rotation_rank, pp):
    """
    Allocates preference points. One point for each rotation in ranked order until points run out. 
    """
    rotation_rank = rotation_rank - 1
    if pp - rotation_rank < 0:
        return 0
    elif pp - rotation_rank >= 1:
        return 1
    else:
        return pp - rotation_rank

def create_preference_list(S_prime, N, M, num_students):
    # just holds the score for a placement
    preference_list=np.zeros((num_students * N * M, ), dtype=int) 

    # holds metadata about placement (student_id, rotation, placement)
    preference_list_meta_data = np.zeros((num_students*N*M, 3),dtype=int)  

    # put info into initialized arrays 
    i = 0
    for k in range(num_students):
        S_prime_k = S_prime[k]
        for row in range(N):
            for col in range(M):
                preference_list_meta_data[i] = [k, row, col] 
                preference_list[i] = S_prime_k[row,col]
                i += 1      

    return preference_list, preference_list_meta_data
    
def sort_preferences(preference_list, preference_list_meta_data):
    # Sort preferences in ascending order
    sort_idxs = np.argsort(preference_list)
    sorted_preferences = preference_list[sort_idxs]
    sorted_meta = preference_list_meta_data[sort_idxs]

    # Sort preferences in descending order
    sorted_preferences = sorted_preferences[::-1]
    sorted_meta = sorted_meta[::-1]
    return sorted_preferences, sorted_meta

def update_placement_dict(preference_list_meta_data, num_students):
    placement_dict = {i:[0]*N for i in range(num_students)}
    for current_student, current_rotation, current_placement in preference_list_meta_data:
        placement_dict[current_student][current_rotation] += 1
    return placement_dict

def place(S_prime,restrictions,N,M,placement_count_original):
    """
    NOT TESTED
    """
    placement_count = placement_count_original.copy()
    printing=False
    num_students = S_prime.shape[0]
    
    # Preparing data for algorithm

    preference_list, preference_list_meta_data = create_preference_list(S_prime, N, M, num_students)
    shuffle_idxs = np.linspace(0,preference_list.shape[0] - 1, preference_list.shape[0]).astype(int)
    random.shuffle(shuffle_idxs)
    preference_list = preference_list[shuffle_idxs]
    preference_list_meta_data = preference_list_meta_data[shuffle_idxs]
    total_placements = 0

    if printing:
        print(preference_list_meta_data)
        print(preference_list) 
        
    scoring_preference_list = preference_list
    scoring_preference_list_meta = copy.deepcopy(preference_list_meta_data)
    preference_list = np.zeros_like(preference_list)
    
    while total_placements < num_students*N:
        # print('STARTING PLACEMENT PROCESS')
        # print(total_placements)
        # Sort preferences in descending order
        sorted_preferences, sorted_meta = sort_preferences(preference_list, preference_list_meta_data)
        
        # Initiate final placement dict
        placements = {}
        
        # Initiate dict for keeping tract of placements left for each student
        placement_dict = update_placement_dict(sorted_meta, num_students)
        
        # Initiate dict to keep track of who has been placed 
        placed_dict = {i:[False,False,False] for i in range(num_students)}

        # Initialize score
        score = 0
        while sorted_preferences.shape[0] > 0:
            current_student, current_rotation, current_placement = sorted_meta[0]
            current_conflicts = restrictions[current_rotation, current_placement]

            score_revert = copy.deepcopy(score)
            placements_revert = copy.deepcopy(placements)
            placement_count_revert = copy.deepcopy(placement_count)
            sorted_preferences_revert = copy.deepcopy(sorted_preferences)
            sorted_meta_revert = copy.deepcopy(sorted_meta) 

            # Check if current placement is available
            if placement_count[current_rotation, current_placement] > 0:
                if printing:
                    print(f'{current_student} placed in ({current_rotation},{current_placement})')
                
                # Add score
                score += sorted_preferences[0]

                # Place student in preferred location (if statement for adding new dict key or not)
                if f'[{current_rotation},{current_placement}]' in placements:
                    placements[f'[{current_rotation},{current_placement}]'].append(current_student)
                else:
                    placements[f'[{current_rotation},{current_placement}]'] = [current_student]

                # Update number of placements available
                placement_count[current_rotation, current_placement] += (-1)

                # If placement becomes full, remove all choices for that placement
                if placement_count[current_rotation, current_placement] == 0:
                    removal_mask = np.invert(((sorted_meta[:,2] == current_placement) & (sorted_meta[:,1] == current_rotation)))
                    sorted_preferences = sorted_preferences[removal_mask]
                    sorted_meta = sorted_meta[removal_mask]

                # Then remove current student from the list (for current rotation)
                removal_mask = np.invert(((sorted_meta[:,0] == current_student) & (sorted_meta[:,1] == current_rotation)))
                if printing:
                    print('\nRemoved the rest of that students placements in that rotation:')
                    print(sorted_meta[np.invert(removal_mask)])
                sorted_preferences = sorted_preferences[removal_mask]
                sorted_meta = sorted_meta[removal_mask]
                
                # And remove any conflicts
                if len(current_conflicts) > 0:
                    for conflict in current_conflicts:
                        removal_mask = np.invert(((sorted_meta[:,0] == current_student) & (sorted_meta[:,1] == conflict[0]) & (sorted_meta[:,2] == conflict[1])))
                        if printing:
                            print('\nRemoved conflict:')
                            print(sorted_meta[np.invert(removal_mask)])
                        sorted_preferences = sorted_preferences[removal_mask]
                        sorted_meta = sorted_meta[removal_mask]
                placement_dict = update_placement_dict(sorted_meta, num_students)
                placed_dict[current_student][current_rotation] = True

                if printing:
                    print('placement dict')
                    print(placement_dict)
                    print('/nplaced dict')
                    print(placed_dict)

                broken=False
                for student in range(num_students):
                    for i in range(N):
                        if (placement_dict[student][i] == 0) and (placed_dict[student][i] == False):
                            # REVERT!!!
                            if printing:
                                print('ABORT MISSION. This will fuck things up')
                                print(f'rotation {i} for student {student} will not be possible')
                            score = copy.deepcopy(score_revert) 
                            placements = copy.deepcopy(placements_revert) 
                            placement_count = copy.deepcopy(placement_count_revert) 
                            sorted_preferences = copy.deepcopy(sorted_preferences_revert) 
                            sorted_meta = copy.deepcopy(sorted_meta_revert) 
                            if printing:
                                print(f'Removing {sorted_meta[0]}')
                            sorted_preferences = sorted_preferences[1:]
                            sorted_meta = sorted_meta[1:]
                            placed_dict[current_student][current_rotation] = False
                            
                            broken = True
                            break
                    if broken:
                        break

                
                

            else: # If placement is full
                # Remove current entry and keep going
                # removal_mask = np.invert(((sorted_meta[:,0] == current_student) & (sorted_meta[:,1:2] == current_rotation)))
                if printing:
                    print(f'Placing {current_student} in ({current_rotation},{current_placement}) failed. ({current_rotation},{current_placement}) full.')
                sorted_preferences = sorted_preferences[1:]
                sorted_meta = sorted_meta[1:]
            if printing:
                print(f'Num preferences left: {sorted_preferences.shape[0]} ')
        total_placements = np.sum(list(map(len, placements.values())))
        if total_placements < num_students*N:
            shuffle_idxs = np.linspace(0,preference_list.shape[0] - 1, preference_list.shape[0]).astype(int)
            random.shuffle(shuffle_idxs)
            preference_list = preference_list[shuffle_idxs]
            preference_list_meta_data = preference_list_meta_data[shuffle_idxs]
            placement_count = placement_count_original.copy()
    return placements, score, scoring_preference_list, scoring_preference_list_meta

def score(placements, scoring_preference_list, scoring_preference_list_meta):
    total = 0
    for p, students in placements.items():
        p = [int(p[1]),int(p[3])]
        for s in students:
            student_vals = np.equal(scoring_preference_list_meta[:,0], s)
            rotation_vals = np.equal(scoring_preference_list_meta[:,1], p[0])
            placement_vals = np.equal(scoring_preference_list_meta[:,2], p[1])
            mask = student_vals & rotation_vals & placement_vals
            total += scoring_preference_list[mask]
    return total


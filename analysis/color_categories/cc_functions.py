"""
testing for naive monkeys
"""
import numpy as np
from scipy.io import loadmat
from sklearn import metrics
from collections import Counter
import os
import pandas as pd
import sys
import json
from scipy.optimize import curve_fit
from scipy.stats import norm
import warnings
from pathlib import Path

# Basic data loading
def extract_behavior_from_mat(mat_file_path, n_colors):
    """
    Extracts basic behavior information per trial from mat files
    - used for naive monkeys (data from PNAS paper)
    Parameters
    ----------
    mat_file_path : TYPE
        DESCRIPTION.
    n_colors : TYPE
        DESCRIPTION.

    Returns
    -------
    starttime : TYPE
        DESCRIPTION.
    session_date : TYPE
        DESCRIPTION.
    cue_val : TYPE
        DESCRIPTION.
    choice_vals : TYPE
        DESCRIPTION.
    response_loc : TYPE
        DESCRIPTION.
    response_val : TYPE
        DESCRIPTION.
    is_correct : TYPE
        DESCRIPTION.

    """
    # Check that this function is actually being used for correct subject set
    if n_colors != 64:
        warnings.warn('WARNING: operations may fail. Expecting 64 colors but received ' + str(n_colors))
        
    # Load mat file into clean dictionary 
    mat_data = loadmat(mat_file_path, simplify_cells=True)
    # Access task variables
    trial_data = mat_data['cleandata']['trialdata']

    # Get cues
    cue_val = trial_data['cues']
    if not np.issubdtype(cue_val.dtype, np.integer): # probably stored as array of objects
        cue_val = cue_val.astype(int)
    # Check min and max cue option are as expected based on n colors
    if np.min(cue_val) != 1:
        sys.exit('min cue value should be 1 but found ' + str(np.min(cue_val)))
    if np.max(cue_val) != n_colors:
        sys.exit('max cue value should be ' + str(n_colors) + ' but found ' + str(np.max(cue_val)))

    # Get choices
    choice_vals = trial_data['choices']
    if choice_vals.ndim == 1:
        choice_vals = np.vstack(choice_vals) # will fail if there were not 4 options present on a trial
    if choice_vals.shape[0] != cue_val.shape[0] or choice_vals.shape[1] != 4:
        sys.exit('choice array dimensions are not as expected')
    
        
    # For monkey P, some trials had 2 choice options that were direct matches to the cue
    # Id these trials to remove them later
    unique_choice_counts = np.apply_along_axis(lambda x: len(np.unique(x)), axis=1, arr=choice_vals)
    single_match_trials = unique_choice_counts == 4

    # Get the chosen color id
    monkey_choice = trial_data['chosen']
    if monkey_choice.ndim != 1:
        sys.exit('chosen id array dimensions are not as expected')
    # Array is type object; replace nans with 100s to identify aborted trials
    response_val = np.zeros(monkey_choice.shape[0], dtype=int)
    for i in range(monkey_choice.shape[0]): 
        try:
            choice_as_int = int(monkey_choice[i])
            response_val[i] = choice_as_int
        except:
            response_val[i] = 100
    # Also replace any double match trials with response 100 
    response_val[~single_match_trials] = 100
    #valid_trials = (response_val > 0) & (response_val < 100)

    # Get response location
    where_matches = (choice_vals == response_val[:, None])
    response_loc = where_matches.argmax(axis=1)
    
    
    # Was choice correct
    is_correct = cue_val == response_val
    is_correct = is_correct.astype(int)

    # Get session date 
    session_dirs = trial_data['dirname']
    if session_dirs.ndim != 1:
        sys.exit('session id array dimensions are not as expected')
    session_date = np.zeros(session_dirs.shape[0], dtype=int)
    for i in range(session_dirs.shape[0]):
        session_name = '20' + str.split(session_dirs[i], '_')[0]
        session_date[i] = session_name

    starttime = trial_data['cue_onset'] # want some chronological time variable to track order of trials
    
    # Everything later is expecting the stimuli to be 0-indexed
    # At this point, shift all cues, choices, and responses so this
    # does not become a problem to deal with at later stages!
    cue_val = cue_val - 1
    choice_vals = choice_vals - 1
    response_val = response_val - 1
    
    # General check that any trial with cue, choice, or response not within expected range 
    # should raise warning and remove from data
    other_bad_idxs = []
    other_bad_idxs.append(np.where(~(cue_val>=0))[0])
    other_bad_idxs.append(np.where(~(cue_val<=n_colors-1))[0])
    other_bad_idxs.append(np.where(~(choice_vals>=0))[0])
    other_bad_idxs.append(np.where(~(choice_vals<=n_colors-1))[0])
    other_bad_idxs.append(np.where(~(response_val>=0))[0])
    other_bad_idxs.append(np.where(~(response_val<=n_colors-1))[0])
    other_bad_idxs = np.hstack(other_bad_idxs)
# =============================================================================
#     other_bad_idxs = []
#     other_bad_idxs.append(np.where(~(cue_val>=1))[0])
#     other_bad_idxs.append(np.where(~(cue_val<=n_colors))[0])
#     other_bad_idxs.append(np.where(~(choice_vals>=1))[0])
#     other_bad_idxs.append(np.where(~(choice_vals<=n_colors))[0])
#     other_bad_idxs.append(np.where(~(response_val>=1))[0])
#     other_bad_idxs.append(np.where(~(response_val<=n_colors))[0])
#     other_bad_idxs = np.hstack(other_bad_idxs)
# =============================================================================

    # Exhaustively replace values on invalid trials
    cue_val[~single_match_trials] = 100
    choice_vals[~single_match_trials] = np.array([100,100,100,100])
    response_val[~single_match_trials] = 100
    response_loc[~single_match_trials] = 100
    cue_val[other_bad_idxs] = 100
    choice_vals[other_bad_idxs] = np.array([100,100,100,100])
    response_val[other_bad_idxs] = 100
    response_loc[other_bad_idxs] = 100
    # Use response_loc as indicator of trials to remove in other analyses
    #response_loc[~single_match_trials] = 100
    #response_loc[~valid_trials] = 100

    # Function would've exited earlier if not 1-indexed but why not do one more check
    if np.min(cue_val.astype(int)) != 0 or np.min(choice_vals.astype(int)) != 0 or np.min(response_val.astype(int)) != 0:
        sys.exit('data are not 0-indexed:')
    if cue_val[cue_val != 100].max() != n_colors-1 or choice_vals[choice_vals != 100].max() != n_colors-1 or response_val[response_val != 100].max() != n_colors-1:
        print(np.max(cue_val.astype(int)), np.max(choice_vals.astype(int)), np.max(response_val.astype(int)))
        sys.exit('data are not 0-indexed')
    
    # Format to df
    session_data =  pd.DataFrame({'trialtime':starttime,
                          'session':session_date,
                          'cue_val':cue_val,
                          'choice_vals':list(choice_vals),
                          'response_loc':response_loc,
                          'response_val':response_val,
                          'is_correct':is_correct})
    
    
    return session_data

def extract_behavior_from_json(session_dir, n_colors):
    """
    Extracts basic behavior information per trial from json strings
    - used for concept monkeys (new data)
    """
    # Check that this function is actually being used for correct subject set
    if n_colors != 83:
        warnings.warn('WARNING: operations may fail. Expecting 83 colors but received ' + str(n_colors))
    
    # Resolve as path
    session_dir = Path(session_dir)
    
    # If task had to restart, there will be multiple json files per session date
    session_paths = [os.path.join(session_dir, x) for x in os.listdir(session_dir) if '.txt' in x]

    session_date_str = session_dir.stem #str.split(session_dir, '/')[-1]
    
    session_data = pd.DataFrame()
    for session_file in session_paths:
        with open(session_file, 'r') as f:
            data_dict = json.load(f)
            if isinstance(data_dict, list):
                data_dict = data_dict[0]
        
        # Get trial times
        print(list(data_dict.keys()))
        starttime = np.array(data_dict['StartTime'], dtype=int) # datetime format as 'time since' i think
        trial_time = np.array(data_dict['TrialTime'], dtype=str) # datetime actual date and time
        trial_in_order = np.all(trial_time[1:] >= trial_time[:-1])
        if trial_in_order != True:
            sys.exit('trial order is not strictly increasing; check your indexing')
            
        # Get reaction times
# =============================================================================
#         response_time  = data_dict['ResponseXYT'] # x,y location of touch, and time of touch for response
#         completed_trials = [i for i in range(len(response_time)) if response_time[i] is not None]
#         response_time_completed_trials = [xyt for xyt in response_time if xyt is not None]
#         response_time_completed_trials = np.array(response_time_completed_trials)[:,2]
#         initiate_time_completed_trials = np.array(data_dict['FixationXYT'])[completed_trials,2] # time of trial initiation (touch textured button)
#         
#         trial_completion_times = response_time_completed_trials - initiate_time_completed_trials # in ms
#         reaction_times = trial_completion_times - 1200 # 1200 is total time from initiation to start of choice period
#         all_trials_reaction_times = np.ones(len(response_time))*(6201)
#         all_trials_reaction_times[completed_trials] = reaction_times
#         print(starttime.shape)
#         print(all_trials_reaction_times.shape)
#         print(trial_time.shape)
# =============================================================================
        
        xty_initiated = data_dict['FixationXYT'] # x loc, y loc, t time of touch for initiation (tap button)
        time_initiated = np.array(xty_initiated)[:,2]
        xyt_responded = data_dict['ResponseXYT']
        xyt_responded = [xyt if xyt is not None else [np.nan, np.nan, np.nan] for xyt in xyt_responded]
        if len(xty_initiated) > len(xyt_responded):
            # Nones are only filled in if followed by completed trials. 
            last_n_aborted = len(xty_initiated) - len(xyt_responded)
            for aborted_trial in range(last_n_aborted):
                xyt_responded.append([np.nan, np.nan, np.nan])
        time_responded = np.array(xyt_responded)[:,2]
        
        print(time_responded.shape)
        print(time_initiated.shape)

        # Extract cue, choice, response info
        cue_val = np.array(data_dict['SampleC'], dtype=int) # cue id val
        correct_item = np.array(data_dict['CorrectItem'], dtype=int) # id val of correct choice
        if np.array_equal(cue_val, correct_item) is False:
            sys.exit('cue id and correct item id do not match')
            
        choice_vals = np.array(data_dict['TestC'], dtype=int) # ntrials x nafc of choice id vals

        response_w_nan = np.array(data_dict['Response'])
        response_w_nan[response_w_nan=='Nan'] = 100
        
        response_loc = response_w_nan.astype(int) # response location (0,1,2,or 3; 100 if aborted trial)

        # Grab choice id val using choices array and respose locations
        response_val = np.full(choice_vals.shape[0], 100) # initialize as array of 100s +
        valid = (response_loc >= 0) & (response_loc < 100) # find non-aborted trials
        response_val[valid] = choice_vals[np.arange(choice_vals.shape[0])[valid], response_loc[valid]] # replace with choice id on non-aborted trials 
        
        # Check if monkey picked correct option
        is_correct = (cue_val == response_val).astype(int)
        
        # Create array of session dates matching number of trials
        session_date = np.ones(cue_val.shape[0]) * int(session_date_str)
        
        subsession_data =  pd.DataFrame({'trialtime':starttime,
                              'session':session_date,
                              'cue_val':cue_val,
                              'choice_vals':list(choice_vals),
                              'response_loc':response_loc,
                              'response_val':response_val,
                              'is_correct':is_correct,
                              'time_initiated':time_initiated,
                              'time_responded':time_responded})
        
        session_data = pd.concat((session_data, subsession_data))
    # Check min and max cue option are as expected based on n colors
    if np.min(session_data['cue_val']) != 0:
        sys.exit('min cue value should be 0 but found ' + str(np.min(session_data['cue_val'])))
    if np.max(session_data['cue_val']) != n_colors-1:
        sys.exit('max cue value should be ' + str(n_colors-1) + ' but found ' + str(np.max(session_data['cue_val'])))
    return session_data

def compute_choice_relations(cue_val, choice_vals, n_colors):

    # Find distance between cue and each choice on that trial
    sub_choice = (np.tile(cue_val, (4,1)).T - choice_vals) % n_colors # need both this
    sub_cue = (choice_vals - np.tile(cue_val, (4,1)).T) % n_colors # and this to determine because on a circle
    stacked_diffs = np.stack([sub_choice, sub_cue], axis=0)
    # Minimum of the cue-choice % n_colors and choice-cue % n_colors is the true distance
    choice_distances = np.min(stacked_diffs, axis=0)

    # Find location of closest distractor (argmin ignoring 0)
    closest_distractor_loc = np.argmin(np.ma.masked_equal(choice_distances, 0), axis = 1) 
    # Also grab value of distractor
    closest_distractor_val = choice_vals[np.arange(choice_vals.shape[0]),closest_distractor_loc]
    # Find distance (number of cues) between cue and closest distractor
    closest_distractor_distance = choice_distances[np.arange(closest_distractor_loc.shape[0]), closest_distractor_loc]

    # Check that distance of closest distractor is valid:
        # if n_colors is even, 3 most extreme distractors could be are (1) farthest, (2) farthest - 1 CW, (3) farthest - 1 CCW
        # if n_colors is odd, 3 most extreme distractors could be are (1) farthest CW, (2) farthest CCW, (3) farthest - 1
    if np.max(closest_distractor_distance) > (n_colors // 2) - 1:
        sys.exit('closest distractor distance is higher than expected based on n cues: ' + str(np.max(closest_distractor_distance)))
    if np.max(closest_distractor_distance) < (n_colors // 2) - 1:
        print('closest distractor distance is lower than expected in position: ' + str(np.argmax(closest_distractor_distance)))
    # Argmin can tell us if shortest dist is clockwise or counterclockwise from cue
    choice_directions = np.argmin(stacked_diffs, axis=0) # 0=cue-choice is smaller, meaning 0= clockwise
    closest_distractor_direction = choice_directions[np.arange(closest_distractor_loc.shape[0]), closest_distractor_loc]
    
    # Check that distance of farthest distractor is valid
    farthest_distractor_loc = np.argmax(choice_distances, axis = 1)
    if np.max(farthest_distractor_loc) > n_colors // 2:
        sys.exit('farthest distractor is higher than expected based on n colors: ' + str(np.max(farthest_distractor_loc)))

    # Double check each trial had 1 match and 3 nonmatches
    n_matches = np.count_nonzero(choice_distances, axis=1)
    if np.any(n_matches == 0) is False and np.any(n_matches != 3):
        sys.exit('you have a trial with more than one correct choice option')
        
    return choice_distances, choice_directions, closest_distractor_distance, closest_distractor_direction, closest_distractor_val

# Psychometric function related
def weibull_cdf(omega, zeta, gamma, l, k):
    """
    Use for fitting psychometric functions
    parameters
    zeta: floor
    gamma: ceiling
    omega: trial difficulty, angular diff between cue and closest foil
    l: slope
    k: inflection point
    """
    # zeta + (100-zeta-gamma)*(1-math.e**(-(omega/l)**k))
    return zeta + (gamma-zeta) * (1 - np.exp(-(omega / l) ** k))

def gaussian_cdf(x, mu, sigma):
    # Use for fitting psychometric functions
    return norm.cdf(x, loc=mu, scale=sigma)

def compute_psychometric_curve(distractor_distances, accuracies, n_colors, weights, use_weights=False, fit_curve = True):
    """
    data should already be grouped by distractor distance

    """
    # turn 83 points into polar angles that wrap around
    radians = np.linspace(0, 2*np.pi, n_colors, endpoint=False)
    angles = radians*180/np.pi

    angle_dists = angles[distractor_distances]
    ascending_angles = np.argsort(angle_dists)
    
    angle_dists_sorted = angle_dists[ascending_angles]
    angle_accs_sorted = accuracies[ascending_angles]
    
    
    if fit_curve == True:
        if use_weights == True: # essentially weight by number of trials in distance bin
            sigma = 1 / np.sqrt(weights)
            
            psycurve_params, _ = curve_fit(weibull_cdf, 
                                           angle_dists_sorted, 
                                           angle_accs_sorted,
                                           bounds=([0, 0, 1e-6, 1e-6],   # zeta, gamma, l, k
                                               [1, 1, np.inf, np.inf]),
                                           sigma=sigma,
                                           maxfev = 8000)
        else:
            psycurve_params, _ = curve_fit(weibull_cdf, 
                                           angle_dists_sorted, 
                                           angle_accs_sorted,
                                           bounds=([0, 0, 1e-6, 1e-6],   # zeta, gamma, l, k
                                               [1, 1, np.inf, np.inf]),
                                           maxfev = 8000)
            
        
        
        zfit, gfit, lfit, kfit = psycurve_params
        yfit = weibull_cdf(angle_dists, zfit, gfit, lfit, kfit)
        
        weibull_params = {'zeta': zfit,
                          'gamma': gfit,
                          'scale': lfit,
                          'shape': kfit}
    
        params, _ = curve_fit(gaussian_cdf, 
                                       angle_dists_sorted, 
                                       angle_accs_sorted,
                                       maxfev = 8000)
        mufit, sigmafit = params
        yfitgauss = gaussian_cdf(angle_dists, mufit, sigmafit)
        
    else:
        yfit, yfitgauss = None, None
        
    return angle_dists_sorted, angle_accs_sorted, yfit, yfitgauss, weibull_params

def compute_weibull_slope_at_mid(x: np.ndarray, yfit: np.ndarray, 
                                 weibull_params: dict, n_colors: int):
    zeta = weibull_params['zeta']
    gamma = weibull_params['gamma']
    scale = weibull_params['scale']
    shape = weibull_params['shape']
    mid = ((gamma - zeta) / 2) + zeta
    slope_at_mid = (gamma - zeta) * (shape / (2 * scale)) * (np.log(2) ** ((shape - 1) / shape))
    # where is this slope? find mid = gamma - zeta
    # find indices of yfit where below and above
    lower_yfit = np.where((yfit[:-1] <= mid) & (yfit[1:] > mid))[0][0]
    print(lower_yfit)
    upper_yfit = lower_yfit + 1
    # get index of that yfit, then find the corresponding x angles, then interpolate to find new x
    lower_x = x[lower_yfit] # if not all distances had data, x != lower_fit
    upper_x = x[upper_yfit]
    # Linear interpolation
    estimated_x = lower_x - ((mid-yfit[lower_yfit])/(yfit[upper_yfit]-yfit[lower_yfit])) * (upper_x-lower_x)
    estimated_theta = estimated_x / n_colors * 360
    return [estimated_theta, mid, slope_at_mid]


# Mixture modeling
def get_choice_prob_matrix(cue_val, choice_vals, response_val, n_colors):
    """
    Parameters
    ----------
    cues : TYPE
        DESCRIPTION.
    choices : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    # Check if values are 1 indexed or 0 indexed
    if np.min(cue_val) == 1 and np.max(cue_val) == n_colors:
        print('cues are 1-indexed; decreasing cue and response ids by 1 for consistency')
        cue_val = cue_val - 1
        response_val = response_val -1
        choice_vals = choice_vals - 1
    # Confusion matrix (rows = cues, columns = choices)
    cue_choice_confusion = metrics.confusion_matrix(cue_val, response_val) 
    
    # Count how many times each cue-choice pairing happened
    # and assign to position in matrix corresponding to conf. matrix
    combination_nums = np.zeros_like(cue_choice_confusion)
    for c in range(n_colors): # for each cue
        c_trials = cue_val == c # find all trials where that was the cue
        c_choices = choice_vals[c_trials] # get choices on all those trials
        c_choices_all = c_choices.flatten() # flatten across trials
        choice_counts = Counter(c_choices_all) # count occurrences of all choice options across all trials
        for ch in range(n_colors):
            combination_nums[c][ch] = choice_counts[ch] # row is cue column is choice
    
    # Normalize counts by number of cue-choice presentations (choice prob matrix)
    if cue_choice_confusion.shape != combination_nums.shape:
        sys.exit('confusion matrix and choice count matrix are not same shape')
    choice_prob_matrix = cue_choice_confusion/combination_nums
    if np.sum(np.isnan(choice_prob_matrix)) != 0:
        #warnings.warn('WARNING: some cue-choice combinations have never happened, replacing with 0')
        warnings.warn('WARNING: some cue-choice combinations have never happened')
    #choice_prob_matrix[np.isnan(choice_prob_matrix)] = 0. # if any combinations have still not happened, replace Nan with 0
    # Transpose to get desired format: cues are columns, choices are rows
    choice_prob_matrix_choice_v_cue = choice_prob_matrix.T 
    
    return cue_choice_confusion, choice_prob_matrix_choice_v_cue, combination_nums.T

def Gauss(theta, alpha, sd, mu, guess):
    return alpha * np.exp(-(theta-mu)**2/2/(sd**2)) + guess

def model_choice_bias(choice_prob_matrix_choice_v_cue, n_colors, theta_shift, weights, use_weights=False, fit_shared_grid=False):
    # Model choice probability vector for each cue as gaussian to estimate the mean
    estimated_means = np.zeros(n_colors)
    estimated_sigmas = np.zeros(n_colors)
    
    choice_bias_curves = []
    
    # Use angles
    thetas = np.arange(0,360,360/n_colors)
    if theta_shift is not None:
        thetas = thetas + theta_shift # apply mucs shift
    for i in range(n_colors):
        cue_choice_arr = choice_prob_matrix_choice_v_cue[:,i] # grab column for that cue
        shift = 180 - thetas[i] # want to shift center of curve to 0
        shifted = thetas + shift
        for j, v in enumerate(shifted):
            if v > 360:
                shifted[j] = v-360
            if v < 0:
                shifted[j] = v + 360
        
        if weights is None:
            sys.exit('weights=presentation counts is needed to ensure cue-choice pairings with no occurrences are ignored during fit')
            
        cue_choice_presentations = weights[:,i]
        valid = cue_choice_presentations != 0
        if np.sum(valid) < cue_choice_presentations.shape[0]:
            print('no cue-choice pairings occurred for cue ', i, ' and choices ', np.where(valid==False))
        # If you don't want to actually use the weights
        if use_weights == False:
            # Just treat all weights as one
            cue_choice_presentations = np.ones((cue_choice_presentations.shape[0]))
            
        # Grab values only if there were actual trials including those cue choice presentations
        shifted = shifted[valid]
        cue_choice_arr = cue_choice_arr[valid]
        cue_choice_presentations = cue_choice_presentations[valid]
        # Convert presentation counts to standard dev of each observation (what curve_fit expects)
        sigma = 1 / np.sqrt(cue_choice_presentations)
        
        mixturemodel_params, mixturemodel_cov = curve_fit(Gauss, shifted, cue_choice_arr, p0=[1,20, 180, 0], sigma=sigma, maxfev=8000)
        alpha, sd, mu, guess = mixturemodel_params
        estimated_means[i] = mu # this is the estimated mean of the distribution
        estimated_sigmas[i] = sd
        
        if fit_shared_grid == True: # if want fit on grid common to both naive and csc monkeys
            x_vals = np.arange(0, 360, 360/83)
            fit_y = Gauss(x_vals, alpha, sd, mu, guess)
            choice_bias_curves.append(np.array([x_vals, fit_y]))
        else:
            fit_y = Gauss(shifted, alpha, sd, mu, guess)
            choice_bias_curves.append(np.array([shifted, cue_choice_arr, fit_y]))

    # Calculate difference in estimated center of distribution from underlying center
    offset_from_center = estimated_means - 180

    return choice_bias_curves, offset_from_center, estimated_sigmas

def fourier_design_matrix(theta, K):
    """
    theta: 1D array of angles (radians)
    K: maximum harmonic
    Returns: X (n_samples x (2K+1)) design matrix
    """
    theta = np.asarray(theta)
    n = theta.shape[0]
    
    # First column: constant term
    X = np.ones((n, 1))
    
    # Add cos(kθ), sin(kθ) columns
    for k in range(1, K+1):
        X = np.column_stack([X, np.cos(k * theta), np.sin(k * theta)])
    
    return X

def get_harmonic(theta ,beta, k):
    return beta[2*k - 1]*np.cos(k*theta) + beta[2*k]*np.sin(k*theta)


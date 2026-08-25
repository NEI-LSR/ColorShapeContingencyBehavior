"""
Compute and plot Gaussian modeling of choice biases
Toggle which subjects / subject sets (csc vs. naive)
Toggle dates included
View for individual subjects and combined (not currently normalized by amount of data per monkey)
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter
import warnings
from analysis.color_categories import cc_functions as color_categories_funcs
from analysis.color_categories import cc_plot_functions as color_categories_plot_funcs

# Change this 
boots = 1000 # set to 1 if don't bootstrap, just use all data once
subsample_size = None # Only use if getting data for power analysis

# Drectories
data_dir = os.path.join('data', 'color_categories')
results_dir = os.path.join('results', 'color_categories')
out_dir = results_dir
color_dir = 'color_definitions'
# Paradigm info
nafc = 4 # how many choice options per trial


for subject_set in ['csc', 'naive']: 
    # Load data
    behavior_data_path = os.path.join(data_dir, subject_set + '_valid_trials.csv')
    behavior_data_valid = pd.read_csv(behavior_data_path)
    if subject_set == 'csc': 
        # Subject and paradigm info
        subjects = ['wooster', 'jeeves', 'jocamo', 'combined']
        
        n_colors=83 # how many hues in the stimulus set

    elif subject_set == 'naive':
        # Subject and paradigm info
        subjects = ['buster', 'morty', 'pollux', 'castor', 'combined']
        n_colors = 64
     
    else:
        print('subject set not recognized. use one of csc or naive')

    # Load sRGB for color categories colors to use for plotting
    try:
        cc_rgb = pd.read_csv(os.path.join(color_dir, 'CC_'+ str(n_colors)+ 'colors_sRGB.csv'), header=None, names=['r','g','b'])
        color_rgb_defs = np.array(cc_rgb[['r','g','b']])/255.
    except:
        cc_rgb = pd.read_csv(os.path.join(color_dir, 'CC_'+ str(n_colors)+ 'colors_sRGB.csv'))
        color_rgb_defs = np.array(cc_rgb[['r','g','b']])/255.
    # Six concepts colors 
    csc_centers = pd.read_csv(os.path.join(color_dir, 'CSC_category_centers.csv'))
    csc_center_angle = csc_centers['angle'].to_numpy()
    csc_center_id = csc_center_angle/360*n_colors
    cc_closest_to_csc = np.round(csc_center_id).astype(int)
    
    # Set up bootstrap
    # How many valid trials did each subject complete
    trial_counts = behavior_data_valid['subject'].value_counts().reset_index()
    fewest_trials = np.min(trial_counts['count'])
    limiting_subject = trial_counts['subject'].iloc[np.argmin(trial_counts['count'])]    
    
    # So long as you are actually bootstrapping, set up the random number generator
    if boots != 1:
        rng = np.random.default_rng()
    all_choice_biases = np.zeros((len(subjects), 3, boots, n_colors))
    average_sigmas = np.zeros((len(subjects),  boots))
    
    
    for s, subject in enumerate(subjects):
        if subject == 'combined':
            # If combining, subsample to fewest trials for all subjects in set, then concat data
            subject_cue_val = []
            subject_response_val = []
            subject_choice_vals = []
            real_subjects = [s for s in subjects if s!='combined'] # same as grabbing df unique subjects unless you're not using all subjects in set
            for subject_id in behavior_data_valid['subject'].unique():
                subject_behavior_valid = behavior_data_valid[behavior_data_valid['subject']==subject_id]
                subject_cue_val.append(subject_behavior_valid['cue_val'].to_numpy())
                subject_response_val.append(subject_behavior_valid['response_val'].to_numpy())
                subject_choice_vals.append(subject_behavior_valid[['choice0', 'choice1', 'choice2', 'choice3']].to_numpy())
            # Determine resample size
            if subsample_size is None:
                resample_size = fewest_trials # resample to smallest subject n trials
                #resample_trial_idxs = np.zeros((boots, len(real_subjects), fewest_trials)) # initialize resample indices
            else: 
                resample_size =subsample_size
                #resample_trial_idxs = np.zeros((boots, len(real_subjects), subsample_size))
                warnings.warn('You are subsampling all subjects based on chosen value ' + str(subsample_size))
        else:
            subject_behavior_valid = behavior_data_valid[behavior_data_valid['subject']==subject]
            # Generate confusion matrix and choice probability matrix
            subject_cue_val = subject_behavior_valid['cue_val'].to_numpy()
            subject_response_val = subject_behavior_valid['response_val'].to_numpy()
            subject_choice_vals = subject_behavior_valid[['choice0', 'choice1', 'choice2', 'choice3']].to_numpy()
            # Determine resample size
            if subsample_size is None:
                resample_size = subject_cue_val.shape[0] # resample to subject full size
            else:
                resample_size = subsample_size
                warnings.warn('You are subsampling all subjects based on chosen value ' + str(subsample_size))
        print('for subject ', subject, 'the resample size is ', resample_size)

        # Run bootstrap
        boot_choice_biases = np.zeros((boots, n_colors))
        boot_choice_bias_sigmas = np.zeros((boots, n_colors))
        for boot in range(boots):
            if subject == 'combined':
                boot_cue_val = []
                boot_choice_vals = []
                boot_response_val = []
                for l in range(len(subject_cue_val)): # for each subject in combined set
                    resample_trial_idxs = rng.choice(np.arange(subject_cue_val[l].shape[0]), size = resample_size, replace=True)
                    boot_cue_val.extend(subject_cue_val[l][resample_trial_idxs])
                    boot_choice_vals.extend(subject_choice_vals[l][resample_trial_idxs])
                    boot_response_val.extend(subject_response_val[l][resample_trial_idxs])
            else:
                resample_trial_idxs = rng.choice(np.arange(subject_cue_val.shape[0]), size = resample_size, replace=True)
                boot_cue_val = subject_cue_val[resample_trial_idxs]
                boot_choice_vals = subject_choice_vals[resample_trial_idxs]
                boot_response_val = subject_response_val[resample_trial_idxs]
            
            # Ensure all inputs are np arrays
            boot_cue_val = np.asarray(boot_cue_val)
            boot_choice_vals = np.asarray(boot_choice_vals)
            boot_response_val = np.asarray(boot_response_val)
            
            cue_choice_confusion, choice_prob_matrix_choice_v_cue, cue_choice_counts = color_categories_funcs.get_choice_prob_matrix(
                boot_cue_val, boot_choice_vals, boot_response_val, n_colors)
            cue_choice_confusion_choice_v_cue = cue_choice_confusion.T # transpose to get same format as choice prob matrix
            
            if cue_choice_confusion_choice_v_cue.shape[0] != n_colors:
                sys.exit('choice probability matrix dimensions expect ' + str(n_colors) + ' squared but got ', cue_choice_confusion_choice_v_cue.shape)
        
            # Estimate choice biases
            theta_shift = np.zeros(n_colors)
            use_thetas = np.arange(0,360,360/n_colors) 

            cue_gauss_fits, choice_biases, estimated_sigmas = color_categories_funcs.model_choice_bias(choice_prob_matrix_choice_v_cue, n_colors, theta_shift, weights=cue_choice_counts, use_weights=False)
            
            gauss_fit_thetas = [x[0] for x in cue_gauss_fits]
            gauss_fit_cue_choice_arr = [x[1] for x in cue_gauss_fits]
            gauss_fit_y = [x[2] for x in cue_gauss_fits]
            
            average_sigma = np.mean(estimated_sigmas) * n_colors / 360 # smoothing is in index units not real angles
            smooth_choice_biases = uniform_filter(choice_biases, size=3, mode = 'wrap')
            
            if boot % 100 == 0:
                print('fitting data on boot ', boot)
                
            if boot % 500 == 0:
                # Plot confusion matrix
                fig, axs = plt.subplots()
                fig = color_categories_plot_funcs.plot_choice_matrix(axs=axs, fig=fig, subject=subject, 
                                          n_colors=n_colors, choice_prob_matrix=cue_choice_confusion_choice_v_cue,
                                          colors = color_rgb_defs, prob=False,
                                          out_dir = None, save = False)
                plt.show(fig)
                plt.close(fig)
                
                # Plot choice probability matrix
                fig, axs = plt.subplots(figsize=(10,10))
                fig = color_categories_plot_funcs.plot_choice_matrix(axs=axs, fig=fig, subject=subject, 
                                          n_colors=n_colors, choice_prob_matrix=choice_prob_matrix_choice_v_cue,
                                          colors = color_rgb_defs, prob=True,
                                          out_dir = out_dir, out_name = subject+'choice_probability_matrix', save = False)
                plt.show(fig)
                plt.close(fig)
            
                # Plot individual mixture model cue choice probability distribution fits
                fig, axs = plt.subplots(9, 10, figsize=(28,20), sharex=True, sharey=True)
                fig = color_categories_plot_funcs.plot_gauss_fits(axs=axs, fig=fig, subject=subject, 
                                    n_colors=n_colors, thetas = gauss_fit_thetas, aligned_matrix=gauss_fit_cue_choice_arr, 
                                    gauss_fits=gauss_fit_y,line_colors=color_rgb_defs,out_dir = out_dir, out_name = subject+'indiv_mm_gauss_fits', save = False)
                plt.show(fig)
                plt.close(fig)
            
        
            all_choice_biases[s][0][boot][:] = choice_biases
            all_choice_biases[s][1][boot][:] = estimated_sigmas
            all_choice_biases[s][2][boot][:] = smooth_choice_biases
            average_sigmas[s][boot] = average_sigma
            

    suffix = ''
    if subsample_size is not None:
        suffix = suffix + '_to_' + str(subsample_size)
    np.savez(os.path.join(out_dir, subject_set + '_choice_biases'+suffix+'.npz'), all_choice_biases=all_choice_biases, average_sigmas=average_sigmas)
    
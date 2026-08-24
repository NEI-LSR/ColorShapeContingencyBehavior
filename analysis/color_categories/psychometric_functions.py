"""
Compute and plot basic accuracy metrics for color categories data:
    Accuracy over time (by session and by trial)
    Accuracy per cue color (not normalized like a choice prob matrix)
    Psychometric functions
Toggle which subjects / subject sets (csc vs. naive)
Toggle dates included
View for individual subjects and combined (not currently normalized by amount of data per monkey)

"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from analysis.color_categories import cc_functions as color_categories_funcs
from analysis.color_categories import cc_plot_functions as color_categories_plot_funcs

# =============================================================================
# plt.rcParams['svg.fonttype'] = 'none'
# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.sans-serif'] = ['Helvetica']
# plt.rcParams['font.serif'] = ['Times']
# =============================================================================
use_fs = 10 # fontsize

# Change this 
subject_set = 'csc' # csc (color-shape stimuli monkeys) or naive (monkeys from PNAS 2025 paper)
remove_learning = True
n_nearby = 1 # 0 if only grab focal color, >0 if grab narrow range around it; e.g., 1 gives [cue-1, cue, cue+1]
use_only_correct_closest = False # if restrict psychometric function analysis to trials where choice was correct or closest foil
# Directories
data_dir = os.path.join('data', 'color_categories')
results_dir = os.path.join('results', 'color_categories')
out_dir = 'figures'
# Paradigm info
nafc = 4 # how many choice options per trial

#############
# Load data #
#############
# Gather data into common format based on subject set
behavior_data_path = os.path.join(data_dir, subject_set + '_valid_trials.csv')
behavior_data_valid = pd.read_csv(behavior_data_path)
if subject_set == 'csc': 
    # Subject and paradigm info
    subjects = ['wooster', 'jeeves', 'jocamo']
    n_colors=83 # how many hues in the stimulus set
elif subject_set == 'naive':
    # Subject and paradigm info
    subjects = ['buster', 'morty', 'pollux', 'castor']
    n_colors = 64
else:
    print('subject set not recognized. use one of csc or naive')
    
#########################
# Get color information #
#########################
# Load sRGB for color categories colors to use for plotting
try:
    cc_rgb = pd.read_csv(os.path.join('color_definitions', 'CC_'+ str(n_colors)+ 'colors_sRGB.csv'), header=None, names=['r','g','b'])
    color_rgb_defs = np.array(cc_rgb[['r','g','b']])/255.
except:
    cc_rgb = pd.read_csv(os.path.join('color_definitions', 'CC_'+ str(n_colors)+ 'colors_sRGB.csv'))
    color_rgb_defs = np.array(cc_rgb[['r','g','b']])/255.
# Six concepts colors 
csc_centers = pd.read_csv(os.path.join('color_definitions', 'CSC_category_centers.csv'))
csc_center_angle = csc_centers['angle'].to_numpy()
csc_center_id = csc_center_angle/360*n_colors
cc_closest_to_csc = np.round(csc_center_id).astype(int)

# Grab small margin of colors around the closest concept color
# Useful for better psychometric function fits (too little data if one cue only)
# but also because the closest concept color can be between two of the 64 or 83 colors
nearby = np.zeros((cc_closest_to_csc.size, n_nearby*2 + 1))
for i, cc_hue in enumerate(cc_closest_to_csc):
    # Find color ids immediately prior and after focal color
    cw_near_hues = np.ones(n_nearby)*cc_hue - np.arange(1, n_nearby+1)
    ccw_near_hues = np.ones(n_nearby)*cc_hue + np.arange(1, n_nearby+1)
    # Sort low to high then wrap to circle
    wrap_cw_near_hues = np.sort(cw_near_hues) % n_colors
    wrap_ccw_near_hues = np.sort(ccw_near_hues) % n_colors
    # assign to array
    near_hues = np.concatenate((wrap_cw_near_hues.astype(int), np.array(cc_hue)[...,np.newaxis], wrap_ccw_near_hues.astype(int)), axis=0, dtype=int)
    nearby[i][:] = near_hues

nearby = nearby.astype(int)
non_nearby = np.delete(np.arange(0,n_colors), nearby.flatten())

#################################
# Subject analysis and plotting #
#################################
# Plot for individual subjects
sliding_window = 1000 # have tested other values like 500 and conclusions do not change and trial cutoffs do not differ substantially
slope_ids = []#['all_nonfocal', 'focal1', 'focal2', 'focal3', 'focal4', 'focal5', 'focal6', 'all', 'all_focal']
save_weibull_slopes = np.zeros((len(subjects), 9, 3)) # will keep a total of 9 slopes (6 focal, avg nonfocal, avg all, avg focal)
subject_curves = []
for s, subject in enumerate(subjects):
    subject_behavior_valid = behavior_data_valid[behavior_data_valid['subject']==subject].reset_index()
    # Just visualizations
    # Plot sliding window average accuracy
    trial_accuracies = subject_behavior_valid['is_correct'].to_numpy()
    fig, axs = plt.subplots()
    fig = color_categories_plot_funcs.plot_acc_over_time(axs=axs, fig=fig, subject=subject, 
                       trial_accuracies=trial_accuracies, window_shape=sliding_window, 
                       title = None, out_dir = None, save = False)
    out_path = os.path.join(out_dir, 'figS3', subject + '_color_categories_learning_curve.svg')
    fig.savefig(out_path)
    out_path = os.path.join(out_dir, 'figS3', subject + '_color_categories_learning_curve.png')
    fig.savefig(out_path)
    plt.show(fig)
    plt.close(fig)
   
    # Plot accuracy per session
    session_accuracies = subject_behavior_valid.groupby('session')['is_correct'].mean().to_numpy()
    session_dates = list(subject_behavior_valid['session'].unique())
    fig, axs = plt.subplots()
    fig = color_categories_plot_funcs.plot_session_accuracy(axs=axs, fig=fig, subject=subject, 
                              session_dates=session_dates, session_accuracies=session_accuracies,
                              out_dir = None, save = False)
    plt.show(fig)
    plt.close(fig)
    
    # Also get reaction time
    if subject_set == 'csc':
        time_initiated = np.array(subject_behavior_valid['time_initiated'])
        time_responded = np.array(subject_behavior_valid['time_responded'])
        reaction_times = time_responded - time_initiated - 1250 # 1250 ms between initiation and choice presentation
        mean_reaction_time = np.mean(reaction_times)
        sample_std_reaction_time = np.std(reaction_times, ddof=1)
        fig, axs = plt.subplots()
        axs.hist(reaction_times, color='gray')
        axs.vlines(mean_reaction_time+sample_std_reaction_time,0,30000)
        axs.vlines(mean_reaction_time-sample_std_reaction_time,0,30000)
        axs.vlines(mean_reaction_time,0,30000, color='red')
        axs.text(.5,.9, 'mean RT: ' + str(mean_reaction_time), transform=axs.transAxes)
        axs.text(.5,.7, 'std RT: ' + str(sample_std_reaction_time), transform=axs.transAxes)
        plt.show(fig)
        plt.close(fig)
        
        print(f"subject {subject} had an average RT of {mean_reaction_time} with std {sample_std_reaction_time}")
    
    
    if remove_learning is True:
        # Remove trials before subject reaches plateau
        # Like with the learning behavior data, we treat plateau as the accuracy of the last 10,000 trials the monkey completed
        # and compute our cutoff as when accuracy reaches 95% of the way between chance and this plateau value
        plateau = subject_behavior_valid['is_correct'][-10000:-1].to_numpy()
        plateau_accuracy = np.mean(plateau)
        threshold = 0.95 * (plateau_accuracy - 0.25) + 0.25
        sliding_avg = np.lib.stride_tricks.sliding_window_view(subject_behavior_valid['is_correct'].to_numpy(), window_shape=sliding_window)
        acc_over_time = sliding_avg.mean(axis=1)
        reaches_plateau = np.where(acc_over_time > threshold)[0][0]
        print(f"subject {subject} reaches plateau at {reaches_plateau} trials")
        print(f"leaving {acc_over_time.shape[0] - reaches_plateau - 1} trials included in psych. functions")

        
        subject_behavior_valid = subject_behavior_valid.iloc[reaches_plateau:]
    
   
    
    # Plot psychometric functions
    suffix = '_range' + str(n_nearby * 2 + 1)
    if use_only_correct_closest is True:
        suffix = suffix + '_correct_or_closest'
        chose_correct_trials = subject_behavior_valid['response_val'] == subject_behavior_valid['cue_val']
        chose_closest_trials = subject_behavior_valid['response_val'] == subject_behavior_valid['closest_distractor_val']
        chose_correct_or_closest = chose_correct_trials + chose_closest_trials
        subject_behavior_valid = subject_behavior_valid[chose_correct_or_closest]
    
    # Psychometric curves
    # Want function for focal colors (color-shape colors), all non-focal colors, and all colors (focal and non-focal)

    # Get focal colors separate
    focal_colors = subject_behavior_valid[subject_behavior_valid['cue_val'].isin(nearby.flatten())]
    #focal_colors_separate = focal_colors.groupby(['cue_val', 'closest_distractor_distance'])['is_correct'].mean().reset_index()
    # Get focal colors together; by not computing acc within each color first, this essentially weights each color by presentation times
    #focal_colors_together = focal_colors.groupby(['closest_distractor_distance'])['is_correct'].mean().reset_index()
    focal_colors_together = focal_colors.groupby('closest_distractor_distance').agg(count=('closest_distractor_distance', 'count'), distance_accuracy=('is_correct', 'mean')).reset_index()
    # Get nonfocal colors; again, ignore cue value so long as cue is within nonfocal group
    nonfocal_colors = subject_behavior_valid[subject_behavior_valid['cue_val'].isin(non_nearby)]
    nonfocal_colors_together = nonfocal_colors.groupby('closest_distractor_distance').agg(count=('closest_distractor_distance', 'count'), distance_accuracy=('is_correct', 'mean')).reset_index()
    #.groupby(['closest_distractor_distance'])['is_correct'].mean().reset_index()
    # Get all colors
    all_colors_together = subject_behavior_valid.groupby('closest_distractor_distance').agg(count=('closest_distractor_distance', 'count'), distance_accuracy=('is_correct', 'mean')).reset_index() #
    #.groupby(['closest_distractor_distance'])['is_correct'].mean().reset_index()
    ####### The question is whether the focal vs nonfocal anova should compare focal w margin or no margin. 
# =============================================================================
#     
#     acc_by_cue_and_distractor = subject_behavior_valid.groupby(['cue_val', 'closest_distractor_distance'])['is_correct'].mean().reset_index()
#     # Pull out focal colors
#     focal_color_psychometrics = acc_by_cue_and_distractor[acc_by_cue_and_distractor['cue_val'].isin(nearby.flatten())]
#     # Average across nonfocal colors; just note this weights each color equally because it averages across cues, instead of computing before grouping by cue
#     nonfocal_color_psychometrics= acc_by_cue_and_distractor[acc_by_cue_and_distractor['cue_val'].isin(non_nearby)].groupby('closest_distractor_distance')['is_correct'].mean().reset_index()
#     # All colors
#     all_color_psychometric = acc_by_cue_and_distractor.groupby('closest_distractor_distance')['is_correct'].mean().reset_index()
#     
# =============================================================================
    
    # Compute curve for nonfocal colors
    nfcangle_dists_sorted, nfcangle_accs_sorted, nfcyfitweibull, _, nfcweibull_params = color_categories_funcs.compute_psychometric_curve(nonfocal_colors_together['closest_distractor_distance'].to_numpy(dtype=int),  
                                                                                                                                          nonfocal_colors_together['distance_accuracy'].to_numpy(dtype=float), n_colors, 
                                                                                                                                          weights=nonfocal_colors_together['count'].to_numpy(dtype=int), use_weights=False, fit_curve = True)
    weibull_slopes_at_mid =[color_categories_funcs.compute_weibull_slope_at_mid(nonfocal_colors_together['closest_distractor_distance'].to_numpy(dtype=int), 
                                                                                nfcyfitweibull, nfcweibull_params, n_colors)]
    slope_ids.append('all_nonfocal')


    color_curves = []
    # Start psychometric functions plot
    fig, ax = plt.subplots(figsize=(1.5,1.5)) #5,5
    for i in range(6):
        # Get focal colors separate
        focal_colors_separate = subject_behavior_valid[subject_behavior_valid['cue_val'].isin(nearby[i])] # focal color + small margin
        #fc_df = focal_colors_separate[focal_colors_separate['cue_val'].isin(nearby[i])]
        fc_df = focal_colors_separate.groupby('closest_distractor_distance').agg(count=('closest_distractor_distance', 'count'), distance_accuracy=('is_correct', 'mean')).reset_index() # collapse across focal colors + small margin
        #.groupby('closest_distractor_distance')['is_correct'].mean().reset_index() 
        fcangle_dists_sorted, fcangle_accs_sorted, fcyfitweibull, _,  fcweibull_params = color_categories_funcs.compute_psychometric_curve(fc_df['closest_distractor_distance'].to_numpy(dtype=int),  
                                                                                                                                           fc_df['distance_accuracy'].to_numpy(dtype=float), n_colors, 
                                                                                                                                           weights=fc_df['count'].to_numpy(dtype=int), use_weights=False,
                                                                                                                                           fit_curve = True)
        
        weibull_slopes_at_mid.append(color_categories_funcs.compute_weibull_slope_at_mid(fc_df['closest_distractor_distance'].to_numpy(dtype=int),
                                                                                         fcyfitweibull, fcweibull_params, n_colors))
        slope_ids.append('focal'+str(i))

        
        
        
        color_curves.append([fc_df['closest_distractor_distance'].to_numpy(),fc_df['distance_accuracy'].to_numpy(),fcyfitweibull])
        ax.scatter(fc_df['closest_distractor_distance'], fc_df['distance_accuracy'], color=color_rgb_defs[cc_closest_to_csc][i], s=2)
        ax.plot(fc_df['closest_distractor_distance'], fcyfitweibull, color=color_rgb_defs[cc_closest_to_csc][i], linewidth=.75)
    ax.scatter(nonfocal_colors_together['closest_distractor_distance'], nonfocal_colors_together['distance_accuracy'], color='black', s=2)
    ax.plot(nonfocal_colors_together['closest_distractor_distance'], nfcyfitweibull, color='black', linewidth=.75)
    #ax.set_xticks(np.arange(np.min(nonfocal_color_psychometrics['closest_distractor_distance']), np.max(nonfocal_color_psychometrics['closest_distractor_distance']+1)),
     #             labels = [str(x) for x in distances_in_angle])
    ax.set_yticks([.25,.5,1.0], labels = ['.25','.5','1.0'], fontsize=use_fs)
    ax.set_ylim((.22,1.1))
    ax.set_xticks([0,np.ceil(n_colors/4).astype(int),np.ceil(n_colors/2).astype(int)], labels=['0', '90', '180'], fontsize=use_fs)
    #ax.set_xlabel('Color difference (cue vs. foil, degrees)', fontsize=use_fs)
    #ax.set_ylabel('Accuracy', fontsize=use_fs)
    title = subject + '_psychometric_functions'
    #plt.axis('equal')
    #plt.axis('square')
    #plt.title(title)
    plt.savefig(os.path.join(out_dir, 'fig7', title + suffix + "_weibull.svg"))
    plt.savefig(os.path.join(out_dir, 'fig7', title + suffix + "_weibull.png"), dpi=300, bbox_inches='tight')

    plt.show()
    plt.close()
    
    color_curves.append([nonfocal_colors_together['closest_distractor_distance'].to_numpy(),
                         nonfocal_colors_together['distance_accuracy'].to_numpy(),
                         nfcyfitweibull])
    
    subject_curves.append([color_curves])
    
    # Fit for all colors
    allcangle_dists_sorted, allcangle_accs_sorted, allcyfitweibull, _, allcweibull_params = color_categories_funcs.compute_psychometric_curve(all_colors_together['closest_distractor_distance'].to_numpy(dtype=int),  
                                                                                                                                              all_colors_together['distance_accuracy'].to_numpy(dtype=float), n_colors, 
                                                                                                                                              weights=all_colors_together['count'].to_numpy(dtype=int), use_weights=False, fit_curve = True)
    weibull_slopes_at_mid.append(color_categories_funcs.compute_weibull_slope_at_mid(all_colors_together['closest_distractor_distance'].to_numpy(dtype=int),
                                                                                     allcyfitweibull, allcweibull_params, n_colors))
    slope_ids.append('all')

        
        
    # Average across focal colors; just note this weights each color equally because it averages across cues, instead of computing before grouping by cue
    avgfcangle_dists_sorted, avgfcangle_accs_sorted, avgfcyfitweibull, _, avgfcweibull_params = color_categories_funcs.compute_psychometric_curve(focal_colors_together['closest_distractor_distance'].to_numpy(dtype=int),  
                                                                                                                                                  focal_colors_together['distance_accuracy'].to_numpy(dtype=float), n_colors, 
                                                                                                                                                  weights=focal_colors_together['count'].to_numpy(dtype=int), use_weights=False, fit_curve = True)
    weibull_slopes_at_mid.append(color_categories_funcs.compute_weibull_slope_at_mid(focal_colors_together['closest_distractor_distance'].to_numpy(dtype=int), 
                                                                                     avgfcyfitweibull, avgfcweibull_params, n_colors))
    slope_ids.append('all_focal')

    
    save_weibull_slopes[s,:] = weibull_slopes_at_mid

        
slope_ids = slope_ids[:int(len(slope_ids)/len(subjects))]
save_out_weibull_slopes = pd.DataFrame(save_weibull_slopes[:,:,2].T, columns=subjects)
save_out_weibull_slopes['slope_id'] = slope_ids
save_out_weibull_slopes.to_csv(os.path.join(results_dir, subject_set + suffix + '_weibull_slopes.csv'), index=False)

halfmax = np.vstack((save_weibull_slopes[:,:,0],save_weibull_slopes[:,:,1]))
halfmax_df = pd.DataFrame(halfmax, columns=slope_ids)
halfmax_df['subject'] = subjects*2
halfmax_df['value'] = ['hue_angle']*len(subjects) + ['weibull_fit_acc']*len(subjects)
halfmax_df.to_csv(os.path.join(results_dir, subject_set + suffix + '_weibull_halfmax_info.csv'), index=False)


# Plot for combined subjects, weighting each subject equally
plot_colors = np.vstack([color_rgb_defs[cc_closest_to_csc], np.array([0.,0.,0.])])
color_avgs = []
for i in range(7):
    x = []
    y1 = []
    y2 = []
    for s in range(len(subject_curves)):
        x.extend(subject_curves[s][0][i][0])
        y1.extend(subject_curves[s][0][i][1])
        y2.extend(subject_curves[s][0][i][2])
    color_df = pd.DataFrame({'x': x, 'acc':y1, 'fit_acc':y2})
    avgs = color_df.groupby('x')[['acc', 'fit_acc']].mean().reset_index()
    
    avgangle_dists_sorted, avgangle_accs_sorted, avgyfitweibull, avgyfitgauss, avgweibull_params = color_categories_funcs.compute_psychometric_curve(avgs['x'].to_numpy(dtype=int),  
                                                                                                                                                     avgs['acc'].to_numpy(dtype=float), n_colors, 
                                                                                                                                                     weights=None, use_weights=False, fit_curve = True)
    avgs['fit_to_avg'] = avgyfitweibull
    color_avgs.append(avgs)

fig, axs = plt.subplots(figsize=(1.5,1.5))
for i in range(7):
    plot_color_df = color_avgs[i]
    axs.scatter(plot_color_df['x'], plot_color_df['acc'], color=plot_colors[i],  s=2)
    axs.plot(plot_color_df['x'], plot_color_df['fit_to_avg'], color=plot_colors[i], linewidth=.75)
axs.set_yticks([.25,.5,1.0], labels = ['.25','.5','1.0'], fontsize=use_fs)
axs.set_ylim((.22,1.1))
axs.set_xticks([0,np.ceil(n_colors/4).astype(int),np.ceil(n_colors/2).astype(int)], labels=['0', '90', '180'], fontsize=use_fs)
#axs.set_xlabel('Color difference (cue vs. foil, degrees)', fontsize=use_fs)
#axs.set_ylabel('Accuracy', fontsize=use_fs)
#axs.set_box_aspect(1)
plt.savefig(os.path.join(out_dir, 'fig7', subject_set + '_combined_'+suffix+'_weibull.svg'))
plt.savefig(os.path.join(out_dir, 'fig7', subject_set + '_combined_'+suffix+'_weibull.png'), dpi=300, bbox_inches='tight')
plt.show()
plt.close()


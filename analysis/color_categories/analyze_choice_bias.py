import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from analysis.color_categories import cc_functions as color_categories_funcs
from analysis.color_categories import cc_plot_functions as color_categories_plot_funcs
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica']
plt.rcParams['font.serif'] = ['Times']

# Change these
new_weighted = False
subsample_size = None
K=6 # fourier components to allow for

# Load data
data_dir = os.path.join('results', 'color_categories')
out_dir = os.path.join('figures', 'fig6')
color_dir = 'color_definitions'

if new_weighted == False:
    suffix = ''
    csc = np.load(os.path.join(data_dir, 'csc_choice_biases.npz'))
    naive = np.load(os.path.join(data_dir, 'naive_choice_biases.npz'))
else:
    suffix = '_weighted'
    csc = np.load(os.path.join(data_dir, 'csc_choice_biases_new_weighting.npz'))
    naive = np.load(os.path.join(data_dir, 'naive_choice_biases_new_weighting.npz'))

if subsample_size is not None:
    suffix = '_subsampled_to_' + str(subsample_size)
    csc = np.load(os.path.join(data_dir, 'csc_choice_biases'+suffix+'.npz'))
    naive = np.load(os.path.join(data_dir, 'naive_choice_biases'+suffix+'.npz'))

# Organize data
csc_choice_bias_arrs = csc['all_choice_biases'] # subjects x bias,sigma,smooth bias, boot, color
csc_sigmas = csc['average_sigmas']
naive_choice_bias_arrs = naive['all_choice_biases'] 
naive_sigmas = naive['average_sigmas']
all_choice_bias_arrs = [arr for arr in csc_choice_bias_arrs]
all_choice_bias_arrs.extend([arr for arr in naive_choice_bias_arrs])
all_sigmas = [arr for arr in csc_sigmas]
all_sigmas.extend([arr for arr in naive_sigmas])
bias_idx = 0
if csc_choice_bias_arrs.shape[1] == 3:
    smooth_bias_idx = 2
    sigma_idx = 1
elif csc_choice_bias_arrs.shape[1] == 4:
    smooth_bias_idx = 3
    sigma_idx = [1,2]
else:
    print('dimensions of input data not as expected')
    

# Get locations and sRGB of concept colors and nonuniformities, for plotting
csc_centers = pd.read_csv(os.path.join(color_dir, 'CSC_category_centers.csv'))
csc_center_angle = csc_centers['angle'].to_numpy()
csc_srgb_path = os.path.join(color_dir, 'CSC_cat_centers_sRGB.csv')
csc_srgb = pd.read_csv(csc_srgb_path, header=None, names=['r','g','b'])
csc_srgb_defs = np.array(csc_srgb[['r','g','b']])/255.
nonunif_locs = np.array([17, 212])

# Estimate choice biases and fourier decompositions
subjects_csc = ['wooster', 'jeeves', 'jocamo']
subjects_naive = ['buster', 'morty', 'pollux', 'castor']
if csc_choice_bias_arrs.shape[0] == 4:
    subjects_csc = subjects_csc + ['combined_csc']
    subjects_naive = subjects_naive + ['combined_naive']
subjects = subjects_csc + subjects_naive 

# Plot settings
size_big = (8,6)
size_small = (2.85,2.2)
size_smaller = (1.4, 1.1) #(1.8,1.35)
use_fs = 10 # fontsize

subject_ylims = [[-25,26], [-25,26],[-40,41], [-40,41], [-50,51], [-50,51], [-50,51], [-50,51],[-40,41]]
plot_sizes = [size_small,size_small,size_small,size_small,size_smaller,size_smaller,size_smaller,size_smaller,size_small]
#suffix = suffix + '_size_small'
    
subject_summary = []
fourier_info = []
fourier_coeffs = np.zeros((len(subjects), 2000, K*2))
fourier_dense = []
for s, subject in enumerate(subjects):
    # Get subject choice biases
    subject_boot_choice_biases = all_choice_bias_arrs[s][bias_idx][:]
    # Get n colors
    n_colors = subject_boot_choice_biases.shape[1]
    # Compute mean
    subject_choice_bias_means = np.mean(subject_boot_choice_biases, axis=0)
    # Print range of choice biases
    print(f"subject {subject}'s choice bias ranged from {np.min(subject_choice_bias_means)} to {np.max(subject_choice_bias_means)}")
    print(f"giving a magnitude range of {np.max(subject_choice_bias_means) + np.abs(np.min(subject_choice_bias_means))}")
    # Sort
    sorted_choice_biases = np.sort(subject_boot_choice_biases, axis=0)
    # Compute quantiles for CI
    subject_choice_bias_lower = np.quantile(sorted_choice_biases, q=.025, axis = 0)
    subject_choice_bias_upper = np.quantile(sorted_choice_biases, q=.975, axis = 0)
    subject_CIs = np.vstack((subject_choice_bias_lower, subject_choice_bias_upper))
    subject_SEs = np.std(subject_boot_choice_biases, axis=0, ddof=1)
    # Compute mean smooth curve
    subject_boot_smooth_choice_biases = all_choice_bias_arrs[s][smooth_bias_idx][:]
    subject_mean_smooth = np.mean(subject_boot_smooth_choice_biases, axis=0)
    
    subject_summary.append([subject_choice_bias_means, subject_mean_smooth, subject_CIs, subject_SEs])
    
    # Fourier regression
    theta = np.arange(0, 2*np.pi,2*np.pi/n_colors)
    x = color_categories_funcs.fourier_design_matrix(theta, K)
    
    theta_dense = np.arange(0, 2*np.pi,2*np.pi/360)
    x_dense = color_categories_funcs.fourier_design_matrix(theta_dense, K)
    
    fourier_powers = np.zeros((csc_sigmas.shape[1], K))
    fourier_fits = np.zeros((csc_sigmas.shape[1], n_colors))
    fourier_eval_dense = np.zeros((csc_sigmas.shape[1], 360))
    for boot in range(subject_boot_choice_biases.shape[0]):
        sample_array = subject_boot_choice_biases[boot]
        sample_array_demeaned = sample_array - np.mean(sample_array)
        
        beta, residuals, rank, s_ = np.linalg.lstsq(x, sample_array_demeaned, rcond=None)

        yfit = x @ beta
        # Find amplitude of each harmonic
        amps = []
        harmonics = []
        coeffs = []
        for k in range(1, K+1):
            a = beta[2*k -1]
            b = beta[2*k]
            amplitude = np.sqrt(a**2 + b**2)
            amps.append(amplitude)
            harmonics.append(color_categories_funcs.get_harmonic(theta, beta, k))
            coeffs.extend([a])
            coeffs.extend([b])
        fourier_coeffs[s][boot] = coeffs
            
        amps = np.asarray(amps)
        # the contribution of frequency k to the signal's variance (power) is proportional to 
        # the square of the fourier coefficient
        structure_accounted_for = (amps**2) / (amps**2).sum()
        fourier_powers[boot] = structure_accounted_for
        fourier_fits[boot] = yfit
        
        fourier_eval_dense[boot] = x_dense @ beta
    fourier_info.append([np.mean(fourier_fits, axis=0), fourier_powers])
    fourier_dense.append(np.mean(fourier_eval_dense, axis=0))



# Plot all of the above, and combine 
for s, subject in enumerate(subjects):

    # Retrieve info to plot
    subject_choice_bias_means = subject_summary[s][0]
    subject_mean_smooth = subject_summary[s][1]
    subject_CIs = subject_summary[s][2]
    subject_SEs = subject_summary[s][3]
    yfit = fourier_info[s][0]
    
    n_colors = subject_choice_bias_means.shape[0]
    use_thetas = np.arange(0,360,360/n_colors) 
        
    # Load sRGB for color categories colors to use for plotting
    try:
        cc_rgb = pd.read_csv(os.path.join(color_dir, 'CC_'+ str(n_colors)+ 'colors_sRGB.csv'), header=None, names=['r','g','b'])
        color_rgb_defs = np.array(cc_rgb[['r','g','b']])/255.
    except:
        cc_rgb = pd.read_csv(os.path.join(color_dir, 'CC_'+ str(n_colors)+ 'colors_sRGB.csv'))
        color_rgb_defs = np.array(cc_rgb[['r','g','b']])/255.  
    csc_center_id = csc_center_angle/360*n_colors
    cc_closest_to_csc = np.round(csc_center_id).astype(int)
    csc_locs_est = use_thetas[cc_closest_to_csc]
    nonunif_id = nonunif_locs/360*n_colors
    cc_closest_to_nonunif = np.round(nonunif_id).astype(int)
    nonunif_color_est = color_rgb_defs[cc_closest_to_nonunif]

    # Plot all this
    fig, axs = plt.subplots(figsize=plot_sizes[s]) 
    fig = color_categories_plot_funcs.plot_choice_bias(axs=axs, fig=fig, subject=subject,
                                                       n_colors=n_colors, choice_biases=subject_choice_bias_means,
                                                       smooth_choice_biases = subject_mean_smooth,thetas=use_thetas,
                                                       colors=color_rgb_defs,
                                                       fourier_fit = yfit,
                                                       confidence_intervals=subject_SEs,
                                                       concept_locations = csc_center_angle,
                                                       concept_colors = csc_srgb_defs,
                                                       nonuniformity_locations = nonunif_locs, 
                                                       nonuniformity_colors =  nonunif_color_est, 
                                                       ylims = subject_ylims[s],
                                                       out_dir=out_dir,out_name = subject+suffix+'_choice_bias_curve', save=True)
    
    plt.show(fig)
    plt.close(fig)
    
    # Determine candidate category centers as negative slope zero-crossings\
    # Find changes from positive to negative in the smoothed curve
    subject_mean_smooth_wrapped = np.concat((subject_mean_smooth, np.array([subject_mean_smooth[0]])))
    start_negative_zero_crossings = np.where((subject_mean_smooth_wrapped[:-1] >= 0) & (subject_mean_smooth_wrapped[1:] < 0))[0]
    end_negative_zero_crossings = start_negative_zero_crossings + 1
    # Linear interpolation
    estimated_crossings = start_negative_zero_crossings - ((subject_mean_smooth_wrapped[start_negative_zero_crossings])/(subject_mean_smooth_wrapped[end_negative_zero_crossings]-subject_mean_smooth_wrapped[start_negative_zero_crossings]))
    # In hue angle
    crossings_theta = estimated_crossings / n_colors * 360
    print(subject)
    print(crossings_theta)

    
# Fourier additional analysis
csc_idxs = [i for i in range(len(subjects)) if subjects[i] in subjects_csc and subjects[i] != 'combined_csc']
csc_fourier = [fourier_info[i] for i in csc_idxs]
csc_powers = [x[1] for x in csc_fourier]
csc_avg_powers = np.mean(csc_powers, axis=0)   

naive_idxs = [i for i in range(len(subjects)) if subjects[i] in subjects_naive and subjects[i] != 'combined_naive']
naive_fourier = [fourier_info[i] for i in naive_idxs]
naive_powers = [x[1] for x in naive_fourier]
naive_avg_powers = np.mean(naive_powers, axis=0)   

power_diffs =  csc_avg_powers - naive_avg_powers

power_diff_mean = np.mean(power_diffs, axis=0)
sorted_power_diffs = np.sort(power_diffs, axis=0)
lower = np.quantile(sorted_power_diffs, .025, axis=0)
upper = np.quantile(sorted_power_diffs, .975, axis=0)
CI = np.vstack((power_diff_mean-lower, upper-power_diff_mean))

fig, axs = plt.subplots(figsize = (1.5,1.5))
axs.bar(np.arange(0,K), power_diff_mean, facecolor='white', edgecolor='black')
axs.errorbar(np.arange(0,K), power_diff_mean,CI, ls='', color='black')
axs.hlines(0, 0, 5, color='black')
#axs.set_ylabel('Harmonic power (trained minus naive monkeys)', fontsize=use_fs)
#axs.set_xlabel('Fourier harmonic', fontsize=use_fs)
axs.set_xticks(np.arange(K), labels = [str(x) for x in np.arange(1, K+1)], fontsize=use_fs)
axs.set_yticks([-.3, 0, .3], labels=[str(x) for x in [-.3, 0, .3]],fontsize=use_fs)
plt.savefig(os.path.join(out_dir, suffix+'fourier_component_comparison.svg'))
plt.savefig(os.path.join(out_dir, suffix+'fourier_component_comparison.png'),dpi=300, bbox_inches='tight')
plt.show()
plt.close()



# =============================================================================
# for i in range(len(subjects)): # plot rel harmonic power for individual subjects
#     fourier_powers_subj = fourier_info[i][1]
#     fps_mean = np.mean(fourier_powers_subj, axis=0)
#     fps_sorted = np.sort(fourier_powers_subj, axis=0)
#     lower = np.quantile(fps_sorted, .025, axis=0)
#     upper = np.quantile(fps_sorted, .975, axis=0)
#     CI = np.vstack((fps_mean-lower, upper-fps_mean))
# 
#     fig, axs = plt.subplots(figsize = (2,2))
#     axs.bar(np.arange(0,K), fps_mean, facecolor='white', edgecolor='black')
#     axs.errorbar(np.arange(0,K), fps_mean,CI, ls='', color='black')
#     #axs.hlines(0, 0, 5, color='black')
#     axs.set_ylabel('Relative harmonic power', fontsize=use_fs)
#     axs.set_xlabel('Fourier harmonic', fontsize=use_fs)
#     axs.set_xticks(np.arange(K), labels = [str(x) for x in np.arange(1, K+1)], fontsize=use_fs)
#     axs.set_yticks([0, .5], labels=[str(x) for x in [0, .5]],fontsize=use_fs)
#     plt.show()
#     plt.close()
# 
# =============================================================================

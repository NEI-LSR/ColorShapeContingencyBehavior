import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica']
plt.rcParams['font.serif'] = ['Times']

data_dir = os.path.join('results', 'color_categories')
out_dir = os.path.join('figures')
correct_closest = False
r = 3 # for focal colors, what was the range around the focal color? should be 3

suffix = 'range' + str(r)
if correct_closest == False:
    csc_path = 'csc_range' + str(r) + '_weibull_slopes.csv'
    naive_path = 'naive_range'+ str(r) +'_weibull_slopes.csv'
else:
    suffix = suffix + '_correct_or_closest'
    csc_path = 'csc_range'+ str(r) +'_correct_or_closest_weibull_slopes.csv'
    naive_path = 'naive_range'+ str(r) +'_correct_or_closest_weibull_slopes.csv'

csc_slopes = pd.read_csv(os.path.join(data_dir, csc_path))
naive_slopes = pd.read_csv(os.path.join(data_dir, naive_path))

# Which slopes to actually plot
slope_ids_to_plot = ['focal0', 'focal1', 'focal2', 'focal3', 'focal4', 'focal5', 'all']
csc_slopes_to_plot = csc_slopes[csc_slopes['slope_id'].isin(slope_ids_to_plot)]#csc_slopes[~csc_slopes['slope_id'].isin(['all_nonfocal', 'all_focal'])]
naive_slopes_to_plot = naive_slopes[naive_slopes['slope_id'].isin(slope_ids_to_plot)]#naive_slopes[~naive_slopes['slope_id'].isin(['all_nonfocal', 'all_focal'])]

# Ensure both dfs are ordered according slope_ids_to_plot
csc_slopes_to_plot['ordered'] = [slope_ids_to_plot.index(x) for x in csc_slopes_to_plot['slope_id']]
naive_slopes_to_plot['ordered'] = [slope_ids_to_plot.index(x) for x in naive_slopes_to_plot['slope_id']]
csc_slopes_to_plot = csc_slopes_to_plot.sort_values(by='ordered')
naive_slopes_to_plot = naive_slopes_to_plot.sort_values(by='ordered')

csc_arr = csc_slopes_to_plot.drop(columns=['slope_id', 'ordered']).to_numpy()
naive_arr = naive_slopes_to_plot.drop(columns=['slope_id', 'ordered']).to_numpy()

csc_srgb = pd.read_csv(os.path.join('color_definitions', 'CSC_cat_centers_sRGB.csv'), header=None, names=['r','g','b'])
csc_srgb_defs = np.array(csc_srgb[['r','g','b']])/255.
if slope_ids_to_plot.index('all') == 6:
    colors = np.vstack((csc_srgb_defs, [0.,0.,0.]))
else:
    sys.exit('check your slope ordering and revisit')

# Plot colored by focal colors
fig, axs = plt.subplots(figsize=(1.5,1.5))
axs.axline((.0025, .0025), slope=1, color='black', linestyle='--', linewidth = .75)
for i in range(csc_arr.shape[1]): # for trained subject
    for j in range(4): # for untrained subject
        axs.scatter(csc_arr.T[i], naive_arr.T[j], color=colors,s=3) # plot all colors 
        axs.set_xticks([0.0025, .02], labels=['0.0025', '0.02'], fontsize=10)
        axs.set_yticks([0.0025, .02], labels=['0.0025', '0.02'], fontsize=10)
        #axs.set_xlabel('Trained monkeys', fontsize=10)
        #axs.set_ylabel('Untrained monkeys', fontsize=10)
#plt.axis('equal')
#plt.axis('square')
plt.savefig(os.path.join(out_dir, 'fig7', 'csc_vs_naive_weibull_slopes_'+suffix+'.svg'))
plt.savefig(os.path.join(out_dir, 'fig7', 'csc_vs_naive_weibull_slopes_'+suffix+'.png'), dpi=300, bbox_inches='tight')
plt.show()
plt.close()

# Plot colored by subject
if slope_ids_to_plot.index('all') == 6:
    markers = ['*']*6 + ['o']
else:
    sys.exit('check your slope ordering and revisit')

subject_facecolors = ['black', 'gray', 'none']
subject_edgecolors = ['black', 'gray', 'black']
fig, axs = plt.subplots(figsize=(3,3))
axs.axline((.0025, .0025), slope=1, color='black', linestyle='--', linewidth = .75)
for i in range(csc_arr.shape[1]):
    for j in range(4):
        for k in range(csc_arr.shape[0]):
            axs.scatter(csc_arr[k,i], naive_arr[k,j], facecolor=subject_facecolors[i], edgecolor = subject_edgecolors[i],marker=markers[k], s=15, alpha=1, linewidths=.5)
            #axs.scatter(csc_arr.T[i], naive_arr.T[j], facecolor=subject_facecolors[i], edgecolor = subject_edgecolors[i],s=15, alpha=1, linewidths=.3)
axs.set_xticks([0.0025, .02], labels=['0.0025', '0.02'], fontsize=10)
axs.set_yticks([0.0025, .02], labels=['0.0025', '0.02'], fontsize=10)
#axs.set_xlabel('Trained monkeys', fontsize=10)
#axs.set_ylabel('Untrained monkeys', fontsize=10)
#plt.axis('equal')
#plt.axis('square')
plt.savefig(os.path.join(out_dir, 'figS5', 'subject_color_code_csc_vs_naive_weibull_slopes_'+suffix+'.svg'))
plt.savefig(os.path.join(out_dir, 'figS5', 'subject_color_code_csc_vs_naive_weibull_slopes_'+suffix+'.png'), dpi=300, bbox_inches='tight')
plt.show()
plt.close()

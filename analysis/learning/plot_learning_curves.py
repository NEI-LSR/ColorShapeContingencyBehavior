"""
This script plots the learning behavioral data, for all tasks shown in Fig. 2
Uses outputs from analysisRL.m and bin_compute_confidence.py.
If long-term memory, plots binned accuracies and conf. intervals, and RL fits
Otherwise just plots binned accuracies
Run for one subject and task at a time, specified below. 
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.io import loadmat

# Make sure text is saved in svgs as text, not path
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.serif'] = ['Times']

# Choose subject
subject = 'w' # one of 'w', 'je', 'jo'

# Choose task
tasks = ['Probe_4AFC', 'Train_4AFC', 'Train_2AFC'] #, 'Train_2AFC_idtrials']
task = tasks[0] # which task to plot

# Load Data 
data_dir = os.path.join('results', 'learning') 
out_dir = os.path.join('figures', 'fig2') 
binned_data_path = subject + '_'+task+'_learning_curve_data_1000_bootstraps_all_binned.npz'

# Plotting specifications based on task
if 'Probe' in binned_data_path:
    has_RL_fit = True # plot RL fits
    has_CIs = True # plot confidence intervals
    has_years = True # include year transitions on x axis
    open_c = False # plot closed circles
    plot_size = (2.5,1.95)
    if subject == 'je':
        yceil = .8
    else:
        yceil = None
else:
    has_RL_fit = False
    has_CIs = True
    yceil = None
    open_c = True
    has_years = True
    if '4AFC' in binned_data_path or 'idtrials' in binned_data_path:
        plot_size = (2.1,1.95)#(2.5,2.25)#(4.7, 4)#(4.3,4.5)#(.78, .58)
    else:
        plot_size = (1.1,1.95)#(1.75, 4)#(1,4.5)#(.18, .58)

# Load binned data 
plot_data = np.load(os.path.join(data_dir, binned_data_path))

# Extract binned accuracies
x = [plot_data['color_x'], plot_data['shape_x']]
y = [plot_data['color_accs'], plot_data['shape_accs']]
bin_data = np.array([x,y])

# If applicable, extract binned accuracy confidence intervals
if has_CIs: 
    x_ci = [plot_data['color_i'], plot_data['shape_i']]
    y_ci = [plot_data['color_ci'], plot_data['shape_ci']]
    ci_data = [x_ci, y_ci]
else: 
    ci_data = None

# If applicable, extract RL fits
if has_RL_fit:
    color_mat = loadmat(os.path.join(data_dir, subject+'_Probe_4AFC_choose_color_RLfit.mat'))
    shape_mat = loadmat(os.path.join(data_dir, subject+'_Probe_4AFC_choose_shape_RLfit.mat'))
    x_fit = [[i for i in range(len(color_mat['mvAvgModel']))], [i for i in range(len(shape_mat['mvAvgModel']))]]
    y_fit = [np.squeeze(color_mat['mvAvgModel']), np.squeeze(shape_mat['mvAvgModel'])] 
    fit_data = [x_fit, y_fit]
else: 
    fit_data = None
    
# If applicable, extract years
if has_years:
    year_labels = plot_data['bin_year']
    if year_labels.shape > x[0].shape: # if more years than bins, drop last, years are aligned to the first bin
        year_labels = year_labels[:x[0].shape[0]] 
    # Only want to plot a year mark at the start of each year
    year_changes = [i for i in range(year_labels.shape[0]) if year_labels[i] != year_labels[i-1]] # which bins are year transitions
    if len(year_changes) == 0:
        year_changes = [0]
    include_years = year_labels[year_changes] # keep those years
    year_bins = x[0][year_changes] # get corresponding trial number (bin) values
    year_bins[0] = 0 # first bin includes trial 0 so align first year to x=0 rather than first bin
    year_data = [year_bins, include_years]
else:
    year_data = None


# Where to save plot out
data_name = str(binned_data_path).split('.')[0]
out_name =  subject + '_'+task+'_learning_curve'

# Plot


def create_save_learning_curve(axs: plt.Axes, fig: plt.Figure, title: str, 
                               bin_data: np.ndarray, ci_data: np.ndarray, 
                               fit_data: np.ndarray, year_data: np.ndarray, x=None, 
                               yceil=None, xposition=0., out_dir=None,
                               open_c=False, set_size=None):
    """
    expect bin_data as 2d nparray of (x,y), groups
    expect raw_data as  3d nparray of groups, (x,y), data (need to supply exact x vals in case does not match boot data
    """
    colors = ["#D95319", "tab:gray"]
    for i in range(bin_data.shape[1]):
        if open_c:
            axs.scatter(bin_data[0][i], bin_data[1][i], facecolor='none', edgecolor=colors[i], s=8, linewidth=.2, rasterized=False)
        else:
            axs.scatter(bin_data[0][i], bin_data[1][i], facecolor=colors[i], edgecolor=colors[i], s=8, linewidth=.5, rasterized=False)
        if ci_data is not None:
            axs.fill_between(ci_data[0][i], np.array(ci_data[1][i]).T[0], np.array(ci_data[1][i]).T[1], alpha=.2, color=colors[i], rasterized=False) # rasterize CIs else get svg rendering issues
        if fit_data is not None:
            axs.plot(fit_data[0][i], fit_data[1][i], color='black', linewidth=1)
    if np.max(bin_data[0]) > 20000:
        xtick = list(range(0, int(np.max(bin_data[0][0])), 20000))
    elif np.max(bin_data[0]) < 10000:
        xtick = [0, 10000]
    else:
        xtick = list(range(0, int(np.max(bin_data[0][0])), 1000))
    
    axs.margins(.05)
    if np.max(bin_data[0]) < 10000:
        axs.margins(.5)
        
    axs.tick_params(axis="both", length=3., pad=1)
    axs.tick_params(axis='x', pad=6)    

    if yceil is None:
        yceil = 1.
    #if yceil is not None:
    #    ytick = [.25,.5,yceil]
    #else:
    #    yceil = 1.
    ytick = [.25,.5,yceil]
    axs.set_yticks(ytick, labels=[str(yt) for yt in ytick], fontsize=10)
    axs.set_xticks(xtick)
    axs.set_xticklabels([int(xt/10000) for xt in xtick],fontsize=10)
    axs.set_ylim((.05, 1.05))#yceil+.05))
    
    axs.tick_params(axis="both", length=4., pad=0.)
    axs.tick_params(axis='x', pad=1) #  + 25 * (xpos - minyval)
    
    if year_data is not None:
        yr_ax = axs.secondary_xaxis(location=.0)
        yr_ax.set_xticks(year_data[0],year_data[1],fontsize=10)
        yr_ax.tick_params(axis='x', pad=.75, length=4.)
        yr_ax.xaxis.set_ticks_position('top')
        yr_ax.xaxis.set_label_position('top')

        
    if set_size is not None:
        l = axs.figure.subplotpars.left
        r = axs.figure.subplotpars.right
        t = axs.figure.subplotpars.top
        b = axs.figure.subplotpars.bottom
        figw = float(set_size[0])/(r-l)
        figh = float(set_size[1])/(t-b)
        axs.figure.set_size_inches(figw, figh)
    
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, title + '.svg'))
    fig.savefig(os.path.join(out_dir, title + '.png'),dpi=300, bbox_inches='tight')
    
    return fig



fig, axs = plt.subplots(figsize = plot_size)
test_plot = create_save_learning_curve(axs, fig, out_name, bin_data, ci_data=ci_data, fit_data=fit_data, year_data = year_data, 
                                       x=None, yceil=yceil, xposition=0., out_dir=out_dir,open_c=False, set_size=plot_size)


###

# =============================================================================
# def _set_size(w,h, ax=None):
#     """
#         force axis to take set size.
#         w, h: width, height in inches
#     """
#     if not ax: ax=plt.gca()
#     l = ax.figure.subplotpars.left
#     r = ax.figure.subplotpars.right
#     t = ax.figure.subplotpars.top
#     b = ax.figure.subplotpars.bottom
#     figw = float(w)/(r-l)
#     figh = float(h)/(t-b)
#     ax.figure.set_size_inches(figw, figh)
#     return ax
# =============================================================================

# =============================================================================
# def _set_fig_params(axs, fig, minyval=None, maxyval=None, xpos=0.):
#     #minyval = min(minyval, -.075 * maxyval)
#     scale = maxyval - minyval
#     maxyval = maxyval + .05 * scale
#    # minyval = minyval - 0 * scale
#     axs.set_ylim((minyval, maxyval))
#     axs.spines['top'].set_visible(False)
#     axs.spines['right'].set_visible(False)
#     axs.spines['bottom'].set_position(('data', xpos))
#     axs.margins(.01)
#     axs.tick_params(axis="both", length=2., pad=0.)
#     axs.tick_params(axis='x', pad=1) #  + 25 * (xpos - minyval)
#     fig.tight_layout()
#     return axs, fig
# ###     axs, fig = _set_fig_params(axs, fig, 0.2, 1., .2)
# =============================================================================
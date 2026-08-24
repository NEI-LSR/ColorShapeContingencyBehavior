"""
Plotting functions for color categories analysis
"""
import numpy as np
import matplotlib.pyplot as plt
import os


# Make sure text is saved in svgs as text, not path
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica']
plt.rcParams['font.serif'] = ['Times']

use_fs = 10 

def plot_acc_over_time(axs: plt.Axes, fig: plt.Figure, subject: str, 
                       trial_accuracies: np.ndarray, window_shape: int, 
                       title: str, out_dir = None, save = False):
    # Compute sliding average
    sliding_avg = np.lib.stride_tricks.sliding_window_view(trial_accuracies, window_shape=window_shape)
    acc_over_time = sliding_avg.mean(axis=1)
    axs.plot(acc_over_time, color='black')
    axs.set_ylim((0,1.0))#(.25, 1.1))
    axs.hlines(0.25,0,trial_accuracies.shape[0], color='black', linestyles='--')
    axs.set_xlabel('Trial')
    axs.set_ylabel('Accuracy')
    if save is True and out_dir is not None:
        fig.savefig(os.path.join(out_dir, title + ".svg"))
    return fig 

def plot_session_accuracy(axs: plt.Axes, fig: plt.Figure, subject: str, 
                          session_dates: list, session_accuracies: np.ndarray,
                          out_dir = None, save = False):
    title = subject + ' accuracy per session'
    axs.scatter(np.arange(session_accuracies.size), session_accuracies, color='black')
    axs.set_ylim((.25, 1.1))
    axs.set_title(title)
    axs.set_xlabel('Session')
    axs.set_ylabel('Accuracy')
    axs.set_xticklabels(session_dates)
    if save is True and out_dir is not None:
        fig.savefig(os.path.join(out_dir, title + ".svg"))
    return fig 

def plot_color_accuracy(axs: plt.Axes, fig: plt.Figure, subject: str, 
                          n_colors: int, color_accuracies: np.ndarray,
                          colors: np.ndarray, polar = True, out_dir = None, 
                          save = False):
    title = subject + ' accuracy per cue color'
    if polar is True:
        theta = np.linspace(0.0, 2 * np.pi, n_colors, endpoint=False)
        width = np.pi / n_colors
        axs = plt.subplot(projection='polar')
        axs.bar(theta, color_accuracies, width=width, bottom=0.0, color=colors)
    else:
        axs.bar(np.arange(n_colors), color_accuracies, color=colors)
        axs.set_xlabel('Cue color id')
        axs.set_ylabel('Accuracy')
    axs.set_title(title)    
    if save is True and out_dir is not None:
        fig.savefig(os.path.join(out_dir, title + ".svg"))
    return fig 

def plot_choice_matrix(axs: plt.Axes, fig: plt.Figure, subject: str, 
                          n_colors: int, choice_prob_matrix: np.ndarray,
                          colors: np.ndarray, prob=True, out_dir = None, 
                          out_name = None, 
                          save = False):
    if prob is True:
        title = subject + ' choice probability matrix'
        vmin=0
        vmax=1
    else:
        title = subject + ' choice confusion matrix'
        vmin=None
        vmax=None
    im = axs.imshow(choice_prob_matrix, cmap='Greys_r', vmin=vmin, vmax=vmax)
    if colors is not None:
        for i in range(n_colors):
            color_circ = plt.Rectangle((i,-2), width=2,height=2, color=colors[i])
            axs.add_patch(color_circ)
            color_circh = plt.Rectangle((-2,i), width=2,height=2, color=colors[i])
            axs.add_patch(color_circh)
    axs.set_xlim(-2, choice_prob_matrix.shape[1])
    axs.set_ylim(choice_prob_matrix.shape[0], -2)
    axs.set_xticks(np.arange(0,n_colors+1,30), [str(x) for x in np.arange(0,n_colors+1,30)], fontsize=use_fs)
    axs.set_yticks(np.arange(0,n_colors+1,30), [str(x) for x in np.arange(0,n_colors+1,30)], fontsize=use_fs)
    axs.set_xlabel('Cue ID', fontsize=use_fs)
    axs.set_ylabel('Choice ID', fontsize=use_fs)
    #fig.colorbar(im, ax=ax)
    cbar = fig.colorbar(im, ax=axs)
    cbar.solids.set_rasterized(True)
    # Set custom tick locations
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    # Set tick labels (optional)
    cbar.set_ticklabels(['0', '0.25', '0.5', '0.75', '1.0'])
    # Change tick label font size
    cbar.ax.tick_params(labelsize=use_fs)
    #axs.set_title(title)    
    if save is True and out_dir is not None:
        fig.savefig(os.path.join(out_dir, out_name + ".svg"))
        fig.savefig(os.path.join(out_dir, out_name + ".png"))
    return fig

def plot_gauss_fits(axs: plt.Axes, fig: plt.Figure, subject: str, 
                    n_colors: int, thetas: np.ndarray, aligned_matrix: np.ndarray, 
                    gauss_fits: np.ndarray,line_colors=None, out_dir = None, out_name=None, save = False):
    """
    subject : str
        subject name, for title and fig saving.
    n_colors : int
        number of colors in stimulus set (64 or 83).
    aligned_matrix : np.ndarray
        shape n_colors x n_colors. columns contain choice probability distributions
        for each cue. 
    gauss_fits : np.ndarray
        shape n_colors x n_colors. columns contain smooth gaussian fits to the 
        choice probability distributions for each cue. .

    """
    title = subject + ' mixture model individual Gaussian fits'
    if line_colors is not None:
        use_colors = line_colors
    else:
        use_colors = 'black'
    axs_flat = axs.flatten()
    for i in range(n_colors):
        sort_by = np.argsort(thetas[i])
        sorted_thetas = thetas[i][sort_by]
        sorted_points = aligned_matrix[i][sort_by]
        sorted_fits = gauss_fits[i][sort_by]
        axs_flat[i].scatter(sorted_thetas, sorted_points, color = 'black', s=40)
        axs_flat[i].plot(sorted_thetas, sorted_fits, color = use_colors[i], linewidth = 3)
        axs_flat[i].set_xlim(0,360)
        axs_flat[i].set_ylim(0,1.0)
    
    fig.suptitle(title)
    fig.tight_layout()
    if out_name is not None:
        title = out_name
    if save is True and out_dir is not None:
        fig.savefig(os.path.join(out_dir, title + ".svg"))
    return fig


def plot_choice_bias(axs: plt.Axes, fig: plt.Figure, subject: str, 
                    n_colors: int, choice_biases: np.ndarray, 
                    smooth_choice_biases: np.ndarray, thetas: np.ndarray,colors: np.ndarray,fourier_fit = None, 
                    confidence_intervals = None, concept_locations = None, concept_colors = None,
                    nonuniformity_locations = None, nonuniformity_colors = None, ylims = None, 
                    out_dir = None, out_name = None, save = False):
    title = subject + ' choice biases'
    #smooth_choice_biases = uniform_filter(choice_biases, size=smooth_size, mode = 'wrap')
    if smooth_choice_biases is not None:
        axs.plot(thetas, smooth_choice_biases, color='black', linewidth=1, zorder=5)
    if fourier_fit is not None:
        axs.plot(thetas, fourier_fit, color='grey', linewidth=1, zorder=5)
    if confidence_intervals is not None:
        if confidence_intervals.ndim == 1:
            y_lower = choice_biases - confidence_intervals
            y_upper = choice_biases +  confidence_intervals
            yerrs = confidence_intervals
        elif confidence_intervals.ndim == 2:
            if confidence_intervals.shape[0] == n_colors:
                confidence_intervals = confidence_intervals.T
            y_lower = confidence_intervals[0]
            y_upper = confidence_intervals[1]
            y_lower_magnitude = choice_biases - y_lower
            y_upper_magnitude = y_upper - choice_biases
            yerrs = np.vstack((y_lower_magnitude, y_upper_magnitude))
            
        else:
            print('cannot parse confidence interval dimensions')
        axs.fill_between(thetas, y_lower, y_upper, color='grey', alpha=.25)
        #axs.errorbar(thetas, choice_biases, yerr=[choice_biases-y_lower,y_upper-choice_biases], ecolor=colors, ls='')
    
    
    axs.hlines(0, 0, 360, color = 'black', linestyles='--', linewidth=1)
    if ylims is not None:
        axs.set_ylim((ylims))
        if ylims[0] in [-30, -45]:
            y_spacing = 15
        elif ylims[0] == -40:
            y_spacing = 20
        else:
            y_spacing = 5
        if concept_locations is not None:
            axs.vlines(concept_locations, ylims[0], ylims[1], color = concept_colors, linewidth=1)
        if nonuniformity_locations is not None:
            axs.vlines(nonuniformity_locations, ylims[0], ylims[1], color = nonuniformity_colors, linestyles='--', linewidth=1)
        axs.set_yticks(np.arange(ylims[0], ylims[1], y_spacing), [str(x) for x in np.arange(ylims[0], ylims[1], y_spacing)], fontsize=use_fs)
   
    if colors is not None:
        axs.scatter(thetas, choice_biases, color=colors, s=8, zorder=4) #55 # use 8 for paper
        
    axs.set_xticks(np.arange(0,361,120), [str(x) for x in np.arange(0,361,120)], fontsize=use_fs)
    #axs.set_xlabel('Cue color (degrees)', fontsize=use_fs)
    #axs.set_ylabel('Choice bias (degrees)', fontsize=use_fs)
    #axs.set_title(title)
    if out_name is not None:
        title = out_name
    if save is True and out_dir is not None:
        fig.savefig(os.path.join(out_dir, title + ".svg"))
        fig.savefig(os.path.join(out_dir, title + ".png"),dpi=300, bbox_inches='tight')
    return fig
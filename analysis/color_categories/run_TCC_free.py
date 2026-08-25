"""
Run the free variation of the TCC model 
"""

import os
import pandas as pd
import numpy as np
import torch
import matplotlib.pyplot as plt
from analysis.color_categories import TCC_model as tcc
from analysis.color_categories import cc_plot_functions as color_categories_plot_funcs

# Toggle this
subject = 'wooster' # one of [wooster, jeeves, jocamo, buster, morty, pollux, castor]
seed = 73 # for initialized similarity matrix
cv = True # fit with cross-validation folds
cv_folds = 5
fix_dprime = True # don't let dprime be a free parameter; see Garside et al.'s methods
epochs = 1000

data_dir = os.path.join('data', 'color_categories')
results_dir = os.path.join('results', 'color_categories')
out_dir = os.path.join('figures', 'figS4')
color_dir = 'color_definitions'

trained_subjects = ['wooster', 'jeeves', 'jocamo']
untrained_subjects = ['buster', 'morty', 'pollux', 'castor']

# Get path to dataframe containing behavioral per-trial data 
if subject in trained_subjects:
    behavior_path = os.path.join(data_dir, 'csc_valid_trials.csv')
    n_colors = 83
elif subject in untrained_subjects:
    behavior_path = os.path.join(data_dir,'naive_valid_trials.csv')
    n_colors = 64
else:
    print('subject not recognized')

# Load behavior data
behavior_data = pd.read_csv(behavior_path)
subject_data = behavior_data[behavior_data['subject']==subject].reset_index(drop=True)
# Grab trial info in numpy arrays
cue_ids = subject_data['cue_val'].to_numpy(dtype=int)
choice_ids = subject_data[['choice0', 'choice1', 'choice2', 'choice3']].to_numpy(dtype=int)
choice_made_ids = subject_data['response_loc'].to_numpy(dtype=int)
choice_correct = subject_data['is_correct'].to_numpy(dtype=int) #0=incorrect trials
incorrect_trial_idxs = np.where(choice_correct==0)[0]

# Initialize model parameters
# Fixed parameters
dprime = 1.0
# Parameters to fit
# Set up random number generator
rng = np.random.default_rng(seed=seed)
# Use to initialize similarity matrix 
free_similarity_matrix = rng.random((n_colors, n_colors)) # values in [0., 1.)

def train_tcc(mod, epochs, cue_id, choice_id, monkey_choice, param_optim, use_title):
    train_loss_ = []
    epoch_i = []
    for epoch in range(epochs):
        # Train model
        mod.train()
        # Get nll
        loss, trial_loss = mod(cue_id, choice_id, monkey_choice)
        param_optim.zero_grad()
        loss.backward()
        param_optim.step()
        
        with torch.no_grad():
            for param in tcc_mod.parameters():
                param.clamp_(min=0., max=1.)
    # =============================================================================
    #     tcc_mod.eval()
    #     with torch.inference_mode():
    #         check_probs = tcc_mod(cue_id, choice_id, monkey_choice)
    # =============================================================================
            
        if epoch % 250 == 0:
            print(epoch, loss)
            train_loss_.append(loss.detach().numpy())
            epoch_i.append(epoch)
            
            fig, ax = plt.subplots(figsize=(15,5))
            ax.imshow(mod.similarity_matrix.detach().numpy().T, cmap='Greys_r') 
            ax.set_title(use_title)
            ax.set_xlabel('cue')
            ax.set_ylabel('choice')
            plt.show()
            plt.close()
            
            for n, param in mod.named_parameters():
                #print('param is ', n)
                if param.grad is None:
                    print(n, 'is none')
                if param.requires_grad is False:
                    print(n, 'is not updating')

    plt.plot(train_loss_)
    plt.show()
    plt.close()
    return mod, loss

sim_mats = np.zeros((cv_folds, n_colors, n_colors))
if cv is True:
    trials = np.arange(len(cue_ids))
    rng.shuffle(trials)
    bins = np.floor(np.linspace(0,len(trials), cv_folds+1)).astype(int)
    train_ids = []
    test_ids = []
    for i in range(cv_folds):
        fold_test_idxs = trials[bins[i]:bins[i+1]]
        test_ids.append(fold_test_idxs)
        train_ids.append(np.delete(trials, np.arange(bins[i],bins[i+1])))

    fold_ll = np.zeros((2,cv_folds))
    for fold in range(cv_folds):
        tcc_mod = tcc.TCC_free(start_dprime=dprime, 
                               start_similarity_matrix=free_similarity_matrix)
        if fix_dprime == True:
            tcc_mod.dprime.requires_grad = False
        
        param_optim = torch.optim.Adam(params=tcc_mod.parameters(), lr=.01)
        
        train_cue_id = cue_ids[train_ids[fold]]
        train_choice_id = choice_ids[train_ids[fold]]
        train_choice_made_ids = choice_made_ids[train_ids[fold]]
        test_cue_id = cue_ids[test_ids[fold]]
        test_choice_id = choice_ids[test_ids[fold]]
        test_choice_made_ids = choice_made_ids[test_ids[fold]]
        test_monkey_choice_correct = choice_correct[test_ids[fold]]
        
        trained_tcc_mod, final_loss = train_tcc(tcc_mod, epochs, train_cue_id, train_choice_id, 
                                                train_choice_made_ids, param_optim, use_title='test')

        trained_tcc_mod.eval()
        with torch.no_grad():
            test_nll, test_trial_nll = trained_tcc_mod(test_cue_id, test_choice_id, test_monkey_choice_correct)
        
        total_trial_ll = -1*test_trial_nll
        
        total_ll = -1*test_nll
        fold_ll[0][fold] = total_ll / len(test_cue_id) # normalize to n trials 
        
        sim_mats[fold] = tcc_mod.similarity_matrix.detach().numpy()
        
    ll_df = pd.DataFrame({'fold_ll':fold_ll[0],'incorrect_trial_fold_ll':fold_ll[1]})
    
out_name = subject + '_free_similarity_matrix'
average_free_similarity_matrix = np.mean(sim_mats, axis=0)
#np.save(os.path.join(results_dir, out_name + '.npy'), average_free_similarity_matrix)


# The matrix needs to be transposed to have choice id as rows
choice_v_cue = average_free_similarity_matrix.T
# Load sRGB for color categories colors to use for plotting
try:
    cc_rgb = pd.read_csv(os.path.join(color_dir, 'CC_'+ str(n_colors)+ 'colors_sRGB.csv'), header=None, names=['r','g','b'])
    color_rgb_defs = np.array(cc_rgb[['r','g','b']])/255.
except:
    cc_rgb = pd.read_csv(os.path.join(color_dir, 'CC_'+ str(n_colors)+ 'colors_sRGB.csv'))
    color_rgb_defs = np.array(cc_rgb[['r','g','b']])/255.
fig, axs = plt.subplots(figsize=(2.9,2.9))#(2.3,2.3))

fig = color_categories_plot_funcs.plot_choice_matrix(axs=axs, fig=fig, subject=subject,
                                                     n_colors=n_colors, choice_prob_matrix=choice_v_cue,
                                                     colors=color_rgb_defs, prob=True, out_dir=out_dir, out_name=out_name, save=True)
plt.show(fig)
plt.close(fig) 
    
   
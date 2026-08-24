"""
Python implementation of TCC free similarity matrix modeling, implemented
in MATLAB in Garside et al., 2025, PNAS
"""
import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Normal
import torch.nn.functional as F

# Set up model
class TCC_free(nn.Module):
    def __init__(self, start_dprime, start_similarity_matrix):
        super().__init__()
        self.dprime = nn.Parameter(torch.tensor(start_dprime, dtype=torch.float32), requires_grad=True)
        self.similarity_matrix = nn.Parameter(torch.tensor(start_similarity_matrix, dtype=torch.float32), requires_grad=True)
        self.normd = Normal(0.,1.)
        
    def forward(self, cue_id, choice_id, monkey_choice):
        # Calculate angular diffs between each pair
        cue_id = torch.tensor(cue_id,dtype=torch.int64)
        choice_id = torch.tensor(choice_id,dtype=torch.int64)
        monkey_choice = torch.tensor(monkey_choice,dtype=torch.int64)
        
        cf = self.similarity_matrix[cue_id[:, None],choice_id]
        cf = cf*self.dprime # Scale by "memory strength"

        # Compute the probability that each choice will be more familiar than each other on each trial
        # Compute the standardized difference between each choice-choice pair
        z_mat = (torch.t(cf)[:,None,:] - torch.t(cf)[None,:,:]) / np.sqrt(2)  # comparison of two gaussians with independent noise
        
        #z_mat = z_mat.T
        # Convert to probability 
        p_mat = self.normd.cdf(z_mat) # each trial 4x4 matrix prob. i beats j
        pmat_star = 0.90*p_mat + 0.15 # MC correction factor
        # calculate probability of each choice option (that option over all other options)
        p_star = torch.prod(pmat_star, dim=1)*(1/(0.90*.5 + 0.15)) # last bit removes the self-comparison

        # Normalize probabilities and scale by temperature
        p_star[p_star>=1] = 1 - 1e-6
        logits_star = torch.log(p_star/(1-p_star)) # convert probabilities to logits
        #logits_scaled = logits_star * self.temperature # scale by temperature
        p_star_norm = F.softmax(logits_star,dim=0)

        # For each trial
        # get the response that was made
        trial_idx = torch.arange(len(monkey_choice))
        prob_of_selected = p_star_norm[monkey_choice,trial_idx] # probability of choosing that response
        # Compute negative log likelihood across all trials
        trial_nll = -1*torch.log(prob_of_selected)
        nll = torch.sum(trial_nll)
        return nll, trial_nll 

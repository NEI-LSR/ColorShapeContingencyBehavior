# Figures guide

This guide describes how to generate each figure in the manuscript. It describes inputs, outputs, and how to run each analysis script. You can find detailed descriptions of what each analysis script does in the README.md as well as at the top of each script. The directory structure of this repository is described in the README.md file.

## Prerequisites/Notes: 

1. Clone this repo and, wherever you're running the code, set your working directory to your cloned repository (i.e., to the directory that contains subdirectories 'data', 'results', etc.). All paths are relative to this directory. 

2. All code has been tested in python 3.12 and MATLAB R2026a. 

3. The wording below assumes you are running all python scripts in a python IDE. They can also be run from a terminal: if variables need to be changed, open the file, change the variable, close the file, then run `python [filename]` in your terminal. None of the scripts use command line arguments. 

4. Each figure is saved out twice, once as a scalable vector graphic (.svg) and once as a png. 

## Learning 

### Fig. 2B, 2D: short-term memory and long-term memory learning curves
1. **Raw trial data** are in `data/learning` and are named as `[subject]_[task]_[x]AFC.csv`. When "task" = "Train" this corresponds to short-term memory trials; "task" = "Probe" corresponds to long-term memory trials. When x=2, this is a 2-alternative forced choice task; when x=4, a 4-alternative forced choice task. 

2. **Basic summary statistics:** Open `analysis/learning/learning_performance.py`. No inputs need to be changed. Click run. This script outputs two items:

    1. `results/learning/[task]plateau_performance_last_10000_trials.csv` for each task "Train_4AFC", "Train_2AFC_idtrials", "Probe_4AFC". These csvs contain each subject's plateau performance (with 95% CI), computed as accuracy over bootstraps of the last 10000 trials. 
    
    2. `results/learning/Probe_2AFCinitial_performance`: a csv containing performance from subjects W and Je on 2AFC long-term memory trials completed before any exposure to the stimuli through short-term memory trials (this is reported in the Methods section). 

3. **Bin and bootstrap trial data:** Open `analysis/learning/bin_compute_confidence.py`. The inputs to this script are the raw trial data and output #1 of step #2 above. At the top of the script, change `subject=''` and `task=''` to the subject and task you want to obtain learning curves for. For Fig. 2B, you will run this 5 times:
    
    - `subject='w'` `task='tasks[2]'` (2AFC short-term memory trials)
    - `subject='w'` `task='tasks[3]'` (4AFC short-term memory trials)
    - `subject='je'` `task='tasks[2]'`
    - `subject='je'` `task='tasks[3]'`
    - `subject='jo'` `task='tasks[2]'`

    and for Fig. 2D, you will run this 3 times:

    - `subject='w'` `task='tasks[1]'` (4AFC long-term memory trials)
    - `subject='je'` `task='tasks[1]'`
    - `subject='jo'` `task='tasks[1]'`

    This outputs two things:

    1. `results/learning/[subject]_[task]_[n]AFC_learning_curve_data_1000_bootstraps_all_binned.npz`: one zipped numpy archive per subject/task combination. Each zip archive contains binned trial data for each trial type and corresponding 95% CIs, as well as year labels for each bin. E.g., `w_Train_4AFC_learning_curve_data_1000_bootstraps_all_binned.npz` is the file for monkey W's 4AFC short-term memory learning curve data.

    2. In your python console it will print out the number of trials and sessions each subject completed, and for how many trial bins of the learning phase of long-term memory trials performance on shape-to-color trials was above performance on color-to-shape trials (see Methods).

4. **Fit reinforcement learning model:** Open `analysis/learning/analysisRL.m` in MATLAB. The input to this script are the raw trial data in `data/learning`. The function `analyse4AFCProbeData()` takes three positional arguments: subject, task, saveFiles. Make sure task = `"Probe_4AFC"` and saveFiles = `true`. Run the script for each subject (`"w"`, `"je"`, and `"jo"`). This outputs 3 items per subject:

     1. `results/learning/[subject]_Probe_4AFC_RL_params.csv`, which contains the RL fit parameters (learning rate, inverse temperature, and initial value / initial performance) and 95% CIs. 
     
     2. `results/learning/[subject]_Probe_4AFC_choose_shape_RLfit.mat`, which contains the RL fit yvalues (accuracies) for color-to-shape trials.
     
     3. `results/learning/[subject]_Probe_4AFC_choose_color_RLfit.mat`, which contains the RL fit yvalues (accuracies) for shape-to-color trials.

5. **Plot figures**: Open `analysis/plot_learning_curves.py`. This script takes as input the outputs of steps 3 and 4 to plot the learning curves shown in Fig. 2B and 2D. Run this script for each subject and task separately by changing the inputs to `subject=''` and `task=''` at the top of the script. This outputs one figure per subject/task combination:

    1. `figures/fig2/[subject]_[task]_[n]AFC_learning_curve.svg`, `.png`.



## Identification (Figs. 3,4)

### Figs. 3B, 3C, 3F: Monkey identification trials
1. **Raw trial data** are in `data/identification/monkeyP3data.csv`.

2. **Analyze and plot**: Open `analysis/identification/MT1P3_analysis.m` in MATLAB. Click Run. A pop-up Options box with a checkbox saying "human data" will appear. Do not check the checkbox. Click continue. The script will run and output 4 items:

    1. `results/identification/monkey_choosecolor_probs.csv`: a csv containing the choose color over choose shape probabilities
    2. `figures/figs3_4/Monkey_bar_chart.svg`, `.png`: Fig. 3B
    3. `figures/figs3_4/Monkey_scatter_identification.svg`, `.png`: Fig. 3C
    4. `figures/figs3_4/Monkey_polar_identification.svg`, `.png`: Fig. 3F

### Fig. 3D: Human colorfulness ratings

1. **Raw trial data** are in `data/identification/MoreColor_i.csv` for $i \in [2,3]$. The different files contain different batches of human participants. 

2. **Analyze and plot**: Open `analysis/identification/MoreColor.m` in MATLAB. Click run. The script will output 2 items.

    1. `results/identification/morecolor_probs.csv`: a csv containing the probability each color is rated more colorful than the other colors
    2. `figures/figs3_4/more_colorful_polar_identification.svg`, `.png`: Fig. 3D

### Fig. 4: Human identification trials

1. **Raw trial data** are in `data/identification/[shapecolor_i].csv` for $i \in [10, 18]$. The different csvs contain different batches of human participants. 

2. **Analyze and plot:** Open `analysis/identification/MT1P3_analysis.m` in MATLAB. Click Run. A pop-up Options box with a checkbox saying "human data" will appear. Check the checkbox. Click continue. This script calls on `getMT1P3HumanData.m` to compile and parse through the 9 input csvs. The script will run and output 4 items:

   1. `results/identification/human_choosecolor_probs.csv`: a csv containing the choose color over choose shape probabilities
    2. `figures/figs3_4/Human_bar_chart.svg`, `.png`: Fig. 4A
    3. `figures/figs3_4/Human_scatter_identification.svg`, `.png`: Fig. 4B
    4. `figures/figs3_4/Human_polar_identification.svg`, `.png`: Fig. 4C


### Fig. 3E: Colorfulness ratings and probability of choosing color comparison

1. **Prerequisite**: You must run the three sections above (Figs. 3B, 3C, 3F; Fig. 3D, and Fig. 4) before completing this. The inputs to this analysis are the `morecolor_probs.csv` and the human or monkey `_choosecolor_probs.csv` files.

2. **Plot comparison:** Open `analysis/identification/plotProbvsMoreColor.m`. Click run. This will display in the MATLAB console the pearson correlation and corresponding p-value for the relationship between the choose color probabilities and the rated as more colorful probabilities (for humans and monkeys separately). It also outputs Fig. 3E at `figures/figs3_4/Monkey_choosecolor_vs_morecolor.svg`, `.png`.

## Color categories (Figs. 6, 7, S3, S4, S5)

### Fig. 6A, 6B, 6C: choice bias curves

1. **Raw trial data** are in `data/color_categories` and are named `csc_valid_trials.csv` and `naive_valid_trials.csv`. Anywhere the prefix "csc" is used refers to the trained ("ColorShapeContingency") monkeys; anywhere the prefix "naive" is used refers to the untrained monkeys (from Garside et al., 2025). Each csv contains all completed trials (aborted trials are excluded) for all subjects in each subject group. All analyses of these data use only completed trials. 

2. **Estimate choice biases:** Open `analysis/color_categories/estimate_choice_bias.py`. At the top of this script under the note "Change this", you can change the number of bootstrap iterations (`boots=`) and trial sample size (`subsample_size=`, e.g., if you wanted to run a power analysis).  Make sure these are set to `boots=1000` and `subsample_size=None`. Click run. This will estimate the choice biases for each subject separately, as well as each combined subject group. This script produces intermediate plots: it will display the cue-choice confusion matrix, choice probability matrix (normalized confusion matrix), and gaussian fits overlaid with choice probability distributions for all cue colors for every 500th bootstrap. It outputs one item per subject group (trained, untrained):

    1. `results/color_categories/csc_chioce_biases.npz` and `results/color_categories/naive_choice_biases.npz`: a zipped archive of numpy arrays. One of the arrays contained in it, `all_choice_biases`, is the input to the next step, and contains all the bootstraped estimates of the choice biases. 

3. **Plot choice biases and run Fourier regression:** Open `analysis/color_categories/analyze_choice_bias.py`. Make sure `subsample_size=None` and `K=6` at the top of this script. If you subsampled in step 2, you would change `subsample_size=` to the subsampled number of trials. `K` is the number of Fourier components to fit in the Fourier regression. Click run; it will run for all subjects and combined subject groups. This script outputs 3 items:

    1. It will print out in your python console, for each subject, the range and magnitude of the range of choice bias. These are reported in the manuscript text.

    2. `figures/fig6/[subject]_choice_bias_curve.svg`, `.png`: Fig. 6A plots (subject = "combined_naive" for averaged untrained monkeys, subject = "buster" for Bu, "castor" for Ca, "pollux" for Po, "morty" for Mo, and Fig. 6B plots (subject = "wooster" for W, "jeeves" for Je, "jocamo" for Jo).

    3. `figures/fig6/fourier_component_comparison.svg`, `.png`: Fig. 6C, the comparison of the relative harmonic power between trained and untrained monkeys. 


### Figs. 7A and S3: Color Categories psychometric functions and learning curves

1. **The input data are again the raw trial data** (`data/color_categories/csc_valid_trials.csv` and `data/color_categories/naive_valid_trials.csv`).

2. **Fit and plot psychometric functions, compute half-max slopes** Open `analysis/color_categories/psychometric_functions.py`. At the top of the script, set   `subject_set = 'naive'`. Make sure `remove_learning = True`, `n_nearby = 1`, and `use_only_correct_closest = False` (see comments in code for more info about these variables). Click run. When it finishes running, go back to the top, set   `subject_set = 'csc'`, and click run again. This script outputs 6 things:

    1. In the python console it will print out the mean and standard deviation of the reaction time per subject for trained subjects. 

    2. In the python console it will print out the trial number where each subject reaches the end of their task "learning phase" (see Methods for details). All trials before then are removed from the psychometric function analysis. It will print how many trials this leaves as a part of the analysis. 

    3. `figures/figS3/[subject]_color_categories_learning_curve.svg`, `.png`: Fig. S3 for each of the trained subjects, the sliding window accuracy learning curves for the color categories task

    4. `figures/fig7/[subject]_psychometric_functions_range3_weibull.svg`, `.png`: Fig. 7A, the psychometric functions for each individual subject and the average across subjects (subject = `naive_combined` for the untrained monkeys, `csc_combined` for the trained monkeys). The individual trained monkeys and the average of the untrained monkeys are reported in Fig. 7A. 

    5. `results/color_categories/[subject_set]_weibull_slopes.csv`: one csv per subject group ("csc", "naive") containing the psychometric function slopes at half-max. There are 9 slopes per subject (6 colored shape colors, all colored shape colors combined, all non colored shape colors combined, all cue colors combined).

    
    6. `results/color_categories/[subject_set]_range3_weibull_halfmax_info.csv`: one csv per subject group ("csc", "naive") containing hue angle and accuracy corresponding to each half-max slope in output #5 above. 

### Figs. 7B and S5: Color categories psychometric function 

1. **The input data are the csvs from output #5 above**, that is, `results/color_categories/csc_weibull_slopes.csv` and `results/color_categories/naive_weibull_slopes.csv`.

2. **Plot comparison of half-max slopes:** Open `analysis/color_categories/psychometric_slopes/py`. Make sure at the top `correct_closest = False` and
`r = 3` (see code for details on these variables). Click run. This outputs two items:

    1. `figures/fig7/csc_vs_naive_weibull_slopes_range3.svg`, `.png`: Fig. 7B, a scatter plot comparing the psychometric function slopes of trained and untrained monkeys

    2. `figures/figS5/subject_color_code_csc_vs_naive_weibull_slopes_range3.svg`, `.png`: Fig. S5, the same plot as 7B but color coded by trained subject. 


### Fig. S4: Color categories free similarity matrices

1. **The input data are the raw trial data** (`data/color_categories/csc_valid_trials.csv` and `data/color_categories/naive_valid_trials.csv`).

2. **Fit TCC free model to choice probabilities and plot free similarity matrices:** Open `analysis/color_categories/run_TCC_free.py`. At the top, set `subject = 'wooster'`. Make sure  `cv=True`, `cv_folds = 5`, `fix_dprime = True`, and `epochs = 1000` (see code for more details on these variables). This will fit the "free" variation of the Target Confusability Competition (TCC) model on the subject's choice probability matrix in 5 cross-validation folds. Click run. The script will produce intermediate plots. For each cross-validation fold, it will plot the randomly initialized free similarity matrix and the matrix on every 250th training epoch. At the end of training for each fold, it will plot the loss function over training epochs. When the script finishes running, return to `subject=''` and iterate through the remaining 6 subjects (jeeves, jocamo, buster, morty, pollux, castor). This script has one output per subject:

    1. `figures/figS4/[subject]_free_similarity_matrix.svg`, `.png`: each subject's free similarity matrix in Fig. S4.

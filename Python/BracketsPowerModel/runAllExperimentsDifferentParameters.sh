#!/bin/bash

# This script runs several experiments and prints timestamps between them.

# #---------- First Batch of 10k Experiments --------------#

# # Run experiment 10k_1, with:
# # 10000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # range of 0.4 for sampling alphas (+/- 0.2 from center).
# date
# ./runExperimentsFlexible.py 10000 0 1 0.4

# # Run experiment 10k_2, with:
# # 10000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # Randomly generated range K, uniformly from [0, 0.4)
# date
# ./runExperimentsFlexible.py 10000 0 0 0.4

# # Run experiment 10k_3, with:
# # 10000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # range of 0.2 for sampling alphas (+/- 0.1 from center)
# date
# ./runExperimentsFlexible.py 10000 0 1 0.2

# # Run experiment 10k_4, with:
# # 10000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # range of 0.1 for sampling alphas (+/- 0.05 from center).
# date
# ./runExperimentsFlexible.py 10000 0 1 0.1

# # Run experiment 10k_5, with:
# # 10000 trials, 
# # fixed R1 alphas (matchup-specific),
# # range of 0.4 for sampling other round alphas (+/- 0.2 from center).
# # (This is very similar to Version 5 from old tests)
# date
# ./runExperimentsFlexible.py 10000 1 1 0.4
# date

# Note: These are the timestamps generated the first time I ran this script, 
# with only the 10k experiments:
# $ ./runAllExperimentsDifferentParameters.sh 
# Thu Feb 22 23:46:47 CST 2018
# Thu Feb 22 23:47:24 CST 2018 (37s elapsed)
# Thu Feb 22 23:48:00 CST 2018 (36s elapsed)
# Thu Feb 22 23:48:36 CST 2018 (36s elapsed)
# Thu Feb 22 23:49:13 CST 2018 (37s elapsed)
# Thu Feb 22 23:49:48 CST 2018 (35s elapsed)


#---------- 50k Experiments --------------#

# # Run experiment 50k_1, with:
# # 50000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # range of 0.4 for sampling alphas (+/- 0.2 from center).
# date
# ./runExperimentsFlexible.py 50000 0 1 0.4

# # Run experiment 50k_2, with:
# # 50000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # Randomly generated range K, uniformly from [0, 0.4)
# date
# ./runExperimentsFlexible.py 50000 0 0 0.4

# # Run experiment 50k_3, with:
# # 50000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # range of 0.2 for sampling alphas (+/- 0.1 from center)
# date
# ./runExperimentsFlexible.py 50000 0 1 0.2

# # Run experiment 50k_4, with:
# # 50000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # range of 0.1 for sampling alphas (+/- 0.05 from center).
# date
# ./runExperimentsFlexible.py 50000 0 1 0.1

# # Run experiment 50k_5, with:
# # 50000 trials, 
# # fixed R1 alphas (matchup-specific),
# # range of 0.4 for sampling other round alphas (+/- 0.2 from center).
# # (This is very similar to Version 5 from old tests)
# date
# ./runExperimentsFlexible.py 50000 1 1 0.4
# date

# Timestamps for 50k experiments (both running and summarizing):
# $ ./runAllExperimentsDifferentParameters.sh; ./summarizeAllExperimentsDifferentParameters.sh
# Fri Feb 23 00:08:19 CST 2018
# Fri Feb 23 00:11:19 CST 2018
# Fri Feb 23 00:14:21 CST 2018
# Fri Feb 23 00:17:31 CST 2018
# Fri Feb 23 00:20:35 CST 2018
# Fri Feb 23 00:23:32 CST 2018
# Fri Feb 23 00:23:32 CST 2018
# Fri Feb 23 00:23:35 CST 2018
# Fri Feb 23 00:23:38 CST 2018
# Fri Feb 23 00:23:42 CST 2018
# Fri Feb 23 00:23:45 CST 2018
# Fri Feb 23 00:23:48 CST 2018

#---------- 10k Experiments --------------#
# Run ten batches of nine experiments 
# (the only difference is the sampling range for the alpha values):

# for batchNum in `seq 1 10`;
# do
# 	for i in `seq 2 10`;
# 	do
# 		if [ $i -lt 10 ]; then
# 			./runExperimentsFlexible.py 10000 0 1 0.$i $batchNum
# 		else
# 			./runExperimentsFlexible.py 10000 0 1 1.0 $batchNum
# 		fi
# 	done
# 	echo $batchNum:
# 	date
# done

# # Batch11: alpha = 0
# ./runExperimentsFixedAlpha.py 10000 11 0
# # Batch12: alpha = -0.5
# ./runExperimentsFixedAlpha.py 10000 12 -0.5
# # Batch13: alpha = -1.0
# ./runExperimentsFixedAlpha.py 10000 13 -1


# # Run experiment 10k_1, with:
# # 10000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # range of 0.1 for sampling alphas (+/- 0.2 from center).
# date
# ./runExperimentsFlexible.py 10000 0 1 0.4

# # Run experiment 10k_2, with:
# # 10000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # Randomly generated range K, uniformly from [0, 0.4)
# date
# ./runExperimentsFlexible.py 10000 0 0 0.4

# # Run experiment 10k_3, with:
# # 10000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # range of 0.2 for sampling alphas (+/- 0.1 from center)
# date
# ./runExperimentsFlexible.py 10000 0 1 0.2

# # Run experiment 10k_4, with:
# # 10000 trials, 
# # randomly sampled R1 alphas (with matchup-specific centers),
# # range of 0.1 for sampling alphas (+/- 0.05 from center).
# date
# ./runExperimentsFlexible.py 10000 0 1 0.1

# # Run experiment 10k_5, with:
# # 10000 trials, 
# # fixed R1 alphas (matchup-specific),
# # range of 0.4 for sampling other round alphas (+/- 0.2 from center).
# # (This is very similar to Version 5 from old tests)
# date
# ./runExperimentsFlexible.py 10000 1 1 0.4
# date

#---------- 1 million-bracket Experiments --------------#
# (the only difference is the sampling range for the alpha values):

# Batch 1:
# for i in `seq 2 10`;
# do
# 	date
# 	echo Experiment 'for' i = $i running
# 	if [ $i -lt 10 ]; then
# 		./runExperimentsFlexible.py 1000000 0 1 0.$i 1
# 	else
# 		./runExperimentsFlexible.py 1000000 0 1 1.0 1
# 	fi
# done
# date

# Batch 2: (fixed alpha values for R1)
# for i in `seq 2 10`;
# do
# 	date
# 	echo Experiment 'for' i = $i running
# 	if [ $i -lt 10 ]; then
# 		./runExperimentsFlexible.py 1000000 1 1 0.$i 2
# 	else
# 		./runExperimentsFlexible.py 1000000 1 1 1.0 2
# 	fi
# done
# date

#---------- 5k Experiments --------------#
# (the only difference is the sampling range for the alpha values):
# for i in `seq 2 10`;
# do
# 	date
# 	echo Experiment 'for' i = $i running
# 	if [ $i -lt 10 ]; then
# 		./runExperimentsFlexible.py 5000 0 1 0.$i 1
# 	else
# 		./runExperimentsFlexible.py 5000 0 1 1.0 1
# 	fi
# done
# date

#---------- 10k Experiments, fixed alphas for R1 --------------#
# (the only difference is the sampling range for the alpha values):
# for i in `seq 2 10`;
# do
# 	date
# 	echo Experiment 'for' i = $i running
# 	if [ $i -lt 10 ]; then
# 		./runExperimentsFlexible.py 10000 1 1 0.$i 14
# 	else
# 		./runExperimentsFlexible.py 10000 1 1 1.0 14
# 	fi
# done
# date

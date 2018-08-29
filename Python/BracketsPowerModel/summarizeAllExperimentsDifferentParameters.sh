#!/bin/bash

# This script summarizes several experiments (and sometimes prints timestamps between them).

#---------- First Batch of 10k Experiments --------------#

# # Summarize experiment 10k_1
# date
# ./summarizeExperimentsFlexible.py 10000 0 1 0.4 > 'exp_10k_1_summary.csv'

# # Summarize experiment 10k_2
# date
# ./summarizeExperimentsFlexible.py 10000 0 0 0.4 > 'exp_10k_2_summary.csv'

# # Summarize experiment 10k_3
# date
# ./summarizeExperimentsFlexible.py 10000 0 1 0.2 > 'exp_10k_3_summary.csv'

# # Summarize experiment 10k_4
# date
# ./summarizeExperimentsFlexible.py 10000 0 1 0.1 > 'exp_10k_4_summary.csv'

# # Summarize experiment 10k_5
# date
# ./summarizeExperimentsFlexible.py 10000 1 1 0.4 > 'exp_10k_5_summary.csv'
# date

# Note: These are the timestamps from the first run of the 10k experiments.
# Total is around 3 seconds, so summarizing does not take much time.
# $ ./summarizeAllExperimentsDifferentParameters.sh
# Thu Feb 22 23:58:59 CST 2018
# Thu Feb 22 23:59:00 CST 2018
# Thu Feb 22 23:59:00 CST 2018
# Thu Feb 22 23:59:01 CST 2018
# Thu Feb 22 23:59:01 CST 2018
# Thu Feb 22 23:59:02 CST 2018


# #---------- 50k Experiments --------------#

# # Summarize experiment 50k_1
# date
# ./summarizeExperimentsFlexible.py 50000 0 1 0.4 > 'exp_50k_1_summary.csv'

# # Summarize experiment 50k_2
# date
# ./summarizeExperimentsFlexible.py 50000 0 0 0.4 > 'exp_50k_2_summary.csv'

# # Summarize experiment 50k_3
# date
# ./summarizeExperimentsFlexible.py 50000 0 1 0.2 > 'exp_50k_3_summary.csv'

# # Summarize experiment 50k_4
# date
# ./summarizeExperimentsFlexible.py 50000 0 1 0.1 > 'exp_50k_4_summary.csv'

# # Summarize experiment 50k_5
# date
# ./summarizeExperimentsFlexible.py 50000 1 1 0.4 > 'exp_50k_5_summary.csv'
# date


#---------- 10k Experiments --------------#
# Summarize ten batches of nine experiments 
# (the only difference is the sampling range for the alpha values):

# for batchNum in `seq 1 10`;
# do
# 	for i in `seq 2 10`;
# 	do
# 		if [ $i -lt 10 ]; then
# 			./summarizeExperimentsFlexible.py 10000 0 1 0.$i $batchNum > 'exp_10k_batch_'$batchNum'_version_'$i'.csv'
# 		else
# 			./summarizeExperimentsFlexible.py 10000 0 1 1.0 $batchNum > 'exp_10k_batch_'$batchNum'_version_'$i'.csv'
# 		fi
# 	done
# 	echo $batchNum:
# 	date
# done

# 10k Experiments, Batches 11 - 13
# ./summarizeExperimentsFlexible.py 10000 0 1 0 11 > 'exp_10k_batch_11.csv'
# ./summarizeExperimentsFlexible.py 10000 0 1 -0.5 12 > 'exp_10k_batch_12.csv'
# ./summarizeExperimentsFlexible.py 10000 0 1 -1 13 > 'exp_10k_batch_13.csv'

# 10k Experiments, Batch 14 (fixed alpha values for R1)
# for i in `seq 2 10`;
# do
# 	date
# 	echo Summarizing experiment 'for' i = $i
# 	if [ $i -lt 10 ]; then
# 		./summarizeExperimentsFlexible.py 10000 1 1 0.$i 14 > 'exp_10k_batch_14_version_'$i'_with_stats.csv'
# 	else
# 		./summarizeExperimentsFlexible.py 10000 1 1 1.0 14 > 'exp_10k_batch_14_version_'$i'_with_stats.csv'
# 	fi
# done
# date

#---------- 1 million-bracket Experiments --------------#
# Summarize one batch of nine experiments 
# (the only difference is the sampling range for the alpha values):

# Batch 1:
# ./summarizeExperimentsFlexibleAllRanges.py 1000000 0 1 1 0.2 1.0 0.1 > 'Summaries/exp_1mil_batch_1_all_versions.csv'

# All Batches:
# for i in `seq 2 10`;
# do
# 	date
# 	echo Summarizing experiment 'for' i = $i
# 	if [ $i -lt 10 ]; then
# 		./summarizeExperimentsFlexible.py 1000000 0 1 0.$i 1 > 'Summaries/exp_1mil_batch_'$batchNum'_version_'$i'.csv'
# 	else
# 		./summarizeExperimentsFlexible.py 1000000 0 1 1.0 1 > 'Summaries/exp_1mil_batch_'$batchNum'_version_'$i'.csv'
# 	fi
# done
# date


# Batch 2: (fixed alpha values for R1)
# for i in `seq 2 10`;
# do
# 	date
# 	echo Summarizing experiment 'for' i = $i
# 	if [ $i -lt 10 ]; then
# 		./summarizeExperimentsFlexible.py 1000000 1 1 0.$i 2 > 'exp_1mil_batch_2_version_'$i'.csv'
# 	else
# 		./summarizeExperimentsFlexible.py 1000000 1 1 1.0 2 > 'exp_1mil_batch_2_version_'$i'.csv'
# 	fi
# done
# date

#---------- 5k Experiments --------------#
# Summarize one batch of nine experiments 
# (the only difference is the sampling range for the alpha values):

# for i in `seq 2 10`;
# do
# 	date
# 	echo Summarizing experiment 'for' i = $i
# 	if [ $i -lt 10 ]; then
# 		./summarizeExperimentsFlexible.py 5000 0 1 0.$i 1 > 'exp_5k_batch_'$batchNum'_version_'$i'.csv'
# 	else
# 		./summarizeExperimentsFlexible.py 5000 0 1 1.0 1 > 'exp_5k_batch_'$batchNum'_version_'$i'.csv'
# 	fi
# done
# date


#---------- 10k Experiments (with stats) --------------#
# Summarize ten batches of nine experiments 
# (the only difference is the sampling range for the alpha values):

# date
# for batchNum in `seq 1 10`;
# do
# 	echo $batchNum:
# 	./summarizeExperimentsFlexibleAllRanges.py 10000 0 1 $batchNum 0.2 1.0 0.1 > 'Summaries/exp_10k_batch_'$batchNum'_all_versions.csv'
# 	date
# done

# Summarize fixed R1 batch (Batch 14):
./summarizeExperimentsFlexibleAllRanges.py 10000 1 1 14 0.2 1.0 0.1 > 'Summaries/exp_10k_batch_14_all_versions.csv'
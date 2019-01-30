#!/usr/bin/env bash


POOL_SIZE=1000
BATCHES=10

declare -a arr=("top_performing" "forward" "bradley-terry" "ludden" "bermudez")

for i in "${arr[@]}"
do
    echo "$i"

    echo "Creating ensemble pool"
    PYTHONPATH=. python Ensemble/modelEnsemble.py $POOL_SIZE $BATCHES Ensemble/models/"$i"_models.json

    echo "Running summarizer"
    PYTHONPATH=. python Ensemble/summarize.py $POOL_SIZE $BATCHES Ensemble/models/"$i"_models.json Summary_"$i"_ensemble

    echo "Preparing for MCB"
    PYTHONPATH=. python Ensemble/prepareForMCB.py $POOL_SIZE ESPN 0 $((BATCHES-1)) Ensemble/models/"$i"_models.json Summary_"$i"_ensemble | tee Summary_"$i"_ensemble/forMCB_count.csv
    PYTHONPATH=. python Ensemble/prepareForMCB.py $POOL_SIZE "Max score" 0 $((BATCHES-1)) Ensemble/models/"$i"_models.json Summary_"$i"_ensemble | tee Summary_"$i"_ensemble/forMCB_score.csv

    echo "Creating score histograms and stats"
    PYTHONPATH=. python Ensemble/scoresHistogram.py $POOL_SIZE $BATCHES Ensemble/models/"$i"_models.json Summary_"$i"_ensemble
done
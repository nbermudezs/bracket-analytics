#!/usr/bin/env bash

POOL_SIZE=100000000
BATCHES=100

PYTHONPATH=. python ludden_generator.py $POOL_SIZE $BATCHES Ensemble/models/ludden_models.json
PYTHONPATH=. python bradley-terry_generator.py $POOL_SIZE $BATCHES Ensemble/models/bradley-terry_models.json
PYTHONPATH=. python bermudez_generator.py $POOL_SIZE $BATCHES Ensemble/models/SA_models.json

PYTHONPATH=. python scoresOnlySummarizer.py $POOL_SIZE $BATCHES Ensemble/models/ludden_models.json Summary_ludden_models
PYTHONPATH=. python scoresOnlySummarizer.py $POOL_SIZE $BATCHES Ensemble/models/bradley-terry_models.json Summary_bradley-terry_models
PYTHONPATH=. python scoresOnlySummarizer.py $POOL_SIZE $BATCHES Ensemble/models/SA_models.json Summary_nbermudez_models

PYTHONPATH=. python prepareForMCB.py $POOL_SIZE ESPN 0 $((BATCHES-1)) Summary_ludden_models > Summary_ludden_models/forMCB_ludden_count.csv
PYTHONPATH=. python prepareForMCB.py $POOL_SIZE "Max score" 0 $((BATCHES-1)) Summary_ludden_models > Summary_ludden_models/forMCB_ludden_score.csv

PYTHONPATH=. python prepareForMCB.py $POOL_SIZE ESPN 0 $((BATCHES-1)) Summary_bradley-terry_models > Summary_ludden_models/forMCB_bradley-terry_count.csv
PYTHONPATH=. python prepareForMCB.py $POOL_SIZE "Max score" 0 $((BATCHES-1)) Summary_bradley-terry_models > Summary_ludden_models/forMCB_bradley-terry_score.csv

PYTHONPATH=. python prepareForMCB.py $POOL_SIZE ESPN 0 $((BATCHES-1)) Summary_nbermudez_models > Summary_ludden_models/forMCB_bermudez_count.csv
PYTHONPATH=. python prepareForMCB.py $POOL_SIZE "Max score" 0 $((BATCHES-1)) Summary_nbermudez_models > Summary_ludden_models/forMCB_bermudez_score.csv
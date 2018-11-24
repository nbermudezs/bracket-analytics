#!/usr/bin/env bash

python Likelihood/analytical/toy.py 1.0 Likelihood/analytical/logs-prod '*' 3
python Likelihood/analytical/toy.py 0.75 Likelihood/analytical/logs-prod '*' 3
python Likelihood/analytical/toy.py 0.5 Likelihood/analytical/logs-prod '*' 3
python Likelihood/analytical/toy.py 0.25 Likelihood/analytical/logs-prod '*' 3

python Likelihood/analytical/toy.py 1.0 Likelihood/analytical/logs-prod '*' 5
python Likelihood/analytical/toy.py 0.75 Likelihood/analytical/logs-prod '*' 5
python Likelihood/analytical/toy.py 0.5 Likelihood/analytical/logs-prod '*' 5
python Likelihood/analytical/toy.py 0.25 Likelihood/analytical/logs-prod '*' 5

python Likelihood/analytical/toy.py 1.0 Likelihood/analytical/logs-prod '*' 8
python Likelihood/analytical/toy.py 0.75 Likelihood/analytical/logs-prod '*' 8
python Likelihood/analytical/toy.py 0.5 Likelihood/analytical/logs-prod '*' 8
python Likelihood/analytical/toy.py 0.25 Likelihood/analytical/logs-prod '*' 8
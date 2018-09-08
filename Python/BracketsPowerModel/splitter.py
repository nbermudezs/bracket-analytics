import json
import numpy as np
import sys

# usage:
# python splitter.py <models.json file> <n_splits> <prefix>
if len(sys.argv) < 4:
    print('Usage: python splitter.py <models.json file> <n_splits> <prefix>')
    exit(1)

models_filename = sys.argv[1]
n_splits = int(sys.argv[2])
prefix = sys.argv[3]

with open(models_filename, 'r') as f:
    data = json.loads(f.read().replace('\n', ''))
    models = data['models']

    splits = np.array_split(models, n_splits)
    for i, group in enumerate(splits):
        split_models = {
            'models': group.tolist()
        }

        with open('{0}_{1:02d}.json'.format(prefix, i), 'w') as out:
            out.write(json.dumps(split_models, indent=4, separators=(',', ': ')))

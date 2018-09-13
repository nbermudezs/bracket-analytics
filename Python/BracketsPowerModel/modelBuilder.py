__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
import os
import sys


experiments_path = sys.argv[1]
ref_model_file = sys.argv[2]
num_batches = int(sys.argv[3])
output_filepath = sys.argv[4]


with open(ref_model_file) as models:
    data = json.load(models)['models']


result = {
    'models': []
}
for model in data:
    valid = True
    for batch in range(num_batches):
        for year in range(2013, 2019):
            path = '{0}/Batch{1:02d}/generatedBrackets_{2}_{3}.json'.format(
                experiments_path,
                batch,
                model['modelName'],
                year)
            if not os.path.exists(path):
                valid = False
                break
    if valid:
        result['models'].append(model)

with open(output_filepath, 'w') as out:
    json.dump(result, out, indent=4, separators=(',', ': '))

__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import sys

generator = sys.argv[1]
n_models = int(sys.argv[2])
batch_size = int(sys.argv[3])
n_batches = int(sys.argv[4])
models_file = sys.argv[5]

for i in range(n_models):
    print('python {0} {1} {2} {3} {4}'.format(generator, batch_size, n_batches, models_file, i))

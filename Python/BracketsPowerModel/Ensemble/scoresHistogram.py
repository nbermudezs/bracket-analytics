__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


from utils.scoresHistogram import analyze


if __name__ == '__main__':
    import sys

    num_trials = int(sys.argv[1])
    num_batches = int(sys.argv[2])
    models_path = sys.argv[3]
    summary_path = sys.argv[4]

    name = models_path.split('/')[-1].replace('.json', '')

    for year in range(2013, 2019):
        for batch_number in range(num_batches):
            analyze(summary_path, name, num_trials, batch_number, year)

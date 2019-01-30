__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
import sys
start = int(sys.argv[1])
end = int(sys.argv[2])
filename = sys.argv[3]

scores = list(range(start, end))
content = {
    'year': 2013,
    'actualBracket': '',
    'scores': scores
}

with open(filename, 'w') as f:
    json.dump(content, f)

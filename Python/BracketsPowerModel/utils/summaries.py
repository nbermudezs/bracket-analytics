__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"

ludden_summary = [
    {
        'modelName': 'power',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'F4_A',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'F4_B',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'NCG',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'E8',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'ludden_models',
        'ref': 'ludden',
        'refType': 'ensemble',
        'label': 'Mixed'
    }
]

bermudez_summary = [
    {
        'modelName': 'SA_power',
        'ref': 'bermudez',
        'refType': 'models'
    },
    {
        'modelName': 'SA_F4_A',
        'ref': 'bermudez',
        'refType': 'models'
    },
    {
        'modelName': 'SA_F4_B',
        'ref': 'bermudez',
        'refType': 'models'
    },
    {
        'modelName': 'SA_NCG',
        'ref': 'bermudez',
        'refType': 'models'
    },
    {
        'modelName': 'SA_E8',
        'ref': 'bermudez',
        'refType': 'models'
    },
    {
        'modelName': 'bermudez_models',
        'ref': 'bermudez',
        'refType': 'ensemble',
        'label': 'Mixed'
    }
]

bradley_terry_summary = [
    {
        'modelName': 'bradley-terry',
        'ref': 'bradley-terry',
        'refType': 'models',
        'label': 'BT'
    },
    {
        'modelName': 'bradley-terry-F4_A',
        'ref': 'bradley-terry',
        'refType': 'models',
        'label': 'BT-F4_A'
    },
    {
        'modelName': 'bradley-terry-F4_B',
        'ref': 'bradley-terry',
        'refType': 'models',
        'label': 'BT-F4_B'
    },
    {
        'modelName': 'bradley-terry-NCG',
        'ref': 'bradley-terry',
        'refType': 'models',
        'label': 'BT-NCG'
    },
    {
        'modelName': 'bradley-terry-E8',
        'ref': 'bradley-terry',
        'refType': 'models',
        'label': 'BT-E8'
    },
    {
        'modelName': 'bradley-terry_models',
        'ref': 'bradley-terry',
        'refType': 'ensemble',
        'label': 'Mixed'
    }
]

top_performing_summary = [
    {
        'modelName': 'E8',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'F4_B',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'bradley-terry-F4_A',
        'ref': 'bradley-terry',
        'refType': 'models',
        'label': 'BT-F4_A'
    },
    {
        'modelName': 'top_performing_models',
        'ref': 'top_performing',
        'refType': 'ensemble',
        'label': 'Mixed'
    }
]

forward_model_summary = [
    {
        'modelName': 'power',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'SA_power',
        'ref': 'bermudez',
        'refType': 'models'
    },
    {
        'modelName': 'bradley-terry',
        'ref': 'bradley-terry',
        'refType': 'models',
        'label': 'BT'
    },
    {
        'modelName': 'forward_models',
        'ref': 'forward',
        'refType': 'ensemble',
        'label': 'Mixed'
    }
]

summaries = {
    'bermudez': bermudez_summary,
    'ludden': ludden_summary,
    'forward': forward_model_summary,
    'bradley-terry': bradley_terry_summary,
    'top_performing': top_performing_summary
}
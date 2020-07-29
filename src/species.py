from enum import Enum

# UNITS:
# - density: kg/m3
# - molar mass: kg/mol

class State(Enum):
    GAS = 1
    LIQUID = 2
    SOLID = 3

gases_dict = {
    'carbon monoxide': {
        'name': 'carbon monoxide',
        'density': 1.139,
        'molar mass': 0.02801
    },
    'hydrogen': { # H2
        'name': 'hydrogen',
        'density': 0.0818,
        'molar mass': 0.002016
    }
}

liquids_dict = {
    'water': {
        'name': 'water',
        'density':  997.5,
        'molar mass': 0.01802
    }, 
    'methanol': {
        'name': 'methanol',
        'density': 788.2,
        'molar mass': 0.03204
    }
}

solids_dict = {
    'wood fiber': {
        'name': 'wood fiber',
        'density': 1.2
    }
}


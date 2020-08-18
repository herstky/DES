from enum import Enum


class Species:
'''UNITS:
   - density: kg/m3
   - molar mass: kg/mol'''
    def __init__(self, name, properties=None):
        self.name = name
        self.properties = properties
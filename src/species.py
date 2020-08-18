'''UNITS:
   - density: kg/m3
   - molar mass: kg/mol'''
class Species:
    def __init__(self, name, properties=None):
        self.name = name
        self.properties = properties
from .event import Event
from .species import Species


class Simulation:
    def __init__(self, gui):
        self.gui = gui
        Event.register_species([
            Species('water', {'state': 'liquid', 'density': 997.5}), 
            Species('fiber', {'state': 'solid', 'density': 1200})
        ])

        self.iteration = 1
        self.modules = []
        self.displays = []

    def run(self):
        ''' Processes all Modules and displays that have been added to this
            Simulation for the current iteration.'''
        for module in self.modules:
            module.simulate()

        for display in self.displays:
            display.update()

        self.iteration += 1     
from .event import Event
from .models import Source, Sink, Splitter, Joiner, Stream
# from .species import State
from .species import Species


class Simulation:
    def __init__(self, gui):
        self.gui = gui
        Event.register_species([Species('water', {'state': 'liquid', 'density': 997.5}), 
                                Species('fiber', {'state': 'solid', 'density': 1200})])
        self.iteration = 1
        self.modules = []
        self.displays = []

    def run(self):
        # print(f'Iteration {self.iteration}, {Event.count} events accumulated')
        for module in self.modules:
            module.simulate()

        for display in self.displays:
            display.update()

        self.iteration += 1     
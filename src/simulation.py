from .event import Event
from .models import Source, Sink, Splitter, Joiner, Stream
from .species import State


class Simulation:
    def __init__(self, gui):
        self.gui = gui
        Event.register_species([('water', State.liquid), ('fiber', State.solid)])
        self.iteration = 1
        self.modules = []
        self.displays = []

    def run(self):
        # print(f'Iteration {self.iteration}, {Event.count} events accumulated')
        for module in self.modules:
            module.process()

        for display in self.displays:
            display.update()

        self.iteration += 1

      
    
      
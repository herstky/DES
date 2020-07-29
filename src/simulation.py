from .event import Event
from .models import Source, Sink, Splitter, Joiner, Stream
from .species import State


class Simulation:
    def __init__(self, gui):
        self.gui = gui
        Event.register_species([('water', State.LIQUID), ('wood fiber', State.SOLID)])
        self.iteration = 1
        self.modules = []

    def run(self):
        print(f'Iteration {self.iteration}, {Event.count} events')
        for module in self.modules:
            module.process()
        # input('Press enter to continue')
        print()
        self.iteration += 1

    def source_to_sink_example(self):
        source = Source(self.gui, 'self, Source', 100)
        sink = Sink(self.gui, 'Sink')
        Stream(self.gui, source.outlet_connections[0], sink.inlet_connections[0])

        return [source, sink]

    def splitter_example(self):
        source = Source(self.gui, 'Source', 100)
        sink1 = Sink(self.gui, 'Sink1')
        sink2 = Sink(self.gui, 'Sink2')
        splitter = Splitter(self.gui, 'Splitter')
        Stream(self.gui, source.outlet_connections[0], splitter.inlet_connections[0])
        Stream(self.gui, splitter.outlet_connections[0], sink1.inlet_connections[0])
        Stream(self.gui, splitter.outlet_connections[1], sink2.inlet_connections[0])
        return [source, splitter, sink1, sink2]

    def split_join_example(self):
        source1 = Source(self.gui, 'Source1', 500)
        sink1 = Sink(self.gui, 'Sink1')
        sink2 = Sink(self.gui, 'Sink2')
        splitter1 = Splitter(self.gui, 'Splitter1')
        splitter2 = Splitter(self.gui, 'Splitter2')
        joiner1 = Joiner(self.gui, 'Joiner1')

        Stream(self.gui, source1.outlet_connections[0], joiner1.inlet_connections[0])
        Stream(self.gui, splitter2.outlet_connections[1], joiner1.inlet_connections[1])
        Stream(self.gui, splitter1.outlet_connections[0], sink1.inlet_connections[0])
        Stream(self.gui, splitter1.outlet_connections[1], splitter2.inlet_connections[0])
        Stream(self.gui, splitter2.outlet_connections[0], sink2.inlet_connections[0])
        Stream(self.gui, joiner1.outlet_connections[0], splitter1.inlet_connections[0])    
    
        return [source1, splitter1, sink1, sink2, splitter2, joiner1]

    def complicated_example1(self):
        source1 = Source(self.gui, 'Source1', 500)
        sink1 = Sink(self.gui, 'Sink1')
        sink2 = Sink(self.gui, 'Sink2')
        splitter1 = Splitter(self.gui, 'Splitter1')
        splitter2 = Splitter(self.gui, 'Splitter2')
        joiner1 = Joiner(self.gui, 'Joiner1')

        Stream(self.gui, source1.outlet_connections[0], joiner1.inlet_connections[0])
        Stream(self.gui, splitter2.outlet_connections[1], joiner1.inlet_connections[1])
        Stream(self.gui, splitter1.outlet_connections[0], sink1.inlet_connections[0])
        Stream(self.gui, splitter1.outlet_connections[1], splitter2.inlet_connections[0])
        Stream(self.gui, splitter2.outlet_connections[0], sink2.inlet_connections[0])
        Stream(self.gui, joiner1.outlet_connections[0], splitter1.inlet_connections[0])    
    
        return [source1, splitter1, sink1, sink2, splitter2, joiner1]
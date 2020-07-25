from src.event import Event
from src.modules import Source, Sink, Splitter, Joiner
from src.stream import Stream
from src.components import Water, Fiber



class Simulation:
    def __init__(self):
        Event.register_components([Water, Fiber])
        self.iteration = 1
        self.modules = self.complicated_example1()

    def run(self):
        print(f'Iteration {self.iteration}, {Event.count} events')
        for module in self.modules:
            module.process()
        # input('Press enter to continue')
        print()
        self.iteration += 1


    def source_to_sink_example(self):
        source = Source('Source', 100)
        sink = Sink('Sink')
        Stream(source.outlet_connections[0], sink.inlet_connections[0])

        return [source, sink]

    def splitter_example(self):
        source = Source('Source', 100)
        sink1 = Sink('Sink1')
        sink2 = Sink('Sink2')
        splitter = Splitter('Splitter')
        Stream(source.outlet_connections[0], splitter.inlet_connections[0])
        Stream(splitter.outlet_connections[0], sink1.inlet_connections[0])
        Stream(splitter.outlet_connections[1], sink2.inlet_connections[0])
        return [source, splitter, sink1, sink2]

    def split_join_example(self):
        source1 = Source('Source1', 500)
        sink1 = Sink('Sink1')
        sink2 = Sink('Sink2')
        splitter1 = Splitter('Splitter1')
        splitter2 = Splitter('Splitter2')
        joiner1 = Joiner('Joiner1')

        Stream(source1.outlet_connections[0], joiner1.inlet_connections[0])
        Stream(splitter2.outlet_connections[1], joiner1.inlet_connections[1])
        Stream(splitter1.outlet_connections[0], sink1.inlet_connections[0])
        Stream(splitter1.outlet_connections[1], splitter2.inlet_connections[0])
        Stream(splitter2.outlet_connections[0], sink2.inlet_connections[0])
        Stream(joiner1.outlet_connections[0], splitter1.inlet_connections[0])    
    
        return [source1, splitter1, sink1, sink2, splitter2, joiner1]

    def complicated_example1(self):
        source1 = Source('Source1', 500)
        sink1 = Sink('Sink1')
        sink2 = Sink('Sink2')
        splitter1 = Splitter('Splitter1')
        splitter2 = Splitter('Splitter2')
        joiner1 = Joiner('Joiner1')

        Stream(source1.outlet_connections[0], joiner1.inlet_connections[0])
        Stream(splitter2.outlet_connections[1], joiner1.inlet_connections[1])
        Stream(splitter1.outlet_connections[0], sink1.inlet_connections[0])
        Stream(splitter1.outlet_connections[1], splitter2.inlet_connections[0])
        Stream(splitter2.outlet_connections[0], sink2.inlet_connections[0])
        Stream(joiner1.outlet_connections[0], splitter1.inlet_connections[0])    
    
        return [source1, splitter1, sink1, sink2, splitter2, joiner1]
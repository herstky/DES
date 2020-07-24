import time

from src.event import Event
from src.modules import Source, Sink, Splitter, Joiner
from src.stream import Stream
from src.components import Water, Fiber


def loop(modules):
    for module in modules:
        module.process()

def source_to_sink_test():
    source = Source('Source', 100)
    sink = Sink('Sink')
    Stream(source.outlet_connections[0], sink.inlet_connections[0])

    return [source, sink]

def splitter_test():
    source = Source('Source', 100)
    sink1 = Sink('Sink1')
    sink2 = Sink('Sink2')
    splitter = Splitter('Splitter')
    Stream(source.outlet_connections[0], splitter.inlet_connections[0])
    Stream(splitter.outlet_connections[0], sink1.inlet_connections[0])
    Stream(splitter.outlet_connections[1], sink2.inlet_connections[0])
    return [source, splitter, sink1, sink2]

def split_join_test():
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


if __name__ == '__main__':
    Event.register_components([Water, Fiber])
    
    # modules = split_join_test()
    modules = split_join_test()
    iteration = 1
    while True:
        print(f'Iteration {iteration}, {Event.count} events')
        loop(modules)
        input('Press enter to continue')
        print()
        iteration += 1

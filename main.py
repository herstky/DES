import time

from event import Event
from module import Module, Source, Sink, Splitter, Joiner
from stream import Stream


def loop(modules):
    for module in modules:
        module.process()


if __name__ == '__main__':
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

    modules = [source1, splitter1, sink1, sink2, splitter2, joiner1]
    while True:
        loop(modules)
        input('Press enter to continue')
        print()

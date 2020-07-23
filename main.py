import time

from event import Event
from module import Module, Source, Sink, Splitter
from stream import Stream


def loop(modules):
    for module in modules:
        module.process()


if __name__ == '__main__':
    source1 = Source('Source1', 500)
    sink1 = Sink('Sink1')
    sink2 = Sink('Sink2')
    splitter1 = Splitter('Splitter1')
    Stream(source.outlet_connections[0], splitter.inlet_connections[0])
    Stream(splitter.outlet_connections[0], sink1.inlet_connections[0])
    Stream(splitter.outlet_connections[1], sink2.inlet_connections[0])
    modules = [source, splitter, sink1, sink2]
    while True:
        loop(modules)
        input('Press enter to continue')
        print()

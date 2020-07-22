from event import Event
from module import Module, Source, Sink, Splitter
from stream import Stream


source = Source(100)
sink = Sink(500)
stream = Stream()


def loop():
    source.process()


if __name__ == '__main__':
    while True:

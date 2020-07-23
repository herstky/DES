from event_queue import EventQueue
from connection import Connection
from event import Event
from stream import Stream


class Module:
    def __init__(self, name='Module'):
        self.name = name
        self.inlet_connections = []
        self.outlet_connections = []
        self.queue = EventQueue()

    def add_inlet_connection(self, connection):
        self.inlet_connections.append(connection)

    def add_outlet_connection(self, connection):
        self.outlet_connections.append(connection)

    def process(self):
        pass


class Source(Module):
    def __init__(self, name='Source', outlet_capacity=1000, event_rate=1000):
        super().__init__(name)
        self.event_rate = event_rate
        self.add_outlet_connection(Connection(self, outlet_capacity, 'Outlet'))

    def process(self):
        connection, *_ = self.outlet_connections
        generated_amount = 0
        for i in range(self.event_rate):
            magnitude = connection.capacity / self.event_rate
            # Create events at outlet connection
            connection.queue.enqueue(Event(magnitude))
            generated_amount += magnitude

        print(f'{self.name} generated {generated_amount}')

        # Push events from outlet connection to inlet of module connected by stream
        connection.push()


class Sink(Module):
    def __init__(self, name='Sink', inlet_capacity=1000):
        super().__init__(name)
        self.add_inlet_connection(Connection(self, inlet_capacity, 'Inlet'))

    def process(self):
        connection, *_ = self.inlet_connections
        destroyed_amount = connection.transfer_to_module()
        self.queue.events.clear()

        print(f'{self.name} destroyed {destroyed_amount}')


class Splitter(Module):
    def __init__(self, name='Splitter', inlet_capacity=1000, split_fraction=.5):
        super().__init__(name)
        self.split_fraction = split_fraction
        self.add_inlet_connection(Connection(self, inlet_capacity, 'Inlet'))
        self.add_outlet_connection(Connection(
            self, inlet_capacity * split_fraction, 'Outlet1'))
        self.add_outlet_connection(Connection(
            self, inlet_capacity * (1 - split_fraction), 'Outlet2'))

    def process(self):
        inlet_connection, *_ = self.inlet_connections
        outlet_connection1, outlet_connection2, *_ = self.outlet_connections

        # Move events from inlet connection to the outlet connections
        inlet_amount = inlet_connection.transfer_to_module()
        split_amount1 = outlet_connection1.transfer_from_module(
            self.queue.amount_queued * self.split_fraction)
        split_amount2 = outlet_connection2.transfer_from_module(
            self.queue.amount_queued)

        print(
            f'{self.name} split {inlet_amount} into streams of {split_amount1} and {split_amount2}')

        # Push events from the outlet connections to inlet of module connected by stream
        outlet_connection1.push()
        outlet_connection2.push()

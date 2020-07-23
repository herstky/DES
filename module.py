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
    def __init__(self, outlet_capacity=1000, event_rate=1000, name='Source'):
        super().__init__(name)
        self.event_rate = event_rate
        self.add_outlet_connection(Connection(self, outlet_capacity, 'Outlet'))

    def process(self):
        connection, *_ = self.outlet_connections 
        for i in range(self.event_rate):
            connection.queue.enqueue(Event(connection.capacity / self.event_rate)) # Create events at outlet connection
        connection.push() # Push events from outlet connection to inlet of module connected by stream



class Sink(Module):
    def __init__(self, inlet_capacity=1000, name='Sink'):
        super().__init__(name)
        self.add_inlet_connection(Connection(self, inlet_capacity, 'Inlet'))

    def process(self):
        connection, *_ = self.inlet_connections
        connection.transfer_to_module()
        self.queue.events.clear()

        
class Splitter(Module):
    def __init__(self, inlet_capacity=1000, split_fraction=.5, name='Splitter'):
        super().__init__(name)
        self.split_fraction = split_fraction
        self.add_inlet_connection(Connection(self, inlet_capacity, 'Inlet'))
        self.add_outlet_connection(Connection(self, inlet_capacity * split_fraction, 'Outlet1'))
        self.add_outlet_connection(Connection(self, inlet_capacity * (1 - split_fraction), 'Outlet2'))


    def process(self):
        inlet_connection, *_ = self.inlet_connections
        outlet_connection1, outlet_connection2, *_ = self.outlet_connections
        
        # Move events from inlet connection to the outlet connections
        inlet_connection.transfer_to_module()
        outlet_connection1.transfer_from_module(self.queue.amount_queued * self.split_fraction)
        outlet_connection2.transfer_from_module(self.queue.amount_queued)

        # Push events from the outlet connections to inlet of module connected by stream
        outlet_connection1.push()
        outlet_connection2.push()

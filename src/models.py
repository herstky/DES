from .event_queue import EventQueue
from .event import Event
from .components import Water, Fiber
from .views import ConnectionView, SourceView, SinkView, SplitterView, JoinerView


class Model:
    def __init__(self, gui, name='Model'):
        self.gui = gui
        self.name = name


class Stream(Model):
    def __init__(self, gui, name='Stream', inlet_connection=None, outlet_connection=None):
        super().__init__(gui, name)
        if inlet_connection:
            self.add_inlet_connection(inlet_connection)
        else:
            self.inlet_connection = None

        if outlet_connection:
            self.add_outlet_connection(outlet_connection)
        else:
            self.outlet_connection = None

    def __del__(self):
        try:
            self.remove_inlet_connection()
            self.remove_outlet_connection()
        except Exception:
            pass

    def add_inlet_connection(self, connection):
        self.inlet_connection = connection
        connection.stream = self

    def add_outlet_connection(self, connection):
        self.outlet_connection = connection
        connection.stream = self

    def remove_inlet_connection(self):
        self.inlet_connection.stream = None
        self.inlet_connection = None
    
    def remove_outlet_connection(self):
        self.outlet_connection.stream = None
        self.outlet_connection = None


class Connection(Model):
    def __init__(self, gui, name='Connection', module=None, capacity=100):
        super().__init__(gui, name)
        self.module = module
        self.capacity = capacity
        self.queue = EventQueue()
        self.stream = None
        self.view = ConnectionView(self)

    def push(self):
        pushed_amount = 0
        while not self.queue.empty() and pushed_amount + self.queue.peek().magnitude <= self.capacity:  # TODO is self.capacity here correct?
            event = self.queue.dequeue()
            self.stream.outlet_connection.queue.enqueue(event)
            pushed_amount += event.magnitude
        print(f'{self.module.name} {self.name} to {self.stream.outlet_connection.module.name} {self.stream.outlet_connection.name} flowrate: {pushed_amount}, accumulated backflow: {self.queue.amount_queued}')

    def transfer_to_module(self, amount=0):
        if amount == 0:
            amount = self.capacity
        transferred_amount = 0
        while not self.queue.empty() and transferred_amount + self.queue.peek().magnitude <= amount <= self.capacity:
            event = self.queue.dequeue()
            self.module.queue.enqueue(event)
            transferred_amount += event.magnitude
        return transferred_amount

    def transfer_from_module(self, amount=0):
        if amount == 0:
            amount = self.capacity
        transferred_amount = 0
        while not self.module.queue.empty() and transferred_amount + self.module.queue.peek().magnitude <= amount <= self.capacity:
            event = self.module.queue.dequeue()
            self.queue.enqueue(event)
            transferred_amount += event.magnitude
        return transferred_amount

    @property
    def backflow(self):
        return min(0, self.capacity - self.queue.amount_queued)


class Module(Model):
    def __init__(self, gui, name='Module'):
        super().__init__(gui, name)        
        self.gui.simulation.modules.append(self)
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
    def __init__(self, gui, name='Source', outlet_capacity=100000, volumetric_fractions=None, event_rate=1000):
        super().__init__(gui, name)
        self.add_outlet_connection(Connection(self.gui, 'Outlet', self, outlet_capacity))
        self.volumetric_fractions = volumetric_fractions
        self.event_rate = event_rate
        self.view = SourceView(self)

    def process(self):
        connection, *_ = self.outlet_connections
        generated_amount = 0
        for i in range(self.event_rate):
            volume = connection.capacity / self.event_rate
            components = []
            if self.volumetric_fractions:
                for component in Event.registered_components:
                    fraction = self.volumetric_fractions[component.name]
                    components.append(Component(fraction * volume))
            else:
                for component in Event.registered_components:
                    fraction = 1 / len(Event.registered_components)
                    components.append(component(fraction * volume))
            
            # Create events at outlet connection
            connection.queue.enqueue(Event(components))
            generated_amount += volume

        print(f'{self.name} generated {generated_amount}')

        # Push events from outlet connection to inlet of module connected by stream
        connection.push()


class Sink(Module):
    def __init__(self, gui, name='Sink', inlet_capacity=100000):
        super().__init__(gui, name)
        self.add_inlet_connection(Connection(self.gui, 'Inlet', self, inlet_capacity))
        self.view = SinkView(self)

    def process(self):
        connection, *_ = self.inlet_connections
        destroyed_amount = connection.transfer_to_module()
        self.queue.events.clear()

        print(f'{self.name} destroyed {destroyed_amount}')


class Splitter(Module):
    def __init__(self, gui, name='Splitter', inlet_capacity=100000, split_fraction=.5):
        super().__init__(gui, name)
        self.split_fraction = split_fraction
        self.add_inlet_connection(Connection(self.gui, 'Inlet', self, inlet_capacity))
        self.add_outlet_connection(Connection(self.gui, 'Outlet1', self, inlet_capacity * split_fraction))
        self.add_outlet_connection(Connection(self.gui, 'Outlet2', self, inlet_capacity * (1 - split_fraction)))
        self.view = SplitterView(self)

    def process(self):
        inlet_connection, *_ = self.inlet_connections
        outlet_connection1, outlet_connection2, *_ = self.outlet_connections

        # Transfer events to Splitter for processing
        inlet_amount = inlet_connection.transfer_to_module()

        # Transfer events to outlet streams
        split_amount1 = outlet_connection1.transfer_from_module(self.queue.amount_queued * self.split_fraction)
        split_amount2 = outlet_connection2.transfer_from_module(self.queue.amount_queued)

        print(f'{self.name} split stream of {inlet_amount} into streams of {split_amount1} and {split_amount2}')

        # Push events from the outlet connections to inlet of module connected by stream
        outlet_connection1.push()
        outlet_connection2.push()


class Joiner(Module):
    def __init__(self, gui, name='Joiner', inlet_capacity1=50000, inlet_capacity2=50000):
        super().__init__(gui, name)
        self.add_inlet_connection(Connection(self.gui, 'Inlet1', self, inlet_capacity1))
        self.add_inlet_connection(Connection(self.gui, 'Inlet2', self, inlet_capacity2))
        self.add_outlet_connection(Connection(self.gui, 'Outlet', self, inlet_capacity1 + inlet_capacity2))
        self.view = JoinerView(self)

    def process(self):
        inlet_connection1, inlet_connection2, *_ = self.inlet_connections
        outlet_connection1, *_ = self.outlet_connections

        # Transfer events to Splitter for processing        
        inlet_amount1 = inlet_connection1.transfer_to_module()
        inlet_amount2 = inlet_connection2.transfer_to_module()

        # Transfer events to outlet streams
        joined_amount = outlet_connection1.transfer_from_module()

        print(f'{self.name} joined streams of {inlet_amount1} and {inlet_amount2} into stream of {joined_amount}')

        # Push events from the outlet connection to inlet of module connected by stream
        outlet_connection1.push()
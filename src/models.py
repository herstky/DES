from enum import Enum

from .event_queue import EventQueue
from .event import Event
from .views import ReadoutView, StreamView, ConnectionView, SourceView, SinkView, SplitterView, JoinerView
from .species import State


class Model:
    def __init__(self, gui, name='Model'):
        self.gui = gui
        self.name = name
        self.view = None


class Readout(Model):
    def __init__(self, gui, name='Readout'):
        super().__init__(gui, name)
        self.view = ReadoutView(self)
        self.gui.simulation.displays.append(self)
        self.stream = None

    def __del__(self):
        self.gui.simulation.displays.remove(self)

    def update(self):
        flowrates = self.stream.inlet_connection.flowrates
        output = ''
        for species in Event.registered_species:
            output += f'{species[0]}: {round(flowrates[species], 3)}\n'
        output = output[:-1]
        self.view.text_item.setPlainText(output)


class Stream(Model):
    def __init__(self, gui, name='Stream'):
        super().__init__(gui, name)
        self.inlet_connection = None
        self.outlet_connection = None
        self.view = StreamView(self)

    def __del__(self):
        if self.inlet_connection:
            self.remove_connection(self.inlet_connection)
        if self.outlet_connection:
            self.remove_connection(self.outlet_connection)

    def add_connection(self, connection):
        if isinstance(connection, InletConnection) and connection.connect(self):
            self.outlet_connection = connection
            return True
        elif isinstance(connection, OutletConnection) and connection.connect(self):
            self.inlet_connection = connection
            return True
        return False

    def remove_connection(self, connection):
        if self.inlet_connection is connection:
            self.inlet_connection.disconnect()
            self.inlet_connection = None
            return True
        elif self.outlet_connection is connection:
            self.outlet_connection.disconnect()
            self.outlet_connection = None
            return True
        return False
        

class Connection(Model):
    class FlowType(Enum):
        push_flow = 1
        pull_flow = 2
    push_flow = FlowType.push_flow
    pull_flow = FlowType.pull_flow

    def __init__(self, gui, name='Connection', module=None, capacity=float('inf')):
        super().__init__(gui, name)
        self.module = module
        self.capacity = capacity
        self.flow_type = Connection.push_flow
        self.queue = EventQueue()
        self.stream = None
        self.view = ConnectionView(self)
        self.reset_flowrates()

    def reset_flowrates(self):
        self.flowrates = {(species_name, state): 0 for species_name, state in Event.registered_species}

    def transfer_events(self, amount=0):
        raise NotImplementedError()

    def connect(self, stream):
        self.stream = stream
        self.view.set_connected(True)
        return True

    def disconnect(self):
        self.stream = None
        self.view.set_connected(False)
        return True

    def push(self):
        raise NotImplementedError()

    def pull(self):
        raise NotImplementedError()

    @property
    def backflow(self):
        return min(0, self.capacity - self.queue.amount_queued)


class InletConnection(Connection):
    def transfer_events(self, amount=0):
        transferred_amount = 0
        if self.flow_type is Connection.pull_flow:
            if amount == 0:
                amount = self.capacity
            while not self.queue.empty() and transferred_amount + self.queue.peek().aggregate_volume() <= amount <= self.capacity:
                event = self.queue.dequeue()
                self.module.queue.enqueue(event)
                transferred_amount += event.aggregate_volume()
        else:
            pass
        return transferred_amount

    def connect(self, stream):
        # Return false if the stream already has a connection to its outlet or if the stream's inlet is not the same type
        if stream.outlet_connection or stream.inlet_connection and stream.inlet_connection.flow_type is not self.flow_type:
            return False
        return super().connect(stream)

    def pull(self):
        if self.flow_type is Connection.push_flow:
            raise ValueError('Flow type mismatch')
        pulled_amount = 0
        self.reset_flowrates()
        while not self.queue.empty() and pulled_amount + self.queue.peek().aggregate_volume() <= self.capacity:
            event = self.stream.inlet_connection.queue.dequeue(event)
            self.queue.enqueue(event)
            pulled_amount += event.aggregate_volume()
            for species in event.registered_species:
                self.flowrates[species] += event.species_volume(species)
        self.stream.inlet_connection.event_queue.amount_queued += self.capacity - pulled_amount
        


class OutletConnection(Connection):
    def transfer_events(self, amount=0):
        transferred_amount = 0
        if self.flow_type is Connection.pull_flow:
            if amount == 0:
                amount = self.capacity
            while not self.module.queue.empty() and transferred_amount + self.module.queue.peek().aggregate_volume() <= amount <= self.capacity:
                event = self.module.queue.dequeue()
                self.queue.enqueue(event)
                transferred_amount += event.aggregate_volume()
        else:
            pass
        return transferred_amount

    def connect(self, stream):
        # Return false if the stream already has a connection to its inlet or if the stream's outlet is not the same type
        if stream.inlet_connection or stream.outlet_connection and stream.outlet_connection.flow_type is not self.flow_type:
            return False
        return super().connect(stream)

    def push(self):
        if self.flow_type is Connection.pull_flow:
            raise ValueError('Flow type mismatch')
        pushed_amount = 0
        self.reset_flowrates()
        while not self.queue.empty() and pushed_amount + self.queue.peek().aggregate_volume() <= self.capacity:  
            event = self.queue.dequeue()
            self.stream.outlet_connection.queue.enqueue(event)
            pushed_amount += event.aggregate_volume()
            for species in event.registered_species:
                self.flowrates[species] += event.species_volume(species)


class Module(Model):
    def __init__(self, gui, name='Module'):
        super().__init__(gui, name)        
        self.gui.simulation.modules.append(self)
        self.inlet_connections = []
        self.outlet_connections = []
        self.queue = EventQueue()

    def __del__(self):
        self.gui.simulation.modules.remove(self)

    def add_inlet_connection(self, connection):
        self.inlet_connections.append(connection)

    def add_outlet_connection(self, connection):
        self.outlet_connections.append(connection)

    def process(self):
        pass


class Source(Module):
    def __init__(self, gui, name='Source', outlet_capacity=10000, volumetric_fractions=None, event_rate=1000):
        super().__init__(gui, name)
        self.add_outlet_connection(OutletConnection(self.gui, 'Outlet', self, outlet_capacity))
        self.volumetric_fractions = volumetric_fractions
        self.event_rate = event_rate
        self.view = SourceView(self)

    def process(self):
        connection, *_ = self.outlet_connections
        generated_amount = 0
        for i in range(self.event_rate):
            volume = connection.capacity / self.event_rate
            species = []
            if self.volumetric_fractions:
                for species_name, state in Event.registered_species:
                    fraction = self.volumetric_fractions[(species_name, state)]
                    species.append((species_name, state, fraction * volume))
            else:
                for species_name, state in Event.registered_species:
                    fraction = 1 / len(Event.registered_species)
                    species.append((species_name, state, fraction * volume))

            # Create events at outlet connection
            connection.queue.enqueue(Event(species))
            generated_amount += volume

        # Push events from outlet connection to inlet of module connected by stream
        connection.push()

class Tank(Module):
    def __init__(self, gui, name='Source'):
        super().__init__(gui, name)



class Pump(Module): # TODO pulls into inlet, pushes to outlet
    pass


class Sink(Module):
    def __init__(self, gui, name='Sink', inlet_capacity=float('inf')):
        super().__init__(gui, name)
        self.add_inlet_connection(InletConnection(self.gui, 'Inlet', self, inlet_capacity))
        self.view = SinkView(self)

    def process(self):
        connection, *_ = self.inlet_connections
        destroyed_amount = connection.transfer_events()
        self.queue.events.clear()


class Splitter(Module):
    def __init__(self, gui, name='Splitter', inlet_capacity=float('inf'), split_fraction=.5):
        super().__init__(gui, name)
        self.split_fraction = split_fraction
        self.add_inlet_connection(InletConnection(self.gui, 'Inlet', self, inlet_capacity))
        self.add_outlet_connection(OutletConnection(self.gui, 'Outlet1', self, inlet_capacity * split_fraction))
        self.add_outlet_connection(OutletConnection(self.gui, 'Outlet2', self, inlet_capacity * (1 - split_fraction)))
        self.view = SplitterView(self)

    def process(self):
        inlet_connection, *_ = self.inlet_connections
        outlet_connection1, outlet_connection2, *_ = self.outlet_connections

        # Transfer events to Splitter for processing
        inlet_amount = inlet_connection.transfer_events()

        # Transfer events to outlet streams
        split_amount1 = outlet_connection1.transfer_events(self.queue.amount_queued * self.split_fraction)
        split_amount2 = outlet_connection2.transfer_events(self.queue.amount_queued)

        # Push events from the outlet connections to inlet of module connected by stream
        outlet_connection1.push()
        outlet_connection2.push()


class Joiner(Module):
    def __init__(self, gui, name='Joiner', inlet_capacity1=50000, inlet_capacity2=50000):
        super().__init__(gui, name)
        self.add_inlet_connection(InletConnection(self.gui, 'Inlet1', self, inlet_capacity1))
        self.add_inlet_connection(InletConnection(self.gui, 'Inlet2', self, inlet_capacity2))
        self.add_outlet_connection(OutletConnection(self.gui, 'Outlet', self, inlet_capacity1 + inlet_capacity2))
        self.view = JoinerView(self)

    def process(self):
        inlet_connection1, inlet_connection2, *_ = self.inlet_connections
        outlet_connection1, *_ = self.outlet_connections

        # Transfer events to Splitter for processing        
        inlet_amount1 = inlet_connection1.transfer_events()
        inlet_amount2 = inlet_connection2.transfer_events()

        # Transfer events to outlet streams
        joined_amount = outlet_connection1.transfer_events()

        # Push events from the outlet connection to inlet of module connected by stream
        outlet_connection1.push()
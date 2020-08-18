import math

from enum import Enum

from .event_queue import EventQueue
from .event import Event
from .views import ReadoutView, StreamView, ConnectionView, SourceView, TankView, PumpView, SinkView, SplitterView, HydrocycloneView, JoinerView
# from .species import State
from .species import Species



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
        flowrates = self.stream.flowrates
        output = ''
        for species in Event.registered_species:
            output += f'{species.name}: {round(flowrates[species], 3)}\n'
        output = output[:-1]
        self.view.text_item.setPlainText(output)


class Stream(Model):
    def __init__(self, gui, name='Stream'):
        super().__init__(gui, name)
        self.inlet_connection = None
        self.outlet_connection = None
        self.view = StreamView(self)
        self.reset_flowrates()

    def __del__(self):
        try:
            self.remove_connection(self.inlet_connection)
        except Exception:
            pass
        try:
            self.remove_connection(self.outlet_connection)
        except Exception:
            pass

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
        
    def other_connection(self, connection):
        if self.inlet_connection is connection:
            return self.outlet_connection
        elif self.outlet_connection is connection:
            return self.inlet_connection
        return None

    def reset_flowrates(self):
        self.flowrates = {species: 0 for species in Event.registered_species}


class Connection(Model):
    def __init__(self, gui, module, capacity=float('inf'), name='Connection'): 
        super().__init__(gui, name)
        self.module = module
        self.capacity = capacity
        self.queue = EventQueue()
        self.stream = None
        self.view = ConnectionView(self)

    # Returns the connection at the other end of this connection's stream, if any
    @property
    def mate(self):
        if self.stream:
            return self.stream.other_connection(self)
        else:
            return None

    def transfer_events(self):
        raise NotImplementedError

    def connect(self, stream):
        self.stream = stream
        self.view.set_connected(True)
        return True

    def disconnect(self):
        self.stream = None
        self.view.set_connected(False)
        return True

    @property
    def backflow(self):
        return min(0, self.capacity - self.queue.volume)

    def push(self):
        pass

    def pull(self):
        pass

class InletConnection(Connection):
    def __init__(self, gui, module, capacity=float('inf'), name='Inlet'):
        super().__init__(gui, module, capacity, name)

    def transfer_events(self):
        transferred_flow = 0
        while not self.queue.empty() and transferred_flow + self.queue.peek().aggregate_volume() <= self.capacity:
            event = self.queue.dequeue()
            self.module.queue.enqueue(event)
            transferred_flow += event.aggregate_volume()
     
        return transferred_flow


class PushInletConnection(InletConnection):
    def __init__(self, gui, module, capacity=float('inf'), name='Inlet'):
        super().__init__(gui, module, capacity, name)
 
    def connect(self, stream):
        if stream.outlet_connection or stream.inlet_connection and not isinstance(stream.inlet_connection, PushOutletConnection):
            return False
        return super().connect(stream)

class PullInletConnection(InletConnection):
    def __init__(self, gui, module, capacity=float('inf'), name='Inlet'):
        super().__init__(gui, module, capacity, name)

    def connect(self, stream):
        if stream.outlet_connection or stream.inlet_connection and not isinstance(stream.inlet_connection, PullOutletConnection):
            return False
        if stream.inlet_connection:
            stream.inlet_connection.capacity = self.capacity
        return super().connect(stream)

    # This connection is the outlet of its stream. The stream's other connection is the inlet which this connection
    # pulls flow from.
    def pull(self):
        pulled_amount = 0
        self.stream.reset_flowrates()
        while not self.mate.queue.empty() and pulled_amount + self.mate.queue.peek().aggregate_volume() <= self.capacity:
            event = self.mate.queue.dequeue()
            self.queue.enqueue(event)
            pulled_amount += event.aggregate_volume()
            for species in event.registered_species:
                self.stream.flowrates[species] += event.species_volume(species)


class OutletConnection(Connection):
    def __init__(self, gui, module, capacity=float('inf'), name='Outlet'):
        super().__init__(gui, module, capacity, name)
        self.flow_fractions = None

    def set_flow_fractions(self, flow_fractions):
        self.flow_fractions = flow_fractions

    def transfer_events(self):
        if not self.flow_fractions:
            self.flow_fractions = {}
            for species in Event.registered_species:
                self.flow_fractions[species] = 1 / len(self.module.outlet_connections)
        
        # Calculate this outlet's share of each species' flow 
        species_outflows = {species: 0 for species in Event.registered_species}
        outflow = 0
        for species in Event.registered_species:
            species_outflow_fraction = self.flow_fractions[species] 
            species_outflow = species_outflow_fraction * self.module.initial_species_volumes[species]
            species_outflows[species] = species_outflow
            outflow += species_outflow

        if not self.module.total_inlet_flow:
            event_share = self.module.initial_queue_length
        else:
            event_share = math.ceil(self.module.initial_queue_length * outflow / self.module.total_inlet_flow) # Number of events sent to this outlet

        events_processed = 0
        transferred_flow = 0
        while not self.module.queue.empty() and events_processed < event_share:
            event = self.module.queue.dequeue()
            for species in Event.registered_species:
                species_event_volume = species_outflows[species] / event_share
                event.set_species_volume(species, species_event_volume)
                transferred_flow += species_event_volume

            self.queue.enqueue(event)
            events_processed += 1
        
        return transferred_flow

class PushOutletConnection(OutletConnection):
    def __init__(self, gui, module, capacity=float('inf'), name='Outlet'):
        super().__init__(gui, module, capacity, name)

    def connect(self, stream):
        if stream.inlet_connection or stream.outlet_connection and not isinstance(stream.outlet_connection, PushInletConnection):
            return False
        return super().connect(stream)

    # This connection is the inlet of its stream. The stream's other connection is the outlet which this connection
    # pushes flow into.
    def push(self):
        pushed_amount = 0
        self.stream.reset_flowrates()
        while not self.queue.empty() and pushed_amount + self.queue.peek().aggregate_volume() <= self.capacity:  
            event = self.queue.dequeue()
            self.mate.queue.enqueue(event)
            pushed_amount += event.aggregate_volume()
            for species in event.registered_species:
                self.stream.flowrates[species] += event.species_volume(species)

class PullOutletConnection(OutletConnection):
    def __init__(self, gui, module, capacity=float('inf'), name='Outlet'):
        super().__init__(gui, module, capacity, name)

    def connect(self, stream):
        if stream.inlet_connection or stream.outlet_connection and not isinstance(stream.outlet_connection, PullInletConnection):
            return False
        if stream.outlet_connection:
            self.capacity = stream.outlet_connection.capacity
        return super().connect(stream)


class Module(Model):
    def __init__(self, gui, name='Module'):
        super().__init__(gui, name)        
        self.gui.simulation.modules.append(self)
        self.inlet_connections = []
        self.inlet_flows = []
        self.outlet_connections = []
        self.outlet_flows = []
        self.queue = EventQueue()

    def __del__(self):
        self.gui.simulation.modules.remove(self)
 
    def add_inlet_connection(self, connection):
        self.inlet_connections.append(connection)

    def add_outlet_connection(self, connection):
        self.outlet_connections.append(connection)

    @property
    def total_inlet_flow(self):
        return sum(self.inlet_flows)

    @property
    def total_outlet_flow(self):
        return sum(self.total_outlet_flow)

    def preprocess(self):
        self.inlet_flows.clear()

        self.initial_queue_length = self.queue.length()
        self.initial_species_volumes = self.queue.species_flows

        for inlet_connection in self.inlet_connections:
            inlet_connection.pull()

        for inlet_connection in self.inlet_connections:
            inlet_flow = inlet_connection.transfer_events()
            self.inlet_flows.append(inlet_flow)

    def process(self):
        raise NotImplementedError
        
    def postprocess(self):
        self.outlet_flows.clear()

        for outlet_connection in self.outlet_connections:
            outlet_flow = outlet_connection.transfer_events()
            self.outlet_flows.append(outlet_flow)

        for outlet_connection in self.outlet_connections:
            outlet_connection.push()

        del self.initial_queue_length
        del self.initial_species_volumes

    def simulate(self):
        self.preprocess()
        self.process()
        self.postprocess()


class Source(Module):
    def __init__(self, gui, name='Source', outlet_capacity=10000, volumetric_fractions=None, event_rate=1000):
        super().__init__(gui, name)
        self.add_outlet_connection(PushOutletConnection(self.gui, self, outlet_capacity))
        self.volumetric_fractions = volumetric_fractions
        self.event_rate = event_rate
        self.view = SourceView(self)

    def process(self):
        connection = self.outlet_connections[0]
        outlet_amount = 0
        for i in range(self.event_rate):
            volume = connection.capacity / self.event_rate
            generated_species = []
            if self.volumetric_fractions:
                for species in Event.registered_species:
                    fraction = self.volumetric_fractions[species]
                    generated_species.append((species, fraction * volume))
            else:
                for species in Event.registered_species:
                    fraction = 1 / len(Event.registered_species)
                    generated_species.append((species, fraction * volume))

            # Create events at outlet connection
            connection.queue.enqueue(Event(generated_species))
            outlet_amount += volume

class Tank(Module):
    def __init__(self, gui, name='Tank', outlet_capacity=float('inf'), volumetric_fractions=None, event_rate=1000):
        super().__init__(gui, name)
        self.add_outlet_connection(PullOutletConnection(self.gui, self, outlet_capacity))
        self.volumetric_fractions = volumetric_fractions
        self.event_rate = event_rate
        self.view = TankView(self)

    def process(self):
        connection = self.outlet_connections[0]
        outlet_amount = 0
        flow_demand = connection.capacity
        for i in range(self.event_rate):
            volume = flow_demand / self.event_rate
            generated_species = []
            if self.volumetric_fractions:
                for species in Event.registered_species:
                    fraction = self.volumetric_fractions[species]
                    generated_species.append((species, fraction * volume))
            else:
                for species in Event.registered_species:
                    fraction = 1 / len(Event.registered_species)
                    generated_species.append((species, fraction * volume))
        
            connection.queue.enqueue(Event(generated_species))
            outlet_amount += volume
        
        
class Pump(Module): 
    def __init__(self, gui, name='Pump', inlet_capacity=5000):
        super().__init__(gui, name)
        self.add_inlet_connection(PullInletConnection(self.gui, self, inlet_capacity))
        self.add_outlet_connection(PushOutletConnection(self.gui, self))
        self.view = PumpView(self)

    def process(self):
        pass


class Sink(Module):
    def __init__(self, gui, name='Sink', inlet_capacity=float('inf')):
        super().__init__(gui, name)
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity))
        self.view = SinkView(self)

    def process(self):
        self.queue.events.clear()


class Splitter(Module):
    def __init__(self, gui, name='Splitter', inlet_capacity=float('inf'), split_fraction=.25):
        super().__init__(gui, name)
        self.split_fraction = split_fraction
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, name='Outlet1'))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, name='Outlet2'))
        self.view = SplitterView(self)

    def process(self):
        inlet_connection = self.inlet_connections[0]
        outlet_connection1, outlet_connection2 = self.outlet_connections

        outlet1_flow_fractions = {}
        outlet2_flow_fractions = {}

        for species in Event.registered_species:
            outlet1_flow_fractions[species] = self.split_fraction
            outlet2_flow_fractions[species] = (1 - self.split_fraction)

        outlet_connection1.set_flow_fractions(outlet1_flow_fractions)
        outlet_connection2.set_flow_fractions(outlet2_flow_fractions)


class Hydrocyclone(Module):
    def __init__(self, gui, name='Hydrocyclone', inlet_capacity=10000, rrv=0.08, rrw=0.14):
        super().__init__(gui, name)
        self.rrv = rrv # Reject rate by volume
        self.rrw = rrw # Reject rate by weight (solids only)
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, name='Outlet1'))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, name='Outlet2'))
        self.view = HydrocycloneView(self)

    def process(self):
        accept_flow_fractions = {}
        reject_flow_fractions = {}

        # TODO rrw should be based on mass, rrv should be a percent of all species, not just water
        for species in Event.registered_species:
            if species.name == 'water':
                accept_flow_fractions[species] = 1 - self.rrv
                reject_flow_fractions[species] = self.rrv
            elif species.name == 'fiber' or species_name == 'filler':
                accept_flow_fractions[species] = 1 - self.rrw
                reject_flow_fractions[species] = self.rrw

        accepts.set_flow_fractions(accept_flow_fractions)
        accepts.set_flow_fractions(reject_flow_fractions)


class Joiner(Module):
    def __init__(self, gui, name='Joiner', inlet_capacity1=float('inf'), inlet_capacity2=float('inf')):
        super().__init__(gui, name)
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity1, 'Inlet1'))
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity2, 'Inlet2'))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, inlet_capacity1 + inlet_capacity2))
        self.view = JoinerView(self)

    def process(self):
        pass
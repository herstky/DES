import math
import sigfig

from enum import Enum

from .event_queue import EventQueue
from .event import Event
from .views import (ReadoutView, StreamView, ConnectionView, SourceView, 
                    TankView, PumpView, SinkView, SplitterView, 
                    HydrocycloneView, JoinerView)
from .species import Species



class Model:
    def __init__(self, gui, name='Model'):
        self.gui = gui
        self.name = name
        self.view = None

    def cleanup(self):
        ''' Override this method to define what happens soon before 
            instances of Model subclasses get deleted.'''
        pass

class Readout(Model):
    def __init__(self, gui, name='Readout'):
        super().__init__(gui, name)
        self.view = ReadoutView(self)
        self.gui.simulation.displays.append(self)
        self.stream = None

    def update(self):
        ''' Gets the current iteration's flowrates of the connected 
            Stream and updates the displayed text view.'''
        flowrates = self.stream.flowrates
        output = ''
        for species in Event.registered_species:
            output += f'{species.name}: {round(flowrates[species], 3)}\n'
        output = output[:-1]
        self.view.text_item.setPlainText(output)
    
    def cleanup(self):
        ''' Removes this Readout instance from any lists that may be 
            tracking it.'''
        try:
            self.gui.simulation.displays.remove(self)
        except Exception:
            pass

        try:
            self.gui.scene.removeItem(self.view.graphics_item)
        except Exception:
            pass

        try:
            self.gui.views.remove(self.view)
        except Exception:
            pass


class FiberReadout(Readout):
    def __init__(self, gui, name='Readout'):
        super().__init__(gui, name)

    def update(self):
        ''' Overrides parent's update method to display values relevant to 
            paper manufacturing.'''
        flowrates = self.stream.flowrates
        liquid_flowrates = {}
        total_liquid_flow = 0
        solid_flowrates = {}
        total_solid_flow = 0
        for species, flowrate in flowrates.items():
            try:
                if species.properties['state'] == 'liquid':
                    liquid_flowrates[species] = flowrate
                    total_liquid_flow += flowrate
                elif species.properties['state'] == 'solid':
                    solid_flowrates[species] = flowrate
                    total_solid_flow += flowrate
            except KeyError as e:
                print('All species must have a "state" property.')

        total_flow = total_liquid_flow + total_solid_flow
        
        if not total_flow:
            output = ''
        else:
            consistency = total_solid_flow / total_flow * 100
            tonnage = total_solid_flow * 60 * 24 / 1000
            output = f'{sigfig.round(total_flow, sigfigs=3)} - {sigfig.round(consistency, sigfigs=3)} - {sigfig.round(tonnage, sigfigs=3)}'
        self.view.text_item.setPlainText(output)


class Stream(Model):
    def __init__(self, gui, name='Stream'):
        super().__init__(gui, name)
        self.inlet_connection = None
        self.outlet_connection = None
        self.view = StreamView(self)
        self.reset_flowrates()

    def cleanup(self):
        ''' Removes this Stream instance from any lists that may be 
            tracking it.'''
        try:
            self.remove_connection(self.inlet_connection)
        except Exception:
            pass

        try:
            self.remove_connection(self.outlet_connection)
        except Exception:
            pass

    def add_connection(self, connection):
        ''' Ensures connection is valid and assigns it to the 
            appropriate connection attribute. Returns True if the 
            connection is valid, otherwise returns False.'''
        if isinstance(connection, InletConnection) and connection.connect(self):
            self.outlet_connection = connection
            return True
        elif isinstance(connection, OutletConnection) and connection.connect(self):
            self.inlet_connection = connection
            return True
        return False

    def remove_connection(self, connection):
        ''' Removes the connection from this Stream instance. Returns 
            True if successful, otherwise returns False.'''
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
        ''' Returns the connection opposite to passed connection.'''
        if self.inlet_connection is connection:
            return self.outlet_connection
        elif self.outlet_connection is connection:
            return self.inlet_connection
        return None

    def reset_flowrates(self):
        ''' Sets all of this Stream instance's flowrates to 0.'''
        self.flowrates = {species: 0 for species in Event.registered_species}


class Connection(Model):
    def __init__(self, gui, module, capacity=float('inf'), name='Connection'): 
        super().__init__(gui, name)
        self.module = module
        self.capacity = capacity
        self.queue = EventQueue()
        self.stream = None
        self.view = ConnectionView(self)

    @property
    def mate(self):
        ''' Property. Returns the connection at the other end of this 
            Connection instance's stream.'''
        if self.stream:
            return self.stream.other_connection(self)
        else:
            return None

    def transfer_events(self):
        ''' This method must be overriden. Defines the behaviour of a 
            Connecction subclass when transferring Events to or from 
            the connected Module. Must return the volume 
            transferred.'''
        raise NotImplementedError

    def connect(self, stream):
        ''' Assigns a Stream to this Connection instance. Updates view 
            to reflect connected state.'''
        self.stream = stream
        self.view.set_connected(True)
        return True 

    def disconnect(self):
        ''' Removes this Connection instance's Stream. Updates view to
            reflect disconnected state.'''
        self.stream = None
        self.view.set_connected(False)
        return True 

    @property
    def backflow(self):
        ''' Returns the volume by which this Connection instance's 
            queue exceeds its capacity.'''
        return min(0, self.capacity - self.queue.volume)

    def push(self):
        ''' Override this method to define a Connection subclass' push 
            flow behaviour'''
        pass

    def pull(self):
        ''' Override this method to define a Connection subclass' pull 
            flow behaviour'''
        pass

class InletConnection(Connection):
    def __init__(self, gui, module, capacity=float('inf'), name='Inlet'):
        super().__init__(gui, module, capacity, name)

    def transfer_events(self):
        ''' Transfers Events from this Connection instance to its 
            Module.'''
        transferred_flow = 0
        while (not self.queue.empty() 
               and transferred_flow 
               + self.queue.peek().aggregate_volume() 
               <= self.capacity):
            event = self.queue.dequeue()
            self.module.queue.enqueue(event)
            transferred_flow += event.aggregate_volume()
     
        return transferred_flow


class PushInletConnection(InletConnection):
    def __init__(self, gui, module, capacity=float('inf'), name='Inlet'):
        super().__init__(gui, module, capacity, name)
 
    def connect(self, stream):
        ''' Checks stream for conflicting Connection. If none are 
            found, calls parent class' connect method and returns 
            True, otherwise returns False.'''
        if (stream.outlet_connection 
            or stream.inlet_connection 
            and not isinstance(stream.inlet_connection, PushOutletConnection)):
            return False
        return super().connect(stream)

class PullInletConnection(InletConnection):
    def __init__(self, gui, module, capacity=float('inf'), name='Inlet'):
        super().__init__(gui, module, capacity, name)

    def connect(self, stream):
        ''' Checks stream for conflicting Connection. If none are 
            found, sets stream's inlet Connection equal to this Connection 
            instance's capacity, calls parent class' connect method and 
            returns True, otherwise returns False.'''
        if (stream.outlet_connection 
            or stream.inlet_connection 
            and not isinstance(stream.inlet_connection, PullOutletConnection)):
            return False
        if stream.inlet_connection:
            stream.inlet_connection.capacity = self.capacity
        return super().connect(stream)

    def pull(self):
        ''' Pulls Events from the connected Stream's other Connection.'''
        pulled_amount = 0
        self.stream.reset_flowrates()
        while (not self.mate.queue.empty() 
               and pulled_amount 
               + self.mate.queue.peek().aggregate_volume() 
               <= self.capacity):
            event = self.mate.queue.dequeue()
            self.queue.enqueue(event)
            pulled_amount += event.aggregate_volume()
            for species in event.registered_species:
                self.stream.flowrates[species] += event.species_volume(species)


class OutletConnection(Connection):
    def __init__(self, gui, module, capacity=float('inf'), name='Outlet'):
        super().__init__(gui, module, capacity, name)
        
        # dict that specifies the fraction of the connected Module's 
        # volumetric feed flow that goes to this OutletConnection for each 
        # species.
        self.flow_fractions = None 

    def set_flow_fractions(self, flow_fractions):
        ''' Assigns flow_fractions to this OutletConnection instance's 
            flow_fractions dict'''
        self.flow_fractions = flow_fractions

    def transfer_events(self):
        ''' Transfers Events from this OutletConnection instance's connected
            module to this OutletConnection instance's queue.'''
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
        ''' Checks stream for conflicting Connection. If none are 
            found, calls parent class' connect method and returns 
            True, otherwise returns False.'''
        if (stream.inlet_connection 
            or stream.outlet_connection 
            and not isinstance(stream.outlet_connection, PushInletConnection)):
            return False
        return super().connect(stream)

    def push(self):
        ''' Pushes Events to the connected Stream's other Connection.'''
        pushed_amount = 0
        self.stream.reset_flowrates()
        while (not self.queue.empty() 
               and pushed_amount 
               + self.queue.peek().aggregate_volume() 
               <= self.capacity):  
            event = self.queue.dequeue()
            self.mate.queue.enqueue(event)
            pushed_amount += event.aggregate_volume()
            for species in event.registered_species:
                self.stream.flowrates[species] += event.species_volume(species)

class PullOutletConnection(OutletConnection):
    def __init__(self, gui, module, capacity=float('inf'), name='Outlet'):
        super().__init__(gui, module, capacity, name)

    def connect(self, stream):
        ''' Checks stream for conflicting Connection. If none are 
            found, sets stream's outlet Connection equal to this Connection 
            instance's capacity, calls parent class' connect method and 
            returns True, otherwise returns False.'''
        if (stream.inlet_connection 
            or stream.outlet_connection 
            and not isinstance(stream.outlet_connection, PullInletConnection)):
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
 
    def generate_flow(self, connection, species_flows):
        ''' Instantiates an Event as specified by species_flows dict and 
            enqueues it to connection's queue.'''
        connection.queue.enqueue(Event(species_flows))


    def purge_flow(self):
        ''' Purges all Events from this Module instance's queue, removing them
            from the Simulation.'''
        self.queue.events.clear()

    def add_inlet_connection(self, connection):
        ''' Adds connection to the end of this Module instance's 
            inlet_connections list.'''
        self.inlet_connections.append(connection)

    def add_outlet_connection(self, connection):
        ''' Adds connection to the end of this Module instance's 
            outlet_connections list.'''
        self.outlet_connections.append(connection)

    @property
    def total_inlet_flow(self):
        ''' Returns the total inlet flow to this Module instance.'''
        return sum(self.inlet_flows)

    @property
    def total_outlet_flow(self):
        ''' Returns the total outlet flow from this Module instance.'''
        return sum(self.total_outlet_flow)

    def preprocess(self):
        ''' Resets this Module instance's attributes relating to inlet flows
            in preparation for the current iteration.'''
        self.inlet_flows.clear()

        for inlet_connection in self.inlet_connections:
            inlet_connection.pull()

        for inlet_connection in self.inlet_connections:
            inlet_flow = inlet_connection.transfer_events()
            self.inlet_flows.append(inlet_flow)

        self.initial_queue_length = self.queue.length()
        self.initial_species_volumes = self.queue.species_flows

    def process(self):
        ''' Override this method to define a Module subclass' behaviour.'''
        raise NotImplementedError
        
    def postprocess(self):
        ''' Resets this Module instance's attributes relating to outlet flows
            following the current iteration.'''
        self.outlet_flows.clear()

        for outlet_connection in self.outlet_connections:
            outlet_flow = outlet_connection.transfer_events()
            self.outlet_flows.append(outlet_flow)

        for outlet_connection in self.outlet_connections:
            outlet_connection.push()

        del self.initial_queue_length
        del self.initial_species_volumes

    def simulate(self):
        ''' Runs this Module instance's preprocess, process, and postprocess 
            methods, in that order, ensuring all attributes are set up and 
            cleaned up properly.'''
        self.preprocess()
        self.process()
        self.postprocess()


class Source(Module):
    def __init__(self, gui, name='Source', outlet_capacity=10000, 
                 volumetric_fractions=None, event_rate=10000):
        super().__init__(gui, name)
        self.add_outlet_connection(PushOutletConnection(self.gui, self, outlet_capacity))
        self.volumetric_fractions = volumetric_fractions
        self.event_rate = event_rate
        self.view = SourceView(self)

    def process(self):
        ''' Generates Events as specified by this Source instance's 
            volumetric_fractions dict or generates an equal split of all 
            Species registered to the Event class if volumetric_fractions is
            not provided.'''
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
            self.generate_flow(connection, generated_species)
            outlet_amount += volume

class Tank(Module):
    def __init__(self, gui, name='Tank', outlet_capacity=float('inf'), 
                 volumetric_fractions=None, event_rate=1000):
        super().__init__(gui, name)
        self.add_outlet_connection(PullOutletConnection(self.gui, self, outlet_capacity))
        self.volumetric_fractions = volumetric_fractions
        self.event_rate = event_rate
        self.view = TankView(self)

    def process(self):
        ''' Generates Events as specified by this Source instance's 
            volumetric_fractions dict or generates an equal split of all 
            Species registered to the Event class if volumetric_fractions is
            not provided.'''
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
        
            # Create events at outlet connection
            self.generate_flow(connection, generated_species)
            outlet_amount += volume
        
        
class Pump(Module): 
    def __init__(self, gui, name='Pump', inlet_capacity=5000):
        super().__init__(gui, name)
        self.add_inlet_connection(PullInletConnection(self.gui, self, inlet_capacity))
        self.add_outlet_connection(PushOutletConnection(self.gui, self))
        self.view = PumpView(self)

    def process(self):
        ''' Passively allows for the inlet and outlet Connections to handle 
            flow through this Pump instance.'''
        pass


class Sink(Module):
    def __init__(self, gui, name='Sink', inlet_capacity=float('inf')):
        super().__init__(gui, name)
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity))
        self.view = SinkView(self)

    def process(self):
        ''' Removes all flow to this Sink instance from the Simulation.'''
        self.purge_flow()


class Splitter(Module):
    def __init__(self, gui, name='Splitter', inlet_capacity=float('inf'), split_fraction=.25):
        super().__init__(gui, name)
        self.split_fraction = split_fraction
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, name='Outlet1'))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, name='Outlet2'))
        self.view = SplitterView(self)

    def process(self):
        ''' Splits flow to this Splitter instance evenly across all Species 
            registered to the Event class, between its two outlets in the 
            proportion specified by the split_fraction.'''
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
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity, name='Feed'))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, name='Accepts'))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, name='Rejects'))
        self.view = HydrocycloneView(self)

    def process(self):
        ''' Splits the flow to this Hydrocyclone instance's inlet connection 
            between its accepts and rejects Connections as specified by its 
            rrv and rrw.'''
        accepts_connection, rejects_connection = self.outlet_connections
        accepts_flow_fractions = {}
        rejects_flow_fractions = {}
    
        total_feed_flow = self.queue.volume # Total volumetric flow at the feed.
        feed_flows = {} # Volumetric flows of all species at the feed.
        feed_mass_flows = {} # Mass flows of all species at the feed.
        feed_liquids_flows = {} # Volumetric flows of all liquid species at the feed.
        total_feed_liquids_flow = 0 # Sum of volumetric flows of all liquid species at the feed.
        liquid_ratios = {} # Ratios of each liquid feed volumetric flow to total_feed_liquids_flow.
        feed_solids_flows = {} # Volumetric flows of all solid species at the feed.

        rejects_flows = {} # Volumetric flows of all species at the rejects.
        rejects_mass_flows = {} # Mass flows of all species at the rejects.
        total_rejects_solids_flow = 0 # Sum of volumetric flows of all solid species at the rejects.
        total_rejects_flow = total_feed_flow * self.rrv # Total volumetric flow at the rejects.

        # Separate liquids from solids and store volumes of each species.
        for species in Event.registered_species:
            try:
                feed_flows[species] = self.queue.species_flows[species]
                feed_mass_flows[species] = feed_flows[species] * species.properties['density']
                if species.properties['state'] == 'liquid':
                    feed_liquids_flows[species] = self.queue.species_flows[species]
                    total_feed_liquids_flow += feed_liquids_flows[species]
                elif species.properties['state'] == 'solid':
                    feed_solids_flows[species] = self.queue.species_flows[species]
                    rejects_mass_flows[species] = feed_mass_flows[species] * self.rrw
                    rejects_flows[species] = rejects_mass_flows[species] / species.properties['density']
                    total_rejects_solids_flow += rejects_flows[species]
  
            except KeyError as e:
                print('All species must have "state" and "density" properties.')

        total_rejects_liquids_flow = total_rejects_flow - total_rejects_solids_flow # Total volumetric flow of all liquids at the rejects.

        # Calculate and store rejects flows for all liquids.
        for liquid, volume in feed_liquids_flows.items():
            try:
                ratio = volume / total_feed_liquids_flow
            except ZeroDivisionError as e:
                print(e)
                ratio = 0
            rejects_flows[liquid] = total_rejects_liquids_flow * ratio

        # Calculate and store flow fractions for accepts and rejects
        for species in Event.registered_species:
            try:
                rejects_fraction = rejects_flows[species] / feed_flows[species]
            except ZeroDivisionError as e:
                print(e)
                rejects_fraction = 0
            accepts_fraction = 1 - rejects_fraction
            rejects_flow_fractions[species] = rejects_fraction
            accepts_flow_fractions[species] = accepts_fraction
        
        accepts_connection.set_flow_fractions(accepts_flow_fractions)
        rejects_connection.set_flow_fractions(rejects_flow_fractions)


class Joiner(Module):
    def __init__(self, gui, name='Joiner', inlet_capacity1=float('inf'), inlet_capacity2=float('inf')):
        super().__init__(gui, name)
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity1, 'Inlet1'))
        self.add_inlet_connection(PushInletConnection(self.gui, self, inlet_capacity2, 'Inlet2'))
        self.add_outlet_connection(PushOutletConnection(self.gui, self, inlet_capacity1 + inlet_capacity2))
        self.view = JoinerView(self)

    def process(self):
        ''' Passively joins the flow from this Joiner instance's two inlet 
            Connections and pushes it to its outlet Connection.'''
        pass
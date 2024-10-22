import math
import sigfig

from enum import Enum

from .event_queue import EventQueue
from .event import Event
from .views import (ReadoutView, StreamView, SocketView, SourceView, 
                    TankView, PumpView, SinkView, SplitterView, 
                    HydrocycloneView, JoinerView, PumpView)
from .dialogs import ModelDialog, PumpDialog, TankDialog, SourceDialog, HydrocycloneDialog
from .species import Species



class Model:
    def __init__(self, gui, name='Model'):
        self.gui = gui
        self.name = name
        self.view = None
        self.dialog_class = ModelDialog
        self.dialog = None

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

    def connect_to_stream(self, stream):
        if stream.readout:
            return False
        self.stream = stream
        stream.readout = self

        return True

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

        try:
            self.stream.readout = None
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
            output = f'{sigfig.round(total_flow, sigfigs=3)} - ' \
                     f'{sigfig.round(consistency, sigfigs=3)} - ' \
                     f'{sigfig.round(tonnage, sigfigs=3)}'

        self.view.text_item.setPlainText(output)


class Stream(Model):
    def __init__(self, gui, name='Stream'):
        super().__init__(gui, name)
        self.inlet_socket = None
        self.outlet_socket = None
        self.readout = None
        self.gui.simulation.streams.append(self)
        self.view = StreamView(self)
        self.reset_flowrates()

    def cleanup(self):
        ''' Removes this Stream instance from any lists that may be 
            tracking it.'''
        try:
            self.remove_socket(self.inlet_socket)
        except Exception:
            pass

        try:
            self.remove_socket(self.outlet_socket)
        except Exception:
            pass

        try:
            self.gui.simulation.streams.remove(self)
        except Exception:
            pass

    def add_socket(self, socket):
        ''' Ensures socket is valid and assigns it to the 
            appropriate socket attribute. Returns True if the 
            socket is valid, otherwise returns False.'''
        if isinstance(socket, InletSocket) and socket.connect(self):
            self.outlet_socket = socket
            return True
        elif isinstance(socket, OutletSocket) and socket.connect(self):
            self.inlet_socket = socket
            return True
        return False

    def remove_socket(self, socket):
        ''' Removes the socket from this Stream instance. Returns 
            True if successful, otherwise returns False.'''
        if self.inlet_socket is socket:
            self.inlet_socket.disconnect()
            self.inlet_socket = None
            return True
        elif self.outlet_socket is socket:
            self.outlet_socket.disconnect()
            self.outlet_socket = None
            return True
        return False
        
    def other_socket(self, socket):
        ''' Returns the socket opposite to socket argument.'''
        if self.inlet_socket is socket:
            return self.outlet_socket
        elif self.outlet_socket is socket:
            return self.inlet_socket
        return None

    def reset_flowrates(self):
        ''' Sets all of this Stream instance's flowrates to 0.'''
        self.flowrates = {species: 0 for species in Event.registered_species}


class Socket(Model):
    def __init__(self, gui, module, capacity=float('inf'), name='Socket'): 
        super().__init__(gui, name)
        self.module = module
        self.capacity = capacity
        self.queue = EventQueue()
        self.stream = None
        self.view = SocketView(self)

    @property
    def mate(self):
        ''' Property. Returns the Socket at the other end of this 
            Socket instance's stream.'''
        if self.stream:
            return self.stream.other_socket(self)
        else:
            return None

    def transfer_events(self):
        ''' This method must be overriden. Defines the behaviour of a 
            Socket subclass when transferring Events to or from 
            the connected Module. Must return the volume 
            transferred.'''
        raise NotImplementedError

    def connect(self, stream):
        ''' Assigns a Stream to this Socket instance. Updates view 
            to reflect connected state.'''
        self.stream = stream
        self.view.set_connected(True)
        return True 

    def disconnect(self):
        ''' Removes this Socket instance's Stream. Updates view to
            reflect disconnected state.'''
        self.stream = None
        self.view.set_connected(False)
        return True 

    @property
    def backflow(self):
        ''' Returns the volume by which this Socket instance's 
            queue exceeds its capacity.'''
        return min(0, self.capacity - self.queue.magnitude)

    def push(self):
        ''' Override this method to define a Socket subclass' push 
            flow behaviour'''
        pass

    def pull(self):
        ''' Override this method to define a Socket subclass' pull 
            flow behaviour'''
        pass

class InletSocket(Socket):
    def __init__(self, gui, module, capacity=float('inf'), name='Inlet'):
        super().__init__(gui, module, capacity, name)

    def transfer_events(self):
        ''' Transfers Events from this Socket instance to its 
            Module.'''
        transferred_flow = 0
        while (not self.queue.empty() 
               and transferred_flow 
               + self.queue.peek().aggregate_magnitude() 
               <= self.capacity):
            event = self.queue.dequeue()
            self.module.queue.enqueue(event)
            transferred_flow += event.aggregate_magnitude()
     
        return transferred_flow


class PushInletSocket(InletSocket):
    def __init__(self, gui, module, capacity=float('inf'), name='Inlet'):
        super().__init__(gui, module, capacity, name)
 
    def connect(self, stream):
        ''' Checks stream for conflicting Socket. If none are 
            found, calls parent class' connect method and returns 
            True, otherwise returns False.'''
        if (stream.outlet_socket
            or stream.inlet_socket
            and not isinstance(stream.inlet_socket, PushOutletSocket)):
            return False
        return super().connect(stream)

class PullInletSocket(InletSocket):
    def __init__(self, gui, module, capacity=0, name='Inlet'):
        super().__init__(gui, module, capacity, name)

    def connect(self, stream):
        ''' Checks stream for conflicting Socket. If none are 
            found, sets stream's inlet Socket equal to this Socket 
            instance's capacity, calls parent class' connect method and 
            returns True, otherwise returns False.'''
        if (stream.outlet_socket
            or stream.inlet_socket
            and not isinstance(stream.inlet_socket, PullOutletSocket)):
            return False
        if stream.inlet_socket:
            stream.inlet_socket.capacity = self.capacity
        return super().connect(stream)

    def pull(self):
        ''' Pulls Events from the connected Stream's other Socket.'''
        pulled_amount = 0
        self.mate.capacity = self.capacity
        self.stream.reset_flowrates()
        while (not self.mate.queue.empty() 
               and pulled_amount 
               + self.mate.queue.peek().aggregate_magnitude() 
               <= self.capacity):
            event = self.mate.queue.dequeue()
            self.queue.enqueue(event)
            pulled_amount += event.aggregate_magnitude()
            for species in event.registered_species:
                self.stream.flowrates[species] += event.species_magnitude(species)


class OutletSocket(Socket):
    def __init__(self, gui, module, capacity=float('inf'), name='Outlet'):
        super().__init__(gui, module, capacity, name)
        
        # dict that specifies the fraction of the connected Module's 
        # volumetric feed flow that goes to this OutletSocket for each 
        # species.
        self.flow_fractions = None 

    def set_flow_fractions(self, flow_fractions):
        ''' Assigns flow_fractions to this OutletSocket instance's 
            flow_fractions dict'''
        self.flow_fractions = flow_fractions

    def transfer_events(self):
        ''' Transfers Events from this OutletSocket instance's connected
            module to this OutletSocket instance's queue.'''
        # If flow fractions to each outlet are not specified, split the flows
        # to the outlets evenly.
        if not self.flow_fractions:
            self.flow_fractions = {}
            for species in Event.registered_species:
                self.flow_fractions[species] = 1 / len(self.module.outlet_sockets)
        
        # Calculate this outlet's share of each species' flow.
        species_outflows = {species: 0 for species in Event.registered_species}
        outflow = 0
        for species in Event.registered_species:
            species_outflow_fraction = self.flow_fractions[species] 
            species_outflow = (species_outflow_fraction 
                               * self.module.initial_species_volumes[species])
            species_outflows[species] = species_outflow
            outflow += species_outflow

        # Determine number of events sent to this outlet.
        if not self.module.total_inlet_flow:
            event_share = self.module.initial_queue_length
        else:
            event_share = min(math.ceil(self.module.initial_queue_length 
                                        * outflow 
                                        / self.module.total_inlet_flow), self.module.queue.length())

        events_processed = 0
        transferred_flow = 0
        while not self.module.queue.empty() and events_processed < event_share:
            event = self.module.queue.dequeue()
            for species in Event.registered_species:
                species_event_volume = species_outflows[species] / event_share
                event.set_species_magnitude(species, species_event_volume)
                transferred_flow += species_event_volume

            self.queue.enqueue(event)
            events_processed += 1
        
        return transferred_flow

class PushOutletSocket(OutletSocket):
    def __init__(self, gui, module, capacity=float('inf'), name='Outlet'):
        super().__init__(gui, module, capacity, name)

    def connect(self, stream):
        ''' Checks stream for conflicting Socket. If none are 
            found, calls parent class' connect method and returns 
            True, otherwise returns False.'''
        if (stream.inlet_socket 
            or stream.outlet_socket 
            and not isinstance(stream.outlet_socket, PushInletSocket)):
            return False
        return super().connect(stream)

    def push(self):
        ''' Pushes Events to the connected Stream's other Socket.'''
        pushed_amount = 0
        self.stream.reset_flowrates()
        while (not self.queue.empty() 
               and pushed_amount 
               + self.queue.peek().aggregate_magnitude() 
               <= self.capacity):  
            event = self.queue.dequeue()
            self.mate.queue.enqueue(event)
            pushed_amount += event.aggregate_magnitude()
            for species in event.registered_species:
                self.stream.flowrates[species] += event.species_magnitude(species)

class PullOutletSocket(OutletSocket):
    def __init__(self, gui, module, capacity=0, name='Outlet'):
        super().__init__(gui, module, capacity, name)

    def connect(self, stream):
        ''' Checks stream for conflicting Socket. If none are 
            found, sets stream's outlet Socket equal to this Socket 
            instance's capacity, calls parent class' connect method and 
            returns True, otherwise returns False.'''
        if (stream.inlet_socket 
            or stream.outlet_socket 
            and not isinstance(stream.outlet_socket, PullInletSocket)):
            return False
        if stream.outlet_socket:
            self.capacity = stream.outlet_socket.capacity
        return super().connect(stream)


class Module(Model):
    def __init__(self, gui, name='Module'):
        super().__init__(gui, name)    
        self._capacity = 0    
        self.gui.simulation.modules.append(self)
        self.inlet_sockets = []
        self.inlet_flows = []
        self.outlet_sockets = []
        self.outlet_flows = []
        self.queue = EventQueue()

    def __del__(self):
        self.gui.simulation.modules.remove(self)
 
    def capacity(self):
        return self._capacity

    def set_capacity(self, capacity):
        self._capacity = capacity

    def generate_flow(self, socket, species_flows):
        ''' Instantiates an Event as specified by species_flows dict and 
            enqueues it to socket's queue.'''
        socket.queue.enqueue(Event(species_flows))


    def purge_flow(self):
        ''' Purges all Events from this Module instance's queue, removing them
            from the Simulation.'''
        self.queue.events.clear()

    def add_inlet_socket(self, socket):
        ''' Adds socket to the end of this Module instance's 
            inlet_sockets list.'''
        self.inlet_sockets.append(socket)

    def add_outlet_socket(self, socket):
        ''' Adds socket to the end of this Module instance's 
            outlet_sockets list.'''
        self.outlet_sockets.append(socket)

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

        for inlet_socket in self.inlet_sockets:
            inlet_socket.pull()

        for inlet_socket in self.inlet_sockets:
            inlet_flow = inlet_socket.transfer_events()
            self.inlet_flows.append(inlet_flow)

        self.initial_queue_length = self.queue.length()
        self.initial_species_volumes = self.queue.species_magnitudes

    def process(self):
        ''' Override this method to define a Module subclass' behaviour.'''
        raise NotImplementedError
        
    def postprocess(self):
        ''' Resets this Module instance's attributes relating to outlet flows
            following the current iteration.'''
        self.outlet_flows.clear()

        for outlet_socket in self.outlet_sockets:
            outlet_flow = outlet_socket.transfer_events()
            self.outlet_flows.append(outlet_flow)

        for outlet_socket in self.outlet_sockets:
            outlet_socket.push()

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
    def __init__(self, gui, name='Source', capacity=10000, 
                 volumetric_fractions=None, event_rate=1000):
        super().__init__(gui, name)
        self.add_outlet_socket(PushOutletSocket(self.gui, self, capacity))
        self.set_capacity(capacity)
        self.volumetric_fractions = volumetric_fractions
        self.event_rate = event_rate
        self.view = SourceView(self)
        self.dialog_class = SourceDialog

    def process(self):
        ''' Generates Events as specified by this Source instance's 
            volumetric_fractions dict or generates an equal split of all 
            Species registered to the Event class if volumetric_fractions is
            not provided.'''
        socket = self.outlet_sockets[0]
        outlet_amount = 0
        for i in range(self.event_rate):
            volume = socket.capacity / self.event_rate
            generated_species = []
            if self.volumetric_fractions:
                for species in Event.registered_species:
                    fraction = self.volumetric_fractions[species]
                    generated_species.append((species, fraction * volume))
            else:
                for species in Event.registered_species:
                    fraction = 1 / len(Event.registered_species)
                    generated_species.append((species, fraction * volume))

            # Create events at outlet socket
            self.generate_flow(socket, generated_species)
            outlet_amount += volume

    def set_capacity(self, capacity):
        self._capacity = capacity
        self.outlet_sockets[0].capacity = capacity

class Tank(Module):
    def __init__(self, gui, name='Tank', capacity=0, 
                 volumetric_fractions=None, event_rate=1000):
        super().__init__(gui, name)
        self.add_outlet_socket(PullOutletSocket(self.gui, self, capacity))
        self.volumetric_fractions = volumetric_fractions
        self.event_rate = event_rate
        self.view = TankView(self)
        self.dialog_class = TankDialog

    def process(self):
        ''' Generates Events as specified by this Source instance's 
            volumetric_fractions dict or generates an equal split of all 
            Species registered to the Event class if volumetric_fractions is
            not provided.'''
        socket = self.outlet_sockets[0]
        outlet_amount = 0
        flow_demand = socket.capacity
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
        
            # Create events at outlet socket
            self.generate_flow(socket, generated_species)
            outlet_amount += volume


class Sink(Module):
    def __init__(self, gui, name='Sink', capacity=float('inf')):
        super().__init__(gui, name)
        self.add_inlet_socket(PushInletSocket(self.gui, self, capacity))
        self.set_capacity(capacity)
        self.view = SinkView(self)

    def process(self):
        ''' Removes all flow to this Sink instance from the Simulation.'''
        self.purge_flow()


class Splitter(Module):
    def __init__(self, gui, name='Splitter', capacity=float('inf'), split_fraction=.25):
        super().__init__(gui, name)
        self.split_fraction = split_fraction
        self.add_inlet_socket(PushInletSocket(self.gui, self, capacity))
        self.add_outlet_socket(PushOutletSocket(self.gui, self, name='Outlet1'))
        self.add_outlet_socket(PushOutletSocket(self.gui, self, name='Outlet2'))
        self.set_capacity(capacity)
        self.view = SplitterView(self)

    def process(self):
        ''' Splits flow to this Splitter instance evenly across all Species 
            registered to the Event class, between its two outlets in the 
            proportion specified by the split_fraction.'''
        inlet_socket = self.inlet_sockets[0]
        outlet_socket1, outlet_socket2 = self.outlet_sockets

        outlet1_flow_fractions = {}
        outlet2_flow_fractions = {}

        for species in Event.registered_species:
            outlet1_flow_fractions[species] = self.split_fraction
            outlet2_flow_fractions[species] = (1 - self.split_fraction)

        outlet_socket1.set_flow_fractions(outlet1_flow_fractions)
        outlet_socket2.set_flow_fractions(outlet2_flow_fractions)


class Hydrocyclone(Module):
    def __init__(self, gui, name='Hydrocyclone', capacity=float('inf'), rrv=0.08, rrw=0.14):
        super().__init__(gui, name)
        self.rrv = rrv # Reject rate by volume
        self.rrw = rrw # Reject rate by weight (solids only)
        self.add_inlet_socket(PushInletSocket(self.gui, self, capacity, name='Feed'))
        self.add_outlet_socket(PushOutletSocket(self.gui, self, name='Accepts'))
        self.add_outlet_socket(PushOutletSocket(self.gui, self, name='Rejects'))
        self.set_capacity(capacity)
        self.view = HydrocycloneView(self)
        self.dialog_class = HydrocycloneDialog

    def process(self):
        ''' Splits the flow to this Hydrocyclone instance's inlet socket 
            between its accepts and rejects Sockets as specified by its 
            rrv and rrw.'''
        accepts_socket, rejects_socket = self.outlet_sockets
        accepts_flow_fractions = {}
        rejects_flow_fractions = {}
    
        total_feed_flow = self.queue.magnitude 
        feed_flows = {} 
        feed_mass_flows = {} 
        feed_liquids_flows = {} 
        total_feed_liquids_flow = 0 
        liquid_ratios = {} 
        feed_solids_flows = {} 

        rejects_flows = {} 
        rejects_mass_flows = {} 
        total_rejects_solids_flow = 0 
        total_rejects_flow = total_feed_flow * self.rrv 

        # Separate liquids from solids and store volumes of each species.
        for species in Event.registered_species:
            try:
                feed_flows[species] = self.queue.species_magnitudes[species]
                feed_mass_flows[species] = (feed_flows[species] * species.properties['density'])
                if species.properties['state'] == 'liquid':
                    feed_liquids_flows[species] = self.queue.species_magnitudes[species]
                    total_feed_liquids_flow += feed_liquids_flows[species]
                elif species.properties['state'] == 'solid':
                    feed_solids_flows[species] = self.queue.species_magnitudes[species]
                    rejects_mass_flows[species] = feed_mass_flows[species] * self.rrw
                    rejects_flows[species] = (rejects_mass_flows[species] / species.properties['density'])
                    total_rejects_solids_flow += rejects_flows[species]
  
            except KeyError as e:
                print('All species must have "state" and "density" properties.')

        total_rejects_liquids_flow = total_rejects_flow - total_rejects_solids_flow 

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
        
        accepts_socket.set_flow_fractions(accepts_flow_fractions)
        rejects_socket.set_flow_fractions(rejects_flow_fractions)


class Joiner(Module):
    def __init__(self, gui, name='Joiner', 
                 inlet_capacity1=float('inf'), inlet_capacity2=float('inf')):
        super().__init__(gui, name)
        self.add_inlet_socket(PushInletSocket(self.gui, self, inlet_capacity1, 'Inlet1'))
        self.add_inlet_socket(PushInletSocket(self.gui, self, inlet_capacity2, 'Inlet2'))
        self.add_outlet_socket(PushOutletSocket(self.gui, self, inlet_capacity1 + inlet_capacity2, 'Outlet'))
        self.set_capacity(inlet_capacity1 + inlet_capacity2)
        self.view = JoinerView(self)

    def process(self):
        ''' Passively joins the flow from this Joiner instance's two inlet 
            Sockets and pushes it to its outlet Socket.'''
        pass

class Pump(Module):
    def __init__(self, gui, name='Pump', capacity=5000):
        super().__init__(gui, name)
        self.add_inlet_socket(PushInletSocket(self.gui, self, capacity, 'Inlet1'))
        self.add_inlet_socket(PullInletSocket(self.gui, self, 0, 'Inlet2'))
        self.add_outlet_socket(PushOutletSocket(self.gui, self, float('inf'), 'Outlet'))
        self.set_capacity(capacity)
        self.view = PumpView(self)
        self.dialog_class = PumpDialog

    def process(self):
        push_inlet_socket, pull_inlet_socket = self.inlet_sockets
        pushed_inlet_flow = self.inlet_flows[0]
        pull_inlet_socket.capacity = self.capacity() - pushed_inlet_flow
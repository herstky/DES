from collections import deque

from .event import Event

class EventQueue:
    def __init__(self):
        self.events = deque()

    def peek(self):
        ''' Returns the Event at the front of the queue.'''
        return self.events[0]

    def enqueue(self, event):
        ''' Adds an Event to the back of the queue.'''
        self.events.append(event)

    def dequeue(self):
        ''' Removes and returns the Event at the front of the queue.'''
        return self.events.popleft()

    def length(self):
        ''' Returns the length of the queue.'''
        return len(self.events)

    def empty(self):
        ''' Returns True if the queue is empty, False otherwise.'''
        return len(self.events) == 0

    def events_per_volume(self, event_volume):
        ''' Returns the number of Events, starting at the front of the queue,
            that contains, in aggregate, the volume specified by event_volume.
        '''
        i = 0
        for event in self.events:
            event_volume -= event.aggregate_volume()
            i += 1
            if event_volume <= 0:
                return i
        else:
            return 0

    @property
    def volume(self):
        ''' Property. Returns the total volume of all Events in the queue.'''
        res = 0
        for event in self.events:
            res += event.aggregate_volume()
        return res

    @property
    def species_flows(self):
        ''' Property. Returns a dictionary mapping each registered Species to its 
            corresponding aggregate volume in the queue.'''
        res = {species: 0 for species in Event.registered_species}
        for event in self.events:
            for species in Event.registered_species:
                res[species] += event.species_volume(species)
        return res
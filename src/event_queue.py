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

    def events_per_magnitude(self, event_magnitude):
        ''' Returns the number of Events, starting at the front of the queue,
            that contains, in aggregate, the magnitude specified by event_magnitude.
        '''
        i = 0
        for event in self.events:
            event_volume -= event.aggregate_magnitude()
            i += 1
            if event_volume <= 0:
                return i
        else:
            return 0

    @property
    def magnitude(self):
        ''' Property. Returns the total volume of all Events in the 
            queue.'''
        res = 0
        for event in self.events:
            res += event.aggregate_magnitude()
        return res

    @property
    def species_magnitudes(self):
        ''' Property. Returns a dictionary mapping each registered Species to its 
            corresponding aggregate magnitude in the queue.'''
        res = {species: 0 for species in Event.registered_species}
        for event in self.events:
            for species in Event.registered_species:
                res[species] += event.species_magnitude(species)
        return res
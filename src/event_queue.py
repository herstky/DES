from collections import deque

from .event import Event

class EventQueue:
    def __init__(self):
        self.events = deque()
        self.amount_queued = 0
        self.species_flows = {species: 0 for species in Event.registered_species}

    def peek(self):
        return self.events[0]

    def enqueue(self, event):
        self.amount_queued += event.aggregate_volume()
        for species in Event.registered_species:
            self.species_flows[species] += event.species_volume(species)
        self.events.append(event)

    def dequeue(self):
        event = self.events.popleft()
        self.amount_queued -= event.aggregate_volume() # TODO Rename queued_volume or total_flow
        for species in Event.registered_species:
            self.species_flows[species] -= event.species_volume(species)
        return event

    def length(self):
        return len(self.events)

    def empty(self):
        return len(self.events) == 0

    def events_per_volume(self, volume):
        i = 0
        for event in self.events:
            volume -= event.aggregate_volume()
            i += 1
            if volume <= 0:
                return i
        else:
            return 0

    def rebalance_event_volumes(self, displaced_volumes):
        amount_queued = 0
        for event in self.events:
            for species in Event.registered_species:
                displaced_species_volume_per_event = displaced_volumes[species] / self.length()
                event.set_species_volume(species, displaced_species_volume_per_event)
                amount_queued += displaced_species_volume_per_event

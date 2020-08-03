from collections import deque

from .event import Event

class EventQueue:
    def __init__(self):
        self.events = deque()
        # self.species_flows = {species: 0 for species in Event.registered_species}

    def peek(self):
        return self.events[0]

    def enqueue(self, event):
        # for species in Event.registered_species:
            # self.species_flows[species] += event.species_volume(species)
        self.events.append(event)

    def dequeue(self):
        # event = 
        # for species in Event.registered_species:
            # self.species_flows[species] -= event.species_volume(species)
        return self.events.popleft()

    def length(self):
        return len(self.events)

    def empty(self):
        return len(self.events) == 0

    def events_per_volume(self, event_volume):
        i = 0
        for event in self.events:
            event_volume -= event.aggregate_volume()
            i += 1
            if event_volume <= 0:
                return i
        else:
            return 0

    def rebalance(self, displaced_volumes):
        # self.species_flows = {species: 0 for species in Event.registered_species}
        for event in self.events:
            for species in Event.registered_species:
                displaced_species_volume_per_event = displaced_volumes[species] / self.length()
                self.species_flows[species] += displaced_species_volume_per_event
                event.set_species_volume(species, displaced_species_volume_per_event)

    @property
    def volume(self):
        res = 0
        for event in self.events:
            res += event.aggregate_volume()
        return res

    @property
    def species_flows(self):
        res = {species: 0 for species in Event.registered_species}
        for event in self.events:
            for species in Event.registered_species:
                res[species] += event.species_volume(species)
        return res

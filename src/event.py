from .species import Species

class Event:
    registered_species = [] 
    count = 0
    def __init__(self, generated_species):
        if len(self.registered_species) == 0:
            raise RuntimeError('You must register at least one species')
    
        self._species_volumes = {species: 0 for species in self.registered_species}

        for species, volume in generated_species:
            self._species_volumes[species] = volume

        Event.count += 1
    
    def __del__(self):
        Event.count -= 1

    @classmethod
    def register_species(cls, species):
        ''' Class method. Adds species to list of registered Species.
        '''
        if type(species) is not list:
            species = [species]
        for _species in species:
            cls.registered_species.append(_species)

    def aggregate_volume(self):
        ''' Returns the total volume of all Species contained in this 
            Event.'''
        total_volume = 0

        for species in self._species_volumes:
            total_volume += self._species_volumes[species]

        return total_volume

    def species_volume(self, species):
        ''' Returns the volume of a specific Species contained in this 
            Event.'''
        return self._species_volumes[species]

    def aggregate_mass(self):
        ''' Returns the total mass of all Species contained in this 
            Event.'''
        total_mass = 0

        for Species in self._species_volumes:
            total_mass += self._species_volumes[species] * species['density']

    def species_mass(self, species):
        ''' Returns the mass of a specific Species contained in this 
            Event.'''
        return self._species_volumes[species] * species['density']

    def set_species_volume(self, species, volume):
        ''' Sets the volume of a specific Species contained in this Event to 
            volume.'''
        self._species_volumes[species] = volume

    def add_species_volume(self, species, volume):
        ''' Adds volume to a specific Species contained in this 
            Event.'''
        self._species_volumes[species] += volume

    def split_species_volume(self, species, split_fraction):
        ''' Multiplies the volume of a specific Species contained in 
            this Event by split_fraction and returns the volume that 
            was removed.'''
        if split_fraction < 0 or split_fraction > 1:
            raise ValueError('split_fraction must be between 0 and 1 (inclusive).')

        volume = self.species_volume(species)
        self.set_species_volume(species, split_fraction * volume)
        return (split_fraction * volume, (1 - split_fraction) * volume)
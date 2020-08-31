from .species import Species

class Event:
    registered_species = [] 
    count = 0
    def __init__(self, generated_species):
        if len(self.registered_species) == 0:
            raise RuntimeError('You must register at least one species')
    
        self._species_magnitudes = {species: 0 for species in self.registered_species}

        for species, magnitude in generated_species:
            self._species_magnitudes[species] = magnitude

        Event.count += 1
    
    def __del__(self):
        Event.count -= 1

    @classmethod
    def register_species(cls, species):
        ''' Class method. Adds species to list of registered Species.'''
        if type(species) is not list:
            species = [species]
        for _species in species:
            cls.registered_species.append(_species)

    def aggregate_magnitude(self):
        ''' Returns the total magnitude of all Species contained in this 
            Event.'''
        total_magnitude = 0

        for species in self._species_magnitudes:
            total_magnitude += self._species_magnitudes[species]

        return total_magnitude

    def species_magnitude(self, species):
        ''' Returns the magnitude of a specific Species contained in this 
            Event.'''
        return self._species_magnitudes[species]

    def set_species_magnitude(self, species, magnitude):
        ''' Sets the magnitude of a specific Species contained in this Event to 
            magnitude.'''
        self._species_magnitudes[species] = magnitude

    def add_species_magnitude(self, species, magnitude):
        ''' Adds magnitude to a specific Species contained in this 
            Event.'''
        self._species_magnitudes[species] += magnitude

    def split_species_magnitude(self, species, split_fraction):
        ''' Multiplies the magnitude of a specific Species contained in 
            this Event by split_fraction and returns the magnitude that 
            was removed.'''
        if split_fraction < 0 or split_fraction > 1:
            raise ValueError('split_fraction must be between 0 and 1 (inclusive).')

        magnitude = self.species_magnitude(species)
        self.set_species_magnitude(species, split_fraction * magnitude)
        return (split_fraction * magnitude, (1 - split_fraction) * magnitude)
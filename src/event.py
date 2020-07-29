from .species import gases_dict, liquids_dict, solids_dict, State

class Event:
    registered_species = [] # contains tuples in the form (species_name, state)
    count = 0
    def __init__(self, generated_species):
        if len(self.registered_species) == 0:
            raise RuntimeError('No species registered')
        
        gases = {species_name: {'data': gases_dict[species_name], 'volume': 0} for species_name, state in self.registered_species if state is State.gas}
        liquids = {species_name: {'data': liquids_dict[species_name], 'volume': 0} for species_name, state in self.registered_species if state is State.liquid}
        solids = {species_name: {'data': solids_dict[species_name], 'volume': 0} for species_name, state in self.registered_species if state is State.solid}
  
        self.species = {State.gas: gases, State.liquid: liquids, State.solid: solids}

        Event.count += 1

        for species_name, species_state, volume in generated_species:
            self.species[species_state][species_name]['volume'] = volume
    
    def __del__(self):
        Event.count -= 1

    @classmethod
    def register_species(cls, species):
        if type(species) is not list:
            species = [species]
        for _species in species:
            cls.registered_species.append(_species)

    def aggregate_volume(self):
        total_volume = 0

        for state in self.species:
            for species_name in self.species[state]: 
                total_volume += self.species[state][species_name]['volume']

        return total_volume

    def species_volume(self, species):
        species_name, state = species
        return self.species[state][species_name]['volume']
            

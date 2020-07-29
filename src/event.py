from .species import gases_dict, liquids_dict, solids_dict, State

class Event:
    registered_species = []
    count = 0
    def __init__(self, generated_species):
        if len(self.registered_species) == 0:
            raise RuntimeError('No species registered')
        
        gases = {species_name: {'data': gases_dict[species_name], 'volume': 0} for species_name, state in self.registered_species if state is State.GAS}
        liquids = {species_name: {'data': liquids_dict[species_name], 'volume': 0} for species_name, state in self.registered_species if state is State.LIQUID}
        solids = {species_name: {'data': solids_dict[species_name], 'volume': 0} for species_name, state in self.registered_species if state is State.SOLID}
  
        self.species = {State.GAS: gases, State.LIQUID: liquids, State.SOLID: solids}

        Event.count += 1
        # self.components = components

        for species_name, species_state, volume in generated_species:
            self.species[species_state][species_name]['volume'] = volume
    
    def __del__(self):
        Event.count -= 1

    # @classmethod
    # def register_components(cls, components):
    #     if type(components) is not list:
    #         components = [components]
    #     for component in components:
    #         cls.registered_components.append(component)

    @classmethod
    def register_species(cls, species):
        if type(species) is not list:
            species = [species]
        for _species in species:
            cls.registered_species.append(_species)

    @property
    def magnitude(self): # TODO rename
        total_volume = 0

        for state in self.species:
            for species_name in self.species[state]: 
                total_volume += self.species[state][species_name]['volume']

        return total_volume
            

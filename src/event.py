from .components import Water, Fiber

class Event:
    registered_components = []
    count = 0
    def __init__(self, components):
        if len(self.registered_components) == 0:
            raise RuntimeError('No components registered')
        
        Event.count += 1
        self.components = components
    
    def __del__(self):
        Event.count -= 1

    @classmethod
    def register_components(cls, components):
        if type(components) is not list:
            components = [components]
        for component in components:
            cls.registered_components.append(component)

    @property
    def magnitude(self): # TODO rename
        total_volume = 0
        for component in self.components:
            total_volume += component.volume
        return total_volume

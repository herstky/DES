class Component:
    name = 'Unnamed Component'
    density = 0
    def __init__(self, name, density, volume):
        self.name = name
        self.density = density # kg/l
        self.volume = volume # l

    @property
    def mass(self):
        return self.density * self.volume

class Water(Component):
    def __init__(self, volume):
        super().__init__('Water', 1, volume)


class Fiber(Component):
    def __init__(self, volume):
        super().__init__('Fiber', 1.2, volume)



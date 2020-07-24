import unittest

from src.components import Component, Water, Fiber

class TestComponent(unittest.TestCase):
    def test_init(self):
        self.assertEqual(Component('Component', 0, 0).name, 'Component')
        self.assertEqual(Component('Component', 10, 0).density, 10)
        self.assertEqual(Component('Component', 0, 10).volume, 10)
        self.assertEqual(Component('Component', 10, 10).mass, 100)

class TestWater(unittest.TestCase):
    def test_init(self):
        self.assertEqual(Water(10).name, 'Water')
        self.assertEqual(Water(10).density, 1)
        self.assertEqual(Water(10).volume, 10)
        self.assertEqual(Water(10).mass, 10)

class TestFiber(unittest.TestCase):
    def test_init(self):
        self.assertEqual(Fiber(10).name, 'Fiber')
        self.assertEqual(Fiber(10).density, 1.2)
        self.assertEqual(Fiber(10).volume, 10)
        self.assertEqual(Fiber(10).mass, 12)
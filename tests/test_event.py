import unittest

from src.event import Event
from src.components import Water, Fiber

class TestEvent(unittest.TestCase):
    def setUp(self):
        Event.registered_components = []

    def test_init_no_registered_components(self):
        self.assertRaises(RuntimeError, Event, [Water(10), Fiber(10)])

    def test_init(self):
        Event.register_components(Water)
        self.assertIsInstance(Event(Water(10)), Event)

    def test_register_components(self):
        Event.register_components(Water)
        self.assertIn(Water, Event.registered_components)

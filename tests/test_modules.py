import unittest

from src.modules import Module, Source, Sink, Splitter, Joiner
from src.connection import Connection
from src.event_queue import EventQueue

class TestModule(unittest.TestCase):
    def setUp(self):
        self.module = Module('Module')

    def test_init(self):
        self.assertEqual(self.module.name, 'Module')
        self.assertListEqual(self.module.inlet_connections, [])
        self.assertListEqual(self.module.outlet_connections, [])
        self.assertIsInstance(self.module.queue, EventQueue)

    def test_add_inlet_connection(self):
        self.assertListEqual(self.module.inlet_connections, [])
        conn1 = Connection()
        self.module.add_inlet_connection(conn1)
        self.assertListEqual(self.module.inlet_connections, [conn1])
        conn2 = Connection()
        self.module.add_inlet_connection(conn2)
        self.assertListEqual(self.module.inlet_connections, [conn1, conn2])
        

    def test_add_outlet_connections(self):
        self.assertListEqual(self.module.outlet_connections, [])
        conn1 = Connection()
        self.module.add_outlet_connection(conn1)
        self.assertListEqual(self.module.outlet_connections, [conn1])
        conn2 = Connection()
        self.module.add_outlet_connection(conn2)
        self.assertListEqual(self.module.outlet_connections, [conn1, conn2])

class TestSource(unittest.TestCase):
    def setUp(self):
        self.source = Source('Source', 1000, None, 100)

    def test_init(self):
        self.assertEqual(self.source.name, 'Source')
        self.assertListEqual(self.source.inlet_connections, [])
        self.assertIsInstance(self.source.outlet_connections[0], Connection)
        self.assertEqual(self.source.outlet_connections[0].capacity, 1000)
        self.assertEqual(len(self.source.outlet_connections), 1)
        self.assertIsInstance(self.source.queue, EventQueue)
        self.assertIs(self.source.volumetric_fractions, None)
        self.assertEqual(self.source.event_rate, 100)
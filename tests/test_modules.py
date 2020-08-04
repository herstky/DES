import unittest

# from src.modules import Module, Source, Sink, Splitter, Joiner
# from src.connection import Connection
# from src.event_queue import EventQueue
# from src.event import Event
# from src.stream import Stream
# # from components import Water



# class TestModule(unittest.TestCase):
#     def setUp(self):
#         self.module = Module('Module')

#     def test_init(self):
#         self.assertEqual(self.module.name, 'Module')
#         self.assertListEqual(self.module.inlet_connections, [])
#         self.assertListEqual(self.module.outlet_connections, [])
#         self.assertIsInstance(self.module.queue, EventQueue)

#     def test_add_inlet_connection(self):
#         self.assertListEqual(self.module.inlet_connections, [])
#         conn1 = Connection()
#         self.module.add_inlet_connection(conn1)
#         self.assertListEqual(self.module.inlet_connections, [conn1])
#         conn2 = Connection()
#         self.module.add_inlet_connection(conn2)
#         self.assertListEqual(self.module.inlet_connections, [conn1, conn2])
        
#     def test_add_outlet_connections(self):
#         self.assertListEqual(self.module.outlet_connections, [])
#         conn1 = Connection()
#         self.module.add_outlet_connection(conn1)
#         self.assertListEqual(self.module.outlet_connections, [conn1])
#         conn2 = Connection()
#         self.module.add_outlet_connection(conn2)
#         self.assertListEqual(self.module.outlet_connections, [conn1, conn2])


# class TestSource(unittest.TestCase):
#     def setUpClass():
#         Event.register_components(Water)

#     def setUp(self):
#         self.source = Source('Source', 1000, None, 100)
#         self.sink = Sink('Sink')
#         Stream(self.source.outlet_connections[0], self.sink.inlet_connections[0])

#     def test_init(self):
#         self.assertEqual(self.source.name, 'Source')
#         self.assertListEqual(self.source.inlet_connections, [])
#         self.assertIsInstance(self.source.outlet_connections[0], Connection)
#         self.assertEqual(self.source.outlet_connections[0].capacity, 1000)
#         self.assertEqual(len(self.source.outlet_connections), 1)
#         self.assertIsInstance(self.source.queue, EventQueue)
#         self.assertIs(self.source.volumetric_fractions, None)
#         self.assertEqual(self.source.event_rate, 100)

#     def assert_connection_states(self, source_outlet, sink_inlet):
#         self.assertEqual(self.source.outlet_connections[0].queue.amount_queued, source_outlet)
#         self.assertEqual(self.sink.inlet_connections[0].queue.amount_queued, sink_inlet)

#     def test_process(self):
#         self.assert_connection_states(0, 0)
        
#         self.source.process()
#         self.assert_connection_states(0, 1000)


# class TestSink(unittest.TestCase):
#     def setUpClass():
#         Event.register_components(Water)

#     def setUp(self):
#         self.source = Source('Source', 1000)
#         self.sink = Sink('Sink')
#         Stream(self.source.outlet_connections[0], self.sink.inlet_connections[0])

#     def test_init(self):
#         self.assertEqual(self.sink.name, 'Sink')
#         self.assertListEqual(self.sink.outlet_connections, [])
#         self.assertIsInstance(self.sink.inlet_connections[0], Connection)
#         self.assertEqual(self.sink.inlet_connections[0].capacity, 1000)
#         self.assertEqual(len(self.sink.inlet_connections), 1)
#         self.assertIsInstance(self.sink.queue, EventQueue)

#     def assert_connection_states(self, source_outlet, sink_inlet):
#         self.assertEqual(self.source.outlet_connections[0].queue.amount_queued, source_outlet)
#         self.assertEqual(self.sink.inlet_connections[0].queue.amount_queued, sink_inlet)

#     def test_process(self):
#         self.assert_connection_states(0, 0)

#         self.source.process()
#         self.assert_connection_states(0, 1000)
        
#         self.sink.process()
#         self.assert_connection_states(0, 0)


# class TestSplitter(unittest.TestCase):
#     def setUpClass():
#         Event.register_components(Water)

#     def setUp(self):
#         self.source = Source('Source', 1000)
#         self.sink1 = Sink('Sink1')
#         self.sink2 = Sink('Sink2')
#         self.splitter = Splitter('Splitter', 1000, .1)
#         Stream(self.source.outlet_connections[0], self.splitter.inlet_connections[0])
#         Stream(self.splitter.outlet_connections[0], self.sink1.inlet_connections[0])
#         Stream(self.splitter.outlet_connections[1], self.sink2.inlet_connections[0])

#     def test_init(self):
#         self.assertEqual(self.splitter.name, 'Splitter')
#         self.assertIsInstance(self.splitter.inlet_connections[0], Connection)
#         self.assertIsInstance(self.splitter.outlet_connections[0], Connection)
#         self.assertIsInstance(self.splitter.outlet_connections[1], Connection)
#         self.assertEqual(self.splitter.inlet_connections[0].capacity, 1000)
#         self.assertEqual(self.splitter.outlet_connections[0].capacity, 100)
#         self.assertEqual(self.splitter.outlet_connections[1].capacity, 900)
#         self.assertEqual(len(self.splitter.inlet_connections), 1)
#         self.assertEqual(len(self.splitter.outlet_connections), 2)
#         self.assertEqual(self.splitter.split_fraction, .1)
#         self.assertIsInstance(self.splitter.queue, EventQueue)

#     def assert_connection_states(self, source_outlet, sink1_inlet, sink2_inlet, splitter_inlet, splitter_outlet1, splitter_outlet2):
#         self.assertEqual(self.source.outlet_connections[0].queue.amount_queued, source_outlet)
#         self.assertEqual(self.sink1.inlet_connections[0].queue.amount_queued, sink1_inlet)
#         self.assertEqual(self.sink2.inlet_connections[0].queue.amount_queued, sink2_inlet)
#         self.assertEqual(self.splitter.inlet_connections[0].queue.amount_queued, splitter_inlet)
#         self.assertEqual(self.splitter.outlet_connections[0].queue.amount_queued, splitter_outlet1)
#         self.assertEqual(self.splitter.outlet_connections[1].queue.amount_queued, splitter_outlet2)

#     def test_process(self):
#         self.assert_connection_states(0, 0, 0, 0, 0, 0)
        
#         self.source.process()
#         self.assert_connection_states(0, 0, 0, 1000, 0, 0)
        
#         self.splitter.process()
#         self.assert_connection_states(0, 100, 900, 0, 0, 0)

#         self.sink1.process()
#         self.assert_connection_states(0, 0, 900, 0, 0, 0)
    
#         self.sink2.process()
#         self.assert_connection_states(0, 0, 0, 0, 0, 0)


# class TestJoiner(unittest.TestCase):
#     def setUpClass():
#         Event.register_components(Water)

#     def setUp(self):
#         self.source1 = Source('Source1', 500)
#         self.source2 = Source('Source2', 500)
#         self.sink = Sink('Sink')
#         self.joiner = Joiner('Joiner', 500, 500)
#         Stream(self.source1.outlet_connections[0], self.joiner.inlet_connections[0])
#         Stream(self.source2.outlet_connections[0], self.joiner.inlet_connections[1])
#         Stream(self.joiner.outlet_connections[0], self.sink.inlet_connections[0])
    
#     def test_init(self):
#         self.assertEqual(self.joiner.name, 'Joiner')
#         self.assertIsInstance(self.joiner.inlet_connections[0], Connection)
#         self.assertIsInstance(self.joiner.inlet_connections[1], Connection)
#         self.assertIsInstance(self.joiner.outlet_connections[0], Connection)
#         self.assertEqual(self.joiner.inlet_connections[0].capacity, 500)
#         self.assertEqual(self.joiner.inlet_connections[1].capacity, 500)
#         self.assertEqual(self.joiner.outlet_connections[0].capacity, 1000)
#         self.assertEqual(len(self.joiner.inlet_connections), 2)
#         self.assertEqual(len(self.joiner.outlet_connections), 1)
#         self.assertIsInstance(self.joiner.queue, EventQueue)

#     def assert_connection_states(self, source1_outlet, source2_outlet, sink_inlet, joiner_inlet1, joiner_inlet2, joiner_outlet):
#         self.assertEqual(self.source1.outlet_connections[0].queue.amount_queued, source1_outlet)
#         self.assertEqual(self.source2.outlet_connections[0].queue.amount_queued, source2_outlet)
#         self.assertEqual(self.sink.inlet_connections[0].queue.amount_queued, sink_inlet)
#         self.assertEqual(self.joiner.inlet_connections[0].queue.amount_queued, joiner_inlet1)
#         self.assertEqual(self.joiner.inlet_connections[1].queue.amount_queued, joiner_inlet2)
#         self.assertEqual(self.joiner.outlet_connections[0].queue.amount_queued, joiner_outlet)

#     def test_process(self):
#         self.assert_connection_states(0, 0, 0, 0, 0, 0)

#         self.source1.process()
#         self.assert_connection_states(0, 0, 0, 500, 0, 0)

#         self.source2.process()
#         self.assert_connection_states(0, 0, 0, 500, 500, 0)

#         self.joiner.process()
#         self.assert_connection_states(0, 0, 1000, 0, 0, 0)

#         self.sink.process()
#         self.assert_connection_states(0, 0, 0, 0, 0, 0)

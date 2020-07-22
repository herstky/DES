from connection import Connection


class Module:
    def __init__(self):
        self.inlet_connections = []
        self.outlet_connections = []

    def add_inlet_connection(self, connection):
        self.inlet_connections.append(connection)

    def add_outlet_connection(self, connection):
        self.outlet_connections.append(connection)

    def process_flows(self):
        total_inflow = 0
        for inlet_connection in self.inlet_connections:
            inlet_connection.process()
            total_inflow += inlet_connection.flowrate

        total_outflow = 0
        for outlet_connection in self.outlet_connections:
            outlet_connection.process()
            total_outflow += outlet_connection.flowrate


class Source(Module):
    def __init__(self, outlet_capacity=0):
        self.outlet_capacity = outlet_capacity
        self.outlet_connection = None


class Sink(Module):
    def __init__(self, inlet_capacity=0):
        self.inlet_capacity = inlet_capacity
        self.inlet_connection = None


class Splitter(Module):
    def __init__(self, inlet_capcity, split_fraction=.5):
        self.inlet_capacity = inlet_capcity
        self.inlet_connection = None
        self.split_fraction = split_fraction
        self.outlet_connection1 = None
        self.outlet_connection2 = None

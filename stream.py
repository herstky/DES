class Stream:
    def __init__(self, inlet_connection=None, outlet_connection=None):
        if inlet_connection:
            self.add_inlet_connection(inlet_connection)
        else:
            self.inlet_connection = None

        if outlet_connection:
            self.add_outlet_connection(outlet_connection)
        else:
            self.outlet_connection = None

    def __del__(self):
        self.remove_inlet_connection()
        self.remove_outlet_connection

    def add_inlet_connection(self, connection):
        self.inlet_connection = connection
        connection.stream = self

    def add_outlet_connection(self, connection):
        self.outlet_connection = connection
        connection.stream = self

    def remove_inlet_connection(self):
        self.inlet_connection.stream = None
        self.inlet_connection = None
    
    def remove_outlet_connection(self):
        self.outlet_connection.stream = None
        self.outlet_connection = None
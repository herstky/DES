class Connection:
    def __init__(self, flowrate=0, capacity=0, stream=None):
        self.flowrate = flowrate
        self.capacity = capacity
        self.connection = stream

    def process(self):
        pass

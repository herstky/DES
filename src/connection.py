from .event_queue import EventQueue


class Connection:
    def __init__(self, module=None, capacity=100, name='Connection'):
        self.module = module
        self.capacity = capacity
        self.name = name
        self.queue = EventQueue()
        self.stream = None

    def push(self):
        pushed_amount = 0
        while not self.queue.empty() and pushed_amount + self.queue.peek().magnitude <= self.capacity:  # TODO is self.capacity here correct?
            event = self.queue.dequeue()
            self.stream.outlet_connection.queue.enqueue(event)
            pushed_amount += event.magnitude
        print(f'{self.module.name} {self.name} to {self.stream.outlet_connection.module.name} {self.stream.outlet_connection.name} flowrate: {pushed_amount}, accumulated backflow: {self.queue.amount_queued}')

    def transfer_to_module(self, amount=0):
        if amount == 0:
            amount = self.capacity
        transferred_amount = 0
        while not self.queue.empty() and transferred_amount + self.queue.peek().magnitude <= amount <= self.capacity:
            event = self.queue.dequeue()
            self.module.queue.enqueue(event)
            transferred_amount += event.magnitude
        return transferred_amount

    def transfer_from_module(self, amount=0):
        if amount == 0:
            amount = self.capacity
        transferred_amount = 0
        while not self.module.queue.empty() and transferred_amount + self.module.queue.peek().magnitude <= amount <= self.capacity:
            event = self.module.queue.dequeue()
            self.queue.enqueue(event)
            transferred_amount += event.magnitude
        return transferred_amount

    @property
    def backflow(self):
        return min(0, self.capacity - self.queue.amount_queued)

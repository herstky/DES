from collections import deque

class EventQueue:
    def __init__(self):
        self.events = deque()
        self.amount_queued = 0

    def peek(self):
        return self.events[0]

    def enqueue(self, event):
        self.amount_queued += event.magnitude
        self.events.append(event)

    def dequeue(self):
        event = self.events.popleft()
        self.amount_queued -= event.magnitude
        return event

    def length(self):
        return len(self.events)

    def empty(self):
        return len(self.events) == 0
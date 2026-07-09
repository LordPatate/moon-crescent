class Listener:
    def receive(self, *args):
        raise NotImplementedError


class BroadCaster:
    def __init__(self):
        self.listeners = []

    def register_listener(self, listener: Listener):
        self.listeners.append(listener)

    def broadcast(self, *args):
        for listener in self.listeners:
            listener.receive(*args)

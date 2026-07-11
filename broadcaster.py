from collections.abc import MutableSequence
from typing import Protocol


class Listener(Protocol):
    def receive(self, *args) -> None: ...


class InnerListener:
    def __init__(self, callback):
        self.callback = callback

    def receive(self, *args) -> None:
        self.callback(*args)


class BroadCaster:
    def __init__(self) -> None:
        self.listeners: MutableSequence[Listener] = []

    def register_listener(self, listener: Listener) -> None:
        self.listeners.append(listener)

    def broadcast(self, *args) -> None:
        for listener in self.listeners:
            listener.receive(*args)

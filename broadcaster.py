from collections.abc import Callable, MutableSequence


class BroadCaster:
    def __init__(self) -> None:
        self.listeners: MutableSequence[Callable[..., None]] = []

    def register_listener(self, callback: Callable[..., None]) -> None:
        self.listeners.append(callback)

    def broadcast(self, *args, **kwargs) -> None:
        for callback in self.listeners:
            callback(*args, **kwargs)

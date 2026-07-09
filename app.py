from collections.abc import Callable, Mapping, Sequence
from typing import Protocol, Tuple, Union

import pygame
from pygame import Vector2, sprite, Surface

Coordinate = Union[Tuple[float, float], Sequence[float], Vector2]
EventTypeID = int


class DisplayFactory(Protocol):
    def __call__(self, size: Coordinate = (0, 0)) -> Surface: ...


def default_display(size: Coordinate = (1280, 720)):
    return pygame.display.set_mode(size, flags=(pygame.SCALED | pygame.RESIZABLE))


def default_background(display: Surface):
    bkg = Surface(display.get_size()).convert()
    bkg.fill(pygame.Color("grey"))
    display.blit(bkg, (0, 0))
    return bkg


class App:
    def __init__(self, display_factory: DisplayFactory = default_display, background=None) -> None:
        self.running: bool = False
        self.clock = pygame.time.Clock()
        self.make_screen: DisplayFactory = display_factory
        self.screen: Surface = self.make_screen()
        self.background: Surface = background or default_background(self.screen)
        self.sprites: sprite.LayeredDirty = sprite.LayeredDirty()
        self.event_handler: Mapping[EventTypeID, Callable[[App, pygame.Event], None]] = {
            pygame.QUIT: App._quit_loop,
            pygame.WINDOWRESIZED: App._resize_event,
        }

    def run(self) -> None:
        """Run the main loop."""
        self.running = True
        self.on_start()
        while self.running:
            for event in pygame.event.get():
                callback = self.event_handler.get(event.type)
                if callback:
                    callback(self, event)
            self.render()
            self.clock.tick(60)

    def render(self) -> None:
        """Draw all sprites and update screen."""
        dirty_rects = self.sprites.draw(self.screen, self.background)
        pygame.display.update(dirty_rects)

    def on_resize(self, new_size) -> None:
        """Called when the windows was resized."""
        screen = self.make_screen(new_size)
        bkg = pygame.transform.scale(self.background, new_size)
        screen.blit(bkg, (0, 0))
        pygame.display.flip()
        self.background = bkg
        self.screen = screen

    def on_start(self) -> None:
        """Called in run() right before entering the main loop."""

    def on_exit(self) -> None:
        """Called when receiving a QUIT event."""

    def _quit_loop(self, _) -> None:
        self.running = False
        self.on_exit()

    def _resize_event(self, event) -> None:
        new_size = (event.x, event.y)
        self.on_resize(new_size)

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Tuple, Union

import pygame
from pygame import Color, Rect, Surface, Vector2, sprite

from broadcaster import BroadCaster

Coordinate = Union[Tuple[float, float], Sequence[float], Vector2]
EventTypeID = int
DEFAULT_DISPLAY_SIZE = (1280, 720)
DEFAULT_DISPLAY_FLAGS = pygame.RESIZABLE


def load_image(path: Path | str, scale: float = 1.):
    image = pygame.image.load(path).convert()
    image = pygame.transform.scale_by(image, scale)
    return image


def proportional_blit(source: Surface, dest: Surface, x: float, y: float, *blit_args) -> Rect:
    """Blit source on dest.
    x and y are coordinates relative to dest's top-left corner;
    expressed as proportions of dest width and height respectively;
    and describe the desired position of the center of source.
    """
    source_w, source_h = source.get_size()
    dest_w, dest_h = dest.get_size()
    x_offset, y_offset = source_w // 2, source_h // 2
    pos = (
        int(dest_w * x) - x_offset,
        int(dest_h * y) - y_offset,
    )
    return dest.blit(source, pos, *blit_args)


class App:
    def __init__(self, size: Coordinate = DEFAULT_DISPLAY_SIZE, display_flags: int = DEFAULT_DISPLAY_FLAGS) -> None:
        self.running: bool = False
        self.clock = pygame.time.Clock()
        self.screen: Surface = pygame.display.set_mode(size, display_flags)
        self.background: Surface = self.make_background(size)
        self.sprites: sprite.LayeredDirty = sprite.LayeredDirty()
        self.event_broadcasters: Sequence[BroadCaster] = [
            BroadCaster() for _ in range(pygame.NUMEVENTS)
        ]
        self.register_event_listener(pygame.QUIT, self._quit_loop)
        self.register_event_listener(pygame.WINDOWRESIZED, self._resize_event)

    def run(self) -> None:
        """Run the main loop."""
        self.running = True
        self.on_start()
        while self.running:
            for event in pygame.event.get():
                self.event_broadcasters[event.type].broadcast(event)
            self.render()
            self.clock.tick(60)

    def render(self) -> None:
        """Draw all sprites and update screen."""
        dirty_rects = self.sprites.draw(self.screen, self.background)
        pygame.display.update(dirty_rects)

    def on_resize(self, new_size) -> None:
        """Called when the window was resized.
        By default, scale the background and redraw all sprites.
        """
        bkg = pygame.transform.scale(self.background, new_size)
        self.background = bkg
        self.screen.blit(bkg, (0, 0))
        pygame.display.flip()
        for sp in self.sprites:
            sp.dirty = 1
        self.render()

    def on_start(self) -> None:
        """Called in run() right before entering the main loop."""

    def on_exit(self) -> None:
        """Called when receiving a QUIT event."""

    def make_background(self, size: Coordinate = DEFAULT_DISPLAY_SIZE) -> Surface:
        """Called during app.__init__ to create app.background."""
        bkg = Surface(size).convert()
        bkg.fill(Color("grey"))
        return bkg

    def register_event_listener(self, event_type: EventTypeID, callback: Callable[..., None]) -> None:
        """Register a callback to the event broadcaster associated with an event type."""
        self.event_broadcasters[event_type].register_listener(callback)

    def _quit_loop(self, _) -> None:
        self.running = False
        self.on_exit()

    def _resize_event(self, event) -> None:
        new_size = (event.x, event.y)
        self.on_resize(new_size)


class OnClickListener(ABC):
    def __init__(self, app: App):
        app.register_event_listener(pygame.MOUSEBUTTONDOWN, self.on_click)

    @abstractmethod
    def on_click(self, event) -> None: ...


class OnClickReleaseListener(ABC):
    def __init__(self, app: App):
        app.register_event_listener(pygame.MOUSEBUTTONUP, self.on_click_release)

    @abstractmethod
    def on_click_release(self, event) -> None: ...


class OnMouseMoveListener(ABC):
    def __init__(self, app: App):
        app.register_event_listener(pygame.MOUSEMOTION, self.on_mouse_move)

    @abstractmethod
    def on_mouse_move(self, event) -> None: ...


def transparent_canvas(size, colorkey=Color("black")) -> Surface:
    surface = Surface(size)
    surface.fill(colorkey)
    surface.set_colorkey(colorkey)
    return surface

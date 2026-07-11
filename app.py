from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Tuple, Union

import pygame
from pygame import Color, Rect, Surface, Vector2, sprite

from broadcaster import BroadCaster, InnerListener

Coordinate = Union[Tuple[float, float], Sequence[float], Vector2]
EventTypeID = int
DEFAULT_DISPLAY_SIZE = (1280, 720)


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
    def __init__(self) -> None:
        self.running: bool = False
        self.clock = pygame.time.Clock()
        self.screen: Surface = self.make_screen()
        self.background: Surface = self.make_background()
        self.sprites: sprite.LayeredDirty = sprite.LayeredDirty()
        self.on_click_broadcaster = BroadCaster()
        self.on_click_release_broadcaster = BroadCaster()
        self.on_mouse_move_broadcaster = BroadCaster()
        self.event_handler: Mapping[EventTypeID, Callable[[pygame.event.Event], None]] = {
            pygame.QUIT: self._quit_loop,
            pygame.WINDOWRESIZED: self._resize_event,
            pygame.MOUSEBUTTONDOWN: self.on_click_broadcaster.broadcast,
            pygame.MOUSEBUTTONUP: self.on_click_release_broadcaster.broadcast,
            pygame.MOUSEMOTION: self.on_mouse_move_broadcaster.broadcast,
        }

    def run(self) -> None:
        """Run the main loop."""
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        self.running = True
        self.on_start()
        while self.running:
            for event in pygame.event.get():
                callback = self.event_handler.get(event.type)
                if callback:
                    callback(event)
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

    def make_background(self, size: Coordinate = DEFAULT_DISPLAY_SIZE):
        bkg = Surface(size).convert()
        bkg.fill(Color("grey"))
        return bkg

    def make_screen(self, size: Coordinate = DEFAULT_DISPLAY_SIZE):
        display_flags = pygame.SCALED | pygame.RESIZABLE
        return pygame.display.set_mode(size, flags=display_flags)

    def _quit_loop(self, _) -> None:
        self.running = False
        self.on_exit()

    def _resize_event(self, event) -> None:
        new_size = (event.x, event.y)
        self.on_resize(new_size)


class OnClickListener(ABC):
    def __init__(self, app: App):
        inner = InnerListener(self.on_click)
        app.on_click_broadcaster.register_listener(inner)

    @abstractmethod
    def on_click(self, event) -> None: ...


class OnClickReleaseListener(ABC):
    def __init__(self, app: App):
        inner = InnerListener(self.on_click_release)
        app.on_click_release_broadcaster.register_listener(inner)

    @abstractmethod
    def on_click_release(self, event) -> None: ...


class OnMouseMoveListener(ABC):
    def __init__(self, app: App):
        inner = InnerListener(self.on_mouse_move)
        app.on_mouse_move_broadcaster.register_listener(inner)

    @abstractmethod
    def on_mouse_move(self, event) -> None: ...

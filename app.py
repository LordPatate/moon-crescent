from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Protocol, Tuple, Union

import pygame
from pygame import Color, Surface, Vector2, sprite

Coordinate = Union[Tuple[float, float], Sequence[float], Vector2]
EventTypeID = int
DEFAULT_DISPLAY_SIZE = (1280, 720)


class SurfaceFromSizeFactory(Protocol):
    def __call__(self, size: Coordinate = (0, 0)) -> Surface: ...


def default_display(size: Coordinate = DEFAULT_DISPLAY_SIZE):
    display_flags = pygame.SCALED | pygame.RESIZABLE
    return pygame.display.set_mode(size, flags=display_flags)


def default_background(size: Coordinate = DEFAULT_DISPLAY_SIZE):
    bkg = Surface(size).convert()
    bkg.fill(Color("grey"))
    return bkg


def load_image(path: Path | str, scale: float = 1.):
    image = pygame.image.load(path).convert()
    image = pygame.transform.scale_by(image, scale)
    return image


def proportional_blit(source: Surface, dest: Surface, x: float, y: float, *blit_args) -> None:
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
    dest.blit(source, pos, *blit_args)


class App:
    def __init__(
            self,
            display_factory: SurfaceFromSizeFactory = default_display,
            background_factory: SurfaceFromSizeFactory = default_background,
    ) -> None:
        self.running: bool = False
        self.clock = pygame.time.Clock()
        self.make_screen: SurfaceFromSizeFactory = display_factory
        self.screen: Surface = self.make_screen()
        self.make_background: SurfaceFromSizeFactory = background_factory
        self.background: Surface = self.make_background()
        self.sprites: sprite.LayeredDirty = sprite.LayeredDirty()
        self.event_handler: Mapping[EventTypeID, Callable[[App, pygame.Event], None]] = {
            pygame.QUIT: App._quit_loop,
            pygame.WINDOWRESIZED: App._resize_event,
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

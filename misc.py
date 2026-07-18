from pathlib import Path

from pygame import Color, Rect, Surface
import pygame


def transparent_canvas(size, colorkey=Color("black")) -> Surface:
    surface = Surface(size)
    surface.fill(colorkey)
    surface.set_colorkey(colorkey)
    return surface


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

from dataclasses import dataclass
import math
from pathlib import Path

import pygame
from pygame import Color, Rect, Surface

from broadcaster import BroadCaster
from app import (DEFAULT_DISPLAY_SIZE, App, Coordinate, OnClickListener, OnClickReleaseListener, OnMouseMoveListener,
                 load_image, proportional_blit)


@dataclass
class Circle:
    center: Coordinate
    radius: float


class SliderControl(
        pygame.sprite.WeakDirtySprite,
        BroadCaster,
        OnClickListener,
        OnClickReleaseListener,
        OnMouseMoveListener,
):
    colorset = [("darkred", "red"), ("yellow3", "yellow")]
    cursor_size = (20, 30)
    cursor_w, cursor_h = cursor_size

    def __init__(self, app: App, pos: Coordinate, val_range: Tuple[float, float], segment_length: int, *groups) -> None:
        pygame.sprite.WeakDirtySprite.__init__(self, *groups)
        BroadCaster.__init__(self)
        OnClickListener.__init__(self, app)
        OnClickReleaseListener.__init__(self, app)
        OnMouseMoveListener.__init__(self, app)
        self.clicked = False
        min_val, max_val = val_range
        self.min_val = min_val
        self.max_val = max_val
        self.segment_length = segment_length  # length, in pixel, of the segment on which the button will slide
        self.val = (max_val - min_val) / 2 + min_val
        self.x_pos = self.cursor_w // 2 + segment_length // 2  # current position of the button relative to the image
        self.rect = Rect(pos, (segment_length + self.cursor_w, self.cursor_h))
        self.update()

    def update(self):
        self.image = Surface(self.rect.size)
        line_color, button_color = self.colorset[int(self.clicked)]
        line_y = self.cursor_h // 2
        half_cursor_w = self.cursor_w // 2
        pygame.draw.line(self.image, line_color, (half_cursor_w, line_y), (half_cursor_w + self.segment_length, line_y))
        pygame.draw.rect(self.image, button_color, Rect((self.x_pos - half_cursor_w, 0), self.cursor_size))
        self.dirty = 1

    def move_to(self, x: int) -> float:
        """Return the new val after moving the button to the corresponding location.
        Param x is the absolute coordinate of where the button is asked to move.
        update() should be called afterwards.
        """
        x -= self.rect.left  # relative to the image
        x = max(10, min(self.segment_length + 10, x))
        self.x_pos = x
        x -= 10  # relative to segment
        self.val = x / self.segment_length * (self.max_val - self.min_val)
        return self.val

    def on_click(self, event):
        pos = event.pos
        if not self.clicked and event.button == 1 and self.rect.collidepoint(pos):
            self.clicked = True
            self.broadcast(self.move_to(int(pos[0])))
            self.update()

    def on_mouse_move(self, event):
        pos = event.pos
        if self.clicked:
            self.broadcast(self.move_to(int(pos[0])))
            self.update()

    def on_click_release(self, event):
        if self.clicked and event.button == 1:
            self.clicked = False
            self.update()


class Shadow(pygame.sprite.WeakDirtySprite):
    shadow_fill, transparent_fill = (Color("black"), Color("white"))

    def __init__(self, surface_size: Coordinate, moon: Circle, *groups) -> None:
        super().__init__(*groups)
        self.moon = moon
        self.canvas_size = surface_size
        r = moon.radius
        self.rect = Rect(
            (self.moon.center[0] - r, self.moon.center[1] - r),
            (2 * r, 2 * r),
        )
        self.image = self._make_canvas()

    def _make_canvas(self) -> Surface:
        canvas = Surface(self.canvas_size)
        canvas.fill(self.transparent_fill)
        canvas.set_colorkey(self.transparent_fill)
        return canvas

    def set_circle(self, circle: Circle) -> None:
        canvas = self._make_canvas()
        pygame.draw.circle(canvas, self.shadow_fill, circle.center, circle.radius)
        self.image = canvas.subsurface(self.rect)

    def update(self, crescent_thickness: float) -> None:
        c = crescent_thickness
        if c == 0:
            self.set_circle(Circle(self.moon.center, 0))
        else:
            r = self.moon.radius
            if abs(r - c) < r / 16:
                # Full moon
                self.image = self._make_canvas().subsurface(self.rect)
            else:
                d = (c / 2) * (1 + (r / (r - c)))
                self.set_circle(Circle(
                    (self.moon.center[0] + d, self.moon.center[1]),
                    math.sqrt(d * d + r * r)
                ))
            self.dirty = 1


class Crescent(App):
    def __init__(self):
        self._moon_img = None
        super().__init__()
        shadow = Shadow(self.screen.get_size(), self.moon, self.sprites)
        r = self.moon.radius
        crescent_thickness_control = SliderControl(
            self,
            self.slider_pos(),
            (-r, +r),
            2 * r,
            self.sprites
        )
        crescent_thickness_control.register_listener(shadow.update)

    @property
    def moon_img(self):
        if not self._moon_img:
            self._moon_img = load_image(Path(__file__).parent.joinpath("images").joinpath("fullmoon.jpg"), scale=0.125)
            self._moon_img.set_colorkey(self.moon_img.get_at((0, 0)))
        return self._moon_img

    def on_resize(self, new_size):
        screen = self.make_screen(new_size)
        bkg = self.make_background(new_size)
        screen.blit(bkg, (0, 0))
        pygame.display.flip()
        self.background = bkg
        self.screen = screen

    def make_background(self, size: Coordinate = DEFAULT_DISPLAY_SIZE) -> Surface:
        bkg = Surface(size)
        bkg.fill(Color("black"))
        moon_rect = proportional_blit(self.moon_img, bkg, 0.5, 0.3)
        self.moon = Circle(moon_rect.center, moon_rect.width // 2)
        return bkg

    def slider_pos(self) -> Coordinate:
        r = self.moon.radius
        center_x, center_y = self.moon.center
        return (center_x - r, center_y + 2 * r)

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

    def __init__(self, app: App, pos: Coordinate, min_val: float, max_val: float, segment_length: int, *groups) -> None:
        super().__init__(*groups)
        BroadCaster.__init__(self)
        OnClickListener.__init__(self, app)
        OnClickReleaseListener.__init__(self, app)
        OnMouseMoveListener.__init__(self, app)
        self.clicked = False
        self.min_val = min_val
        self.max_val = max_val
        self.segment_length = segment_length  # length, in pixel, of the segment on which the button will slide
        self.val = (max_val - min_val) / 2 + min_val
        self.x_pos = 10 + segment_length // 2  # current position of the button relative to the image
        self.rect = Rect(pos, (segment_length + 20, 30))
        self.update()

    def update(self):
        self.image = Surface((self.segment_length + 20, 30))
        line_color, button_color = self.colorset[int(self.clicked)]
        pygame.draw.line(self.image, line_color, (10, 15), (10 + self.segment_length, 15))
        pygame.draw.rect(self.image, button_color, Rect((self.x_pos - 10, 0), (20, 30)))
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

    def set_half(self):
        canvas = self._make_canvas()
        r = self.moon.radius
        rect = Rect(
            (self.moon.center[0] - r, self.moon.center[1] - r),
            (r, 2 * r),
        )
        pygame.draw.rect(canvas, self.shadow_fill, rect)

    def receive(self, crescent_thickness: float) -> None:
        c = crescent_thickness
        if c == 0:
            self.set_circle(Circle(self.moon.center, 0))
        else:
            r = self.moon.radius
            if r - c == 0:
                self.set_half()
            else:
                d = (c / 2) * (1 + (r / (r - c)))
                self.set_circle(Circle(
                    (self.moon.center[0] + d, self.moon.center[1]),
                    math.sqrt(d * d + r * r)
                ))
            self.dirty = 1


class Crescent(App):
    def __init__(self):
        super().__init__()
        r = self.moon.radius
        shadow = Shadow(self.screen.get_size(), self.moon, self.sprites)
        crescent_thickness_control = SliderControl(
            self,
            (self.moon.center[0] - r, self.moon.center[1] + 2 * r),
            -self.moon.radius, +self.moon.radius,
            2 * self.moon.radius,
            self.sprites
        )
        crescent_thickness_control.register_listener(shadow)

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
        moon_img = load_image(Path("images").joinpath("fullmoon.jpg"), scale=0.125)
        moon_img.set_colorkey(moon_img.get_at((0, 0)))
        moon_rect = proportional_blit(moon_img, bkg, 0.5, 0.3)
        self.moon = Circle(moon_rect.center, moon_rect.width // 2)
        return bkg


def main():
    pygame.init()
    app = Crescent()
    app.run()
    pygame.quit()


if __name__ == "__main__":
    main()

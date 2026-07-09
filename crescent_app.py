from dataclasses import dataclass
import math
from pathlib import Path

from broadcaster import BroadCaster
import pygame
from pygame import Color, Rect, Surface

from app import DEFAULT_DISPLAY_SIZE, App, Coordinate, load_image, proportional_blit


@dataclass
class Circle:
    center: Coordinate
    radius: float


class SliderControl(pygame.sprite.WeakDirtySprite, BroadCaster):
    colorset = [("darkred", "red"), ("yellow3", "yellow")]

    def __init__(self, pos: Coordinate, min_val: float, max_val: float, segment_length: int, *groups) -> None:
        super().__init__(*groups)
        BroadCaster.__init__(self)
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
        Param x is the absolute coordinate of where the button is asked to move."""
        x -= self.rect.left  # relative to the image
        x = max(10, min(self.segment_length + 10, x))
        self.x_pos = x
        x -= 10  # relative to segment
        self.val = x / self.segment_length * (self.max_val - self.min_val)
        self.update()
        return self.val

    def on_clicked(self, pos: Coordinate):
        if not self.clicked and self.rect.collidepoint(pos):
            self.clicked = True
            self.broadcast(self.move_to(int(pos[0])))

    def on_move(self, pos: Coordinate):
        if self.clicked:
            self.broadcast(self.move_to(int(pos[0])))

    def on_click_released(self):
        self.clicked = False
        self.update()


class Shadow(pygame.sprite.WeakDirtySprite):
    shadow_fill, transparent_fill = (Color("black"), Color("white"))

    def __init__(self, surface_size: Coordinate, *groups) -> None:
        super().__init__(*groups)
        self.canvas_size = surface_size
        self.image = self._make_canvas()
        self.rect = self.image.get_rect()

    def _make_canvas(self) -> Surface:
        canvas = Surface(self.canvas_size)
        canvas.fill(self.transparent_fill)
        canvas.set_colorkey(self.transparent_fill)
        return canvas

    def set_circle(self, circle: Circle) -> None:
        canvas = self._make_canvas()
        self.rect = pygame.draw.circle(canvas, self.shadow_fill, circle.center, circle.radius)
        self.image = canvas.subsurface(self.rect)

    def set_half(self, moon: Circle):
        canvas = self._make_canvas()
        r = moon.radius
        rect = Rect(
            (moon.center[0] - r, moon.center[1] - r),
            (r, 2 * r),
        )
        self.rect = pygame.draw.rect(canvas, self.shadow_fill, rect)

    def update(self, crescent_thickness: float, moon: Circle) -> None:
        c = crescent_thickness
        if c == 0:
            self.set_circle(Circle(moon.center, 0))
        else:
            r = moon.radius
            if r - c == 0:
                self.set_half(moon)
            else:
                d = (c / 2) * (1 + (r / (r - c)))
                self.set_circle(Circle(
                    (moon.center[0] + d, moon.center[1]),
                    math.sqrt(d * d + r * r)
                ))
            self.dirty = 1


class Crescent(App):
    def __init__(self):
        super().__init__()
        r = self.moon.radius
        self.shadow = Shadow(self.screen.get_size(), self.sprites)
        self.crescent_thickness_control = SliderControl(
            (self.moon.center[0] - r, self.moon.center[1] + 2 * r),
            -self.moon.radius, +self.moon.radius,
            2 * self.moon.radius,
            self.sprites
        )
        self.crescent_thickness_control.register_listener(self)
        self.event_handler[pygame.MOUSEBUTTONDOWN] = Crescent.on_mouse_button_down
        self.event_handler[pygame.MOUSEBUTTONUP] = Crescent.on_mouse_button_up
        self.event_handler[pygame.MOUSEMOTION] = Crescent.on_mouse_move
        self.clicking = False

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

    def on_mouse_button_down(self, event):
        if event.button == 1 and not self.clicking:
            self.clicking = True
            self.crescent_thickness_control.on_clicked(event.pos)

    def on_mouse_button_up(self, _):
        self.clicking = False
        self.crescent_thickness_control.on_click_released()

    def on_mouse_move(self, event):
        if self.clicking:
            self.crescent_thickness_control.on_move(event.pos)

    def receive(self, crescent_thickness):
        self.shadow.update(crescent_thickness, self.moon)


def main():
    pygame.init()
    app = Crescent()
    app.run()
    pygame.quit()


if __name__ == "__main__":
    main()

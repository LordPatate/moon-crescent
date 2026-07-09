from dataclasses import dataclass
from pathlib import Path

import pygame

from app import DEFAULT_DISPLAY_SIZE, App, Coordinate, load_image, proportional_blit


@dataclass
class Moon:
    center: Coordinate
    radius: float


class Crescent(App):    
    def on_resize(self, new_size):
        screen = self.make_screen(new_size)
        bkg = self.make_background(new_size)
        screen.blit(bkg, (0, 0))
        pygame.display.flip()
        self.background = bkg
        self.screen = screen

    def make_background(self, size: Coordinate = DEFAULT_DISPLAY_SIZE) -> pygame.Surface:
        bkg = pygame.Surface(size)
        bkg.fill(pygame.Color("black"))
        moon_img = load_image(Path("images").joinpath("fullmoon.jpg"), scale=0.125)
        moon_img.set_colorkey(moon_img.get_at((0, 0)))
        moon_rect = proportional_blit(moon_img, bkg, 0.5, 0.3)
        self.moon = Moon(moon_rect.center, moon_rect.width // 2)
        return bkg


def main():
    pygame.init()
    app = Crescent()
    app.run()
    pygame.quit()


if __name__ == "__main__":
    main()

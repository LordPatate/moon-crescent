import pygame

from app import App


class Crescent(App):
    def __init__(self):
        super().__init__()


def main():
    pygame.init()
    app = Crescent()
    app.run()
    pygame.quit()


if __name__ == "__main__":
    main()

import pygame
from scripts.chunks import Chonky
from scripts.clock import Clock
from scripts.window import Window
from scripts.input import Input

class Editor:
    def __init__(self):
        self.clock = Clock()
        self.window = Window(self)
        self.chunks = Chonky(self)
        self.input = Input(self)

    def update(self):
        self.window.update()
        self.input.update()
        self.clock.tick()

    def run(self):
        self.running = True

        self.clock.start()
        while self.running:
            self.update()

        pygame.quit()

    def stop(self):
        self.running = False

if __name__ == '__main__':
    Editor().run()
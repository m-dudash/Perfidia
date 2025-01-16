import pygame as pg
from start_screen import StartScreen
class Game:
    def __init__(self):
        pg.init()
        self.display_surface = pg.display.set_mode((1280, 720))
        pg.display.set_caption("Perfidia")
        self.clock = pg.time.Clock()
        self.running = True

    def run(self):
        """Основной игровой цикл."""
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
            self.display_surface.fill((30, 30, 30))
            pg.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    start_screen = StartScreen(game.display_surface)

    if start_screen.run():
        game.run()

    pg.quit()

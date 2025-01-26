import pygame as pg
from hell_screen import HellScreen
from level import Level
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
        # Отображение стартового экрана
        start_screen = StartScreen(self.display_surface)
        if not start_screen.run():  # Если игрок закрыл стартовый экран
            self.running = False
            return

        level_number = 1
        while self.running and level_number <= 9:  # Максимум 9 уровней
            # Показ переходного экрана
            hell_screen = HellScreen(self.display_surface, level_number)
            if not hell_screen.run():  # Если игрок закрыл переходный экран
                break



            # Загрузка уровня
            
            level_obj = Level(self.display_surface, level_number)
    
            level_running = True  # Флаг работы уровня
            while level_running:
                # Расчет времени между кадрами
                dt = self.clock.tick(60) / 1000
                if dt > 0.3:
                    dt = 0.3
                # Обработка событий
                '''
                Все исправино. Переходим к следующей цели - враги. На карту я добавил на слое Objects точки enemy типа points где должны спавниться враги. На врагов так же работает притяжение. Они нападают на игрока если он приблизился ближе семи плиток к врагу. Спрайты врагов в assets/enemy/ папки male,female,twisted/ и в каждой tile0.png -
                '''
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                        level_running = False
                        break
                    if event.type == pg.KEYDOWN and event.key == pg.K_TAB:  # Переход на следующий уровень
                        level_number += 1
                        level_running = False
                        break
                

                teleport_triggered = level_obj.update(dt)
                if teleport_triggered:
                    level_number += 1
                    level_running = False
                    # Выходим из while, загружаем след. уровень
                    break
                
                
                # Обновление и отрисовка уровня
                self.display_surface.fill((0, 0, 0))  # Очистка экрана
                level_obj.draw()
                pg.display.update()

                # Проверка завершения игры
                if level_number > 9:
                    self.running = False
                    level_running = False
                    break

        pg.quit()


if __name__ == "__main__":
    game = Game()
    game.run()

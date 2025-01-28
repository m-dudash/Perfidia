import pygame as pg
from hell_screen import HellScreen
from level import Level
from start_screen import StartScreen


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pg.mixer.music.set_volume(0.5)
        self.display_surface = pg.display.set_mode((1280, 720))
        pg.display.set_caption("Perfidia")
        self.clock = pg.time.Clock()
        self.running = True

    def show_game_over_screen(self):
        """Отображение экрана Game Over и ожидание выхода."""
        game_over_image = pg.image.load("assets/game_over.png").convert_alpha()
        game_over_rect = game_over_image.get_rect(center=(1280 // 2, 720 // 2))
        
        self.display_surface.fill((0, 0, 0))
        self.display_surface.blit(game_over_image, game_over_rect)
        pg.display.update()

        # Ожидание закрытия игры
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:  # Закрытие игры
                    waiting = False
                    self.running = False


    def run(self):
        """Основной игровой цикл."""
        start_screen = StartScreen(self.display_surface)
        if not start_screen.run():  # Если игрок закрыл стартовый экран
            self.running = False
            return

        level_number = 1
        while self.running and level_number <= 9:  # Максимум 9 уровней
            # Показ переходного экрана
            hell_screen = HellScreen(self.display_surface, level_number)
            if not hell_screen.run():
                break

            # Загрузка уровня
            level_obj = Level(self.display_surface, level_number)
            level_running = True
            try:
                pg.mixer.music.load(f"assets/audio/music/{level_obj.level_type}.wav")
                pg.mixer.music.play(-1)  # -1 означает бесконечное повторение
                print("Level music loaded and playing.")
            except pg.error as e:
                print(f"Error with: {level_obj.level_type}.wav: {e}")

            while level_running:
                dt = self.clock.tick(60) / 1000  # Ограничение FPS и расчёт dt
                if dt > 0.3:
                    dt = 0.3

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.mixer.music.stop()
                        self.running = False
                        level_running = False
                        break
                    if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                        print("Переключение на следующий уровень (отладка)")
                        level_number += 1
                        level_running = False
                        break

                # Обновление уровня
                result = level_obj.update(dt)

                if result == "next_level":
                    level_number += 1
                    level_running = False
                elif result == "game_over":
                    pg.mixer.music.load(f"assets\\audio\music\Death.wav")
                    pg.mixer.music.play(0) 
                    self.show_game_over_screen()
                    self.running = False
                    level_running = False

                # Отрисовка уровня
                self.display_surface.fill((0, 0, 0))
                level_obj.draw()
                pg.display.update()

            if level_number > 9:  # Проверка завершения всех уровней
                self.running = False

        pg.quit()



if __name__ == "__main__":
    game = Game()
    game.run()

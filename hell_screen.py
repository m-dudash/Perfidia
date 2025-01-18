import pygame as pg

class HellScreen:
    def __init__(self, display_surface, level_number):
        self.display_surface = display_surface
        self.level_number = level_number
        self.clock = pg.time.Clock()
        self.running = True
        self.image = pg.image.load(f"assets/hells/hell_{self.level_number}.png").convert_alpha()
        self.fade_in = True
        self.alpha = 0
        self.fade_speed = 6  # Скорость анимации

    def run(self):
        """Анимация переходного экрана."""
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    return False
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:  #пропуск анимации
                    self.running = False
                    return True

            # Логика анимации
            if self.fade_in:
                self.alpha += self.fade_speed
                if self.alpha >= 255:
                    self.alpha = 255
                    self.fade_in = False
                    pg.time.delay(1000)
            else:
                self.alpha -= self.fade_speed
                if self.alpha <= 0:
                    self.alpha = 0
                    self.running = False  # Завершаем экран

            # Применяем альфа-канал
            self.image.set_alpha(self.alpha)
            self.display_surface.fill((0, 0, 0))  # Очищаем экран
            self.display_surface.blit(self.image, (0, 0))  # Отображаем изображение
            pg.display.update()
            self.clock.tick(60)

        return True

import pygame as pg
import sys

class Cutscene:
    def __init__(self, display_surface, death_frames):
        """
        Инициализация кат-сцены.

        :param display_surface: Поверхность для отрисовки кат-сцены.
        :param death_frames: Список кадров анимации смерти игрока.
        :param text: Текст, отображаемый после или во время анимации.
        :param font_path: Путь к файлу шрифта (опционально).
        :param font_size: Размер шрифта.
        :param typing_speed: Скорость печати текста (символов в секунду).
        """
        self.display_surface = display_surface
        self.death_frames = death_frames
        self.text = "Your soul left your body at the Devil's mere sight."
        self.font = pg.font.Font("assets\\alagard.ttf", 46)
        self.current_text = ""  # Текущий отображаемый текст
        self.text_index = 0  # Индекс текущего символа
        self.typing_speed = 19  # Символов в секунду
        self.typing_interval = 1 / self.typing_speed  # Интервал между символами
        self.time_since_last_char = 0  # Время с последнего добавленного символа

        # Анимация
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_cooldown = 0.16  # Секунд между кадрами

        # Управление временем
        self.clock = pg.time.Clock()

        # Состояние кат-сцены
        self.running = True

        # Увеличение размера игрока
        self.scale_factor = 6  # Коэффициент увеличения

    def run(self):
        pg.mixer.music.load(f"assets\\audio\music\Final.wav")
        pg.mixer.music.play(0) 
        while self.running:
            dt = self.clock.tick(60) / 1000  # Получаем dt в секундах
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

            # Обновление анимации
            self.animation_timer += dt
            if self.animation_timer >= self.animation_cooldown:
                self.animation_timer = 0
                if self.frame_index < len(self.death_frames) - 1:
                    self.frame_index += 1
                else:
                    self.frame_index = len(self.death_frames) - 1  # Остановиться на последнем кадре

            # Обновление текста (эффект печатающейся строки)
            if self.text_index < len(self.text):
                self.time_since_last_char += dt
                if self.time_since_last_char >= self.typing_interval:
                    self.time_since_last_char = 0
                    self.current_text += self.text[self.text_index]
                    self.text_index += 1

            # Проверка завершения кат-сцены
            # Завершить, когда анимация и текст полностью отображены
            if self.text_index == len(self.text):
                pg.time.delay(5000)  # Небольшая задержка перед выходом
                self.running = False

            # Отрисовка
            self.display_surface.fill((32, 1, 1))

            # Отрисовка текущего кадра анимации смерти, увеличенного
            current_frame = self.death_frames[self.frame_index]
            scaled_frame = pg.transform.scale(current_frame, (int(current_frame.get_width() * self.scale_factor),
                                                             int(current_frame.get_height() * self.scale_factor)))
            frame_rect = scaled_frame.get_rect(center=(self.display_surface.get_width() // 2 + 100, self.display_surface.get_height() // 2 - 170))
            self.display_surface.blit(scaled_frame, frame_rect)

            # Отрисовка текста с эффектом печати
            text_surface = self.font.render(self.current_text, True, (255, 255, 255))  # Белый цвет текста
            text_rect = text_surface.get_rect(center=(self.display_surface.get_width() // 2, self.display_surface.get_height() // 2 + 200))
            self.display_surface.blit(text_surface, text_rect)

            pg.display.update()

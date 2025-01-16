import pygame as pg

class StartScreen:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.clock = pg.time.Clock()
        self.running = True
        self.gif_frames = self.load_gif_frames("assets/perfidia_screen")
        self.frame_index = 0
        self.frame_delay = 70  # миллисекунды между кадрами
        self.last_frame_time = pg.time.get_ticks()

    def load_gif_frames(self, path):
        """Загрузка кадров GIF как отдельных изображений."""
        frames = []
        for i in range(1, 6): 
            frame_path = f"{path}/frame_{i:01}.png"
            frame = pg.image.load(frame_path).convert_alpha()
            frames.append(frame)
        return frames

    def run(self):
        """Цикл стартового экрана."""
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    return False
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.running = False
                    return True

            # Обновление кадра GIF
            current_time = pg.time.get_ticks()
            if current_time - self.last_frame_time >= self.frame_delay:
                self.frame_index = (self.frame_index + 1) % len(self.gif_frames)
                self.last_frame_time = current_time

            # Отрисовка текущего кадра
            self.display_surface.fill((0, 0, 0))
            self.display_surface.blit(self.gif_frames[self.frame_index], (0, 0))
            pg.display.update()
            self.clock.tick(60)

        return False

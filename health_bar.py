import pygame as pg

class HealthBar:
    def __init__(self, owner, offset_y=-10):
        """
        Класс HealthBar привязан к объекту (owner), например, игроку или врагу.

        :param owner: объект, к которому привязан хиллбар (например, Player).
        :param offset_y: смещение по вертикали относительно объекта.
        """
        self.owner = owner
        self.offset_y = offset_y  # Смещение по вертикали
        self.scale = (70,20)  # Размер (ширина, высота)
        self.health_bar_images = {
            i: pg.image.load(f'assets/health_bar/bar{i}.png').convert_alpha()
            for i in range(0, 101, 10)
        }
        self.image = self.health_bar_images[100]  # Начальное значение 100 HP

    def update(self):
        """Обновляет изображение хиллбара в зависимости от здоровья владельца."""
        health_percent = max(0, min(100, self.owner.health))  # Ограничение от 0 до 100
        health_tier = (health_percent // 10) * 10  # Округление до ближайшего десятка
        self.image = self.health_bar_images[health_tier]

    def draw(self, surface, camera_x, vertical_offset):
        """
        Отрисовывает хиллбар на поверхности.

        :param surface: поверхность для рисования.
        :param camera_x: позиция камеры по X.
        :param vertical_offset: вертикальное смещение уровня.
        """
        health_bar_x = self.owner.rect.centerx - self.image.get_width() // 2 - camera_x
        health_bar_y = self.owner.rect.top + self.offset_y + vertical_offset
        surface.blit(self.image, (health_bar_x, health_bar_y))

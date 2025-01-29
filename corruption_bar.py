import pygame as pg

class CorruptionBar:
    def __init__(self, owner, corruption_rate, offset_y=-30):
        """
        Класс CorruptionBar привязан к объекту (owner), например, игроку.

        :param owner: объект, к которому привязан CorruptionBar (например, Player).
        :param corruption_rate: количество единиц коррупции, добавляемых каждую секунду.
        :param offset_y: смещение по вертикали относительно объекта.
        """
        self.owner = owner
        self.offset_y = offset_y  # Смещение по вертикали
        self.corruption_rate = corruption_rate  # Единиц коррупции в секунду
        self.corruption = 0  # Текущий уровень коррупции

        # Загрузка изображений CorruptionBar
        self.corruption_bar_images = {}
        for i in range(0, 101, 5):
            image_path = f'assets/corruption_bar/bar{i}.png'

            original_image = pg.image.load(image_path).convert_alpha()

            original_width, original_height = original_image.get_size()
            new_width = int(original_width * 0.7)
            new_height = int(original_height * 0.8)
            new_image = pg.transform.scale(original_image, (new_width, new_height))
            self.corruption_bar_images[i] = new_image
        
        self.image = self.corruption_bar_images[0]  # Начальное значение 0

        # Таймер для отслеживания времени
        self.timer = 0  # Время в секундах

    def update(self, dt):
        """
        Обновляет уровень коррупции и изображение бара.
        :param dt: время с последнего кадра в секундах.
        """
        self.timer += dt
        if self.timer >= 1.0:
            # Увеличиваем коррупцию на corruption_rate каждую секунду
            self.corruption += self.corruption_rate
            self.timer -= 1.0  # Сбрасываем таймер на 1 секунду

            # Ограничиваем значение до 100
            if self.corruption >= 100:
                self.corruption = 100
                # Игрок умирает, получив урон равный его здоровью
                self.owner.get_hit(self.owner.health)

            # Обновляем изображение бара
            corruption_tier = (self.corruption // 5) * 5  # Округление до ближайших 5
            self.image = self.corruption_bar_images[int(corruption_tier)]

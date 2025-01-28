import pygame as pg

class Fire(pg.sprite.Sprite):
    """
    Класс для анимации огня.
    """
    def __init__(self, pos, fire_type, group, scale=1.5, animation_speed=0.1):
        """
        :param pos: (x, y) координаты точки размещения огня
        :param fire_type: тип огня (d_fire, r_fire, b_fire)
        :param group: группа спрайтов, куда будет добавлен огонь
        :param scale: коэффициент увеличения размера огня
        :param animation_speed: скорость анимации (секунды между кадрами)
        """
        super().__init__(group)
        
        # Загрузка кадров в зависимости от типа огня
        self.frames = [
            pg.image.load(f"assets/fire/{fire_type}/tile{i}.png").convert_alpha()
            for i in range(6)  # tile0.png ... tile5.png
        ]

        # Масштабируем все кадры
        self.frames = [pg.transform.scale(frame, 
                    (int(frame.get_width() * scale), int(frame.get_height() * scale)))
                       for frame in self.frames]
        
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_cooldown = animation_speed  # Секунды между кадрами

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)  # Привязка midbottom к точке
        
        # Создаём уменьшенный damage_rect для нанесения урона   
        damage_width = int(self.rect.width * 0.5)
        damage_height = int(self.rect.height * 0.09)
        self.damage_rect = pg.Rect(0, 0, damage_width, damage_height)
        self.damage_rect.center = self.rect.center  # Центрируем damage_rect

    def animate(self, dt):
        """
        Анимация огня.
        """
        self.animation_timer += dt
        if self.animation_timer >= self.animation_cooldown:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def update(self, dt):
        """
        Обновление огня.
        """
        self.animate(dt)

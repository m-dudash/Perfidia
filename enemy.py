# enemy.py

import pygame as pg
import random

TILE_SIZE = 32  # если нужно

class Enemy(pg.sprite.Sprite):
    """
    Класс врага:
      - Случайно выбирает тип (male/female/twisted),
      - Загрузка анимаций (stand, walk, hit, death),
      - Гравитация, коллизия с тайлами,
    """
    def __init__(self, pos, collision_tiles):
        super().__init__()
        
        # 1) Выбираем тип врага
        self.enemy_type = random.choice(["male","female","twisted"])
        
        # 2) Загружаем анимации
        # Папки: assets/enemy/male/stand/tile0..tile4, etc.
        self.stand_frames = self.load_frames(f"assets/enemy/{self.enemy_type}/stand", 5)
        self.walk_frames = self.load_frames(f"assets/enemy/{self.enemy_type}/walk", 8)
        self.hit_frames  = self.load_frames(f"assets/enemy/{self.enemy_type}/hit", 5)
        self.death_frames= self.load_frames(f"assets/enemy/{self.enemy_type}/death", 8)

        # Начальное состояние
        self.state = 'stand'  # 'stand' / 'walk' / 'hit' / 'death'
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_cooldown = 0.08

        # Текущее изображение и прямоугольник
        self.image = self.stand_frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # Коллизии - хитбокс (как у игрока)
        self.hitbox = pg.Rect(self.rect.x, self.rect.y, 24, 48)
        self.hitbox.midbottom = self.rect.midbottom

        # Физика
        self.velocity = pg.Vector2(0,0)
        self.walk_speed = 120   
        self.gravity = 800
        self.on_ground = False
        self.facing_right = True

        # Коллизия с тайлами (Base)
        self.collision_tiles = collision_tiles

        # Дистанция агро
        self.aggro_range = 224  # 7 тайлов * 32

    def load_frames(self, folder, count):
        """
        Загрузить count кадров: tile0.png ... tile{count-1}.png
        """
        frames = []
        for i in range(count):
            # Например: assets/enemy/male/stand/tile0.png
            path = f"{folder}/tile{i}.png"
            surf = pg.image.load(path).convert_alpha()
            frames.append(surf)
        return frames

    def update(self, dt, player):
        """
        Главная логика врага:
         1) Проверка дистанции до игрока, выбор состояния (stand/walk)
         2) Установка velocity.x в сторону игрока (если walk)
         3) Применение гравитации
         4) Движение, проверка коллизий
         5) Анимация
        """
        # 1) Проверяем дистанцию
        dist = abs(player.rect.centerx - self.rect.centerx)  # по X
        # или 2D dist = player.rect.center - self.rect.center => length
        # но пусть упрощённо: если по X < aggro => walk
        if dist < self.aggro_range:
            self.state = 'walk'
        else:
            self.state = 'stand'

        # 2) Логика walk/stand
        if self.state == 'walk':
            # Идём к игроку
            if player.rect.centerx > self.rect.centerx:
                # игрок справа
                self.facing_right = True
                self.velocity.x = self.walk_speed
            else:
                # игрок слева
                self.facing_right = False
                self.velocity.x = -self.walk_speed
        else:
            self.velocity.x = 0

        # Применяем гравитацию (если не on_ground)
        if not self.on_ground:
            self.velocity.y += self.gravity * dt

        # Горизонталь
        old_x = self.hitbox.x
        self.hitbox.x += int(self.velocity.x * dt)
        if self.check_collision():
            self.hitbox.x = old_x

        # Вертикаль
        old_y = self.hitbox.y
        self.hitbox.y += int(self.velocity.y * dt)
        self.on_ground = False
        if self.check_collision():
            self.hitbox.y = old_y
            if self.velocity.y > 0:
                self.on_ground = True
            self.velocity.y = 0

        # Синхронизируем rect
        self.rect.midbottom = self.hitbox.midbottom

        # Анимация
        self.animate(dt)

    def animate(self, dt):
        self.animation_timer += dt

        # Выбираем список кадров
        if self.state == 'stand':
            frames = self.stand_frames
        elif self.state == 'walk':
            frames = self.walk_frames
        elif self.state == 'hit':
            frames = self.hit_frames
        elif self.state == 'death':
            frames = self.death_frames
        else:
            frames = self.stand_frames  # Fallback на случай ошибки


        # Переключение кадров
        if self.animation_timer >= self.animation_cooldown:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)

        # Устанавливаем изображение
        if 0 <= self.frame_index < len(frames):  # Добавим явную проверку границ
            self.image = frames[self.frame_index]
        else:
            print(f"Error: Invalid frame_index {self.frame_index} for state {self.state} in type {self.enemy_type}")
            self.frame_index = 0
            self.image = frames[self.frame_index]

        # Флип
        if self.facing_right:
            self.image = pg.transform.flip(self.image, True, False)

    def check_collision(self):
        """
        Возвращаем True, если hitbox пересекает любой tile.rect из self.collision_tiles.
        """
        for tile in self.collision_tiles:
            if tile.rect.colliderect(self.hitbox):
                return True
        return False

# enemy.py

import time
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
        
        
        # Загрузка звуковых эффектов
        try:
            self.death1 = pg.mixer.Sound(f"assets\\audio\sfx\enemy\die\death1.wav")
            self.death2 = pg.mixer.Sound(f"assets\\audio\sfx\enemy\die\death2.wav")
            self.hit1 = pg.mixer.Sound(f"assets\\audio\sfx\enemy\hit\hit1.wav")
            self.hit2 = pg.mixer.Sound(f"assets\\audio\sfx\enemy\hit\hit2.wav")
            print("Enemy sound effects loaded successfully.")
        except pg.error as e:
            print(f"Error: {e}")


        self.death1.set_volume(0.4)
        self.death2.set_volume(0.4)
        self.hit1.set_volume(0.4)
        self.hit2.set_volume(0.4)
        # Начальное состояние
        self.state = 'stand'  # 'stand' / 'walk' / 'hit' / 'death'
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_cooldown = 0.08
        
        self.health = random.choice([5,12])

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

        # Дистанция агро и атаки
        self.aggro_range = 224  # 7 тайлов * 32
        self.attack_range = 25  # Дистанция для атаки
        self.attack_damage = 8
        self.attack_cooldown = 1.5  # Враги атакуют каждые 1.5 сек
        self.last_attack_time = time.time() - self.attack_cooldown
        self.is_attacking = False  # Флаг текущей атаки
        
        
        

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
        1) Проверка дистанции до игрока, выбор состояния (stand/walk/attack)
        2) Установка velocity.x в сторону игрока (если walk)
        3) Применение гравитации
        4) Движение, проверка коллизий
        5) Анимация
        """
        
        if self.state == 'death':
            # Только обновляем анимацию смерти, чтобы проиграть кадры
            self.animate_death(dt)
            return

        if self.is_attacking:
            # Если враг в процессе атаки, обновляем анимацию атаки
            self.animate_attack(dt, player)
            return

        # 1) Проверяем дистанцию (по обоим осям)
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = (dx**2 + dy**2) ** 0.5


        if dist < self.attack_range:
            if (time.time() - self.last_attack_time) >= self.attack_cooldown  and player.state != 'death':
                self.start_attack(player)
            else:
                self.state = 'stand'
        elif dist < self.aggro_range:
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

        # 3) Горизонталь
        old_x = self.hitbox.x
        self.hitbox.x += int(self.velocity.x * dt)
        # Проверяем столкновение с тайлами и игроком
        if self.check_collision([player.hitbox]):
            self.hitbox.x = old_x

        # 4) Вертикаль
        old_y = self.hitbox.y
        self.hitbox.y += int(self.velocity.y * dt)
        self.on_ground = False
        if self.check_collision([player.hitbox]):
            self.hitbox.y = old_y
            if self.velocity.y > 0:
                self.on_ground = True
            self.velocity.y = 0

        # 5) Синхронизируем rect
        self.rect.midbottom = self.hitbox.midbottom

        # 6) Анимация
        self.animate(dt)


        
    
    
    def start_attack(self, player):
        """Запуск атаки на игрока."""
        self.is_attacking = True
        sound = random.choice((self.hit1, self.hit2))
        sound.play()
        self.state = 'attack'
        self.frame_index = 0
        self.animation_timer = 0
        self.last_attack_time = time.time()
        # Остановить движение во время атаки
        self.velocity.x = 0
    def animate_attack(self, dt, player):
        """Анимация атаки врага."""
        self.animation_timer += dt
        if self.animation_timer >= self.animation_cooldown:
            self.animation_timer = 0
            self.frame_index += 1


            if self.frame_index >= len(self.hit_frames):
                # Завершаем атаку
                self.is_attacking = False
                self.state = 'stand'
                self.frame_index = 0
            else:
                # На определённом кадре атака наносит урон
                if self.frame_index == 2:
                    # Определяем область атаки
                    attack_width = 50  # Ширина области атаки (настраивайте по необходимости)
                    attack_height = self.hitbox.height  # Высота совпадает с хитбоксом

                    # Создаём attack_rect вокруг врага
                    # Например, прямоугольник над врагом
                    attack_rect = pg.Rect(
                        self.hitbox.x - (attack_width // 2),  # Смещение по X
                        self.hitbox.y,                      # Смещение по Y
                        attack_width, 
                        attack_height
                    )

                    # Визуализация attack_rect для отладки (можно удалить после проверки)
                   
                    # Проверяем пересечение с игроком
                    if attack_rect.colliderect(player.hitbox):
                        player.get_hit(self.attack_damage)
                        print(f"Enemy at {self.rect.topleft} dealt {self.attack_damage} damage to Player.")

        # Обновляем изображение только если атака все еще продолжается
        if self.is_attacking and 0 <= self.frame_index < len(self.hit_frames):
            self.image = self.hit_frames[self.frame_index]
            # Флипируем изображение только тогда, когда враг смотрит вправо
            if self.facing_right:
                self.image = pg.transform.flip(self.image, True, False)

        

            
        
    def get_hit(self, damage):
        """Вызов при попадании удара игрока."""
        if self.state == 'death':
            return  # уже умирает, не реагируем
        
        self.health -= damage
        print(f"ENEMY HP {self.health}")
        if self.health <= 0:
            sound = random.choice((self.death1, self.death2))
            sound.play()
            # Запускаем анимацию смерти
            self.state = 'death'
            self.frame_index = 0
            self.animation_timer = 0
    def animate_death(self, dt):
           # 1) Проверяем сразу: если уже вышли за кадры — убираем врага
        if self.frame_index >= len(self.death_frames):
            self.kill()
            return

        self.animation_timer += dt
        if self.animation_timer >= self.animation_cooldown:
            self.animation_timer = 0
            self.frame_index += 1  # переходим к следующему кадру
            # Проверяем, не вышли ли за предел
            if self.frame_index >= len(self.death_frames):
                # Враг уже доиграл анимацию смерти
                self.kill()  # убираем спрайт из группы
                return

        # Теперь frame_index гарантированно в диапазоне
        self.image = self.death_frames[self.frame_index]
        if self.facing_right:
            self.image = pg.transform.flip(self.image, True, False)

        
    def animate(self, dt):
        if self.state in ['hit', 'death']:
            return
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
    def check_collision(self, additional_rects=[]):
        """
        Возвращает True, если hitbox пересекается с любым tile.rect из self.collision_tiles
        или с любым rect из additional_rects.
        """
        for tile in self.collision_tiles:
            if tile.rect.colliderect(self.hitbox):
                return True
        for rect in additional_rects:
            if rect.colliderect(self.hitbox):
                return True
        return False



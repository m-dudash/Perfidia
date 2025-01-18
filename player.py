import pygame as pg

class Player(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # 1) ЗАГРУЖАЕМ КАДРЫ (без обрезки),
        #    предполагаем, что они смотрят влево по умолчанию:
        self.idle_frames = [pg.image.load(f'assets/player/stand/tile{i}.png').convert_alpha() for i in range(5)]
        self.walk_frames = [pg.image.load(f'assets/player/walk/tile{i}.png').convert_alpha() for i in range(8)]
        self.jump_frames = [pg.image.load(f'assets/player/jump/tile{i}.png').convert_alpha() for i in range(4)]
        self.fall_frames = [pg.image.load(f'assets/player/fall/tile{i}.png').convert_alpha() for i in range(4)]
        self.run_frames = [pg.image.load(f'assets/player/run/tile{i}.png').convert_alpha() for i in range(8)]
        
        # Начальный кадр
        self.frame_index = 0
        self.image = self.idle_frames[self.frame_index]
        
        # Основной rect (для рисования)
        self.rect = self.image.get_rect(topleft=pos)

        # HITBOX — для коллизий (меньше, чем спрайт). 
        # Подберите размеры под «тело» персонажа.
        self.hitbox = pg.Rect(self.rect.x, self.rect.y, 24, 48)
        self.hitbox.midbottom = self.rect.midbottom

        # Физика
        self.velocity = pg.Vector2(0, 0)
        self.walk_speed = 100      # обычная скорость
        self.run_speed = 180       # скорость при беге
        self.jump_speed = -270
        self.gravity = 800
        self.on_ground = False
        # Исходные спрайты (налево). Если True => flip вправо.
        self.facing_right = True

        # Анимация
        self.state = 'idle'   # idle / walk / jump / fall
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_cooldown = 0.12

        # Ограничим dt
        self.max_dt = 0.03

    def handle_input(self, dt):
        keys = pg.key.get_pressed()

        self.running = (keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT])

        if keys[pg.K_a]:
            speed_x = self.run_speed if self.running else self.walk_speed
            self.velocity.x = -speed_x
            self.facing_right = False

        elif keys[pg.K_d]:
            speed_x = self.run_speed if self.running else self.walk_speed
            self.velocity.x = speed_x
            self.facing_right = True

        else:
            self.velocity.x = 0


        # Прыжок
        if keys[pg.K_SPACE] and self.on_ground:
            self.velocity.y = self.jump_speed
            self.on_ground = False

        # Гравитация
        if not self.on_ground:
            self.velocity.y += self.gravity * dt

    def get_state(self):
        # Если стоим на земле
        if self.on_ground:
            if abs(self.velocity.x) > 0:
                # Проверяем, бежим ли
                if self.running:
                    return 'run'  # <-- Новое состояние
                else:
                    return 'walk'
            else:
                return 'idle'
        else:
            # В воздухе
            if self.velocity.y < -1:
                return 'jump'
            else:
                return 'fall'


    def animate(self, dt):
        self.animation_timer += dt
        new_state = self.get_state()

        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.animation_timer = 0

        # Выбираем кадры
        if self.state == 'idle':
            frames = self.idle_frames
        elif self.state == 'walk':
            frames = self.walk_frames
        elif self.state == 'run':
            frames = self.run_frames
        elif self.state == 'jump':
            frames = self.jump_frames
        else:  # fall
            frames = self.fall_frames

        # Переключаем кадры
        if self.animation_timer >= self.animation_cooldown:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)

        # Берём текущий кадр
        self.image = frames[self.frame_index]

        # Если кадры смотрят влево, а facing_right=True => flip
        if self.facing_right:
            flipped = pg.transform.flip(self.image, True, False)
            self.image = flipped

    def check_collision(self, level):   #True / False
        return level.check_collision(self.hitbox) 

    def horizontal_movement(self, dt, level):
        dx = self.velocity.x * dt
        old_x = self.hitbox.x
        self.hitbox.x += int(dx)

        if self.check_collision(level):
            self.hitbox.x = old_x

    def vertical_movement(self, dt, level):
        dy = self.velocity.y * dt
        old_y = self.hitbox.y
        self.hitbox.y += int(dy)

        if self.check_collision(level):
            # Откат
            self.hitbox.y = old_y
            if self.velocity.y > 0:
                self.on_ground = True
            self.velocity.y = 0
        else:
            self.on_ground = False

    def post_ground_check(self, level):
        """
        Дополнительная проверка: если мы «впритык» над тайлом, 
        но velocity.y≈0, считаем, что мы на земле.
        
        Смысл: опускаем hitbox на 1 px, проверяем коллизию:
          - Если есть коллизия => on_ground=True, поднимаем обратно, velocity.y=0.
          - Иначе => on_ground= False.
        """
        if self.velocity.y >= 0:
            # Попробуем опустить hitbox на 1 пиксель
            self.hitbox.y += 1
            if self.check_collision(level):
                self.on_ground = True
                self.velocity.y = 0
            else:
                self.on_ground = False
            # Возвращаем назад
            self.hitbox.y -= 1

    def update(self, dt, level):
        # 1) Ограничим dt
        if dt > self.max_dt:
            dt = self.max_dt

        # 2) Инпут
        self.handle_input(dt)

        # 3) Движение по X -> коллизия
        self.horizontal_movement(dt, level)

        # 4) Движение по Y -> коллизия
        self.vertical_movement(dt, level)

        # 5) post_ground_check: проверяем, не висим ли «впритык» над тайлом
        self.post_ground_check(level)

        # 6) Синхронизируем rect с hitbox
        self.rect.midbottom = self.hitbox.midbottom

        # 7) Анимация
        self.animate(dt)

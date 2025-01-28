import pygame as pg
from health_bar import HealthBar
import random

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
        self.hit_frames  = [pg.image.load(f'assets/player/hit/tile{i}.png').convert_alpha() for i in range(6)]
        self.death_frames = [pg.image.load(f'assets/player/death/tile{i}.png').convert_alpha() for i in range(10)]
        
        # Загрузка звуков
        try:
            self.sword1 = pg.mixer.Sound("assets\\audio\sfx\player\sword\Sword_Attack_1.wav")
            self.sword2 = pg.mixer.Sound("assets\\audio\sfx\player\sword\Sword_Attack_2.wav")
            self.sword3 = pg.mixer.Sound("assets\\audio\sfx\player\sword\Sword_Attack_3.wav")
            self.burn_sound = pg.mixer.Sound("assets\\audio\sfx\player\\burn.wav")
            self.fall_sound = pg.mixer.Sound("assets\\audio\sfx\player\\fall.wav")
            self.jump_sound = pg.mixer.Sound("assets\\audio\sfx\player\jump.wav")
            print("Player sound effects loaded successfully.")
        except pg.error as e:
            print(f"Error: {e}")
            
        
        self.fall_sound.set_volume(0.3)
        self.sword1.set_volume(0.5)
        self.sword2.set_volume(0.5)
        self.sword3.set_volume(0.5)
        self.burn_sound.set_volume(0.4)
        
        # Начальный кадр
        self.frame_index = 0
        self.image = self.idle_frames[self.frame_index]
        
        # Основной rect (для рисования)
        self.rect = self.image.get_rect(topleft=pos)

        # HITBOX — для коллизий (меньше, чем спрайт). 
        self.hitbox = pg.Rect(self.rect.x, self.rect.y, 24, 48)
        self.hitbox.midbottom = self.rect.midbottom

        # Физика
        self.velocity = pg.Vector2(0, 0)
        self.walk_speed = 130      # обычная скорость
        self.run_speed = 200       # скорость при беге
        self.jump_speed = -350
        self.gravity = 1000
        self.on_ground = False
        # Исходные спрайты (налево). Если True => flip вправо.
        self.facing_right = True
        
        self.health = 100
        self.damage_done = False  # Флаг для предотвращения многократного нанесения урона
        self.is_dead = False
        # Анимация
        self.state = 'idle'   # idle / walk / jump / fall
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_cooldown = 0.09
        self.attack_frame = 0
        self.is_attacking = False
        # Ограничим dt
        self.max_dt = 0.03
        
        self.health_bar = HealthBar(self)
        
        self.last_fire_damage_time = 0
        
    def handle_fire_damage(self, fire_sprites):
        """
        Проверяет столкновение с огнём и наносит урон каждые 200 мс.
        """
        current_time = pg.time.get_ticks()

        # Проверяем столкновение с любым огнём
        if any(fire.damage_rect.colliderect(self.hitbox) for fire in fire_sprites):
            # Проверяем, прошло ли 200 мс с последнего урона
            if current_time - self.last_fire_damage_time >= 1000:
                self.get_hit(3)  # Наносим 1 урон
                self.burn_sound.play()
                self.last_fire_damage_time = current_time  # Обновляем таймер
    
    
    def get_hit(self, damage):
        """Обработка получения урона игроком."""
        if self.is_dead:
            return
        self.health -= damage
        print(f"PLAYER HP: {self.health}")
 
        if self.health <= 0:
            self.is_dead = True
            self.state = "death"
            self.velocity.x = 0
            self.frame_index = 0
            self.animation_timer = 0
            self.fall_sound.play()
            if not hasattr(self, "death_time"):  # Устанавливаем только один раз
                self.death_time = pg.time.get_ticks()

    def handle_input(self, dt):
        if self.is_dead:
            return  # Не обрабатываем ввод, если игрок мертв
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
            self.jump_sound.play()
            self.velocity.y = self.jump_speed
            self.on_ground = False

        # Гравитация
        if not self.on_ground:
            self.velocity.y += self.gravity * dt
            
        # Удар (ЛКМ)
        mouse_buttons = pg.mouse.get_pressed(num_buttons=3)
        left_click = mouse_buttons[0]  # 0 - LMB, 1 - RMB, 2 - MMB
        if left_click and not self.is_attacking:
            self.start_attack()

    def start_attack(self):
        """Переход в состояние 'hit'. Сбрасываем кадры анимации."""
        self.is_attacking = True
        self.state = 'hit'
        self.frame_index = 0
        self.animation_timer = 0
        sound = random.choice((self.sword1, self.sword2, self.sword3))
        sound.play()

        
    def get_state(self):
        
        if self.is_attacking:
            return 'hit'
        
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

        if self.state != "death" and new_state != self.state:
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
        elif self.state == 'hit':
            frames = self.hit_frames
        elif self.state == 'death':
            frames = self.death_frames
        else:  # fall
            frames = self.fall_frames

        # Переключаем кадры
        if self.animation_timer >= self.animation_cooldown:
            self.animation_timer = 0
            self.frame_index += 1

            # Если анимация смерти завершилась, остаёмся на последнем кадре
            if self.state == 'death' and self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1

            # Если анимация удара завершилась, сбрасываем флаг `is_attacking`
            elif self.state == 'hit' and self.frame_index >= len(frames):
                self.is_attacking = False  # Завершаем атаку
                self.state = 'idle'  # Переход в состояние "idle"
                self.frame_index = 0

            # Зацикливание для других состояний
            elif self.frame_index >= len(frames):
                self.frame_index = 0

        # Берём текущий кадр
        self.image = frames[self.frame_index]

        # Если кадры смотрят влево, а facing_right=True => flip
        if self.facing_right:
            flipped = pg.transform.flip(self.image, True, False)
            self.image = flipped


       
         
    def do_attack_damage(self, level):
        """
        Наносит урон врагам, если игрок атакует.
        """
        if self.state == 'hit' and self.frame_index == 4:
            # Увеличиваем радиус удара игрока
            attack_width = 25  # Увеличенный радиус удара (ширина)
            attack_height = self.hitbox.height  # Высота совпадает с высотой хитбокса игрока

            if self.facing_right:
                # Удар направлен вправо
                attack_rect = pg.Rect(
                    self.hitbox.right, 
                    self.hitbox.top, 
                    attack_width, 
                    attack_height
                )
            else:
                # Удар направлен влево
                attack_rect = pg.Rect(
                    self.hitbox.left - attack_width, 
                    self.hitbox.top, 
                    attack_width, 
                    attack_height
                )

            # Проверяем, попадают ли враги в область атаки
            for enemy in level.enemies:
                if attack_rect.colliderect(enemy.hitbox):
                    enemy.get_hit(1) 
                    print(f"Player attacked enemy at {enemy.rect.topleft}!")


    def check_collision(self, level):   #True / False
        return level.check_collision(self.hitbox) 

    def horizontal_movement(self, dt, level):
        if self.is_attacking:
            return
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
                self.fall_sound.play()
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
            self.health_bar.update()  # Обновляем хиллбар
            # 1) Ограничим dt
            if dt > self.max_dt:
                dt = self.max_dt

            # 2) Инпут
            self.handle_input(dt)

            # 3) Движение по X
            self.horizontal_movement(dt, level)

            # 4) Движение по Y
            self.vertical_movement(dt, level)

            # 5) post_ground_check
            self.post_ground_check(level)

            # 6) Синхронизируем rect
            self.rect.midbottom = self.hitbox.midbottom

            # 7) Нанесение урона, если атакуем
            if self.is_attacking:
                self.do_attack_damage(level)

            # 8) Анимация
            self.animate(dt)

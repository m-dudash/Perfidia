import pygame as pg
from pytmx.util_pygame import load_pygame
from player import Player

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 32

class Tile(pg.sprite.Sprite):
    def __init__(self, pos, surf, group):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

class Level:
    def __init__(self, surface, level_number):
        self.surface = surface
        self.level_number = level_number
        
        # Группы спрайтов для тайлов
        self.base_sprites = pg.sprite.Group()
        self.decor_sprites = pg.sprite.Group()
        self.collision_tiles = []

        # Загружаем TMX
        self.tmx_data = load_pygame(f"assets/map/level{level_number}.tmx")
        self.level_width = self.tmx_data.width * TILE_SIZE
        self.level_height = self.tmx_data.height * TILE_SIZE

        self.load_tiles()
        self.player = self.create_player()

        # Камера/Зум
        self.zoom_factor = 2.3
        self.vertical_offset = -250
        self.virtual_screen_w = int(SCREEN_WIDTH / self.zoom_factor)
        self.virtual_screen_h = int(SCREEN_HEIGHT / self.zoom_factor)
        self.camera_x = 0
        self.offscreen = pg.Surface((self.virtual_screen_w, self.virtual_screen_h))

        # ---------------- ПАРАЛЛАКСНЫЙ ФОН ----------------
        # Предположим, для 1-го уровня мы берём "grey"
        # Слои: background_layer, back_layer, middle_layer, front_layer
        # parallax_factor (0.0 => зафиксирован, 1.0 => движется вместе с камерой)
        # Обычно дальний слой движется медленнее (0.1..0.2), ближний быстрее (0.5..0.7).
        if self.level_number == 1:
            folder = "grey"
        else:
            # Если есть другие варианты (red, yellow, blue), 
            # можно switch-case, но пока оставим
            folder = "grey"

        self.parallax_layers = [
            (pg.image.load(f"assets/background/{folder}/background layer.png").convert_alpha(), 0.1),
            (pg.image.load(f"assets/background/{folder}/back layer.png").convert_alpha(), 0.3),
            (pg.image.load(f"assets/background/{folder}/middle layer.png").convert_alpha(), 0.5),
            (pg.image.load(f"assets/background/{folder}/front layer.png").convert_alpha(), 0.7)
            ]
        # Note: картинки могут быть большими; смотрите, чтобы 
        # background_layer покрывало весь экран (или тильте их).
        
        self.teleport_rect = self.create_portal()  #создание портала

    def load_tiles(self):
        for layer in self.tmx_data.layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    if surf is None:
                        continue
                    pos = (x*TILE_SIZE, y*TILE_SIZE)
                    if layer.name == "Base":
                        t = Tile(pos, surf, self.base_sprites)
                        self.collision_tiles.append(t)
                    elif layer.name == "Decor":
                        Tile(pos, surf, self.decor_sprites)

    def create_player(self):
        for obj in self.tmx_data.objects:
            if obj.name == "spawnpoint":
                return Player((obj.x - 32, obj.y - 64))
        return Player((200,200))
    
    def create_portal(self):
        """
        Сканируем объекты Tiled. Если найдём obj.name=='teleport', 
        считаем, что это прямоугольник (type='zone'), берём x,y,w,h.
        Создаём pg.Rect, храним в self.teleport_rect.
        Если не найдём — None.
        """
        for obj in self.tmx_data.objects:
            if obj.name == "teleport":
                # x,y,width,height
                # В Tiled x,y — координата левого верхнего угла,
                # w,h — ширина/высота
                rect = pg.Rect(obj.x, obj.y, obj.width, obj.height)
                return rect
        return None

    def check_collision(self, rect):
        for tile in self.collision_tiles:
            if tile.rect.colliderect(rect):
                return True
        return False

    def update(self, dt):
        if self.player:
            self.player.update(dt, self)
            # Проверка, не пересеклись ли с teleport_rect
            if self.teleport_rect:
                if self.teleport_rect.colliderect(self.player.hitbox):
                    # сообщаем "переход на след. уровень"
                    return True  # значит "переход"
        self.update_camera_x()

        return False  # остаться на том же уровне


    def update_camera_x(self):
        if not self.player:
            return
        player_center_x = self.player.rect.centerx
        half_virt_w = self.virtual_screen_w // 2
        desired_camera_x = player_center_x - half_virt_w

        if desired_camera_x < 0:
            desired_camera_x = 0
        max_cam_x = self.level_width - self.virtual_screen_w
        if max_cam_x < 0:
            max_cam_x = 0
        if desired_camera_x > max_cam_x:
            desired_camera_x = max_cam_x

        self.camera_x = desired_camera_x

    def draw(self):
        """
        1) Очищаем offscreen,
        2) Рисуем ПАРАЛЛАКСНЫЙ ФОН (с учётом camera_x, parallax_factor),
        3) Рисуем тайлы (base, decor) и игрока,
        4) Масштабируем всё => real screen.
        """
        # 1) Очищаем offscreen
        self.offscreen.fill((0, 0, 0))

        # 2) Рисуем параллаксный фон
        #    Для каждого слоя (image, factor), 
        #    берём offset_x = camera_x * factor, и повторяем по ширине offscreen.
        for (bg_image, factor) in self.parallax_layers:
            self.draw_parallax_layer(bg_image, factor)

        # 3) Рисуем тайлы и игрока
        self.draw_level_objects()

        # 4) Масштабируем offscreen => real screen
        if self.zoom_factor != 1.0:
            new_w = int(self.virtual_screen_w * self.zoom_factor)
            new_h = int(self.virtual_screen_h * self.zoom_factor)
            scaled = pg.transform.scale(self.offscreen, (new_w, new_h))
            self.surface.blit(scaled, (0,0))
        else:
            self.surface.blit(self.offscreen, (0,0))

        pg.display.update()

    def draw_parallax_layer(self, bg_image, factor):
        """
        Рисуем один слой параллакса по горизонтали (tile),
        но по оси Y он НЕ зависит от factor (все на одном уровне).
        """
        offset_x = int(self.camera_x * factor)
        # Все слои на одинаковой высоте:
        offset_y = self.vertical_offset * 0.13 # НЕ умножаем на factor!

        # Размер картинки
        w = bg_image.get_width()
        h = bg_image.get_height()

        # Ширина offscreen
        screen_w = self.virtual_screen_w
        screen_h = self.virtual_screen_h

        # Начало X, чтобы "зациклить" картинку по модулю её ширины
        start_x = - (offset_x % w)

        # По оси Y ставим просто offset_y (или 0, если не надо двигать).
        # Если фон достаточно высокий и закрывает весь экран, можно не тильтовать по Y.
        y = offset_y

        x = start_x
        while x < screen_w:
            self.offscreen.blit(bg_image, (x, y))
            x += w

    def draw_level_objects(self):
        """
        Рисуем Base, Decor, Player на offscreen
        с учётом camera_x (полный), vertical_offset.
        """
        def draw_off(img, wx, wy):
            sx = wx - self.camera_x
            sy = wy + self.vertical_offset
            self.offscreen.blit(img, (sx, sy))

        # Base
        for tile in self.base_sprites:
            draw_off(tile.image, tile.rect.x, tile.rect.y)
        # Decor
        for tile in self.decor_sprites:
            draw_off(tile.image, tile.rect.x, tile.rect.y)
        # Player
        if self.player:
            draw_off(self.player.image, self.player.rect.x, self.player.rect.y)

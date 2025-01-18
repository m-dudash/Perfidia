import pygame as pg
from pytmx.util_pygame import load_pygame
from player import Player

# Настройки разрешения реального окна
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
# Размер тайла
TILE_SIZE = 32

class Tile(pg.sprite.Sprite):
    """
    Класс-обёртка для одного тайла (image + rect).
    """
    def __init__(self, pos, surf, group):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

class Level:
    """
    Основной класс уровня, который:
      1) Загружает карту (.tmx),
      2) Создаёт тайлы (Base - коллизионные, Decor - декоративные),
      3) Создаёт игрока по spawnpoint,
      4) Проверяет столкновения (check_collision),
      5) Реализует “виртуальное окно” (offscreen) для рисования:
         - camera_x двигаем, чтобы игрок был по центру (с учётом зума),
         - vertical_offset - фиксированный вертикальный сдвиг,
      6) Масштабирует (зум) offscreen единым куском => нет дыр между тайлами,
      7) Выводит на реальный экран (SCREEN_WIDTH×SCREEN_HEIGHT).
    """

    def __init__(self, surface, level_number):
        """
        :param surface: реальный Surface (окно), куда в конце выводим картинку.
        :param level_number: номер или имя уровня, чтобы загрузить tmx (f'level{level_number}.tmx')
        """
        self.surface = surface
        self.level_number = level_number

        # Группы для разных типов тайлов
        self.base_sprites = pg.sprite.Group()   # непроходимые
        self.decor_sprites = pg.sprite.Group()  # декоративные
        self.collision_tiles = []               # список непроходимых

        # Загрузим карту Tiled (через pytmx)
        self.tmx_data = load_pygame(f"assets/map/level{level_number}.tmx")

        # Считаем реальный размер уровня (в пикселях)
        self.level_width = self.tmx_data.width * TILE_SIZE
        self.level_height = self.tmx_data.height * TILE_SIZE

        # Загрузим тайлы
        self.load_tiles()

        # Создадим игрока
        self.player = self.create_player()

        # --------------- НАСТРОЙКИ КАМЕРЫ И ЗУМА ---------------

        # 1) zoom_factor: насколько “приближаем” картинку,
        #    рисуя на offscreen, а потом растягивая на реальный экран.
        #    >1 => приближение, <1 => отдаление.
        self.zoom_factor = 2.3  # можно изменить

        # 2) vertical_offset: фиксированный сдвиг по Y (например, -100 => поднимаем всё)
        #    Это позволяет игроку быть ближе к нижней части экрана.
        #    (По оси Y мы камеру за игроком не двигаем.)
        self.vertical_offset = -250

        # 3) Для точного центрирования игрока надо определить “виртуальную ширину”:
        #    При зуме мы будем растягивать offscreen => real_screen.
        #    offscreen будет меньше реального окна, чтобы при растяжке
        #    игрок оказался именно по центру финального экрана.
        #
        #    Если реальный экран 1280×720, а zoom=1.3,
        #    то виртуальное окно (offscreen) будет 1280/1.3 примерно = 984 px
        #    в ширину. По высоте аналогично. Но высота нам особо не важна, раз
        #    мы не двигаем камеру по Y.
        #
        # Итог: virtual_screen_w × virtual_screen_h — размер “виртуального окна”,
        #       в котором игрок будет по центру. Затем масштабируем -> SCREEN_WIDTH×SCREEN_HEIGHT.
        self.virtual_screen_w = int(SCREEN_WIDTH / self.zoom_factor)
        self.virtual_screen_h = int(SCREEN_HEIGHT / self.zoom_factor)

        # camera_x: сдвиг уровня по X (в “виртуальных” координатах),
        #           чтобы игрок был в центре offscreen.
        self.camera_x = 0

        # Создаём offscreen Surface размером virtual_screen_w×virtual_screen_h
        # На него будем рисовать в draw().
        self.offscreen = pg.Surface((self.virtual_screen_w, self.virtual_screen_h))

    def load_tiles(self):
        """
        Проходим по слоям tmx:
          - Base => непроходимые, добавляем в base_sprites + collision_tiles
          - Decor => декоративные.
        """
        for layer in self.tmx_data.layers:
            if hasattr(layer, 'data'):  # слой с тайлами
                for x, y, surf in layer.tiles():
                    if surf is None:
                        continue
                    pos = (x * TILE_SIZE, y * TILE_SIZE)
                    if layer.name == "Base":
                        tile = Tile(pos, surf, self.base_sprites)
                        self.collision_tiles.append(tile)
                    elif layer.name == "Decor":
                        Tile(pos, surf, self.decor_sprites)

    def create_player(self):
        """
        Ищем объект spawnpoint, ставим игрока туда.
        Если не нашли — (200,200).
        """
        for obj in self.tmx_data.objects:
            if obj.name == "spawnpoint":
                return Player((obj.x-32, obj.y-64))
        return Player((200, 200))

    def check_collision(self, rect):
        """
        Проверяем пересечение rect с любым непроходимым тайлом (Base).
        """
        for tile in self.collision_tiles:
            if tile.rect.colliderect(rect):
                return True
        return False

    def update(self, dt):
        """
        Вызывается каждый кадр:
          1) Обновляем игрока,
          2) Обновляем camera_x, чтобы игрок был по центру “виртуального” окна.
        """
        if self.player:
            self.player.update(dt, self)
        self.update_camera_x()

    def update_camera_x(self):
        """
        Делаем, чтобы игрок был по центру виртуального окна (self.virtual_screen_w).
        Пока не достигли краёв уровня.
        """
        if not self.player:
            return

        # Центр игрока
        player_center_x = self.player.rect.centerx

        # Половина виртуального окна
        half_virt_w = self.virtual_screen_w // 2

        # Желательный camera_x таков, чтобы player_center_x оказался в середине virtual_screen_w
        desired_camera_x = player_center_x - half_virt_w

        # Ограничим, чтобы не выйти за границы карты:
        #   0 <= camera_x <= (level_width - virtual_screen_w)
        if desired_camera_x < 0:
            desired_camera_x = 0
        max_cam_x = self.level_width - self.virtual_screen_w
        if max_cam_x < 0:
            # Случай, когда уровень уже меньше виртуального окна
            max_cam_x = 0
        if desired_camera_x > max_cam_x:
            desired_camera_x = max_cam_x

        self.camera_x = desired_camera_x

    def draw(self):
        """
        1) Очищаем offscreen,
        2) Рисуем тайлы (Base, Decor) и игрока на offscreen с учётом camera_x, vertical_offset,
        3) Масштабируем offscreen => real_screen (self.surface) по zoom_factor,
        4) Игрок оказывается ровно по центру реального окна (по X),
           без дыр между тайлами, сцена поднята на vertical_offset по Y.
        """
        # 1) Очищаем offscreen
        self.offscreen.fill((30,30,30))

        # Функция: нарисовать один спрайт (tile/игрок) на offscreen
        def draw_on_offscreen(image, world_x, world_y):
            """
            :param image: Surface спрайта
            :param world_x, world_y: мировые координаты (без зума)
            Мы учтём camera_x и vertical_offset, выведем на offscreen.
            """
            screen_x = world_x - self.camera_x
            screen_y = world_y + self.vertical_offset
            self.offscreen.blit(image, (screen_x, screen_y))

        # 2.1) Рисуем Base
        for tile in self.base_sprites:
            draw_on_offscreen(tile.image, tile.rect.x, tile.rect.y)

        # 2.2) Рисуем Decor
        for tile in self.decor_sprites:
            draw_on_offscreen(tile.image, tile.rect.x, tile.rect.y)

        # 2.3) Рисуем игрока
        if self.player:
            draw_on_offscreen(self.player.image, 
                              self.player.rect.x, 
                              self.player.rect.y)

        # 3) Теперь масштабируем offscreen => реальный экран
        if self.zoom_factor != 1.0:
            new_w = int(self.virtual_screen_w * self.zoom_factor)
            new_h = int(self.virtual_screen_h * self.zoom_factor)
            scaled = pg.transform.scale(self.offscreen, (new_w, new_h))

            # Выводим scaled на (0,0) реального окна
            # (То есть вся картинка займёт real_screen)
            self.surface.blit(scaled, (0, 0))

        else:
            # Без зума
            self.surface.blit(self.offscreen, (0, 0))

        pg.display.update()

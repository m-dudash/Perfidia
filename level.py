import pygame as pg
from pytmx.util_pygame import load_pygame
from player import Player

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
        
        # Группа для отрисовки Base-тайлов и Decor-тайлов отдельно (или общая, как хотите)
        self.base_sprites = pg.sprite.Group()
        self.decor_sprites = pg.sprite.Group()

        # Список коллизионных тайлов
        self.collision_tiles = []

        # Загружаем карту
        self.tmx_data = load_pygame(f'assets/map/level{level_number}.tmx')
        
        # Загружаем тайлы
        self.load_tiles()
        
        # Создаём игрока
        self.player = self.create_player()

    def load_tiles(self):
        """
        Сканируем все слои. Если layer.name == 'Base' - считаем коллизионным.
        Если layer.name == 'Decor' - считаем неколлизионным.
        """
        for layer in self.tmx_data.layers:
            if hasattr(layer, 'data'):  # это слой с тайлами
                for x, y, surf in layer.tiles():
                    if surf is None:
                        continue  # пропуск пустых
                    pos = (x * TILE_SIZE, y * TILE_SIZE)

                    if layer.name == "Base":
                        # Создаём спрайт тайла и добавляем его в коллизионную группу
                        tile_sprite = Tile(pos, surf, self.base_sprites)
                        self.collision_tiles.append(tile_sprite)
                    elif layer.name == "Decor":
                        # Это просто декор, не участвует в коллизии
                        Tile(pos, surf, self.decor_sprites)

    def create_player(self):
        """Находим в Objects объект 'spawnpoint'. Иначе (200,200)."""
        for obj in self.tmx_data.objects:
            if obj.name == "spawnpoint":
                return Player((obj.x, obj.y - 64))  # например, -64, если спрайт выше
        # fallback
        return Player((200, 200))

    def check_collision(self, rect):
        """Проверяем столкновение с любым Base-тайлом."""
        for tile in self.collision_tiles:
            if tile.rect.colliderect(rect):
                return True
        return False

    def update(self, dt):
        if self.player:
            self.player.update(dt, self)

    def draw(self):
        """
        Сначала рисуем Base (или сначала Decor — зависит от того, что вы хотите «на заднем плане»).
        Потом Decor (или Base).
        Потом игрока.
        """
        # Заливаем фон
        self.surface.fill((0, 0, 0))

        # Base
        self.base_sprites.draw(self.surface)

        # Decor (если хотите, чтобы декор рисовался поверх)
        self.decor_sprites.draw(self.surface)

        # Игрок
        if self.player:
            self.surface.blit(self.player.image, self.player.rect)

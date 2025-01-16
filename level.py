import pygame as pg
from pytmx.util_pygame import load_pygame

TILE_SIZE = 32

class Tile(pg.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

class Level:
    def __init__(self, surface, level_number):
        self.surface = surface
        self.level_number = level_number

        # Группы спрайтов
        self.all_sprites = pg.sprite.Group()

        # Загрузка карты и тайлов
        self.tmx_data = load_pygame(f'assets/map/level{level_number}.tmx')  # Загрузка карты
        self.load_tiles()  # Загружаем тайлы

    def draw(self):
        """Рисует все спрайты на поверхности."""
        self.all_sprites.draw(self.surface)

    def load_tiles(self):
        """Загружает тайлы из карты и добавляет их в группы."""
        for layer in self.tmx_data.layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * TILE_SIZE, y * TILE_SIZE)
                    Tile(pos, surf, self.all_sprites)  # Создаем тайлы и добавляем их в группу

    def update(self):
        """Обновляет все спрайты."""
        self.all_sprites.update()

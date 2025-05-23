# tilemap.py
import pygame
from constants import *

class TileMap:
    def __init__(self, source):
        if isinstance(source, str):
            # Load from file
            with open(source, 'r') as f:
                lines = f.readlines()
            lines = [line.rstrip('\n').ljust(GRID_WIDTH)[:GRID_WIDTH] for line in lines]
            while len(lines) < GRID_HEIGHT:
                lines.append(' ' * GRID_WIDTH)
            lines = lines[:GRID_HEIGHT]  # Trim if too many lines
            self.grid = [[char for char in line] for line in lines]
        else:
            # Direct grid initialization
            self.grid = source
        self.height = GRID_HEIGHT
        self.width = GRID_WIDTH

    def get(self, x, y):
        try:
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                return self.grid[y][x]
        except IndexError:
            pass
        return STONE

    def set(self, x, y, value):
        try:
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                self.grid[y][x] = value
        except IndexError:
            pass

    def draw(self, surface):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == DIAMOND:
                    # Draw upside-down triangle for diamond
                    center_x = x * TILE_SIZE + TILE_SIZE // 2
                    top_y = y * TILE_SIZE + TILE_SIZE - 2  # Bottom point
                    left_x = center_x - 6  # Half of edge length
                    right_x = center_x + 6
                    bottom_y = y * TILE_SIZE + 2  # Top points
                    
                    pygame.draw.polygon(
                        surface,
                        TILE_COLORS[DIAMOND],
                        [(center_x, top_y), (left_x, bottom_y), (right_x, bottom_y)]
                    )
                elif tile != AIR:
                    self.draw_tile(surface, x, y, tile)

    def draw_tile(self, surface, x, y, tile):
        color = TILE_COLORS.get(tile, (255, 0, 0))
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, color, rect)

        if tile == LADDER:
            px = x * TILE_SIZE
            py = y * TILE_SIZE
            pygame.draw.rect(surface, (220, 220, 220), (px + 2, py, 2, TILE_SIZE))
            pygame.draw.rect(surface, (220, 220, 220), (px + TILE_SIZE - 4, py, 2, TILE_SIZE))
            for i in range(3, TILE_SIZE, 5):
                pygame.draw.line(surface, (180, 180, 180), (px + 2, py + i), (px + TILE_SIZE - 4, py + i), 1)


def load_level_from_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    lines = [line.rstrip('\n').ljust(GRID_WIDTH)[:GRID_WIDTH] for line in lines]
    while len(lines) < GRID_HEIGHT:
        lines.append(' ' * GRID_WIDTH)

    tilemap = []
    player_start = (1, 1)
    opponents = []

    for y, line in enumerate(lines):
        row = []
        for x, char in enumerate(line):
            if char == ' ':
                row.append(AIR)
            elif char == '=':
                row.append(EARTH)
            elif char == '#':
                row.append(LADDER)
            elif char == '*':
                row.append(STONE)
            elif char == '@':
                player_start = (x, y)
                row.append(AIR)
            elif char == '$':
                opponents.append((x, y))
                row.append(AIR)
            else:
                row.append(AIR)
        tilemap.append(row)

    return TileMap(tilemap), player_start, opponents
# tilemap.py
import pygame
from constants import *

# File format character mappings
FILE_CHAR_AIR = ' '
FILE_CHAR_EARTH = '='
FILE_CHAR_STONE = '*'
FILE_CHAR_LADDER = '#'
FILE_CHAR_DIAMOND = 'v'
FILE_CHAR_PLAYER = 'P'
FILE_CHAR_OPPONENT = 'O'
FILE_CHAR_EXIT = 'E'

# Mapping from tile types to file characters
TILE_TO_CHAR = {
    AIR: FILE_CHAR_AIR,
    EARTH: FILE_CHAR_EARTH,
    STONE: FILE_CHAR_STONE,
    LADDER: FILE_CHAR_LADDER,
    DIAMOND: FILE_CHAR_DIAMOND,
    PLAYER: FILE_CHAR_PLAYER,
    OPPONENT: FILE_CHAR_OPPONENT,
    EXIT: FILE_CHAR_EXIT
}

# Mapping from file characters to tile types
CHAR_TO_TILE = {
    FILE_CHAR_AIR: AIR,
    FILE_CHAR_EARTH: EARTH,
    FILE_CHAR_STONE: STONE,
    FILE_CHAR_LADDER: LADDER,
    FILE_CHAR_DIAMOND: DIAMOND,
    FILE_CHAR_PLAYER: PLAYER,
    FILE_CHAR_OPPONENT: OPPONENT,
    FILE_CHAR_EXIT: EXIT
}

class TileMap:
    def __init__(self, source):
        self.timer_seconds = 120  # Default 2 minutes (02:00)
        
        if isinstance(source, str):
            # Load from file
            with open(source, 'r') as f:
                lines = f.readlines()
            
            # Check if the first line contains a timer in mm:ss format
            if lines and lines[0].strip().count(':') == 1:
                try:
                    time_parts = lines[0].strip().split(':')
                    if len(time_parts) == 2 and all(part.isdigit() for part in time_parts):
                        minutes = int(time_parts[0])
                        seconds = int(time_parts[1])
                        self.timer_seconds = minutes * 60 + seconds
                        # Remove the timer line from the level data
                        lines = lines[1:]
                except (ValueError, IndexError):
                    # If there's any error parsing the timer, use the default
                    pass
            
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

    def get_tile_by_pixel_coords(self, px, py):
        return self.get(int(px // TILE_SIZE), int(py // TILE_SIZE))

    def get_pixel_coords_of_tile(self, tx, ty):
        return (tx * TILE_SIZE, ty * TILE_SIZE)

    def is_ground(self, tile):
        return tile in [EARTH, STONE]

    def is_standable(self, tile):
        return tile in [EARTH, STONE, LADDER]

    def set(self, x, y, value):
        try:
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                self.grid[y][x] = value
        except IndexError:
            pass

    def draw(self, surface, y_offset=0):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                self.draw_tile(surface, x, y, tile, y_offset)

    def draw_tile(self, surface, x, y, tile, y_offset=0):
        color = TILE_COLORS.get(tile, (255, 0, 0))

        if tile == LADDER:
            self.draw_ladder(surface, x, y, y_offset)
        elif tile == DIAMOND:
            self.draw_diamond(surface, x, y, y_offset)
        elif tile != AIR:
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + y_offset, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

    def draw_diamond(self, surface, x, y, y_offset):
        center_x = x * TILE_SIZE + TILE_SIZE // 2
        top_y = y * TILE_SIZE + TILE_SIZE - 2 + y_offset  # Bottom point
        left_x = center_x - 6  # Half of edge length
        right_x = center_x + 6
        bottom_y = y * TILE_SIZE + 2 + y_offset  # Top points
        
        pygame.draw.polygon(
            surface,
            TILE_COLORS[DIAMOND],
            [(center_x, top_y), (left_x, bottom_y), (right_x, bottom_y)]
        )

    def draw_ladder(self, surface, x, y, y_offset):
        px = x * TILE_SIZE
        py = y * TILE_SIZE + y_offset
        pygame.draw.rect(surface, (220, 220, 220), (px + 2, py, 2, TILE_SIZE))
        pygame.draw.rect(surface, (220, 220, 220), (px + TILE_SIZE - 4, py, 2, TILE_SIZE))
        for i in range(3, TILE_SIZE, 5):
            pygame.draw.line(surface, (180, 180, 180), (px + 2, py + i), (px + TILE_SIZE - 4, py + i), 1)
            
    def save_to_file(self, file_handle, include_entities=False, player_pos=None, opponent_positions=None):
        """Save the tilemap to an open file handle
        
        Args:
            file_handle: An open file handle to write to
            include_entities: Whether to include player and opponents in the output
            player_pos: Tuple of (x, y) for player position if include_entities is True
            opponent_positions: List of (x, y) tuples for opponent positions if include_entities is True
        """
        # Create a temporary grid for saving that includes entities if requested
        temp_grid = [row[:] for row in self.grid]  # Deep copy the grid
        
        # Add player and opponents to the grid if requested
        if include_entities:
            if player_pos:
                px, py = player_pos
                if 0 <= px < self.width and 0 <= py < self.height:
                    temp_grid[py][px] = PLAYER
                    
            if opponent_positions:
                for ox, oy in opponent_positions:
                    if 0 <= ox < self.width and 0 <= oy < self.height:
                        temp_grid[oy][ox] = OPPONENT
        
        # Write the level data
        for y in range(self.height):
            line = ''
            for x in range(self.width):
                tile = temp_grid[y][x]
                # Use the tile-to-character mapping
                line += TILE_TO_CHAR.get(tile, FILE_CHAR_AIR)  # Default to AIR if unknown tile
            file_handle.write(line + '\n')


def load_level_from_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    lines = [line.rstrip('\n').ljust(GRID_WIDTH)[:GRID_WIDTH] for line in lines]
    while len(lines) < GRID_HEIGHT:
        lines.append(FILE_CHAR_AIR * GRID_WIDTH)

    tilemap = []
    player_start = (1, 1)  # Default player position if not found
    opponents = []

    for y, line in enumerate(lines):
        row = []
        for x, char in enumerate(line):
            # Handle special cases for player and opponents
            if char == FILE_CHAR_PLAYER:
                player_start = (x, y)
                row.append(AIR)  # Player position is stored as AIR in the tilemap
            elif char == FILE_CHAR_OPPONENT:
                opponents.append((x, y))
                row.append(AIR)  # Opponent positions are stored as AIR in the tilemap
            else:
                # Use the character-to-tile mapping for regular tiles
                tile = CHAR_TO_TILE.get(char, AIR)  # Default to AIR if unknown character
                row.append(tile)
        tilemap.append(row)

    return TileMap(tilemap), player_start, opponents
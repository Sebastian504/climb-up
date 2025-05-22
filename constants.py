# constants.py

# Tile size and grid
TILE_SIZE = 16
GRID_WIDTH = 60
GRID_HEIGHT = 40
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

# Tile types
AIR = 0
EARTH = 1
STONE = 2
LADDER = 3

# Colors (grayscale)
TILE_COLORS = {
    AIR: (30, 30, 30),
    EARTH: (100, 100, 100),
    STONE: (180, 180, 180),
    LADDER: (0, 0, 0),
}

# Directions
DIR_LEFT = -1
DIR_RIGHT = 1

# Player & opponent visuals
PLAYER_COLOR = (255, 255, 255)
OPPONENT_COLOR = (180, 180, 255)

# Movement config
MOVE_SPEED = 1
GRAVITY = 0.33
MOVE_INTERVAL = 150  # ms

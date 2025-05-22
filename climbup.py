import pygame
import sys

# --- Config ---
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
    LADDER: (220, 220, 220),
}

# Movement directions
DIR_LEFT = -1
DIR_RIGHT = 1

PLAYER_COLOR = (255, 255, 255)
OPPONENT_COLOR = (180, 180, 255)

MOVE_SPEED = 1  # pixels per frame
GRAVITY = 0.33
MOVE_INTERVAL = 150  # milliseconds

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Climb Up")
clock = pygame.time.Clock()

# --- Utility ---
def is_solid(tile):
    return tile == EARTH or tile == STONE

def draw_tile_air(surface, x, y):
    pygame.draw.rect(surface, TILE_COLORS[AIR], (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_tile_earth(surface, x, y):
    pygame.draw.rect(surface, TILE_COLORS[EARTH], (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_tile_stone(surface, x, y):
    pygame.draw.rect(surface, TILE_COLORS[STONE], (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_tile_ladder(surface, x, y):
    draw_tile_air(surface, x, y)
    px = x * TILE_SIZE
    py = y * TILE_SIZE
    pygame.draw.rect(surface, (220, 220, 220), (px + 2, py, 2, TILE_SIZE))
    pygame.draw.rect(surface, (220, 220, 220), (px + TILE_SIZE - 4, py, 2, TILE_SIZE))
    for i in range(3, TILE_SIZE, 5):
        pygame.draw.line(surface, (180, 180, 180), (px + 2, py + i), (px + TILE_SIZE - 4, py + i), 1)

def draw_map(surface, tilemap):
    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):
            if tile == AIR:
                draw_tile_air(surface, x, y)
            elif tile == EARTH:
                draw_tile_earth(surface, x, y)
            elif tile == STONE:
                draw_tile_stone(surface, x, y)
            elif tile == LADDER:
                draw_tile_ladder(surface, x, y)

def draw_stick_figure(surface, px, py, state, frame, facing):
    cx = px + TILE_SIZE // 2
    cy = py + TILE_SIZE // 2
    pygame.draw.circle(surface, PLAYER_COLOR, (cx, cy), 6)

def draw_player(surface):
    draw_stick_figure(surface, int(game.player.px), int(game.player.py), game.player.state, game.player.anim_frame, game.player.facing)

def draw_opponents(surface):
    for ox_px, oy_px in game.opponents.positions:
        rect = pygame.Rect(int(ox_px), int(oy_px), TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, OPPONENT_COLOR, rect)

def get_tile(x, y):
    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        return game.tilemap[y][x]
    return STONE

def set_tile(x, y, value):
    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        game.tilemap[y][x] = value

def load_level_from_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Pad lines to required width
    lines = [line.rstrip('\n').ljust(GRID_WIDTH)[:GRID_WIDTH] for line in lines]
    # Pad the number of lines to match GRID_HEIGHT
    while len(lines) < GRID_HEIGHT:
        lines.append(' ' * GRID_WIDTH)

    tilemap = []
    player_start = (1, 1)
    opps = []
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
                opps.append([x, y])
                row.append(AIR)
            else:
                row.append(AIR)
        tilemap.append(row)

    return tilemap, player_start, opps


# --- Game Classes ---

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.px = x * TILE_SIZE
        self.py = y * TILE_SIZE
        self.vx = 0
        self.vy = 0
        self.facing = DIR_RIGHT
        self.state = "idle"
        self.prev_state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0


class Opponents:
    def __init__(self, tile_positions):
        self.positions = [(x * TILE_SIZE, y * TILE_SIZE) for x, y in tile_positions]


class GameState:
    def __init__(self):
        self.tilemap, (px, py), opp_tiles = load_level_from_file("level1.txt")
        self.player = Player(px, py)
        self.opponents = Opponents(opp_tiles)
        self.running = True

# --- Game State ---
game = GameState()

# --- Main Loop ---
def handle_player_controls(keys, current_time):
    p = game.player

    if keys[pygame.K_LEFT]:
        p.facing = DIR_LEFT
        p.vx = -MOVE_SPEED
    elif keys[pygame.K_RIGHT]:
        p.facing = DIR_RIGHT
        p.vx = MOVE_SPEED
    else:
        p.vx = 0

    is_climbable = (
        get_tile(p.x, p.y) == LADDER or
        get_tile(p.x - 1, p.y) == LADDER or
        get_tile(p.x + 1, p.y) == LADDER
    )
    on_ladder = get_tile(p.x, p.y) == LADDER
    below = get_tile(p.x, p.y + 1)

    if keys[pygame.K_UP] and (
        is_climbable or get_tile(p.x, p.y - 1) == LADDER or get_tile(p.x, int((p.py - 4) // TILE_SIZE)) == LADDER or get_tile(p.x, p.y + 1) == LADDER):
        if get_tile(p.x, p.y) != LADDER:
            if get_tile(p.x - 1, p.y) == LADDER:
                p.px = (p.x - 1) * TILE_SIZE
            elif get_tile(p.x + 1, p.y) == LADDER:
                p.px = (p.x + 1) * TILE_SIZE
            p.x = int(p.px // TILE_SIZE)
        p.vy = -MOVE_SPEED
        p.state = "climbing"
    elif keys[pygame.K_DOWN] and (
        is_climbable or get_tile(p.x, p.y + 1) == LADDER or get_tile(p.x, int((p.py + TILE_SIZE + 4) // TILE_SIZE)) == LADDER):
        if get_tile(p.x, p.y) != LADDER:
            if get_tile(p.x - 1, p.y) == LADDER:
                p.px = (p.x - 1) * TILE_SIZE
            elif get_tile(p.x + 1, p.y) == LADDER:
                p.px = (p.x + 1) * TILE_SIZE
            p.x = int(p.px // TILE_SIZE)
        p.vy = MOVE_SPEED
        p.state = "climbing"
    elif not (is_solid(below) or below == LADDER) and not on_ladder:
        p.vy += GRAVITY
        p.state = "falling"
    else:
        p.vy = 0

    if p.state not in ["climbing", "falling"]:
        if p.vx != 0:
            p.state = "running"
        else:
            p.state = "idle"

    if p.state != p.prev_state:
        p.anim_frame = 0
        p.anim_timer = current_time
    p.prev_state = p.state

    next_px = p.px + p.vx
    edge_px = next_px + TILE_SIZE - 1 if p.vx > 0 else next_px
    next_tile_x = int(edge_px // TILE_SIZE)
    next_tile_y = int(p.py // TILE_SIZE)
    if not is_solid(get_tile(next_tile_x, next_tile_y)):
        p.px = next_px

    p.py += p.vy
    p.x = int(p.px // TILE_SIZE)
    p.y = int(p.py // TILE_SIZE)

    if keys[pygame.K_SPACE]:
        dig_dir = -p.facing
        dig_x = p.x + dig_dir
        dig_y = p.y + 1
        if get_tile(dig_x, dig_y) == EARTH:
            set_tile(dig_x, dig_y, AIR)

    if p.state == "falling":
        below = get_tile(p.x, p.y + 1)
        if is_solid(below):
            p.py = (p.y // 1) * TILE_SIZE
            p.vy = 0
            p.state = "idle""idle"

def handle_opponent_controls():
    new_opponents = []
    for ox_px, oy_px in game.opponents.positions:
        ox = int(ox_px // TILE_SIZE)
        oy = int(oy_px // TILE_SIZE)
        dx = game.player.px - ox_px
        dy = game.player.py - oy_px

        vx, vy = 0, 0
        below = get_tile(ox, oy + 1)
        current = get_tile(ox, oy)

        if below == AIR and current != LADDER:
            vy = MOVE_SPEED
        elif dy < 0 and (current == LADDER or get_tile(ox, oy - 1) == LADDER):
            if not is_solid(get_tile(ox, oy - 1)):
                vy = -MOVE_SPEED
        if not (below == AIR and current != LADDER):
            step = 1 if dx > 0 else -1
            target_tile = get_tile(ox + step, oy)
            below_target = get_tile(ox + step, oy + 1)
            if (target_tile in [AIR, LADDER]) and (below_target in [EARTH, STONE, LADDER]):
                vx = step * MOVE_SPEED
            elif target_tile in [AIR, LADDER] and below_target == AIR:
                vx = step * MOVE_SPEED

        new_opponents.append((ox_px + vx, oy_px + vy))
    game.opponents.positions = new_opponents

def check_game_over():
    px, py = game.player.px, game.player.py
    pw, ph = TILE_SIZE, TILE_SIZE
    player_rect = pygame.Rect(px, py, pw, ph)

    for ox_px, oy_px in game.opponents.positions:
        opp_rect = pygame.Rect(ox_px, oy_px, TILE_SIZE, TILE_SIZE)
        if player_rect.colliderect(opp_rect):
            print("Game Over: Caught by an opponent!")
            return True
    return False

def draw_everything():
    screen.fill((0, 0, 0))
    draw_map(screen, game.tilemap)
    draw_player(screen)
    draw_opponents(screen)
    pygame.display.flip()

running = True
while running:
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_player_controls(keys, current_time)

    handle_opponent_controls()

    if check_game_over():
        running = False

    if current_time - game.player.anim_timer >= 16:
        if game.player.state in ["running", "climbing"]:
            game.player.anim_frame = (game.player.anim_frame + 1) % 8
            game.player.anim_timer = current_time

    draw_everything()
    clock.tick(60)

pygame.quit()
sys.exit()

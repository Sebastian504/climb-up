# entities.py
import pygame
from constants import *

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

    def handle_input(self, keys, tilemap, current_time):
        if keys[pygame.K_LEFT]:
            self.facing = DIR_LEFT
            self.vx = -MOVE_SPEED
        elif keys[pygame.K_RIGHT]:
            self.facing = DIR_RIGHT
            self.vx = MOVE_SPEED
        else:
            self.vx = 0

        is_climbable = (
            tilemap.get(self.x, self.y) == LADDER or
            tilemap.get(self.x - 1, self.y) == LADDER or
            tilemap.get(self.x + 1, self.y) == LADDER
        )
        on_ladder = tilemap.get(self.x, self.y) == LADDER
        below = tilemap.get(self.x, self.y + 1)

        if keys[pygame.K_UP] and (
            is_climbable or tilemap.get(self.x, self.y - 1) == LADDER or
            tilemap.get(self.x, int((self.py - 4) // TILE_SIZE)) == LADDER or
            tilemap.get(self.x, self.y + 1) == LADDER):
            if tilemap.get(self.x, self.y) != LADDER:
                if tilemap.get(self.x - 1, self.y) == LADDER:
                    self.px = (self.x - 1) * TILE_SIZE
                elif tilemap.get(self.x + 1, self.y) == LADDER:
                    self.px = (self.x + 1) * TILE_SIZE
                self.x = int(self.px // TILE_SIZE)
            self.vy = -MOVE_SPEED
            self.state = "climbing"
        elif keys[pygame.K_DOWN] and (
            is_climbable or tilemap.get(self.x, self.y + 1) == LADDER or
            tilemap.get(self.x, int((self.py + TILE_SIZE + 4) // TILE_SIZE)) == LADDER):
            if tilemap.get(self.x, self.y) != LADDER:
                if tilemap.get(self.x - 1, self.y) == LADDER:
                    self.px = (self.x - 1) * TILE_SIZE
                elif tilemap.get(self.x + 1, self.y) == LADDER:
                    self.px = (self.x + 1) * TILE_SIZE
                self.x = int(self.px // TILE_SIZE)
            self.vy = MOVE_SPEED
            self.state = "climbing"
        elif not (tilemap.get(self.x, self.y + 1) in [EARTH, STONE, LADDER]) and not on_ladder:
            self.vy += GRAVITY
            self.state = "falling"
        else:
            self.vy = 0

        if self.state not in ["climbing", "falling"]:
            if self.vx != 0:
                self.state = "running"
            else:
                self.state = "idle"

        if self.state != self.prev_state:
            self.anim_frame = 0
            self.anim_timer = current_time
        self.prev_state = self.state

        next_px = self.px + self.vx
        edge_px = next_px + TILE_SIZE - 1 if self.vx > 0 else next_px
        next_tile_x = int(edge_px // TILE_SIZE)
        next_tile_y = int(self.py // TILE_SIZE)
        if not tilemap.get(next_tile_x, next_tile_y) in [EARTH, STONE]:
            self.px = next_px

        self.py += self.vy
        self.x = int(self.px // TILE_SIZE)
        self.y = int(self.py // TILE_SIZE)

        if keys[pygame.K_SPACE]:
            dig_dir = -self.facing
            dig_x = self.x + dig_dir
            dig_y = self.y + 1
            if tilemap.get(dig_x, dig_y) == EARTH:
                tilemap.set(dig_x, dig_y, AIR)

        if self.state == "falling" and tilemap.get(self.x, self.y + 1) in [EARTH, STONE]:
            self.py = (self.y // 1) * TILE_SIZE
            self.vy = 0
            self.state = "idle"

    def draw(self, surface):
        cx = self.px + TILE_SIZE // 2
        cy = self.py + TILE_SIZE // 2
        pygame.draw.circle(surface, PLAYER_COLOR, (int(cx), int(cy)), 6)


class Opponents:
    def __init__(self, tile_positions):
        self.positions = [(x * TILE_SIZE, y * TILE_SIZE) for x, y in tile_positions]

    def update(self, player, tilemap):
        new_positions = []
        for ox_px, oy_px in self.positions:
            ox = int(ox_px // TILE_SIZE)
            oy = int(oy_px // TILE_SIZE)
            dx = player.px - ox_px
            dy = player.py - oy_px

            vx, vy = 0, 0
            below = tilemap.get(ox, oy + 1)
            current = tilemap.get(ox, oy)

            if below == AIR and current != LADDER:
                vy = MOVE_SPEED
            elif dy < 0 and (current == LADDER or tilemap.get(ox, oy - 1) == LADDER):
                if tilemap.get(ox, oy - 1) not in [EARTH, STONE]:
                    vy = -MOVE_SPEED
            if not (below == AIR and current != LADDER):
                step = 1 if dx > 0 else -1
                target_tile = tilemap.get(ox + step, oy)
                below_target = tilemap.get(ox + step, oy + 1)
                if (target_tile in [AIR, LADDER]) and (below_target in [EARTH, STONE, LADDER]):
                    vx = step * MOVE_SPEED
                elif target_tile in [AIR, LADDER] and below_target == AIR:
                    vx = step * MOVE_SPEED

            new_positions.append((ox_px + vx, oy_px + vy))
        self.positions = new_positions

    def draw(self, surface):
        for ox_px, oy_px in self.positions:
            rect = pygame.Rect(int(ox_px), int(oy_px), TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, OPPONENT_COLOR, rect)

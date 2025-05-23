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

        # Get current grid position
        current_tile_x = int(self.px // TILE_SIZE)
        current_y = int(self.py // TILE_SIZE)
        
        # Calculate overlap with current tile
        px_in_tile = self.px % TILE_SIZE
        overlap_current = min(TILE_SIZE - px_in_tile, TILE_SIZE)
        overlap_next = px_in_tile
        
        # Check if we have 50% overlap with a ladder
        on_ladder = False
        if tilemap.get(current_tile_x, current_y) == LADDER and overlap_current >= TILE_SIZE/2:
            on_ladder = True
        elif tilemap.get(current_tile_x + 1, current_y) == LADDER and overlap_next >= TILE_SIZE/2:
            on_ladder = True
        
        # For climbability, we'll be a bit more lenient (allow mounting from nearby)
        is_climbable = on_ladder or (
            (tilemap.get(current_tile_x - 1, current_y) == LADDER and px_in_tile < 6) or
            (tilemap.get(current_tile_x + 1, current_y) == LADDER and px_in_tile > TILE_SIZE - 6)
        )
        
        below = tilemap.get(current_tile_x, current_y + 1)

        if keys[pygame.K_UP] and (
            is_climbable or
            tilemap.get(current_tile_x, current_y - 1) == LADDER or
            tilemap.get(current_tile_x, current_y + 1) == LADDER):
            # Find the ladder we can mount
            target_x = None
            if tilemap.get(current_tile_x - 1, current_y) == LADDER and px_in_tile < 6:
                target_x = current_tile_x - 1
            elif tilemap.get(current_tile_x + 1, current_y) == LADDER and px_in_tile > TILE_SIZE - 6:
                target_x = current_tile_x + 1
            elif tilemap.get(current_tile_x, current_y) == LADDER:
                target_x = current_tile_x
                
            # Always center on ladder when climbing
            if target_x is not None:
                self.x = target_x
                # Center player (12px wide) on ladder (16px wide)
                self.px = target_x * TILE_SIZE + (TILE_SIZE - 12) // 2 - 1
            elif on_ladder:
                # If already on a ladder, stay centered
                self.px = current_tile_x * TILE_SIZE + (TILE_SIZE - 12) // 2 - 1
            self.vy = -MOVE_SPEED
            self.state = "climbing"
        elif keys[pygame.K_DOWN] and (
            (is_climbable or tilemap.get(current_tile_x, current_y + 1) == LADDER) and
            tilemap.get(current_tile_x, current_y + 1) not in [EARTH, STONE]):
            # Find the ladder we can mount
            target_x = None
            if tilemap.get(current_tile_x - 1, current_y) == LADDER and px_in_tile < 6:
                target_x = current_tile_x - 1
            elif tilemap.get(current_tile_x + 1, current_y) == LADDER and px_in_tile > TILE_SIZE - 6:
                target_x = current_tile_x + 1
            elif tilemap.get(current_tile_x, current_y) == LADDER:
                target_x = current_tile_x
                
            # Always center on ladder when climbing
            if target_x is not None:
                self.x = target_x
                # Center player (12px wide) on ladder (16px wide)
                self.px = target_x * TILE_SIZE + (TILE_SIZE - 12) // 2 - 1
            elif on_ladder:
                # If already on a ladder, stay centered
                self.px = current_tile_x * TILE_SIZE + (TILE_SIZE - 12) // 2 - 1
            self.vy = MOVE_SPEED
            self.state = "climbing"
        elif not (tilemap.get(current_tile_x, current_y + 1) in [EARTH, STONE, LADDER]) and not on_ladder:
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
        
        # When moving horizontally off a ladder, check both current and target positions
        if self.state == "climbing" and self.vx != 0:
            # Get the grid-aligned y position
            grid_y = (next_tile_y * TILE_SIZE)
            # If we're slightly above the grid and there's ground at either position, snap to grid
            if self.py < grid_y + TILE_SIZE and (
                tilemap.get(self.x, next_tile_y + 1) in [EARTH, STONE] or
                tilemap.get(next_tile_x, next_tile_y + 1) in [EARTH, STONE]
            ):
                self.py = grid_y
                
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

        if self.state == "falling" and tilemap.get(current_tile_x, current_y + 1) in [EARTH, STONE]:
            self.py = (self.y // 1) * TILE_SIZE
            self.vy = 0
            self.state = "idle"

    def draw(self, surface):
        cx = self.px + TILE_SIZE // 2
        cy = self.py + TILE_SIZE // 2
        pygame.draw.circle(surface, PLAYER_COLOR, (int(cx), int(cy)), 6)
        #pygame.draw.rect(surface, PLAYER_COLOR, (self.px, self.py, TILE_SIZE, TILE_SIZE))


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
                if target_tile not in [EARTH, STONE] and below_target in [EARTH, STONE, LADDER]:
                    vx = step * MOVE_SPEED

            new_positions.append((ox_px + vx, oy_px + vy))
        self.positions = new_positions

    def draw(self, surface):
        for ox_px, oy_px in self.positions:
            rect = pygame.Rect(int(ox_px), int(oy_px), TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, OPPONENT_COLOR, rect)
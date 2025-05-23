# player.py
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
        # Process horizontal movement input
        self._process_horizontal_input(keys)
        
        # Get current position info
        current_tile_x, current_y, px_in_tile = self._get_current_position()
        
        # Check ladder interaction
        on_ladder, is_climbable = self._check_ladder_interaction(tilemap, current_tile_x, current_y, px_in_tile)
        
        # Process vertical movement
        self._process_vertical_movement(keys, tilemap, current_tile_x, current_y, on_ladder, is_climbable, px_in_tile)
        
        # Update animation state
        self._update_animation_state(current_time)
        
        # Apply horizontal movement with collision detection
        self._apply_horizontal_movement(tilemap, current_tile_x, current_y)
        
        # Apply vertical movement
        self._apply_vertical_movement()
        
        # Update grid coordinates
        self._update_grid_coordinates()
        
        # Handle special actions (digging)
        self._handle_special_actions(keys, tilemap)
        
        # Check for landing after falling
        self._check_landing(tilemap, current_tile_x, current_y)

    def _process_horizontal_input(self, keys):
        """Process left/right movement input"""
        if keys[pygame.K_LEFT]:
            self.facing = DIR_LEFT
            self.vx = -MOVE_SPEED
        elif keys[pygame.K_RIGHT]:
            self.facing = DIR_RIGHT
            self.vx = MOVE_SPEED
        else:
            self.vx = 0
    
    def _get_current_position(self):
        """Calculate current position and tile information"""
        current_tile_x = int(self.px // TILE_SIZE)
        current_y = int(self.py // TILE_SIZE)
        px_in_tile = self.px % TILE_SIZE
        return current_tile_x, current_y, px_in_tile
    
    def _check_ladder_interaction(self, tilemap, current_tile_x, current_y, px_in_tile):
        """Check if player is on or near a ladder"""
        # Calculate overlap with current and next tile
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
            (tilemap.get(current_tile_x - 1, current_y) == LADDER and px_in_tile < 3) or
            (tilemap.get(current_tile_x + 1, current_y) == LADDER and px_in_tile > TILE_SIZE - 3)
        )
        
        return on_ladder, is_climbable
    
    def _find_nearest_ladder(self, tilemap, current_tile_x, current_y, px_in_tile):
        """Find the nearest ladder that can be mounted"""
        target_x = None
        if tilemap.get(current_tile_x, current_y) == LADDER:
            target_x = current_tile_x
        elif tilemap.get(current_tile_x, current_y + 1) == LADDER:
            target_x = current_tile_x
        elif tilemap.get(current_tile_x - 1, current_y) == LADDER and px_in_tile < 3:
            target_x = current_tile_x - 1
        elif tilemap.get(current_tile_x + 1, current_y) == LADDER and px_in_tile > TILE_SIZE - 3:
            target_x = current_tile_x + 1
        else:
            target_x = None
        return target_x
    
    def _center_on_ladder(self, target_x, current_tile_x, on_ladder):
        """Center the player on a ladder"""
        if target_x is not None:
            self.x = target_x
            # Center player (12px wide) on ladder (16px wide)
            self.px = target_x * TILE_SIZE + (TILE_SIZE - 12) // 2 - 1
        elif on_ladder:
            # If already on a ladder, stay centered
            self.px = current_tile_x * TILE_SIZE + (TILE_SIZE - 12) // 2 - 1
    
    def _process_vertical_movement(self, keys, tilemap, current_tile_x, current_y, on_ladder, is_climbable, px_in_tile):
        """Process climbing up/down ladders and falling"""
        # Check tile below player
        below = tilemap.get(current_tile_x, current_y + 1)
        
        # Climbing up
        if keys[pygame.K_UP] and (
            is_climbable or
            tilemap.get(current_tile_x, current_y - 1) == LADDER or
            tilemap.get(current_tile_x, current_y + 1) == LADDER):
            
            target_x = self._find_nearest_ladder(tilemap, current_tile_x, current_y, px_in_tile)
            self._center_on_ladder(target_x, current_tile_x, on_ladder)
            self.vy = -MOVE_SPEED
            self.state = "climbing"
        
        # Climbing down
        elif keys[pygame.K_DOWN] and (
            (is_climbable or tilemap.get(current_tile_x, current_y + 1) == LADDER) and
            tilemap.get(current_tile_x, current_y + 1) not in [EARTH, STONE]):
            
            target_x = self._find_nearest_ladder(tilemap, current_tile_x, current_y, px_in_tile)
            self._center_on_ladder(target_x, current_tile_x, on_ladder)
            self.vy = MOVE_SPEED
            self.state = "climbing"
        
        # Falling
        elif not (tilemap.get(current_tile_x, current_y + 1) in [EARTH, STONE, LADDER]) and not on_ladder:
            self.vy += GRAVITY
            self.state = "falling"
        
        # Standing on solid ground
        else:
            self.vy = 0
    
    def _update_animation_state(self, current_time):
        """Update animation state based on movement"""
        if self.state not in ["climbing", "falling"]:
            if self.vx != 0:
                self.state = "running"
            else:
                self.state = "idle"

        if self.state != self.prev_state:
            self.anim_frame = 0
            self.anim_timer = current_time
        self.prev_state = self.state
    
    def _apply_horizontal_movement(self, tilemap, current_tile_x, current_y):
        """Apply horizontal movement with collision detection"""
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
        
        # Move horizontally if not blocked by a wall
        if not tilemap.get(next_tile_x, next_tile_y) in [EARTH, STONE]:
            self.px = next_px
    
    def _apply_vertical_movement(self):
        """Apply vertical movement"""
        self.py += self.vy
    
    def _update_grid_coordinates(self):
        """Update grid coordinates based on pixel position"""
        self.x = int(self.px // TILE_SIZE)
        self.y = int(self.py // TILE_SIZE)
    
    def _handle_special_actions(self, keys, tilemap):
        """Handle special actions like digging"""
        if keys[pygame.K_SPACE]:
            dig_dir = -self.facing
            dig_x = self.x + dig_dir
            dig_y = self.y + 1
            if tilemap.get(dig_x, dig_y) == EARTH:
                tilemap.set(dig_x, dig_y, AIR)
    
    def _check_landing(self, tilemap, current_tile_x, current_y):
        """Check if player has landed after falling"""
        if self.state == "falling" and tilemap.get(current_tile_x, current_y + 1) in [EARTH, STONE]:
            self.py = (self.y // 1) * TILE_SIZE
            self.vy = 0
            self.state = "idle"
    
    def draw(self, surface):
        cx = self.px + TILE_SIZE // 2
        cy = self.py + TILE_SIZE // 2
        pygame.draw.circle(surface, PLAYER_COLOR, (int(cx), int(cy)), 6)
        #pygame.draw.rect(surface, PLAYER_COLOR, (self.px, self.py, TILE_SIZE, TILE_SIZE))

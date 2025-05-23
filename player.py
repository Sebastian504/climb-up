# player.py
import pygame
from constants import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a surface for the player
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(PLAYER_COLOR)
        # Create a rect for positioning (top-left corner aligned with tile)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        # Movement variables
        self.vx = 0
        self.vy = 0
        self.facing = DIR_RIGHT
        self.state = "idle"
        self.prev_state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0
    
    def get_pixel_position(self):
        """Return the current pixel position as a tuple (px, py)"""
        return (self.rect.centerx, self.rect.centery)
    
    def get_tile_position(self):
        """Calculate and return the current tile position as a tuple (x, y)"""
        # Calculate tile coordinates from pixel coordinates
        x = int(self.rect.centerx // TILE_SIZE)
        y = int(self.rect.centery // TILE_SIZE)
        return (x, y)
    
    def get_center_position(self):
        """Return the center pixel position as a tuple (center_x, center_y)"""
        return self.get_pixel_position()

    def handle_input(self, keys, tilemap, current_time):
        # Process horizontal movement input
        self._process_horizontal_input(keys)
        
        # Get current position info
        current_tile_x, current_y, px_in_tile = self._get_current_position()
        
        # Process vertical movement
        self._process_vertical_movement(keys, tilemap, current_tile_x, current_y, px_in_tile)
        
        # Update animation state
        self._update_animation_state(current_time)
        
        # Apply horizontal movement with collision detection
        self._apply_horizontal_movement(tilemap, current_tile_x, current_y)
        
        # Apply vertical movement
        self._apply_vertical_movement()
        
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
        current_tile_x = int(self.rect.centerx // TILE_SIZE)
        current_y = int(self.rect.centery // TILE_SIZE)
        px_in_tile = (self.rect.centerx - TILE_SIZE // 2) % TILE_SIZE
        return current_tile_x, current_y, px_in_tile
    
    def _check_ladder_interaction(self, tilemap):
        """Check if player is on or near a ladder"""
        position = self.get_tile_position()
        on_ladder = tilemap.get(position[0], position[1]) == LADDER
        
        return on_ladder
    
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
    
    def _center_on_ladder(self):
        """Center the player on a ladder by snapping to the center of the current tile"""
        # compute the x coordinate to be in the middle of the current tile
        self.rect.centerx = self.get_tile_position()[0] * TILE_SIZE + TILE_SIZE // 2
    
    def _process_vertical_movement(self, keys, tilemap, current_tile_x, current_y, px_in_tile):
        """Process climbing up/down ladders and falling"""
        # Check tile below player
        below = tilemap.get(current_tile_x, current_y + 1)
        on_ladder = self._check_ladder_interaction(tilemap)
        lower_edge_on_ladder = tilemap.get_tile_by_pixel_coords(self.rect.centerx, self.rect.bottom - 1) == LADDER
        above_ladder = tilemap.get(current_tile_x, current_y + 1) == LADDER
        
        # Climbing up
        if keys[pygame.K_UP]:
            #print(lower_edge_on_ladder, tilemap.get_tile_by_pixel_coords(self.rect.centerx, self.rect.bottom))
            if lower_edge_on_ladder:            
                self._center_on_ladder()
                self.vy = -MOVE_SPEED
                self.state = "climbing"
            else:
                self.vy = 0
                self.state = "idle"
            
        
        # Climbing down
        elif keys[pygame.K_DOWN]:
        
            if on_ladder:
                self._center_on_ladder()
                # check that the bottom edge of the player has not yet reached the ground below the ladder
                bottom_of_player = self.rect.bottom
                tile_at_lower_end = tilemap.get_tile_by_pixel_coords(self.rect.centerx, bottom_of_player)
                if tilemap.is_ground(tile_at_lower_end):
                    self.vy = 0
                else:
                    self.vy = MOVE_SPEED
                    self.state = "climbing"
            elif above_ladder:
                self._center_on_ladder()
                self.vy = MOVE_SPEED
                self.state = "climbing"
            else:
                self.vy = 0
                self.state = "idle"
        
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
        next_x = self.rect.x + self.vx
        edge_x = next_x + TILE_SIZE - 1 if self.vx > 0 else next_x
        next_tile_x = int(edge_x // TILE_SIZE)
        next_tile_y = int(self.rect.y // TILE_SIZE)
        
        # When moving horizontally off a ladder, check both current and target positions
        if self.state == "climbing" and self.vx != 0:
            # Get the grid-aligned y position
            grid_y = (next_tile_y * TILE_SIZE)
            # If we're slightly above the grid and there's ground at either position, snap to grid
            current_tile_x = int(self.rect.x // TILE_SIZE)
            if self.rect.y < grid_y + TILE_SIZE and (
                tilemap.get(current_tile_x, next_tile_y + 1) in [EARTH, STONE] or
                tilemap.get(next_tile_x, next_tile_y + 1) in [EARTH, STONE]
            ):
                self.rect.y = grid_y
        
        # Move horizontally if not blocked by a wall
        if not tilemap.get(next_tile_x, next_tile_y) in [EARTH, STONE]:
            self.rect.x = next_x
    
    def _apply_vertical_movement(self):
        """Apply vertical movement"""
        self.rect.y += self.vy
    
    def _handle_special_actions(self, keys, tilemap):
        """Handle special actions like digging"""
        if keys[pygame.K_SPACE]:
            dig_dir = -self.facing
            # Calculate tile position from pixel position
            x, y = self.get_tile_position()
            dig_x = x + dig_dir
            dig_y = y + 1
            if tilemap.get(dig_x, dig_y) == EARTH:
                tilemap.set(dig_x, dig_y, AIR)
    
    def _check_landing(self, tilemap, current_tile_x, current_y):
        """Check if player has landed after falling"""
        if self.state == "falling" and tilemap.get(current_tile_x, current_y + 1) in [EARTH, STONE]:
            # Snap to grid when landing
            self.rect.y = current_y * TILE_SIZE
            self.vy = 0
            self.state = "idle"
    
    def draw(self, surface):
        # Draw the sprite directly to the surface
        surface.blit(self.image, self.rect)
        
        # Draw a circle at the center for debug purposes
        pygame.draw.circle(surface, (0, 255, 0), (int(self.rect.centerx), int(self.rect.centery)), 4)

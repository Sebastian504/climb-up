# character.py
import pygame
from constants import *

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        # Create a surface for the character
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
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

    def _snap_to_current_tile_x(self):
        """Snap the player's x position to the center of the current tile"""
        self.rect.x = int(self.rect.centerx // TILE_SIZE) * TILE_SIZE

    def _snap_to_current_tile_y(self):
        """Snap the player's y position to the center of the current tile"""
        self.rect.y = int(self.rect.centery // TILE_SIZE) * TILE_SIZE

    def _snap_to_current_tile_xy(self):
        self.snap_to_current_tile_x()
        self.snap_to_current_tile_y()

    def handle_input(self, keys, tilemap, current_time):
        bottom_y = self.rect.bottom   
        tile_just_below_bottom = tilemap.get_tile_by_pixel_coords(self.rect.centerx, bottom_y + 1)
        # if we are not supported below the bottom pixel, then fall
        if not (tilemap.is_standable(tile_just_below_bottom) or self._check_on_ladder(tilemap)):
            self.vy += GRAVITY
            self.vx = 0
            self.state = "falling"
        # else look at input in keys and act accordingly:
        else:
            self.state = "" # needs to be set
            self._process_horizontal_input(keys)
            self.vy = 0
            
            # if we want to go up
            if keys[pygame.K_UP]:
                on_ladder = self._check_bottom_on_ladder(tilemap)
                if on_ladder:
                    self.vy = -MOVE_SPEED
                    self.state = "climbing"
            elif keys[pygame.K_DOWN]:
                on_ladder = self._check_on_ladder(tilemap)
                # we can only move down if we are on a ladder and have not yet reached the ground
                if on_ladder and not self._check_bottom_on_ground(tilemap):
                    self.vy = MOVE_SPEED
                    self.state = "climbing"
                    
        self._update_animation_state(current_time)
        # Handle special actions (digging)
        self._handle_special_actions(keys, tilemap)    

        # Apply horizontal movement with collision detection
        self._apply_horizontal_movement(tilemap)
        
        # snap to tile in x direction depending on movement type
        self._apply_snapping()

        # Apply vertical movement
        self._apply_vertical_movement(tilemap)    

    def _apply_snapping(self):
        if self.state in ["climbing", "falling"]:
            self._snap_to_current_tile_x()
        if self.state in ["running"]:
            self._snap_to_current_tile_y()

    def _check_on_ladder(self, tilemap):
        """Check if player is on or directly above a ladder"""
        position = self.get_tile_position()
        on_ladder = tilemap.get(position[0], position[1]) == LADDER or tilemap.get(position[0], position[1] + 1) == LADDER
        return on_ladder

    def _check_bottom_on_ladder(self, tilemap):
        """Check is bottom pixel of player is on a ladder tile"""
        on_ladder = tilemap.get_tile_by_pixel_coords(self.rect.centerx, self.rect.bottom - 1) == LADDER 
        return on_ladder

    def _check_current_tile_is_ladder(self, tilemap):
        """Check if player is on the ladder. Above is not enough (more strict that _check_on_ladder)"""
        position = self.get_tile_position()
        on_ladder = tilemap.get(position[0], position[1]) == LADDER
        return on_ladder        

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
    
    def _check_bottom_on_ground(self, tilemap):
        """Check if bottom pixel of player is on a ground tile"""
        on_ground = tilemap.get_tile_by_pixel_coords(self.rect.centerx, self.rect.bottom) in [EARTH, STONE]
        return on_ground

    def _check_top_against_ground(self, tilemap):
        """Check if the top of the player touches ground from the bottom"""
        against_ground = tilemap.get_tile_by_pixel_coords(self.rect.centerx, self.rect.top - 1) in [EARTH, STONE]
        return against_ground

    def _apply_vertical_movement(self, tilemap):
        """Apply vertical movement"""
        if self.vy > 0:
            if not self._check_bottom_on_ground(tilemap):
                self.rect.y += self.vy
            else:
                self._snap_to_current_tile_y()
        elif self.vy < 0:
            if not self._check_top_against_ground(tilemap):
                self.rect.y += self.vy
            else:
                self._snap_to_current_tile_y()

    def _center_on_tile(self):
        self._snap_to_current_tile_x()

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
    
    def _apply_horizontal_movement(self, tilemap):
        """Apply horizontal movement with collision detection"""
        next_x = self.rect.x + self.vx
        edge_x = next_x + TILE_SIZE - 1 if self.vx > 0 else next_x
        next_tile_x = int(edge_x // TILE_SIZE)
        next_tile_y = int(self.rect.y // TILE_SIZE)
        
        # Move horizontally if not blocked by a wall
        if not tilemap.get(next_tile_x, next_tile_y) in [EARTH, STONE]:
            self.rect.x = next_x

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
    
    def draw(self, surface):
        # Draw the sprite directly to the surface
        surface.blit(self.image, self.rect)
        
        # Draw a circle at the center for debug purposes
        pygame.draw.circle(surface, (0, 255, 0), (int(self.rect.centerx), int(self.rect.centery)), 4)

# opponent.py
import pygame
from constants import *

class Opponent(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a surface for the opponent
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(OPPONENT_COLOR)
        # Create a rect for positioning (top-left corner aligned with tile)
        self.rect = self.image.get_rect()
        # Fix the x-coordinate to match the tile position exactly
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        # Movement variables
        self.vx = 0  # Horizontal velocity
        self.vy = 0  # Vertical velocity
    
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
    
    def update(self, player, tilemap):
        # Get current tile coordinates
        x, y = self.get_tile_position()
        
        # Initialize velocity
        self.vx = 0
        self.vy = 0
        
        # Get current tile information
        current_tile = tilemap.get(x, y)      # Tile the opponent is on
        below_tile = tilemap.get(x, y + 1)    # Tile below the opponent
        
        # Calculate distance to player
        player_center_x, player_center_y = player.get_center_position()
        center_x, center_y = self.get_center_position()
        dx = player_center_x - center_x  # Horizontal distance to player
        dy = player_center_y - center_y  # Vertical distance to player
        
        # Determine horizontal direction toward player
        step = 1 if dx > 0 else -1 if dx < 0 else 0
        
        # Check if we're falling (no solid ground beneath us and not on a ladder)
        is_falling = below_tile == AIR and current_tile != LADDER
        
        # STEP 1: Apply gravity if needed
        if is_falling:
            self.vy = MOVE_SPEED  # Fall down
        # STEP 2: If not falling, determine movement based on player position
        else:
            # Check if we're on a ladder
            on_ladder = current_tile == LADDER
            
            # If on a ladder, decide whether to climb up/down
            if on_ladder:
                # Climb up if player is above
                if dy < 0 and tilemap.get(x, y-1) != EARTH and tilemap.get(x, y-1) != STONE:
                    self.vy = -MOVE_SPEED
                # Climb down if player is below
                elif dy > 0 and below_tile != EARTH and below_tile != STONE:
                    self.vy = MOVE_SPEED
            
            # Decide on horizontal movement
            target_tile = tilemap.get(x + step, y)  # Tile we would move into
            below_target = tilemap.get(x + step, y + 1)  # Tile below our target
            
            # Only move horizontally if we won't hit a wall
            if target_tile != EARTH and target_tile != STONE:
                # Check if moving would cause a fall
                would_fall = below_target == AIR and target_tile != LADDER
                
                # Only move if it's safe or if player is below (worth falling for)
                if not would_fall or dy > 0:
                    self.vx = step * MOVE_SPEED
        
        # Apply movement with collision detection
        self._apply_movement(tilemap)
    
    def _apply_movement(self, tilemap):
        # Apply horizontal movement first
        if self.vx != 0:
            # Calculate next position
            next_x = self.rect.x + self.vx
            
            # Check for collision with walls
            next_tile_x = int((next_x + (TILE_SIZE-1 if self.vx > 0 else 0)) // TILE_SIZE)
            current_tile_y = int(self.rect.centery // TILE_SIZE)
            
            # Don't move into walls
            if tilemap.get(next_tile_x, current_tile_y) not in [EARTH, STONE]:
                self.rect.x = next_x
        
        # Then apply vertical movement
        if self.vy != 0:
            # Calculate next position
            next_y = self.rect.y + self.vy
            
            # Check for collision with floor/ceiling
            current_tile_x = int(self.rect.centerx // TILE_SIZE)
            next_tile_y = int((next_y + (TILE_SIZE-1 if self.vy > 0 else 0)) // TILE_SIZE)
            
            # Don't move into walls
            if tilemap.get(current_tile_x, next_tile_y) not in [EARTH, STONE]:
                self.rect.y = next_y
            else:
                # If we hit the ground, stop falling
                if self.vy > 0:
                    # Align to the top of the tile we hit
                    self.rect.y = next_tile_y * TILE_SIZE - TILE_SIZE
    
    def draw(self, surface):
        # Draw the sprite directly to the surface
        surface.blit(self.image, self.rect)
        
        # Draw a circle at the center for debug purposes
        pygame.draw.circle(surface, (255, 0, 0), (int(self.rect.centerx), int(self.rect.centery)), 4)

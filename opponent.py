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
        return (self.rect.x + TILE_SIZE // 2, self.rect.y + TILE_SIZE // 2)
    
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
        
        # Determine if player is above or below
        player_is_above = dy < 0
        player_is_below = dy > 0
        
        # Determine horizontal direction toward player
        step = (dx > 0) - (dx < 0)  # Move right if player is to the right, otherwise left, not at all if player is directly above or below
        
        # Check tiles in potential movement directions
        x, y = self.get_tile_position()
        target_tile = tilemap.get(x + step, y)      # Tile we would move into horizontally
        below_target = tilemap.get(x + step, y + 1)  # Tile below our target position
        above_tile = tilemap.get(x, y - 1)           # Tile above us
        #print("ttile=", target_tile, " btile=", below_target, " atile=", above_tile, " step=", step, " position=", (self.px, self.py), " tilepos=", self.get_tile_position())
        
        # Check if we're falling (not on solid ground or ladder)
        is_falling = below_tile == AIR and current_tile != LADDER
        
        # Check if moving horizontally would cause a fall
        would_fall = target_tile not in [EARTH, STONE] and below_target == AIR
        
        # RULE 1: Apply gravity if falling
        if is_falling:
            self.vy = MOVE_SPEED  # Fall down
        
        # RULE 2: Horizontal movement
        else:  # Only move horizontally if not falling
            # Check if moving would bring us closer to player AND we are not blocked:
            if step != 0 and target_tile not in [EARTH, STONE]:
                # If moving would cause a fall
                if would_fall:
                    # Only fall if player is below us
                    if player_is_below:
                        self.vx = step * MOVE_SPEED
                else:
                    # Safe to move horizontally (won't fall)
                    self.vx = step * MOVE_SPEED
            # RULE 3: Climb ladders based on player position
            elif current_tile == LADDER:  # We're on a ladder
                if player_is_above and above_tile not in [EARTH, STONE]:
                    # Climb up if player is above and no obstacle
                    self.vy = -MOVE_SPEED
                elif player_is_below and below_tile not in [EARTH, STONE]:
                    # Climb down if player is below and no obstacle
                    self.vy = MOVE_SPEED
                # For horizontal movement from ladder, explicitly check target tile
                elif target_tile not in [EARTH, STONE]:
                    # Double-check the target tile at the exact position we'd move to
                    x, y = self.get_tile_position()
                    next_tile_x = x + step
                    if tilemap.get(next_tile_x, y) not in [EARTH, STONE]:
                        # Only move horizontally if the target tile is not a wall
                        self.vx = step * MOVE_SPEED
            else: # don't move   
                self.vx = 0
                self.vy = 0
        

        
        # Calculate next position in pixel coordinates
        next_x = self.rect.x + self.vx
        next_y = self.rect.y + self.vy
        
        # Convert to tile coordinates for final collision check
        next_tile_x = int(next_x // TILE_SIZE)
        next_tile_y = int(next_y // TILE_SIZE)
        
        # If moving horizontally, check the leading edge
        if self.vx > 0:  # Moving right
            edge_x = next_x + TILE_SIZE - 1
            edge_tile_x = int(edge_x // TILE_SIZE)
            # Check if we would move into a wall
            if tilemap.get(edge_tile_x, next_tile_y) in [EARTH, STONE]:
                # Don't allow moving into walls
                next_x = self.rect.x
        elif self.vx < 0:  # Moving left
            edge_tile_x = int(next_x // TILE_SIZE)
            # Check if we would move into a wall
            if tilemap.get(edge_tile_x, next_tile_y) in [EARTH, STONE]:
                # Don't allow moving into walls
                next_x = self.rect.x
        
        # Update the position
        self.rect.x = next_x
        self.rect.y = next_y
    
    def draw(self, surface):
        # Draw the sprite directly to the surface
        surface.blit(self.image, self.rect)
        
        # Draw a circle at the center for debug purposes
        pygame.draw.circle(surface, (255, 0, 0), (int(self.rect.centerx), int(self.rect.centery)), 4)

# opponent.py
import pygame
from constants import *

class Opponents:
    def __init__(self, tile_positions):
        self.positions = [(x * TILE_SIZE, y * TILE_SIZE) for x, y in tile_positions]

    def update(self, player, tilemap):
        new_positions = []
        for ox_px, oy_px in self.positions:
            # Convert pixel coordinates to tile coordinates for logic
            ox = int(ox_px // TILE_SIZE)
            oy = int(oy_px // TILE_SIZE)
            
            # Initialize velocity
            vx, vy = 0, 0
            
            # Get current tile information
            current_tile = tilemap.get(ox, oy)      # Tile the opponent is on
            below_tile = tilemap.get(ox, oy + 1)    # Tile below the opponent
            
            # Calculate distance to player
            dx = player.px - ox_px  # Horizontal distance to player
            dy = player.py - oy_px  # Vertical distance to player
            
            # Determine if player is above or below
            player_is_above = dy < 0
            player_is_below = dy > 0
            
            # Determine horizontal direction toward player
            step = 1 if dx > 0 else -1  # Move right if player is to the right, otherwise left
            
            # Check tiles in potential movement directions
            target_tile = tilemap.get(ox + step, oy)      # Tile we would move into horizontally
            below_target = tilemap.get(ox + step, oy + 1)  # Tile below our target position
            above_tile = tilemap.get(ox, oy - 1)           # Tile above us
            
            # Check if we're falling (not on solid ground or ladder)
            is_falling = below_tile == AIR and current_tile != LADDER
            
            # Check if moving horizontally would cause a fall
            would_fall = target_tile not in [EARTH, STONE] and below_target == AIR
            
            # RULE 1: Apply gravity if falling
            if is_falling:
                vy = MOVE_SPEED  # Fall down
            
            # RULE 2: Climb ladders based on player position
            elif current_tile == LADDER:  # We're on a ladder
                if player_is_above and above_tile not in [EARTH, STONE]:
                    # Climb up if player is above and no obstacle
                    vy = -MOVE_SPEED
                elif player_is_below and below_tile not in [EARTH, STONE]:
                    # Climb down if player is below and no obstacle
                    vy = MOVE_SPEED
                elif target_tile not in [EARTH, STONE]:
                    # If we can't climb toward player, try moving horizontally
                    # Only if the target tile is not a wall
                    vx = step * MOVE_SPEED
            
            # RULE 3: Horizontal movement
            elif not is_falling:  # Only move horizontally if not falling
                # Check if moving would bring us closer to player
                moving_toward_player = (step > 0 and dx > 0) or (step < 0 and dx < 0)
                
                if moving_toward_player and target_tile not in [EARTH, STONE]:
                    # If moving would cause a fall
                    if would_fall:
                        # Only fall if player is below us
                        if player_is_below:
                            vx = step * MOVE_SPEED
                    else:
                        # Safe to move horizontally (won't fall)
                        vx = step * MOVE_SPEED
            
            # Apply movement in pixel coordinates
            next_x = ox_px + vx
            next_y = oy_px + vy
            
            # Add the final position
            new_positions.append((next_x, next_y))
        
        self.positions = new_positions
    
    def draw(self, surface):
        for ox_px, oy_px in self.positions:
            rect = pygame.Rect(int(ox_px), int(oy_px), TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, OPPONENT_COLOR, rect)

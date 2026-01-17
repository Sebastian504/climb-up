# opponent.py
import pygame
from character import Character
from constants import *

class Opponent(Character):
    def __init__(self, x, y):
        super().__init__(x, y, OPPONENT_COLOR)
        # AI state variables
        self.ai_keys = {}
        self.update_timer = 0
    
    def update(self, player, tilemap):
        """Update the opponent based on AI decisions"""
        # Reset AI key presses
        self.ai_keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_SPACE: False
        }
        
        # Make AI decisions every frame for full speed movement
        self._make_ai_decisions(player, tilemap)
        
        # Use the Character's handle_input method with our simulated key presses
        current_time = pygame.time.get_ticks()
        self.handle_input(self.ai_keys, tilemap, current_time)
    
    def _make_ai_decisions(self, player, tilemap):
        """Make AI decisions and set key presses accordingly"""
        # Get positions
        player_x, player_y = player.get_tile_position()
        opponent_x, opponent_y = self.get_tile_position()
        
        # Calculate distances
        dx = player_x - opponent_x
        dy = player_y - opponent_y
        
        # Check surroundings
        current_tile = tilemap.get(opponent_x, opponent_y)
        below_tile = tilemap.get(opponent_x, opponent_y + 1)
        above_tile = tilemap.get(opponent_x, opponent_y - 1)
        left_tile = tilemap.get(opponent_x - 1, opponent_y)
        right_tile = tilemap.get(opponent_x + 1, opponent_y)
        
        # Check if we're on or near a ladder
        on_ladder = current_tile == LADDER
        ladder_below = below_tile == LADDER
        ladder_above = above_tile == LADDER
        
        # DECISION 1: Vertical movement (ladders)
        if on_ladder or ladder_below:
            # If player is above us, try to climb up
            if dy < 0 and (on_ladder or ladder_above):
                self.ai_keys[pygame.K_UP] = True
            # If player is below us, try to climb down
            elif dy > 0 and (on_ladder or ladder_below):
                self.ai_keys[pygame.K_DOWN] = True
        
        # DECISION 2: Horizontal movement
        # Prioritize vertical movement if significant vertical distance
        if abs(dy) <= 3 or not (on_ladder or ladder_below):
            # Move left toward player
            if dx < 0 and left_tile not in [EARTH, STONE]:
                self.ai_keys[pygame.K_LEFT] = True
            # Move right toward player
            elif dx > 0 and right_tile not in [EARTH, STONE]:
                self.ai_keys[pygame.K_RIGHT] = True
        
        # DECISION 3: Look for ladders if significant vertical distance
        if abs(dy) > 3 and not on_ladder:
            # Check for ladders to the left
            if left_tile == LADDER or tilemap.get(opponent_x - 1, opponent_y + 1) == LADDER:
                self.ai_keys[pygame.K_LEFT] = True
            # Check for ladders to the right
            elif right_tile == LADDER or tilemap.get(opponent_x + 1, opponent_y + 1) == LADDER:
                self.ai_keys[pygame.K_RIGHT] = True
    
    def draw(self, surface):
        # Draw the sprite directly to the surface
        surface.blit(self.image, self.rect)
        
        # Draw a circle at the center for debug purposes
        pygame.draw.circle(surface, (255, 0, 0), (int(self.rect.centerx), int(self.rect.centery)), 4)

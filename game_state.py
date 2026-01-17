# game_state.py
import pygame
import time
from tilemap import TileMap
from constants import PLAYER, OPPONENT, DIAMOND, AIR, EXIT
from player import Player
from opponent import Opponent
from constants import TILE_SIZE

# Define status bar height as a constant
STATUS_BAR_HEIGHT = 30

class Game:
    def __init__(self, level_filename):
        self.tilemap = TileMap(level_filename)
        self.player = None
        self.opponents = []
        self.running = True
        self.diamonds_remaining = 0
        
        # Timer initialization
        self.timer_seconds = self.tilemap.timer_seconds
        self.start_time = time.time()
        self.time_remaining = self.timer_seconds
        
        # Diamond tracking
        self.diamonds_collected = 0
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.opponents_group = pygame.sprite.Group()
        
        # Find player, opponents, and count diamonds in the level
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                tile = self.tilemap.get(x, y)
                if tile == PLAYER:
                    self.player = Player(x, y)
                    self.all_sprites.add(self.player)
                    self.tilemap.set(x, y, AIR)
                elif tile == OPPONENT:
                    # Create opponent at the correct tile position
                    opponent = Opponent(x, y)  # Removed incorrect +1 offset
                    self.opponents.append(opponent)
                    self.opponents_group.add(opponent)
                    self.all_sprites.add(opponent)
                    self.tilemap.set(x, y, AIR)
                elif tile == DIAMOND:
                    self.diamonds_remaining += 1
        
        # Set total diamonds after counting them in the level
        self.total_diamonds = self.diamonds_remaining

    def check_game_over(self):
        # Check if player collided with an opponent
        if pygame.sprite.spritecollideany(self.player, self.opponents_group):
            return True
        
        # Check if time ran out
        if self.time_remaining <= 0:
            return True
        
        # Check if player fell to the bottom of the level
        player_x, player_y = self.player.get_tile_position()
        if player_y >= self.tilemap.height - 1:
            return True
            
        return False

    def check_win_condition(self):
        # Can only win if all diamonds are collected
        if self.diamonds_remaining > 0:
            return False
        
        # Win condition: All diamonds collected and player reached the top row
        player_x, player_y = self.player.get_tile_position()
        return player_y == 0 or self.tilemap.get(player_x, player_y) == EXIT

    def check_diamond_collection(self):
        # Check if player is on a diamond
        player_x, player_y = self.player.get_tile_position()
        if self.tilemap.get(player_x, player_y) == DIAMOND:
            self.tilemap.set(player_x, player_y, AIR)
            self.diamonds_remaining -= 1
            self.diamonds_collected += 1
            
    def update_timer(self):
        # Calculate time remaining
        elapsed = time.time() - self.start_time
        self.time_remaining = max(0, self.timer_seconds - elapsed)
        
    def get_timer_string(self):
        # Format the remaining time as mm:ss
        minutes = int(self.time_remaining) // 60
        seconds = int(self.time_remaining) % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def get_diamonds_collected(self):
        # Return the number of diamonds collected
        return self.diamonds_collected
        
    def get_total_diamonds(self):
        # Return the total number of diamonds in the level
        return self.total_diamonds
        
    def draw(self, screen, debug_overlay=False, draw_game_info_func=None, draw_debug_overlay_func=None):
        """Draw the game state to the screen
        
        Args:
            screen: The pygame surface to draw on
            debug_overlay: Whether to draw the debug overlay
            draw_game_info_func: Function to draw game info (timer, diamonds)
            draw_debug_overlay_func: Function to draw debug overlay
        """
        # Draw everything
        screen.fill((0, 0, 0))  # Black background
        
        # Draw the tilemap with offset for status bar
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                tile = self.tilemap.get(x, y)
                if tile != AIR:  # Don't draw air tiles
                    self.tilemap.draw_tile(screen, x, y, tile, y_offset=STATUS_BAR_HEIGHT)
        
        # Store original sprite positions
        original_positions = []
        for sprite in self.all_sprites:
            original_positions.append(sprite.rect.copy())
            sprite.rect.y += STATUS_BAR_HEIGHT
        
        # Draw all sprites at once using the sprite group
        self.all_sprites.draw(screen)
        
        # Restore original sprite positions
        for i, sprite in enumerate(self.all_sprites):
            sprite.rect = original_positions[i]
        
        # Draw game info (timer and diamond counter) if function provided
        if draw_game_info_func:
            draw_game_info_func(screen, self)
        
        # Draw debug overlay if enabled and function provided
        if debug_overlay and draw_debug_overlay_func:
            draw_debug_overlay_func(screen, self, y_offset=STATUS_BAR_HEIGHT)
        
        # Update the display
        pygame.display.flip()
    
    def update(self, keys, current_time):
        """Update all game state in a single method
        
        Args:
            keys: The current keyboard state
            current_time: The current game time in milliseconds
        """
        # Update player based on input
        self.player.handle_input(keys, self.tilemap, current_time)
        
        # Check if player collected a diamond
        self.check_diamond_collection()
        
        # Update each opponent individually
        for opponent in self.opponents:
            opponent.update(self.player, self.tilemap)
            
        # Update the timer
        self.update_timer()
        
    def save_level(self, filename):
        """Save the current level state to a file"""
        with open(filename, 'w') as f:
            # Write the timer as the first line
            minutes = int(self.timer_seconds) // 60
            seconds = int(self.timer_seconds) % 60
            f.write(f"{minutes:02d}:{seconds:02d}\n")
            
            # Get player and opponent positions
            player_pos = None
            if self.player:
                player_pos = self.player.get_tile_position()
                
            opponent_positions = []
            for opponent in self.opponents:
                opponent_positions.append(opponent.get_tile_position())
            
            # Use the tilemap's save_to_file method to write the level data
            self.tilemap.save_to_file(f, True, player_pos, opponent_positions)

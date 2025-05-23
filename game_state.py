# game_state.py
import pygame
from tilemap import TileMap
from constants import PLAYER, OPPONENT, DIAMOND, AIR, EXIT
from player import Player
from opponent import Opponent
from constants import TILE_SIZE

class GameState:
    def __init__(self, level_filename):
        self.tilemap = TileMap(level_filename)
        self.player = None
        self.opponents = []
        self.running = True
        self.diamonds_remaining = 0
        
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
                    # Add 1 to x to fix the positioning issue
                    opponent = Opponent(x + 1, y)
                    self.opponents.append(opponent)
                    self.opponents_group.add(opponent)
                    self.all_sprites.add(opponent)
                    self.tilemap.set(x, y, AIR)
                elif tile == DIAMOND:
                    self.diamonds_remaining += 1

    def check_game_over(self):
        # Use pygame's built-in sprite collision detection
        if pygame.sprite.spritecollideany(self.player, self.opponents_group):
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

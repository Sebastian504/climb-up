# game_state.py
import pygame
from tilemap import TileMap
from constants import PLAYER, OPPONENT, DIAMOND, AIR, EXIT
from player import Player
from opponent import Opponents
from constants import TILE_SIZE

class GameState:
    def __init__(self, level_filename):
        self.tilemap = TileMap(level_filename)
        self.player = None
        self.opponents = Opponents([])
        self.running = True
        self.diamonds_remaining = 0
        self.opponent_positions = []
        
        # Find player, opponents, and count diamonds in the level
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                tile = self.tilemap.get(x, y)
                if tile == PLAYER:
                    self.player = Player(x, y)
                    self.tilemap.set(x, y, AIR)
                elif tile == OPPONENT:
                    self.opponent_positions.append((x, y))
                    self.tilemap.set(x, y, AIR)
                elif tile == DIAMOND:
                    self.diamonds_remaining += 1
        
        # Initialize opponents after collecting all positions
        self.opponents = Opponents(self.opponent_positions)

    def check_game_over(self):
        player_rect = pygame.Rect(self.player.px, self.player.py, TILE_SIZE, TILE_SIZE)
        for ox_px, oy_px in self.opponents.positions:
            opp_rect = pygame.Rect(ox_px, oy_px, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(opp_rect):
                return True
        return False

    def check_win_condition(self):
        # Can only win if all diamonds are collected
        if self.diamonds_remaining > 0:
            return False
        
        # Win condition: All diamonds collected and player reached the top row
        return self.player.y == 0 or self.tilemap.get(self.player.x, self.player.y) == EXIT

    def check_diamond_collection(self):
        # Check if player is on a diamond
        if self.tilemap.get(self.player.x, self.player.y) == DIAMOND:
            self.tilemap.set(self.player.x, self.player.y, AIR)
            self.diamonds_remaining -= 1

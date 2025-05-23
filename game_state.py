# game_state.py
import pygame
from tilemap import load_level_from_file
from entities import Player, Opponents
from constants import TILE_SIZE

class GameState:
    def __init__(self, level_filename):
        self.tilemap, player_start, opp_tiles = load_level_from_file(level_filename)
        self.player = Player(*player_start)
        self.opponents = Opponents(opp_tiles)
        self.running = True

    def check_game_over(self):
        px, py = self.player.px, self.player.py
        player_rect = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)
        for ox_px, oy_px in self.opponents.positions:
            opp_rect = pygame.Rect(ox_px, oy_px, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(opp_rect):
                return True
        return False

    def check_win_condition(self):
        return self.player.py <= 0

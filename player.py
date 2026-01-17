# player.py
from character import Character
from constants import *

class Player(Character):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_COLOR)

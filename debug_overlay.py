# debug_overlay.py
import pygame
from constants import *

def draw_debug_overlay(screen, game, y_offset=0):
    """Draw debug information including coordinates and grid"""
    font = pygame.font.SysFont(None, 18)
    
    # Player debug
    tx, ty = game.player.get_tile_position()
    px, py = game.player.get_pixel_position()
    t, b = game.player.rect.top, game.player.rect.bottom
    center_x, center_y = game.player.get_center_position()
    
    # Draw a circle at the center of the player
    pygame.draw.circle(screen, (0,255,0), (center_x, center_y + y_offset), 4)
    
    # Draw a rectangle around the player's tile
    pygame.draw.rect(screen, (0,255,0), (tx*TILE_SIZE, ty*TILE_SIZE + y_offset, TILE_SIZE, TILE_SIZE), 1)
    
    # Display both tile and pixel coordinates
    state = game.player.state 
    player_text = font.render(f"P: ({tx},{ty})({int(t)},{int(b)}){state}", True, (0,255,0))
    screen.blit(player_text, (int(px)+TILE_SIZE, int(py) + y_offset))
    
    # Opponent debug
    for idx, opponent in enumerate(game.opponents):
        tx, ty = opponent.get_tile_position()
        px, py = opponent.get_pixel_position()
        center_x, center_y = opponent.get_center_position()
        
        # Draw a circle at the center of the opponent
        pygame.draw.circle(screen, (255,0,0), (center_x, center_y + y_offset), 4)
        
        # Draw a rectangle around the opponent's tile
        pygame.draw.rect(screen, (255,0,0), (tx*TILE_SIZE, ty*TILE_SIZE + y_offset, TILE_SIZE, TILE_SIZE), 1)
        
        # Display both tile and pixel coordinates
        opp_text = font.render(f"O{idx}: ({tx},{ty}) px=({int(px)},{int(py)})", True, (255,0,0))
        screen.blit(opp_text, (int(px)+TILE_SIZE, int(py) + y_offset))
    
    # Draw grid points
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            pygame.draw.rect(screen, (255,100,100), (x * TILE_SIZE, y * TILE_SIZE + y_offset, 1, 1))

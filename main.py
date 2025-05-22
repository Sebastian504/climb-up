# main.py
import pygame
import sys
from constants import *
from game_state import GameState

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Climb Up")
    clock = pygame.time.Clock()

    game = GameState()

    while game.running:
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False

        game.player.handle_input(keys, game.tilemap, current_time)
        game.opponents.update(game.player, game.tilemap)

        if game.check_game_over():
            game.running = False

        if current_time - game.player.anim_timer >= 16:
            if game.player.state in ["running", "climbing"]:
                game.player.anim_frame = (game.player.anim_frame + 1) % 8
                game.player.anim_timer = current_time

        screen.fill((0, 0, 0))
        game.tilemap.draw(screen)
        game.player.draw(screen)
        game.opponents.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

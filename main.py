# main.py
import pygame
import sys
from constants import *
from game_state import GameState

def show_message(screen, text):
    font = pygame.font.SysFont(None, 72)
    message = font.render(text, True, (255, 255, 255))
    rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(message, rect)

    subfont = pygame.font.SysFont(None, 36)
    prompt = subfont.render("Press any key to play again", True, (200, 200, 200))
    subrect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(prompt, subrect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Climb Up")
    clock = pygame.time.Clock()

    while True:
        game = GameState()

        while game.running:
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            game.player.handle_input(keys, game.tilemap, current_time)
            game.opponents.update(game.player, game.tilemap)

            if game.check_game_over():
                show_message(screen, "Game Over")
                break

            if game.check_win_condition():
                show_message(screen, "You Win!")
                break

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

if __name__ == "__main__":
    main()
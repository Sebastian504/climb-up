# main.py
import pygame
import sys
import argparse
from constants import *
from game_state import GameState

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

def clear_screen(screen):
    screen.fill(BLACK)
    pygame.display.flip()

def show_message(screen, text, subtext=None, wait_for_input=True, clear=False):
    if clear:
        clear_screen(screen)
    else:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)  # 50% transparent
        screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont(None, 72)
    message = font.render(text, True, WHITE)
    rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(message, rect)

    if subtext:
        subfont = pygame.font.SysFont(None, 36)
        prompt = subfont.render(subtext, True, GRAY)
        subrect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(prompt, subrect)

    pygame.display.flip()

    if wait_for_input:
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False

def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                return

def parse_arguments():
    parser = argparse.ArgumentParser(description='Climb Up - A puzzle platformer game')
    parser.add_argument('--level', type=int, default=1, help='Starting level number (default: 1)')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Climb Up")
    clock = pygame.time.Clock()

    level_index = args.level  # Start at the specified level
    debug_overlay = True  # Toggle with F3

    while True:
        level_file = f"levels/level{level_index:03d}.lvl"
        try:
            game = GameState(level_file)
        except FileNotFoundError:
            show_message(screen, "You finished all levels!", "Press ENTER to quit")
            pygame.time.wait(1000)
            wait_for_key()
            break

        show_message(screen, f"Level {level_index}", "Press ENTER to start", clear=True)

        while game.running:
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F3:
                        debug_overlay = not debug_overlay

            # Update game state
            game.player.handle_input(keys, game.tilemap, current_time)
            game.check_diamond_collection()  # Check if player collected a diamond
            game.opponents.update(game.player, game.tilemap)

            # Draw everything
            screen.fill(BLACK)
            game.tilemap.draw(screen)
            game.player.draw(screen)
            game.opponents.draw(screen)
            
            # Draw debug overlay if enabled
            if debug_overlay:
                font = pygame.font.SysFont(None, 18)
                # Player debug
                px, py = int(game.player.px), int(game.player.py)
                pygame.draw.circle(screen, (0,255,0), (px+TILE_SIZE//2, py+TILE_SIZE//2), 4)
                player_text = font.render(f"P: ({game.player.x},{game.player.y}) px=({px},{py})", True, (0,255,0))
                screen.blit(player_text, (px+TILE_SIZE, py))
                # Opponent debug
                for idx, (ox_px, oy_px) in enumerate(game.opponents.positions):
                    ox, oy = int(ox_px // TILE_SIZE), int(oy_px // TILE_SIZE)
                    pygame.draw.circle(screen, (255,0,0), (int(ox_px)+TILE_SIZE//2, int(oy_px)+TILE_SIZE//2), 4)
                    opp_text = font.render(f"O{idx}: ({ox},{oy}) px=({int(ox_px)},{int(oy_px)})", True, (255,0,0))
                    screen.blit(opp_text, (int(ox_px)+TILE_SIZE, int(oy_px)))
                for x in range(GRID_WIDTH):
                    for y in range(GRID_HEIGHT):
                        pygame.draw.rect(screen, (255,100,100), (x * TILE_SIZE, y * TILE_SIZE, 1, 1))
            
            pygame.display.flip()

            if game.check_game_over():
                show_message(screen, "Game Over", None, False)
                pygame.time.wait(2000)  # Wait 2 seconds
                show_message(screen, "Game Over", "Press ENTER to try again")
                break

            if game.check_win_condition():
                show_message(screen, "You Win!", None, False)
                pygame.time.wait(2000)  # Wait 2 seconds
                show_message(screen, "You Win!", "Press ENTER for next level")
                level_index += 1
                break

            if current_time - game.player.anim_timer >= 16:
                if game.player.state in ["running", "climbing"]:
                    game.player.anim_frame = (game.player.anim_frame + 1) % 8
                    game.player.anim_timer = current_time

            clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
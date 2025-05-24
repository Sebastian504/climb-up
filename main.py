# main.py
import pygame
import sys
import argparse
import os
from constants import *
from game_state import Game, STATUS_BAR_HEIGHT
from level_editor import run_level_editor
from debug_overlay import draw_debug_overlay

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
HIGHLIGHT = (255, 255, 0)  # Yellow for highlighting selected menu items

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
    """Wait for any key press and return the key that was pressed"""
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
                return event.key

def parse_arguments():
    parser = argparse.ArgumentParser(description='Climb Up - A puzzle platformer game')
    parser.add_argument('--level', type=int, default=None, help='Starting level number')
    return parser.parse_args()

def draw_menu(screen, menu_items, selected_index):
    # Clear the screen
    screen.fill(BLACK)
    
    # Draw title
    font_title = pygame.font.SysFont(None, 72)
    title = font_title.render("CLIMB UP", True, WHITE)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title, title_rect)
    
    # Draw menu items
    font_menu = pygame.font.SysFont(None, 48)
    menu_y = SCREEN_HEIGHT // 2
    menu_rects = []
    
    for i, item in enumerate(menu_items):
        color = HIGHLIGHT if i == selected_index else WHITE
        text = font_menu.render(item, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, menu_y))
        
        # Draw button background for better clickability
        button_rect = text_rect.inflate(40, 20)  # Make clickable area larger than text
        if i == selected_index:
            # Draw a highlight background for the selected item
            pygame.draw.rect(screen, (50, 50, 80), button_rect, border_radius=5)
        
        # Draw button border
        pygame.draw.rect(screen, (100, 100, 150), button_rect, 2, border_radius=5)
        
        # Draw the text
        screen.blit(text, text_rect)
        
        # Store the rectangle for click detection
        menu_rects.append(button_rect)
        
        menu_y += 60
    
    pygame.display.flip()
    
    return menu_rects

def get_level_input(screen):
    # Draw input prompt
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 48)
    prompt = font.render("Enter Level Number:", True, WHITE)
    prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(prompt, prompt_rect)
    
    # Input box
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, WHITE, input_box, 2)
    
    # Instructions
    font_small = pygame.font.SysFont(None, 24)
    instructions = font_small.render("Press ENTER when done, ESC to cancel", True, GRAY)
    instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
    screen.blit(instructions, instructions_rect)
    
    pygame.display.flip()
    
    # Text input handling
    input_text = ""
    active = True
    
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        level = int(input_text)
                        return level
                    except ValueError:
                        # Invalid input, show error
                        error_text = font_small.render("Please enter a valid number", True, (255, 0, 0))
                        screen.blit(error_text, (input_box.x, input_box.y + 60))
                        pygame.display.flip()
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isdigit() and len(input_text) < 3:  # Limit to 3 digits
                    input_text += event.unicode
        
        # Redraw input box and text
        pygame.draw.rect(screen, BLACK, (input_box.x + 2, input_box.y + 2, input_box.width - 4, input_box.height - 4))
        text_surface = font.render(input_text, True, WHITE)
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        pygame.display.flip()
        
        pygame.time.delay(50)  # Small delay to prevent high CPU usage

# Game status bar height is now defined in game_state.py

def draw_game_info(screen, game):
    """Draw game information (timer and diamond counter) at the top of the screen"""
    # Create info bar at the top
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, STATUS_BAR_HEIGHT))
    
    # Draw frame around the status bar
    pygame.draw.rect(screen, (100, 100, 100), (0, 0, SCREEN_WIDTH, STATUS_BAR_HEIGHT), 2)
    
    # Use fixed-width font for consistent display
    try:
        font = pygame.font.SysFont("consolas", 18)  # Half the size, fixed-width font
    except:
        # Fallback to a common monospace font if consolas is not available
        font = pygame.font.SysFont("courier", 18)
    
    # Draw timer
    time_string = game.get_timer_string()
    timer_text = font.render(time_string, True, (255, 255, 255))
    timer_rect = timer_text.get_rect(midright=(SCREEN_WIDTH - 20, STATUS_BAR_HEIGHT // 2))
    screen.blit(timer_text, timer_rect)
    
    # Draw diamond counter
    diamonds_collected = game.get_diamonds_collected()
    total_diamonds = game.get_total_diamonds()
    
    # Draw diamond symbol (upside-down triangle as used in the game)
    diamond_size = 12
    diamond_x = 20
    diamond_y = STATUS_BAR_HEIGHT // 2
    diamond_points = [
        (diamond_x, diamond_y + diamond_size//2),  # Bottom point
        (diamond_x - diamond_size//2, diamond_y - diamond_size//2),  # Top-left
        (diamond_x + diamond_size//2, diamond_y - diamond_size//2)   # Top-right
    ]
    pygame.draw.polygon(screen, (255, 255, 0), diamond_points)  # Yellow diamond
    
    # Draw diamond counter text
    diamond_text = font.render(f" {diamonds_collected}/{total_diamonds}", True, (255, 255, 255))
    diamond_rect = diamond_text.get_rect(midleft=(diamond_x + diamond_size, STATUS_BAR_HEIGHT // 2))
    screen.blit(diamond_text, diamond_rect)

def main_menu(screen):
    menu_items = ["Start Game", "Start at Level", "Level Editor", "Quit"]
    selected_index = 0
    
    while True:
        menu_rects = draw_menu(screen, menu_items, selected_index)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                # Highlight menu item when mouse hovers over it
                for i, rect in enumerate(menu_rects):
                    if rect.collidepoint(event.pos):
                        if selected_index != i:
                            selected_index = i
                            menu_rects = draw_menu(screen, menu_items, selected_index)
                        break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if clicking on a menu item
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(event.pos):
                            # Handle menu selection
                            if i == 0:  # Start Game
                                return 1  # Start at level 1
                            elif i == 1:  # Start at Level
                                level = get_level_input(screen)
                                if level is not None:
                                    return level
                                # Redraw menu when returning from level input
                                menu_rects = draw_menu(screen, menu_items, selected_index)
                            elif i == 2:  # Level Editor
                                # Run the level editor
                                run_level_editor(screen)
                                # Redraw the menu when returning from the editor
                                menu_rects = draw_menu(screen, menu_items, selected_index)
                            elif i == 3:  # Quit
                                pygame.quit()
                                sys.exit()
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_items)
                    menu_rects = draw_menu(screen, menu_items, selected_index)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                    menu_rects = draw_menu(screen, menu_items, selected_index)
                elif event.key == pygame.K_RETURN:
                    if selected_index == 0:  # Start Game
                        return 1  # Start at level 1
                    elif selected_index == 1:  # Start at Level
                        level = get_level_input(screen)
                        if level is not None:
                            return level
                        # Redraw menu when returning from level input
                        menu_rects = draw_menu(screen, menu_items, selected_index)
                    elif selected_index == 2:  # Level Editor
                        # Run the level editor
                        run_level_editor(screen)
                        # Redraw the menu when returning from the editor
                        menu_rects = draw_menu(screen, menu_items, selected_index)
                    elif selected_index == 3:  # Quit
                        pygame.quit()
                        sys.exit()

def main():
    args = parse_arguments()

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Climb Up')
    clock = pygame.time.Clock()
    debug_overlay = False

    # If level is provided via command line, start directly at that level
    # Otherwise show the main menu
    if args.level is not None:
        level_index = args.level
    else:
        level_index = main_menu(screen)
    
    while True:
        level_file = f"levels/level{level_index:03d}.lvl"
        
        # Check if the level file exists
        if not os.path.exists(level_file):
            show_message(screen, f"Level {level_index} not found", "Press any key to return to menu")
            level_index = main_menu(screen)
            continue
            
        game = Game(level_file)
        
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

            # Update all game state in one call
            game.update(keys, current_time)
            
            # Draw the game
            game.draw(screen, debug_overlay, draw_game_info, draw_debug_overlay)

            if game.check_game_over():
                # Different message if time ran out
                if game.time_remaining <= 0:
                    show_message(screen, "Time's Up!", None, False)
                else:
                    show_message(screen, "Game Over", None, False)
                pygame.time.wait(2000)  # Wait 2 seconds
                show_message(screen, "Game Over", "Press ENTER to try again")
                # When player dies, restart the same level
                break

            if game.check_win_condition():
                show_message(screen, "You Win!", None, False)
                pygame.time.wait(2000)  # Wait 2 seconds
                show_message(screen, "You Win!", "Press ENTER for next level")
                level_index += 1  # Move to the next level
                break

            if current_time - game.player.anim_timer >= 16:
                if game.player.state in ["running", "climbing"]:
                    game.player.anim_frame = (game.player.anim_frame + 1) % 8
                    game.player.anim_timer = current_time

            clock.tick(60)
        
        # Check if we should return to the main menu after a level ends
        if not os.path.exists(f"levels/level{level_index:03d}.lvl"):
            show_message(screen, "No more levels!", "Press any key to return to menu")
            level_index = main_menu(screen)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
# level_editor.py
import pygame
import sys
import os
import tkinter as tk
from tkinter import filedialog
from constants import *
from tilemap import TileMap
from game_state import Game
from player import Player
from opponent import Opponent

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
HIGHLIGHT = (255, 255, 0)  # Yellow for highlighting

# Tile palette definitions
PALETTE_TILES = [
    {'tile': AIR, 'name': 'Air', 'color': (0, 0, 0), 'border': True},
    {'tile': EARTH, 'name': 'Earth', 'color': TILE_COLORS[EARTH]},
    {'tile': STONE, 'name': 'Stone', 'color': TILE_COLORS[STONE]},
    {'tile': LADDER, 'name': 'Ladder', 'color': (139, 69, 19)},  # Brown for ladder
    {'tile': DIAMOND, 'name': 'Diamond', 'color': TILE_COLORS[DIAMOND]},
    {'tile': PLAYER, 'name': 'Player', 'color': PLAYER_COLOR},  # Use player color from constants
    {'tile': OPPONENT, 'name': 'Opponent', 'color': OPPONENT_COLOR},  # Use opponent color from constants
    {'tile': EXIT, 'name': 'Exit', 'color': (0, 255, 255)}  # Cyan for exit
]

class LevelEditor:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create a new empty level with default settings
        self.create_new_level()
        
        # Editor state
        self.selected_tile_index = 0  # Start with AIR selected
        self.is_drawing = False
        self.is_erasing = False
        self.grid_visible = True
        self.modified = False  # Track if level has been modified
        
        # Palette area dimensions
        self.palette_width = 150
        self.palette_height = SCREEN_HEIGHT
        self.palette_x = SCREEN_WIDTH - self.palette_width
        self.tile_size_in_palette = 32
        self.palette_padding = 10
        self.palette_top_margin = 80  # Add margin at the top for the title
        
        # Initialize Tkinter for file dialogs
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
    def get_tile_at_position(self, pos):
        """Convert screen position to grid coordinates"""
        x, y = pos
        if x < self.palette_x:  # Make sure we're in the grid area
            grid_x = x // TILE_SIZE
            grid_y = y // TILE_SIZE
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                return grid_x, grid_y
        return None
        
    def remove_entity_at_position(self, grid_pos):
        """Remove any entity (player or opponent) at the specified grid position"""
        if not grid_pos:
            return False
            
        x, y = grid_pos
        # Check if player is at this position
        if self.game_state.player:
            px, py = self.game_state.player.get_tile_position()
            if px == x and py == y:
                self.game_state.player = None
                self.modified = True
                return True
        
        # Check if any opponent is at this position
        for i, opponent in enumerate(self.game_state.opponents):
            ox, oy = opponent.get_tile_position()
            if ox == x and oy == y:
                # Remove this opponent
                opponent.kill()  # Remove from sprite groups
                self.game_state.opponents.pop(i)
                self.modified = True
                return True
                
        return False
    
    def get_palette_item_at_position(self, pos):
        """Check if position is on a palette item and return its index"""
        x, y = pos
        if x >= self.palette_x:  # Make sure we're in the palette area
            for i, _ in enumerate(PALETTE_TILES):
                item_y = self.palette_top_margin + i * (self.tile_size_in_palette + self.palette_padding)
                item_rect = pygame.Rect(
                    self.palette_x + self.palette_padding,
                    item_y,
                    self.tile_size_in_palette,
                    self.tile_size_in_palette
                )
                if item_rect.collidepoint(pos):
                    return i
        return None
    
    def draw_palette(self):
        """Draw the tile palette on the right side of the screen"""
        # Draw palette background
        pygame.draw.rect(self.screen, GRAY, (self.palette_x, 0, self.palette_width, self.palette_height))
        
        # Draw palette title
        font = pygame.font.SysFont(None, 24)
        small_font = pygame.font.SysFont(None, 18)  # Smaller font for tile names
        title = font.render("Tile Palette", True, WHITE)
        title_rect = title.get_rect(center=(self.palette_x + self.palette_width // 2, 20))
        self.screen.blit(title, title_rect)
        
        # Draw timer editor
        timer_label = small_font.render("Level Timer (mm:ss):", True, WHITE)
        timer_label_rect = timer_label.get_rect(topleft=(self.palette_x + 10, self.palette_top_margin - 30))
        self.screen.blit(timer_label, timer_label_rect)
        
        # Draw timer value with edit hint
        timer_value = small_font.render(f"{self.game_state.get_timer_string()} (T to edit)", True, HIGHLIGHT)
        timer_value_rect = timer_value.get_rect(topleft=(self.palette_x + 10, timer_label_rect.bottom + 5))
        self.screen.blit(timer_value, timer_value_rect)
        
        # Draw each palette item
        for i, item in enumerate(PALETTE_TILES):
            item_y = self.palette_top_margin + i * (self.tile_size_in_palette + self.palette_padding)
            item_rect = pygame.Rect(
                self.palette_x + self.palette_padding,
                item_y,
                self.tile_size_in_palette,
                self.tile_size_in_palette
            )
            
            # Draw tile background
            color = item['color']
            pygame.draw.rect(self.screen, color, item_rect)
            
            # Draw border for air (to make it visible) or for selected item
            if i == self.selected_tile_index:
                pygame.draw.rect(self.screen, HIGHLIGHT, item_rect, 3)
            elif item.get('border', False):  # For AIR tile
                pygame.draw.rect(self.screen, WHITE, item_rect, 1)
            
            # Draw special tile visualizations (same as in game)
            tile_type = item['tile']
            if tile_type == LADDER:
                # Draw ladder rungs
                for j in range(1, 3):
                    pygame.draw.line(
                        self.screen, 
                        BLACK,
                        (item_rect.left, item_rect.top + j * item_rect.height // 3),
                        (item_rect.right, item_rect.top + j * item_rect.height // 3),
                        2
                    )
            elif tile_type == PLAYER:
                # Draw a circle for player
                pygame.draw.circle(
                    self.screen,
                    PLAYER_COLOR,  # Use player color from constants
                    (item_rect.centerx, item_rect.centery),
                    item_rect.width // 3
                )
            elif tile_type == OPPONENT:
                # Draw a circle for opponent
                pygame.draw.circle(
                    self.screen,
                    OPPONENT_COLOR,  # Use opponent color from constants
                    (item_rect.centerx, item_rect.centery),
                    item_rect.width // 3
                )
            elif tile_type == DIAMOND:
                # Draw a diamond shape
                points = [
                    (item_rect.centerx, item_rect.top + 2),
                    (item_rect.right - 2, item_rect.centery),
                    (item_rect.centerx, item_rect.bottom - 2),
                    (item_rect.left + 2, item_rect.centery)
                ]
                pygame.draw.polygon(self.screen, (255, 255, 0), points)
            
            # Draw tile name with smaller font
            name = small_font.render(item['name'], True, WHITE)
            name_rect = name.get_rect(midleft=(item_rect.right + 5, item_rect.centery))
            self.screen.blit(name, name_rect)
            
        # Draw buttons below the palette
        button_height = 30
        button_width = (self.palette_width - 3 * self.palette_padding) // 3
        button_y = SCREEN_HEIGHT - 60
        
        # Load button
        load_rect = pygame.Rect(self.palette_x + self.palette_padding, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, load_rect)
        pygame.draw.rect(self.screen, BLACK, load_rect, 1)
        load_text = small_font.render("Load", True, BLACK)
        load_text_rect = load_text.get_rect(center=load_rect.center)
        self.screen.blit(load_text, load_text_rect)
        
        # Save button
        save_rect = pygame.Rect(load_rect.right + self.palette_padding, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, save_rect)
        pygame.draw.rect(self.screen, BLACK, save_rect, 1)
        save_text = small_font.render("Save", True, BLACK)
        save_text_rect = save_text.get_rect(center=save_rect.center)
        self.screen.blit(save_text, save_text_rect)
        
        # Exit button
        exit_rect = pygame.Rect(save_rect.right + self.palette_padding, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, exit_rect)
        pygame.draw.rect(self.screen, BLACK, exit_rect, 1)
        exit_text = small_font.render("Exit", True, BLACK)
        exit_text_rect = exit_text.get_rect(center=exit_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
        
        # Store button rects for click detection
        self.load_button_rect = load_rect
        self.save_button_rect = save_rect
        self.exit_button_rect = exit_rect
    
    def draw_grid(self):
        """Draw the grid lines"""
        if not self.grid_visible:
            return
            
        for x in range(0, self.palette_x, TILE_SIZE):
            pygame.draw.line(self.screen, LIGHT_GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, LIGHT_GRAY, (0, y), (self.palette_x, y), 1)
    
    def create_new_level(self):
        """Create a new empty level"""
        # Create a temporary level file
        temp_level = [[AIR for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_state = Game(temp_level)
        self.game_state.timer_seconds = 120  # Default 2 minutes
    
    def draw_tilemap(self):
        """Draw the current tilemap and entities"""
        # Draw the tilemap
        self.game_state.tilemap.draw(self.screen)
        
        # Draw player if exists
        if self.game_state.player:
            pygame.draw.circle(
                self.screen,
                PLAYER_COLOR,
                self.game_state.player.get_pixel_position(),
                TILE_SIZE // 2
            )
        
        # Draw opponents
        for opponent in self.game_state.opponents:
            pygame.draw.circle(
                self.screen,
                OPPONENT_COLOR,
                opponent.get_pixel_position(),
                TILE_SIZE // 2
            )

    def draw_status_bar(self):
        """Draw status bar with helpful information"""
        status_height = 30
        pygame.draw.rect(self.screen, BLACK, (0, SCREEN_HEIGHT - status_height, SCREEN_WIDTH, status_height))
        
        font = pygame.font.SysFont(None, 18)  # Consistent small font size
        
        # Show current selected tile
        selected_name = PALETTE_TILES[self.selected_tile_index]['name']
        selected_text = font.render(f"Selected: {selected_name}", True, WHITE)
        self.screen.blit(selected_text, (10, SCREEN_HEIGHT - status_height + 5))
        
        # Show controls
        controls_text = font.render("Left-click: Draw | Right-click: Erase | G: Toggle Grid", True, WHITE)
        controls_rect = controls_text.get_rect(midright=(self.palette_x - 10, SCREEN_HEIGHT - status_height + 15))
        self.screen.blit(controls_text, controls_rect)
        
        # Show modified indicator
        if self.modified:
            modified_text = font.render("*", True, HIGHLIGHT)
            self.screen.blit(modified_text, (self.palette_x - 30, SCREEN_HEIGHT - status_height + 5))
    
    def place_tile(self, grid_pos, tile):
        """Place a tile at the specified grid position"""
        if grid_pos:
            x, y = grid_pos
            
            # Handle special tiles (player, opponent) separately
            if tile == PLAYER:
                # Create or move player
                if self.game_state.player:
                    # Update existing player position
                    self.game_state.player.rect.x = x * TILE_SIZE
                    self.game_state.player.rect.y = y * TILE_SIZE
                else:
                    # Create new player
                    self.game_state.player = Player(x, y)
                    self.game_state.all_sprites.add(self.game_state.player)
                self.modified = True
                return
            
            elif tile == OPPONENT:
                # Create a new opponent
                new_opponent = Opponent(x, y)
                self.game_state.opponents.append(new_opponent)
                self.game_state.opponents_group.add(new_opponent)
                self.game_state.all_sprites.add(new_opponent)
                self.modified = True
                return
            
            # For regular tiles, update the tilemap
            current_tile = self.game_state.tilemap.get(x, y)
            if current_tile != tile:
                self.game_state.tilemap.set(x, y, tile)
                self.modified = True
    
    def load_level(self):
        """Load a level from a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Level files", "*.lvl"), ("All files", "*.*")],
            initialdir="levels"
        )
        
        if filename:
            # Use Game to load the level
            self.game_state = Game(filename)
            self.modified = False
            self.is_drawing = False
            self.is_erasing = False
    
    def save_level(self):
        """Save the current level to a file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".lvl",
            filetypes=[("Level files", "*.lvl"), ("All files", "*.*")],
            initialdir="levels"
        )
        
        if filename:
            # Use GameState's save_level method
            self.game_state.save_level(filename)
            self.modified = False
            self.is_drawing = False
            self.is_erasing = False
    
    def confirm_discard_changes(self):
        """Ask user to confirm discarding changes"""
        if not self.modified:
            return True
            
        # Use pygame to show a simple confirmation dialog
        dialog_width, dialog_height = 400, 200
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        dialog_surface = pygame.Surface((dialog_width, dialog_height))
        dialog_surface.fill(GRAY)
        pygame.draw.rect(dialog_surface, BLACK, (0, 0, dialog_width, dialog_height), 2)
        
        font = pygame.font.SysFont(None, 24)
        title = font.render("Unsaved Changes", True, WHITE)
        message = font.render("You have unsaved changes. Discard them?", True, WHITE)
        yes_text = font.render("Yes (Y)", True, WHITE)
        no_text = font.render("No (N)", True, WHITE)
        
        dialog_surface.blit(title, (dialog_width // 2 - title.get_width() // 2, 30))
        dialog_surface.blit(message, (dialog_width // 2 - message.get_width() // 2, 70))
        dialog_surface.blit(yes_text, (dialog_width // 4 - yes_text.get_width() // 2, 130))
        dialog_surface.blit(no_text, (3 * dialog_width // 4 - no_text.get_width() // 2, 130))
        
        self.screen.blit(dialog_surface, (dialog_x, dialog_y))
        pygame.display.flip()
        
        waiting = True
        result = False
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        result = True
                        waiting = False
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        result = False
                        waiting = False
        
        return result
    
    def edit_timer(self):
        """Edit the level timer"""
        # Use pygame to show a simple input dialog
        dialog_width, dialog_height = 400, 200
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        dialog_surface = pygame.Surface((dialog_width, dialog_height))
        dialog_surface.fill(GRAY)
        pygame.draw.rect(dialog_surface, BLACK, (0, 0, dialog_width, dialog_height), 2)
        
        font = pygame.font.SysFont(None, 24)
        title = font.render("Edit Level Timer", True, WHITE)
        message = font.render("Enter new timer (mm:ss):", True, WHITE)
        current_timer = self.game_state.get_timer_string()
        timer_text = font.render(current_timer, True, WHITE)
        
        dialog_surface.blit(title, (dialog_width // 2 - title.get_width() // 2, 30))
        dialog_surface.blit(message, (dialog_width // 2 - message.get_width() // 2, 70))
        dialog_surface.blit(timer_text, (dialog_width // 2 - timer_text.get_width() // 2, 110))
        
        self.screen.blit(dialog_surface, (dialog_x, dialog_y))
        pygame.display.flip()
        
        waiting = True
        new_timer = current_timer
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                    elif event.key == pygame.K_BACKSPACE:
                        new_timer = new_timer[:-1]
                    elif event.unicode.isdigit() or event.unicode == ':':
                        new_timer += event.unicode
                    elif event.key == pygame.K_ESCAPE:
                        waiting = False
                        new_timer = current_timer
            
            # Update the timer text
            timer_text = font.render(new_timer, True, WHITE)
            dialog_surface.blit(timer_text, (dialog_width // 2 - timer_text.get_width() // 2, 110))
            self.screen.blit(dialog_surface, (dialog_x, dialog_y))
            pygame.display.flip()
        
        # Update the timer in game_state
        try:
            if new_timer.count(':') == 1:
                minutes, seconds = map(int, new_timer.split(':'))
                self.game_state.timer_seconds = minutes * 60 + seconds
                self.modified = True
        except (ValueError, IndexError):
            pass  # Keep the current timer if there's an error
    
    def run(self):
        """Main editor loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.confirm_discard_changes():
                        self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if clicking on buttons
                    if hasattr(self, 'load_button_rect') and self.load_button_rect.collidepoint(event.pos):
                        if self.confirm_discard_changes():
                            self.load_level()
                    elif hasattr(self, 'save_button_rect') and self.save_button_rect.collidepoint(event.pos):
                        self.save_level()
                    elif hasattr(self, 'exit_button_rect') and self.exit_button_rect.collidepoint(event.pos):
                        if self.confirm_discard_changes():
                            self.running = False
                    # Check if clicking in palette
                    palette_index = self.get_palette_item_at_position(event.pos)
                    if palette_index is not None:  # Fix for palette selection
                        self.selected_tile_index = palette_index
                    else:
                        # Otherwise, place/erase tile
                        grid_pos = self.get_tile_at_position(event.pos)
                        if event.button == 1:  # Left click
                            self.is_drawing = True
                            self.place_tile(grid_pos, PALETTE_TILES[self.selected_tile_index]['tile'])
                        elif event.button == 3:  # Right click
                            self.is_erasing = True
                            self.place_tile(grid_pos, AIR)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_drawing = False
                    elif event.button == 3:
                        self.is_erasing = False
                
                elif event.type == pygame.MOUSEMOTION:
                    # Continue drawing/erasing if mouse button is held
                    grid_pos = self.get_tile_at_position(event.pos)
                    if self.is_drawing:
                        self.place_tile(grid_pos, PALETTE_TILES[self.selected_tile_index]['tile'])
                    elif self.is_erasing:
                        self.place_tile(grid_pos, AIR)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.confirm_discard_changes():
                            self.running = False
                    elif event.key == pygame.K_g:
                        self.grid_visible = not self.grid_visible
                    elif event.key == pygame.K_s:
                        self.save_level()
                    elif event.key == pygame.K_l:
                        if self.confirm_discard_changes():
                            self.load_level()
                    elif event.key == pygame.K_n:
                        if self.confirm_discard_changes():
                            # Create a new empty level
                            self.create_new_level()
                            self.modified = False
                    elif event.key == pygame.K_t:
                        # Edit the timer
                        self.edit_timer()
            
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_tilemap()
            self.draw_grid()
            self.draw_palette()
            self.draw_status_bar()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return False  # Return to main menu when done

def run_level_editor(screen):
    """Entry point to run the level editor"""
    editor = LevelEditor(screen)
    return editor.run()

if __name__ == "__main__":
    # For testing the editor directly
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Climb Up - Level Editor")
    run_level_editor(screen)
    pygame.quit()

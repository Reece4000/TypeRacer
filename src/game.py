import pygame
import random
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime
from src.easing import Easing
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

title_mod = Easing(0, decay=0.1)
bg_brightness_mod = Easing(0, decay=0.1)


# Constants - Retro CRT Color Scheme
# Base resolution (will be scaled)
BASE_WIDTH = 640
BASE_HEIGHT = 720

FPS = 30

# Retro green phosphor CRT colors
CRT_BLACK = (10, 12, 10)
CRT_GREEN = (51, 255, 51)
CRT_GREEN_DIM = (20, 120, 20)
CRT_GREEN_BRIGHT = (102, 255, 102)
CRT_AMBER = (255, 176, 0)
CRT_AMBER_DIM = (153, 102, 0)

# Alternative retro palette
RETRO_BG = (24, 20, 37)
RETRO_BLUE = (76, 132, 255)
RETRO_PINK = (255, 89, 157)
RETRO_PURPLE = (138, 68, 255)
RETRO_CYAN = (51, 255, 219)
RETRO_WHITE = (230, 230, 230)
RETRO_GREEN = (102, 255, 102)
RETRO_RED = (255, 89, 89)
RETRO_YELLOW = (255, 234, 89)

# Game colors (retro theme)
BG_COLOR = RETRO_BG
TEXT_COLOR = RETRO_CYAN
TITLE_COLOR = RETRO_PINK
INPUT_BG = (40, 35, 60)
INPUT_TEXT = RETRO_WHITE
CORRECT_COLOR = RETRO_GREEN
INCORRECT_COLOR = RETRO_RED
STATS_COLOR = RETRO_YELLOW
BUTTON_COLOR = RETRO_PURPLE
BUTTON_HOVER = RETRO_PINK

# Scanline effect
SCANLINE_ALPHA = 30
SCANLINE_SPACING = 3

# UI Geometry - All rect definitions in one place
# Buttons
BUTTON_W = 180
BUTTON_H = 42
BUTTON_RESET = pygame.Rect(BASE_WIDTH // 2 - BUTTON_W - 4, BASE_HEIGHT - (BUTTON_H + 12), BUTTON_W, BUTTON_H)
BUTTON_SCORES = pygame.Rect(BASE_WIDTH // 2 + 4, BASE_HEIGHT - (BUTTON_H + 12), BUTTON_W, BUTTON_H)
BUTTON_BACK = pygame.Rect(BASE_WIDTH // 2 - BUTTON_W // 2, BASE_HEIGHT - (BUTTON_H + 12), BUTTON_W, BUTTON_H)

# Input box
INPUT_BOX_WIDTH = 480
INPUT_BOX_HEIGHT = 64
INPUT_BOX_X = (BASE_WIDTH - INPUT_BOX_WIDTH) // 2
INPUT_BOX_Y = 480
INPUT_BOX = pygame.Rect(INPUT_BOX_X, INPUT_BOX_Y, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)

# Timer
TIMER_Y = 620
TIMER_WIDTH = 288
TIMER_HEIGHT = 64
TIMER_RECT = pygame.Rect(BASE_WIDTH // 2 - 144, TIMER_Y - 32, TIMER_WIDTH, TIMER_HEIGHT)

# Game over overlay
GAME_OVER_BOX_WIDTH = 400
GAME_OVER_BOX_HEIGHT = 240
GAME_OVER_BOX_X = (BASE_WIDTH - GAME_OVER_BOX_WIDTH) // 2
GAME_OVER_BOX_Y = (BASE_HEIGHT - GAME_OVER_BOX_HEIGHT) // 2
GAME_OVER_BOX = pygame.Rect(GAME_OVER_BOX_X, GAME_OVER_BOX_Y, GAME_OVER_BOX_WIDTH, GAME_OVER_BOX_HEIGHT)

# Y positions
TITLE_Y = 40
ROAD_START_Y = 440
ROAD_SPACING_Y = 28
STATS_Y = 560
SCORES_HEADER_Y = 130
SCORES_LIST_X = 100
SCORES_LIST_Y = 180


class TypeRacerGame:
    def __init__(self):
        # Create a window with SCALED flag for integer scaling (maintains pixel-perfect rendering)
        self.screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT))
        pygame.display.set_caption("TYPE RACER")

        # Set icon if available
        try:
            icon_path = Path(__file__).parent.parent / "resources" / "car.ico"
            icon = pygame.image.load(str(icon_path))
            pygame.display.set_icon(icon)
        except:
            pass

        self.clock = pygame.time.Clock()
        self.running = True

        # Load sounds
        self.load_sounds()

        # Load fonts
        self.load_fonts()

        # Game state
        self.reset_game()

        # Load words
        self.load_words()

        # UI elements
        self.input_text = ""
        self.input_active = True
        self.input_flash = False
        self.flash_timer = 0

        # Scanline surface for retro effect
        self.create_scanlines()

        # Initialize database
        self.init_database()

        # Screen state
        self.current_screen = "game"  # "game" or "scores"

        self.init_crt_effects()

    def init_crt_effects(self):
        w, h = self.screen.get_size()

        # --- Scanlines ---
        self.scanlines = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            darkness = 60 if (y % 2 == 0) else 0
            pygame.draw.line(self.scanlines, (0, 0, 0, darkness), (0, y), (w, y))

        # --- Aperture grille mask (vertical RGB stripes) ---
        self.aperture = pygame.Surface((w, h), pygame.SRCALPHA)
        stripe_w = 3
        for x in range(0, w, stripe_w * 3):
            pygame.draw.rect(self.aperture, (255, 0, 0, 25), (x, 0, stripe_w, h))
            pygame.draw.rect(self.aperture, (0, 255, 0, 25), (x + stripe_w, 0, stripe_w, h))
            pygame.draw.rect(self.aperture, (0, 0, 255, 25), (x + stripe_w * 2, 0, stripe_w, h))

        # --- Noise buffer ---
        self.noise_surface = pygame.Surface((w, h), pygame.SRCALPHA)

    def load_sounds(self):
        """Load sound effects"""
        try:
            sound_path = Path(__file__).parent.parent / "resources" / "sounds"
            self.sound_good = pygame.mixer.Sound(str(sound_path / "good.mp3"))
            self.sound_bad = pygame.mixer.Sound(str(sound_path / "bad.mp3"))
            self.sound_start = pygame.mixer.Sound(str(sound_path / "start.mp3"))

            # Adjust volume
            self.sound_good.set_volume(0.5)
            self.sound_bad.set_volume(0.5)
            self.sound_start.set_volume(0.3)
        except Exception as e:
            print(f"Error loading sounds: {e}")
            self.sound_good = None
            self.sound_bad = None
            self.sound_start = None

    def load_fonts(self):
        """Load retro-style fonts"""
        # Font sizes (scaled down for smaller UI)
        font_size_title = 64
        font_size_large = 56
        font_size_medium = 36
        font_size_small = 24
        font_size_tiny = 16

        # Try to load the custom pixel fonts
        try:
            fonts_path = Path(__file__).parent.parent / "resources" / "fonts" / "pixel"

            # Use different fonts for different parts of the app for variety
            self.font_title = pygame.font.Font(str(fonts_path / "PixelOperator-Bold.ttf"), font_size_title)
            self.font_large = pygame.font.Font(str(fonts_path / "PixelOperatorMono-Bold.ttf"), font_size_large)
            self.font_medium = pygame.font.Font(str(fonts_path / "PixelOperatorMono-Bold.ttf"), font_size_medium)
            self.font_small = pygame.font.Font(str(fonts_path / "PixelOperatorMono.ttf"), font_size_small)
            self.font_tiny = pygame.font.Font(str(fonts_path / "PixelOperatorMono-Bold.ttf"), font_size_tiny)

            # Store the base font path for dynamic font loading
            self.pixel_font_path = fonts_path / "PixelOperatorMono.ttf"
            self.pixel_font_bold_path = fonts_path / "PixelOperatorMono-Bold.ttf"

            # Cache for dynamically loaded fonts to reduce CPU usage
            self.font_cache = {}

        except Exception as e:
            print(f"Could not load custom font: {e}")
            # Fallback to system fonts
            font_names = ['Courier New', 'Consolas', 'Monaco', 'monospace']
            self.font_title = pygame.font.SysFont(font_names, font_size_title, bold=True)
            self.font_large = pygame.font.SysFont(font_names, font_size_large, bold=True)
            self.font_medium = pygame.font.SysFont(font_names, font_size_medium, bold=True)
            self.font_small = pygame.font.SysFont(font_names, font_size_small, bold=True)
            self.font_tiny = pygame.font.SysFont(font_names, font_size_tiny, bold=False)
            self.pixel_font_path = None
            self.pixel_font_bold_path = None
            self.font_cache = {}

    def create_scanlines(self):
        """Create scanline overlay for CRT effect"""
        self.scanline_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        for y in range(0, BASE_HEIGHT, SCANLINE_SPACING):
            pygame.draw.line(self.scanline_surface, (0, 0, 0, SCANLINE_ALPHA),
                           (0, y), (BASE_WIDTH, y), 1)

    def init_database(self):
        """Initialize SQLite database for storing scores"""
        try:
            db_path = Path(__file__).parent.parent / "scores.db"
            self.db_conn = sqlite3.connect(str(db_path))
            cursor = self.db_conn.cursor()

            # Create scores table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wpm REAL NOT NULL,
                    accuracy REAL NOT NULL,
                    words_typed INTEGER NOT NULL,
                    date_time TEXT NOT NULL
                )
            ''')
            self.db_conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
            self.db_conn = None

    def save_score(self):
        """Save the current score to the database"""
        if self.db_conn is None:
            return

        try:
            cursor = self.db_conn.cursor()
            date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                INSERT INTO scores (wpm, accuracy, words_typed, date_time)
                VALUES (?, ?, ?, ?)
            ''', (self.wpm, self.accuracy, self.words_typed_successfully, date_time))

            self.db_conn.commit()
            print(f"Score saved: WPM={self.wpm:.1f}, Accuracy={self.accuracy:.1f}%")
        except Exception as e:
            print(f"Error saving score: {e}")

    def get_all_scores(self):
        """Retrieve all scores from the database, ordered by date"""
        if self.db_conn is None:
            return []

        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                SELECT wpm, accuracy, words_typed, date_time
                FROM scores
                ORDER BY date_time DESC
                LIMIT 20
            ''')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving scores: {e}")
            return []

    def load_words(self):
        """Load words from file"""
        try:
            words_path = Path(__file__).parent.parent / "resources" / "data" / "words.txt"
            with open(words_path, 'r') as file:
                content = file.read()
                self.all_words = content.split()
                self.shuffle_words()
        except Exception as e:
            print(f"Error loading words: {e}")
            self.all_words = ["error", "loading", "words", "file"]
            self.passage = self.all_words.copy()
            self.word_index = 0

    def shuffle_words(self):
        """Shuffle and prepare word passage"""
        shuffled = self.all_words.copy()
        random.shuffle(shuffled)
        # Reverse order like original
        self.passage = shuffled[::-1]
        self.word_index = 0

    def reset_game(self):
        """Reset game state"""
        self.word_index = 0
        self.turn = 0
        self.words_typed_successfully = 0
        self.words_typed_total = 0
        self.accuracy = 0.0
        self.wpm = 0.0
        self.time_remaining = 60.0  # 60 seconds countdown
        self.game_started = False
        self.game_ended = False
        self.input_text = ""
        self.input_flash = False
        self.flash_timer = 0

        # Reshuffle words if already loaded
        if hasattr(self, 'all_words'):
            self.shuffle_words()

    def get_current_word(self):
        """Get the current word to type"""
        if self.word_index < len(self.passage):
            return self.passage[self.word_index]
        return ""

    def get_upcoming_words(self, count=13):
        """Get upcoming words for road display"""
        words = []
        for i in range(count):
            idx = self.word_index + i
            if idx < len(self.passage):
                words.append(self.passage[idx])
            else:
                words.append("")
        return words

    def update_timer(self, dt):
        """Update game timer - countdown mode"""
        if self.game_started and not self.game_ended:
            self.time_remaining -= dt

            # Check if time is up
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.game_ended = True
                self.save_score()

            # Calculate WPM based on time elapsed
            time_elapsed = 60.0 - self.time_remaining
            if time_elapsed > 0:
                self.wpm = (self.words_typed_successfully / time_elapsed) * 60

    def process_word_input(self):
        """Process the typed word"""
        if not self.input_text.strip():
            return

        # Don't process if game has ended
        if self.game_ended:
            return

        # Start game on first word
        if self.turn == 0:
            self.game_started = True
            if self.sound_start:
                self.sound_start.play()

        current_word = self.get_current_word()
        typed_word = self.input_text.strip()

        self.turn += 1
        self.words_typed_total += 1

        # Check if correct
        if current_word == typed_word:
            self.words_typed_successfully += 1
            self.input_flash = CORRECT_COLOR
            if self.sound_good:
                bg_brightness_mod.current = 64
                self.sound_good.play()
        else:
            self.input_flash = INCORRECT_COLOR
            if self.sound_bad:
                bg_brightness_mod.current = -64
                self.sound_bad.play()

        # Update accuracy
        if self.words_typed_total > 0:
            self.accuracy = (self.words_typed_successfully / self.words_typed_total) * 100

        # Move to next word
        self.word_index += 1
        self.input_text = ""
        self.flash_timer = 0.3  # Flash for 300ms

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                # SCALED mode handles resizing automatically
                pass

            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.process_word_input()

                elif event.key == pygame.K_BACKSPACE:
                    if mods & pygame.KMOD_CTRL:
                        self.input_text = ""
                    else:
                        self.input_text = self.input_text[:-1]

                elif event.key == pygame.K_DELETE and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # CTRL+DELETE deletes entire word
                    self.input_text = ""

                elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.reset_game()

                else:
                    # Add character to input
                    if event.unicode.isprintable() and event.unicode not in [' ', '\r', '\n']:
                        self.input_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Handle mouse clicks on button release (SCALED mode handles coordinate translation)
                self.handle_mouse_click(event.pos)

    def handle_mouse_click(self, pos):
        """Handle mouse button clicks on release"""
        if self.current_screen == "game":
            if BUTTON_RESET.collidepoint(pos):
                self.reset_game()
                return

            if BUTTON_SCORES.collidepoint(pos):
                self.current_screen = "scores"
                return

        elif self.current_screen == "scores":
            if BUTTON_BACK.collidepoint(pos):
                self.current_screen = "game"
                return

    def draw_retro_text(self, text, font, color, x, y, center=False, shadow=True):
        """Draw text with retro glow effect"""
        # Shadow/glow
        if shadow:
            shadow_color = (color[0] // 3, color[1] // 3, color[2] // 3)
            shadow_surf = font.render(text, True, shadow_color)
            shadow_rect = shadow_surf.get_rect()
            if center:
                shadow_rect.center = (x + 2, y + 2)
            else:
                shadow_rect.topleft = (x + 2, y + 2)
            self.screen.blit(shadow_surf, shadow_rect)

        # Main text
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surf, text_rect)

        return text_rect

    def draw_road(self):
        """Draw the road of upcoming words with retro 3D perspective effect - bottom to top"""
        words = self.get_upcoming_words(13)

        for i, word in enumerate(words):
            if not word:
                word = "..."

            # Position 0 (closest to input) is at bottom
            # Higher positions move upward
            y_pos = ROAD_START_Y - (i * ROAD_SPACING_Y)

            # Calculate size dynamically - smooth decrease for ALL positions
            # Start at 36 and decrease smoothly (scaled down)
            font_size = max(10, int(36 - (i * 2)))  # Decreases from 36 to 10

            # Load font dynamically with caching to reduce CPU usage
            if self.pixel_font_path:
                try:
                    # Create cache key based on font size and style
                    cache_key = (font_size, i == 0)

                    # Check if font is already in cache
                    if cache_key not in self.font_cache:
                        if i == 0:
                            # Current word - use bold font
                            self.font_cache[cache_key] = pygame.font.Font(str(self.pixel_font_bold_path), font_size)
                        else:
                            # Other words - use regular font
                            self.font_cache[cache_key] = pygame.font.Font(str(self.pixel_font_path), font_size)

                    font = self.font_cache[cache_key]
                except:
                    font = self.font_small
            else:
                # Fallback
                font = pygame.font.SysFont(['Courier New', 'Consolas', 'Monaco', 'monospace'], font_size, bold=(i == 0))

            # Calculate color based on distance with smooth gradient
            # Use a single color (cyan) and fade it smoothly
            if i == 0:
                # Current word - highlighted in pink
                color = TITLE_COLOR
                word_display = f">>> {word} <<<"
            else:
                # All other words - smooth fade from bright cyan to very dim cyan
                # Create smooth exponential fade
                intensity = max(0.15, 1.0 - (i * 0.07))  # Smooth fade from 1.0 to 0.15

                # Use cyan (TEXT_COLOR) as base and fade it
                color = (int(TEXT_COLOR[0] * intensity),
                        int(TEXT_COLOR[1] * intensity),
                        int(TEXT_COLOR[2] * intensity))

                dash_count = (15 - len(word)) // 2
                word_display = f"{'-' * dash_count} {word} {'-' * dash_count}"

            self.draw_retro_text(word_display, font, color, BASE_WIDTH // 2, y_pos, center=True)

    def draw_input_box(self):
        """Draw the input text box with retro styling"""
        # Flash effect
        if self.input_flash and self.flash_timer > 0:
            box_color = self.input_flash
        else:
            box_color = INPUT_BG

        # Draw box with border
        pygame.draw.rect(self.screen, box_color, INPUT_BOX)
        pygame.draw.rect(self.screen, RETRO_PURPLE, INPUT_BOX, 3)

        # Draw inner glow
        pygame.draw.rect(self.screen, RETRO_PINK, INPUT_BOX.inflate(-6, -6), 1)

        # Draw input text
        text_to_show = self.input_text if self.input_text else ""
        self.draw_retro_text(text_to_show, self.font_large, INPUT_TEXT,
                           INPUT_BOX.centerx, INPUT_BOX.centery, center=True, shadow=False)

        # Draw blinking cursor
        if int(pygame.time.get_ticks() / 500) % 2 == 0:
            cursor_x = INPUT_BOX.centerx + self.font_large.size(text_to_show)[0] // 2 + 5
            cursor_y = INPUT_BOX.y + 12
            pygame.draw.rect(self.screen, RETRO_CYAN, (cursor_x, cursor_y, 3, 40))

    def draw_stats(self):
        """Draw statistics with retro styling"""
        stats_text = f"WORDS: {self.words_typed_successfully}  |  WPM: {self.wpm:.1f}  |  ACC: {self.accuracy:.1f}%"
        self.draw_retro_text(stats_text, self.font_small, STATS_COLOR,
                           BASE_WIDTH // 2, STATS_Y, center=True)

    def draw_timer(self):
        """Draw countdown timer with retro digital clock styling"""
        seconds = int(self.time_remaining)
        time_str = f"00:{seconds:02d}"

        # Change color based on time remaining
        if self.time_remaining <= 10:
            timer_color = RETRO_RED  # Red when low
        elif self.time_remaining <= 30:
            timer_color = RETRO_YELLOW  # Yellow as warning
        else:
            timer_color = RETRO_CYAN  # Cyan normally

        # Draw border
        pygame.draw.rect(self.screen, RETRO_PURPLE, TIMER_RECT, 3)
        pygame.draw.rect(self.screen, RETRO_PINK, TIMER_RECT.inflate(-6, -6), 1)

        self.draw_retro_text(time_str, self.font_large, timer_color,
                             BASE_WIDTH // 2, TIMER_Y, center=True)

    def draw_buttons(self):
        """Draw retro styled buttons"""
        mouse_pos = pygame.mouse.get_pos()

        # Reset button
        color = BUTTON_HOVER if BUTTON_RESET.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, BUTTON_RESET)
        pygame.draw.rect(self.screen, RETRO_CYAN, BUTTON_RESET, 2)
        self.draw_retro_text("RESET", self.font_small, RETRO_WHITE,
                           BUTTON_RESET.centerx, BUTTON_RESET.centery, center=True, shadow=False)

        # Scores button
        color = BUTTON_HOVER if BUTTON_SCORES.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, BUTTON_SCORES)
        pygame.draw.rect(self.screen, RETRO_CYAN, BUTTON_SCORES, 2)
        self.draw_retro_text("SCORES", self.font_small, RETRO_WHITE,
                           BUTTON_SCORES.centerx, BUTTON_SCORES.centery, center=True, shadow=False)

    def draw_title(self):
        """Draw retro game title"""
        title = "TYPE RACER"
        self.draw_retro_text(title, self.font_title, TITLE_COLOR,
                           BASE_WIDTH // 2, TITLE_Y, center=True)

    def draw_game_over(self):
        """Draw game over overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game over box
        pygame.draw.rect(self.screen, INPUT_BG, GAME_OVER_BOX)
        pygame.draw.rect(self.screen, RETRO_PURPLE, GAME_OVER_BOX, 4)
        pygame.draw.rect(self.screen, RETRO_PINK, GAME_OVER_BOX.inflate(-8, -8), 2)

        # Game over text
        self.draw_retro_text("TIME'S UP!", self.font_title, RETRO_RED,
                           BASE_WIDTH // 2, GAME_OVER_BOX.y + 48, center=True)

        # Final stats
        stats_y = GAME_OVER_BOX.y + 104
        self.draw_retro_text(f"WPM: {self.wpm:.1f}", self.font_medium, RETRO_CYAN,
                           BASE_WIDTH // 2, stats_y, center=True, shadow=False)

        stats_y += 40
        self.draw_retro_text(f"Accuracy: {self.accuracy:.1f}%", self.font_small, RETRO_YELLOW,
                           BASE_WIDTH // 2, stats_y, center=True, shadow=False)

        stats_y += 32
        self.draw_retro_text(f"Words: {self.words_typed_successfully}", self.font_small, RETRO_GREEN,
                           BASE_WIDTH // 2, stats_y, center=True, shadow=False)

        # Instructions
        stats_y += 40
        self.draw_retro_text("Press CTRL+R to play again", self.font_tiny, RETRO_WHITE,
                           BASE_WIDTH // 2, stats_y, center=True, shadow=False)

    def crt_horizontal_warp(self, source):
        w, h = source.get_size()
        # Ensure warped surface uses SRCALPHA for transparency if needed
        warped = pygame.Surface((w, h), pygame.SRCALPHA)
        time_ms = pygame.time.get_ticks()

        for y in range(h):
            # Calculate the shift (same as before)
            shift = int(2 * math.sin(y * 0.005 + time_ms * 0.002))

            # This method uses Pygame's efficient internal blitting function
            # It copies the strip of the 'source' (area=...) onto 'warped'
            # but offset by 'shift' pixels at the current row 'y'.
            warped.blit(source, (shift, y), area=pygame.Rect(0, y, w, 1))

        return warped

    def draw_crt_noise(self):
        w, h = self.noise_surface.get_size()

        # 1. Decay the old noise
        # Blit the existing noise surface onto itself, but with slight transparency.
        # This simulates a mild phosphor decay, creating "streaks" instead of blinking dots.
        self.noise_surface.blit(self.noise_surface, (0, 0))
        # Fill with a very faint black (low alpha) to decay the old noise gently
        decay_layer = pygame.Surface((w, h), pygame.SRCALPHA)
        decay_layer.fill((0, 0, 0, 10))  # Alpha 10 for soft decay
        self.noise_surface.blit(decay_layer, (0, 0))

        # 2. Add New Random Noise (More efficient way)
        amount = max(100, (w * h) // 1000)

        # Use a small temporary surface for noise (faster than drawing 1x1 rects)
        # The `amount` of noise is now represented by the number of dots drawn.

        for _ in range(amount):
            x = random.randrange(0, w)
            y = random.randrange(0, h)

            # Color: Use a slightly wider range for better visual pop
            v = random.randint(100, 180)
            a = random.randint(10, 30)

            # Option A: Use a temporary small surface for drawing the dot (very minor perf gain over rect)
            dot = pygame.Surface((1, 1), pygame.SRCALPHA)
            dot.fill((v, v, v, a))
            self.noise_surface.blit(dot, (x, y))

            # Option B: Stick to your original, simple, and readable method:
            # pygame.draw.rect(self.noise_surface, (v, v, v, a), (x, y, 1, 1))

        return self.noise_surface

    def draw_scores_screen(self):
        """Draw the scores display screen"""
        # Clear screen
        self.draw_retro_grid()

        # Title
        self.draw_retro_text("HIGH SCORES", self.font_title, TITLE_COLOR,
                             BASE_WIDTH // 2, TITLE_Y, center=True)

        # Back button
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if BUTTON_BACK.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, BUTTON_BACK)
        pygame.draw.rect(self.screen, RETRO_CYAN, BUTTON_BACK, 2)
        self.draw_retro_text("BACK", self.font_small, RETRO_WHITE,
                           BUTTON_BACK.centerx, BUTTON_BACK.centery, center=True, shadow=False)

        # Get scores from database
        scores = self.get_all_scores()

        # Draw headers
        header_text = f"{'#':<2s}    {'WPM':>6s}      {'ACC%':>6s}      {'WORDS':>5s}    DATE & TIME"
        self.draw_retro_text(header_text, self.font_tiny, RETRO_CYAN,
                           SCORES_LIST_X, SCORES_HEADER_Y, center=False, shadow=False)

        # Draw separator line
        separator_y = SCORES_HEADER_Y + 30
        pygame.draw.line(self.screen, RETRO_PURPLE,
                        (50, separator_y), (BASE_WIDTH - 50, separator_y), 2)

        # Draw scores
        y_pos = SCORES_LIST_Y
        if not scores:
            self.draw_retro_text("No scores yet. Play a game to set one!",
                               self.font_small, RETRO_YELLOW,
                               BASE_WIDTH // 2, y_pos + 50, center=True)
        else:
            for i, (wpm, accuracy, words_typed, date_time) in enumerate(scores[:15], 1):
                score_line = f"{i:<2d}     {wpm:>6.1f}     {accuracy:>6.1f}     {words_typed:>5d}     {date_time}"

                # Color based on rank
                if i == 1:
                    color = RETRO_YELLOW  # Gold for first
                elif i == 2:
                    color = RETRO_WHITE  # Silver for second
                elif i == 3:
                    color = RETRO_PINK  # Bronze for third
                else:
                    color = TEXT_COLOR

                self.draw_retro_text(score_line, self.font_tiny, color,
                                   SCORES_LIST_X, y_pos, center=False, shadow=False)
                y_pos += 35

        # Apply scanline effect
        self.screen.blit(self.scanline_surface, (0, 0))

    def update(self, dt):
        """Update game logic"""
        self.update_timer(dt)

        # Update flash timer
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.input_flash = False

    def draw_bg(self):
        # Clear screen
        if bg_brightness_mod.is_animating:
            r, g, b = BG_COLOR
            curr = bg_brightness_mod.current
            rand = random.randint(0, 8)
            if curr < 0:
                r = min(255, max(r - int(bg_brightness_mod.current + rand), 0))
                g = min(255, max(g + int(bg_brightness_mod.current / 2 + rand / 2), 0))
            else:
                r = min(255, max(r - int(bg_brightness_mod.current / 2 + rand / 3), 0))
                g = min(255, max(g + int(bg_brightness_mod.current + rand / 2), 0))
            b = min(255, max(b + rand, 0))
            bg = (r, g, b)
        else:
            # Base colour
            r0, g0, b0 = BG_COLOR

            # Low-frequency brightness oscillation (CRT phosphor decay / refresh)
            # Produces values roughly in the 0.95–1.05 range
            t = pygame.time.get_ticks() * 0.001
            lf = 1.0 + 0.03 * math.sin(t * 55.0)  # small amplitude, moderate speed

            # High-frequency noise (beam jitter / line noise)
            hf = random.uniform(-0.015, 0.015)

            scale = lf + hf

            # Apply combined scaling
            r = int(r0 * scale)
            g = int(g0 * scale)
            b = int(b0 * scale)

            bg = (r, g, b)

        self.screen.fill(bg)

    def draw(self):
        """Draw everything"""
        self.draw_bg()
        if self.current_screen == "scores":
            self.draw_scores_screen()
        else:
            # Draw grid background for retro effect
            self.draw_retro_grid()

            # Draw game elements
            self.draw_title()
            self.draw_road()
            self.draw_input_box()
            self.draw_stats()
            self.draw_timer()
            self.draw_buttons()

            # Show game over message if time's up
            if self.game_ended:
                self.draw_game_over()

            # Apply scanline effect
            self.screen.blit(self.scanline_surface, (0, 0))

        # Update display
        frame = self.crt_horizontal_warp(self.screen)

        frame.blit(self.scanlines, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        frame.blit(self.aperture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        # frame.blit(self.draw_crt_noise(), (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        self.screen.blit(frame, (0, 0))

        pygame.display.flip()
        bg_brightness_mod.update()

    def draw_retro_grid(self):
        """Draw a subtle grid background for retro aesthetic"""
        grid_color = (30, 25, 45)
        spacing = 40

        # Vertical lines
        for x in range(0, BASE_WIDTH, spacing):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, BASE_HEIGHT), 1)

        # Horizontal lines
        for y in range(0, BASE_HEIGHT, spacing):
            pygame.draw.line(self.screen, grid_color, (0, y), (BASE_WIDTH, y), 1)

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            self.handle_events()
            self.update(dt)
            self.draw()

        # Close database connection
        if hasattr(self, 'db_conn') and self.db_conn:
            self.db_conn.close()

        pygame.quit()
        sys.exit()


def main():
    game = TypeRacerGame()
    game.run()


if __name__ == "__main__":
    main()

"""
Configuration settings for Type Racer - Retro Edition
Modify these values to customize the game
"""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900
FPS = 60

# Retro CRT Color Scheme
# You can change these to customize the look

# Original green phosphor CRT colors
CRT_BLACK = (10, 12, 10)
CRT_GREEN = (51, 255, 51)
CRT_GREEN_DIM = (20, 120, 20)
CRT_GREEN_BRIGHT = (102, 255, 102)
CRT_AMBER = (255, 176, 0)
CRT_AMBER_DIM = (153, 102, 0)

# Retro synthwave palette (default)
RETRO_BG = (24, 20, 37)           # Deep purple background
RETRO_BLUE = (76, 132, 255)       # Bright blue
RETRO_PINK = (255, 89, 157)       # Hot pink
RETRO_PURPLE = (138, 68, 255)     # Bright purple
RETRO_CYAN = (51, 255, 219)       # Neon cyan
RETRO_WHITE = (230, 230, 230)     # Off-white
RETRO_GREEN = (102, 255, 102)     # Bright green
RETRO_RED = (255, 89, 89)         # Bright red
RETRO_YELLOW = (255, 234, 89)     # Bright yellow

# Active color scheme (change these to switch themes)
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

# CRT Effect settings
SCANLINE_ALPHA = 30        # Transparency of scanlines (0-255)
SCANLINE_SPACING = 3       # Pixels between scanlines

# Audio settings
SOUND_VOLUME_EFFECTS = 0.5  # Volume for correct/incorrect sounds (0.0-1.0)
SOUND_VOLUME_START = 0.3    # Volume for start sound (0.0-1.0)

# Gameplay settings
WORDS_TO_DISPLAY = 15      # Number of upcoming words to show
FLASH_DURATION = 0.3       # Duration of color flash in seconds

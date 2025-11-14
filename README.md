# TYPE RACER - RETRO EDITION

A typing speed game with a retro CRT aesthetic, built with Pygame.

## Features

- **Retro CRT Visual Style**: Scanlines, phosphor glow effects, and vintage color palette
- **Real-time Metrics**: Track your Words Per Minute (WPM) and accuracy
- **Sound Effects**: Audio feedback for correct and incorrect words
- **1000 Common Words**: Practice with the most frequently used English words
- **Infinite Gameplay**: Words are shuffled and repeated endlessly

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

Run the game:
```bash
python run_game.py
```

### Controls

- **Type the word** you see highlighted at the top of the road
- **Press SPACE or ENTER** to submit your word
- **BACKSPACE** to delete characters
- **CTRL+R** to reset the game
- **ESC** to quit

### Gameplay

- Type each word as accurately and quickly as possible
- Your statistics (Words typed, WPM, Accuracy) update in real-time
- Green flash = correct word
- Red flash = incorrect word
- The road shows upcoming words in perspective

## Project Structure

```
TypeRacer/
├── src/
│   └── game.py              # Main game implementation
├── resources/
│   ├── sounds/
│   │   ├── good.mp3         # Correct word sound
│   │   ├── bad.mp3          # Incorrect word sound
│   │   └── start.mp3        # Game start sound
│   ├── data/
│   │   ├── words.txt        # 1000 common English words
│   │   └── bath.txt         # Additional text data
│   └── car.ico              # Game icon
├── run_game.py              # Game launcher
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Legacy Files

The following files are from the original Tkinter version and can be removed:
- `main.py` (root directory)
- `TypeRacer/main.py`
- Duplicate `.mp3` files in root and TypeRacer/ directories
- Duplicate `.txt` files in root directory

## Credits

Original Tkinter version refactored to Pygame with enhanced retro aesthetics.

## Color Scheme

The game uses a custom retro color palette inspired by 1980s computer terminals:
- Background: Deep purple/blue (#18142A)
- Primary text: Cyan (#33FFDB)
- Highlights: Pink (#FF599D) and Purple (#8A44FF)
- Correct: Green (#66FF66)
- Incorrect: Red (#FF5959)
- Stats: Yellow (#FFEA59)

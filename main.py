"""
Type Racer - Retro Edition
A typing speed game with a retro CRT aesthetic

Launch this file to start the game
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from game import main

if __name__ == "__main__":
    main()

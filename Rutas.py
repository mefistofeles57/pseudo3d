import sys
from pathlib import Path

#carpeta del juego, la de los .py o la temporal de PyInstaller en el exe
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE=Path(sys._MEIPASS)
else:
    BASE=Path(__file__).resolve().parent
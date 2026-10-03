# /// script
# dependencies = [
#  "pygame-ce",
# ]
# ///
# pygbag (versión web) solo instala las dependencias declaradas en este bloque

import asyncio
import pygame
from Juego import Juego

asyncio.run(Juego().run())

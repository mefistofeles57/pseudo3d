import pygame
from ImageCache import ImageCache
from DefaultDrawer import DefaultDrawer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class Escenario:


    def __init__(self,context:"GameContext"):
        self.name="Escenario"
        #carretera
        self.half_width=0.8
        self.road_colors=[(102,102,102),(88,88,88)]
        #exterior
        self.outside_colors=[(78,209,74),(47,163,59)]
        #cielo
        self.sky_dark=(40, 120, 255)
        self.sky_light=(180, 235, 255)
        #arcen
        self.arcen_width=0.15
        self.arcen_freq=1
        self.arcen_color=[(102,102,102)]
        #sombra(
        self.shadow_color=(0,0,0)
        self.shadow_alpha=60
        self.shadow_width_factor=1.2
        self.shadow_height=0.05

        #fondo
        self.f_img1=pygame.image.load("img/hills.png").convert_alpha()
        self.f_img2=pygame.transform.flip(self.f_img1, True, False)
        self.bgcolor=(28,40,52)

        #cache
        self.cache=ImageCache(context)
        self.cache.addImage("signal.arrow","signal.arrow.png",(0.5,1.0),True,True)
        self.cache.addImage("arbol","arbol.png",(0.5,1.0),True,True)
        self.cache.addImage("arbusto","arbusto.png",(0.5,1.0),True,True)
        self.cache.addImage("farola","farola.png",(0.7,0.98),True,True)
        self.cache.addImage("palmera","palmera.png",(0.5,1.0),True,True)
        self.cache.addImage("piedra","piedra.png",(0.5,1.0),True,False)

        self.drawer=DefaultDrawer()

    def swapFondo(self):
        if self.f_img1!=None and self.f_img2!=None:
            aux=self.f_img1
            self.f_img1=self.f_img2
            self.f_img2=aux




import pygame
from ImageCache import ImageCache
from Object import Object
from VisualObjProfile import VisualObjProfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext


class Player(Object):
    def __init__(self,context:"GameContext"):
        self.context=context
        self.speed=5.0
        self.img="coche"
        self.metadata=None
        self.vs=None
        self.x_rel=0.0
        self.vx=0.0
        self.c=0.0
        self.target_c=0.0
        self.z=0.0
        self.fuerza_volante=10.0
        self.cache=ImageCache(ImageCache.getPlayerConfig(),context)
        self.cache.addImage("coche","coche.png",(0.5,0.95),False,True)
        profile=VisualObjProfile()
        profile.shadow_color=(74, 69, 64)
        profile.shadow_alpha=100
        profile.shadow_width_factor=1.2
        profile.shadow_height=0.2
        profile.cache=self.cache
        self.profile=profile


    def update(self,dt):
        intensidad=7.5
        dz=self.speed*dt
        self.z+=dz

        if self.vs!=None:
            giro_player=self.get_volante()*dz
            curva_pista=self.vs.curve*intensidad
            self.target_c=giro_player-curva_pista
            self.c+=(self.target_c-self.c)*8.0*dt
            self.vx+=self.c*dz

        self.x_rel+=self.vx*dt
        self.vx*=0.95

    def get_volante(self):
        left_pressed=self.context.keys[pygame.K_LEFT]
        right_pressed=self.context.keys[pygame.K_RIGHT]
        
        i=0

        if left_pressed and not right_pressed:
            i=-1
        elif right_pressed and not left_pressed:
            i=1

        return i*self.fuerza_volante

    


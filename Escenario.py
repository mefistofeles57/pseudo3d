import pygame
from ImageCache import ImageCache
from DefaultDrawer import DefaultDrawer
from Background import Background
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class Escenario:


    def __init__(self,context:"GameContext"):
        self.name="Escenario"
        #carretera
        self.half_width=1.0
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

        #fondo

        mov=75

        self.fondos=[]
        b=Background("img/nube1.png",False,False,mov*0.05,context,None,x=400,y=400)
        self.fondos.append(b)
        b=Background("img/nube2.png",False,False,mov*0.05,context,None,x=800,y=200)
        self.fondos.append(b)
        b=Background("img/hills.png",True,False,mov*0.1,context,(27,41,53),y=context.camera.horizon)
        self.fondos.append(b)
        b=Background("img/near_hills.png",True,True,mov*0.5,context,(31,159,68),y=context.camera.horizon)
        self.fondos.append(b)



        #cache
        self.cache=ImageCache(None,context)
        self.cache.addImage("signal.arrow","signal.arrow.png",(0.5,1.0),True,True)
        self.cache.addImage("arbol","arbol.png",(0.5,1.0),True,True)
        self.cache.addImage("arbusto","arbusto.png",(0.5,1.0),True,True)
        self.cache.addImage("farola","farola.png",(0.7,0.98),True,True)
        self.cache.addImage("palmera","palmera.png",(0.5,1.0),True,True)
        self.cache.addImage("piedra","piedra.png",(0.5,1.0),True,False)
        self.cache.addImage("quitamiedos","quitamiedos.png",(0.5,2.0),False,False)
        self.cache.addImage("poste","poste.2.png",(0.5,1.0),False,True)

        self.drawer=DefaultDrawer()





import pygame
from pathlib import Path
from ImageCache import ImageCache
from DefaultDrawer import DefaultDrawer
from Background import Background
from Material import Material
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class Escenario:


    def __init__(self,context:"GameContext"):
        self.name="Escenario"
        self.context=context
        #materiales
        hierba = Material()
        hierba.name="hierba"
        hierba.agarre_x=0.5
        hierba.amplitud=0.005
        hierba.frecuencia=4.0
        hierba.friccion_z=0.6
        hierba.drag_z=3.0
        asfalto=Material()
        arcen=Material()
        arcen.agarre_x=0.9
        arcen.friccion_z=0.9
        #carretera
        #self.half_width=1.0
        self.road_limit=1.5
        self.road_colors=[(102,102,102),(88,88,88)]
        self.road_material=asfalto
        #exterior
        self.outside_colors=[(78,209,74),(47,163,59)]
        self.outside_material=hierba
        #cielo
        self.sky_dark=(40, 120, 255)
        self.sky_light=(180, 235, 255)
        #arcen
        self.arcen_width=0.15
        self.arcen_freq=1
        self.arcen_color=[(102,102,102)]
        self.arcen_material=arcen


        #fondo

        mov=75

        sprite_resize=self.context.gen_scale

        self.fondos=[]
        b=Background("img/nube1.png",False,False,mov*0.5,context,None,x=400,y=400,resize=sprite_resize)
        self.fondos.append(b)
        b=Background("img/nube2.png",False,False,mov*0.5,context,None,x=800,y=200,resize=sprite_resize)
        self.fondos.append(b)
        b=Background("img/hills.png",True,False,mov*1.0,context,(27,41,53),y=context.camera.horizon,resize=sprite_resize)
        self.fondos.append(b)
        b=Background("img/near_hills.png",True,True,mov*4.0,context,(31,159,68),y=context.camera.horizon,resize=sprite_resize)
        self.fondos.append(b)



        #cache
        self.cache=ImageCache(None,context)
        self.cache.addImage("signal.arrow","signal.arrow.png",(0.5,1.0),True,True)
        self.cache.addImage("curva","curva.png",(0.5,1.0),True,True)
        self.cache.addImage("curva.s","curva.s.png",(0.5,1.0),False,True)
        self.cache.addImage("rasante","rasante.png",(0.5,1.0),False,True)
        self.cache.addImage("arbol","arbol.1.png",(0.55,1.0),False,True)
        self.cache.addImage("arbol.2","arbol.2.png",(0.5,1.0),False,True)
        self.cache.addImage("arbol.3","arbol.3.png",(0.5,1.0),False,True)
        self.cache.addImage("arbol.4","arbol.2.png",(0.55,1.0),False,True)
        self.cache.addImage("arbusto","arbusto.png",(0.5,1.0),False,False)
        self.cache.addImage("farola","farola.png",(0.7,1.0),True,True)
        self.cache.addImage("palmera","palmera.png",(0.5,1.0),True,True)
        self.cache.addImage("piedra","piedra.png",(0.5,1.0),False,False)
        self.cache.addImage("quitamiedos","quitamiedos.png",(0.5,2.0),False,False)
        self.cache.addImage("poste","poste.2.png",(0.5,1.0),False,True)
        self.cache.addImage("checkpoint","checkpoint.png",(0.6,1.0),False,True)

        self.cache.addAnimation("enemigo.1","enemigo.1.png",(0.5,1.0),False,True,ancho=256,alto=256)

        self.images={}
        base = Path(__file__).resolve().parent
        self.images["flecha.1"]=pygame.image.load(base/"img"/"flecha.1.png").convert_alpha()
        self.images["flecha.2"]=pygame.image.load(base/"img"/"flecha.2.png").convert_alpha()
        self.images["linea"]=pygame.image.load(base/"img"/"linea.png").convert_alpha()
        self.images["parrilla"]=pygame.image.load(base/"img"/"parrilla.png").convert_alpha()


        self.drawer=DefaultDrawer(context)





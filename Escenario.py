import pygame
import sys
from pathlib import Path
from ImageCache import ImageCache
from DefaultDrawer import DefaultDrawer
from Background import Background
from Material import Material
from AssetStreamer import AssetStreamer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class RecursosEscenario:
    def __init__(self,context):
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent
        self.base=base

        hierba = Material()
        hierba.name="hierba"
        hierba.agarre_x=0.5
        hierba.amplitud=0.005
        hierba.frecuencia=4.0
        hierba.friccion_z=0.6
        hierba.drag_z=3.0
        arcen=Material()
        arcen.agarre_x=0.9
        arcen.friccion_z=0.9
        self.hierba=hierba
        self.asfalto=Material()
        self.arcen=arcen

        self.cache=ImageCache(None,context)
        self.streamer=AssetStreamer(self.cache,str(base/"circuits/assets.json"))
        self.images={}
        self.images["flecha.1"]=pygame.image.load(str(base/"img"/"flecha.1.png")).convert_alpha()
        self.images["flecha.2"]=pygame.image.load(str(base/"img"/"flecha.2.png")).convert_alpha()
        self.images["linea"]=pygame.image.load(str(base/"img"/"linea.png")).convert_alpha()
        self.images["parrilla"]=pygame.image.load(str(base/"img"/"parrilla.png")).convert_alpha()
        self.drawer=DefaultDrawer(context)

class Escenario:
    def __init__(self,context,recursos):
        self.context=context
        self.recursos=recursos
        self.cache=recursos.cache
        self.streamer=recursos.streamer
        self.images=recursos.images
        self.drawer=recursos.drawer

class Bosque(Escenario):
    def __init__(self,context,recursos):
        super().__init__(context,recursos)
        self.name="Bosque"
        self.ancho_defecto=1.0
        self.margin_limit=0.5
        self.road_colors=[(102,102,102),(88,88,88)]
        self.road_material=recursos.asfalto
        self.outside_colors=[(78,209,74),(47,163,59)]
        self.outside_material=recursos.hierba
        self.sky_dark=(40, 120, 255)
        self.sky_light=(180, 235, 255)
        self.arcen_width=0.15
        self.arcen_freq=1
        self.arcen_color=[(102,102,102)]
        self.arcen_material=recursos.arcen

        mov=75
        sprite_resize=context.gen_scale
        base=recursos.base
        self.fondos=[]

        esc_pixel=3
        b=Background(base/"img/fondo.bosque.n.1.png",False,False,mov*0.5,context,None,x=450,y=200,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/fondo.bosque.n.2.png",False,False,mov*0.5,context,None,x=820,y=260,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/fondo.bosque.n.3.png",False,False,mov*0.5,context,None,x=1180,y=170,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/fondo.bosque.l.png",True,False,mov*1.0,context,(138,165,216),y=context.camera.horizon,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/fondo.bosque.m.png",True,True,mov*4.0,context,(72,126,102),y=context.camera.horizon+15,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)


class DesiertoRoca(Escenario):
    def __init__(self,context,recursos):
        super().__init__(context,recursos)
        self.name="DesiertoRoca"
        self.ancho_defecto=1.3
        self.margin_limit=0.5
        self.road_colors=[(74,64,56),(64,55,48)]
        self.road_material=recursos.asfalto
        self.outside_colors=[(201,123,74),(178,108,64)]
        self.outside_material=recursos.hierba
        self.sky_dark=(111,168,199)
        self.sky_light=(242,166,90)
        self.arcen_width=0.15
        self.arcen_freq=1
        self.arcen_color=[(74,64,56)]
        self.arcen_material=recursos.arcen

        mov=75
        sprite_resize=context.gen_scale
        base=recursos.base
        self.fondos=[]

        b=Background(base/"img/nube1.png",False,False,mov*0.5,context,None,x=400,y=400,resize=sprite_resize)
        self.fondos.append(b)
        b=Background(base/"img/nube2.png",False,False,mov*0.5,context,None,x=800,y=200,resize=sprite_resize)
        self.fondos.append(b)
        b=Background(base/"img/hills.png",True,False,mov*1.0,context,(110,50,40),y=context.camera.horizon,resize=sprite_resize)
        self.fondos.append(b)
        b=Background(base/"img/near_hills.png",True,True,mov*4.0,context,(178,108,64),y=context.camera.horizon,resize=sprite_resize)
        self.fondos.append(b)

class Pradera(Escenario):
    def __init__(self,context,recursos):
        super().__init__(context,recursos)
        self.name="Pradera"
        self.ancho_defecto=0.75
        self.margin_limit=0.5
        self.road_colors=[(89,86,79),(80,77,70)]
        self.road_material=recursos.asfalto
        self.outside_colors=[(111,168,90),(96,150,78)]
        self.outside_material=recursos.hierba
        self.sky_dark=(126,200,227)
        self.sky_light=(234,247,232)
        self.arcen_width=0.15
        self.arcen_freq=1
        self.arcen_color=[(89,86,79)]
        self.arcen_material=recursos.arcen

        mov=75
        sprite_resize=context.gen_scale
        base=recursos.base
        self.fondos=[]

        b=Background(base/"img/nube1.png",False,False,mov*0.5,context,None,x=400,y=400,resize=sprite_resize)
        self.fondos.append(b)
        b=Background(base/"img/nube2.png",False,False,mov*0.5,context,None,x=800,y=200,resize=sprite_resize)
        self.fondos.append(b)
        b=Background(base/"img/hills.png",True,False,mov*1.0,context,(60,90,50),y=context.camera.horizon,resize=sprite_resize)
        self.fondos.append(b)
        b=Background(base/"img/near_hills.png",True,True,mov*4.0,context,(111,168,90),y=context.camera.horizon,resize=sprite_resize)
        self.fondos.append(b)

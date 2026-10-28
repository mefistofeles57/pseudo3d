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
        hierba.amplitud=0.003
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
        self.images["flecha.1.amarillo"]=pygame.image.load(str(base/"img"/"flecha.1.amarilla.png")).convert_alpha()
        self.images["flecha.2.amarillo"]=pygame.image.load(str(base/"img"/"flecha.2.amarilla.png")).convert_alpha()
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
        self.cables=False
        #luces de faros
        self.luz_color=None
        self.luz_umbrales=[0.25,0.5,0.8]
        self.luz_mezcla=[0.0,0.18,0.34,0.5]
        self.faro_inicio=0.3
        self.faro_fin=3.0
        self.faro_intensidad=0.7
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

        esc_pixel=4
        b=Background(base/"img/desierto.nube.g.png",False,False,mov*0.5,context,None,x=380,y=180,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/desierto.nube.p.png",False,False,mov*0.5,context,None,x=900,y=250,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/desierto.nube.g.png",False,False,mov*0.5,context,None,x=1250,y=150,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/desierto.rocas.fondo.1.png",False,False,mov*2.0,context,None,x=700,y=context.camera.horizon+15,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/desierto.rocas.fondo.2.png",False,False,mov*2.0,context,None,x=1400,y=context.camera.horizon+15,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/fondo.desierto.m.png",True,False,mov*3.0,context,(199,122,85),y=context.camera.horizon+5,resize=sprite_resize*3.0,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/fondo.desierto.c.png",True,True,mov*4.0,context,(184,106,72),y=context.camera.horizon+10,resize=sprite_resize*3.0,color_clave=True)
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
        self.arcen_freq=2
        self.arcen_color=[(150,112,72),(134,99,62)]
        self.arcen_material=recursos.arcen
        self.cables=True

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
        b=Background(base/"img/pradera.fondo.l.png",True,False,mov*1.0,context,(63,63,116),y=context.camera.horizon,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/pradera.fondo.c.png",True,True,mov*4.0,context,(75,105,47),y=context.camera.horizon+30,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)


class Noche(Escenario):
    def __init__(self,context,recursos):
        super().__init__(context,recursos)
        self.name="Noche"
        self.ancho_defecto=0.75
        self.margin_limit=0.5
        self.arcen_width=0.2
        self.road_colors=[(46, 40, 62),(40, 35, 55)]
        self.road_material=recursos.asfalto
        self.outside_colors=[(30, 24, 48),(26, 21, 42)]
        self.outside_material=recursos.hierba
        self.sky_dark=(26, 16, 51)
        self.sky_light=(168, 72, 118)
        self.arcen_freq=1
        self.arcen_color=[(64, 54, 80)]
        self.arcen_material=recursos.arcen
        self.luz_color=(255,158,74)
        self.faro_inicio=0.5
        self.faro_pico=2.5
        self.faro_fin=9.0
        self.faro_intensidad=1.0
        self.luz_umbrales=[0.1,0.25,0.4,0.55,0.7,0.85]
        self.luz_mezcla=[0.0,0.04,0.08,0.12,0.16,0.2,0.24]

        mov=75
        sprite_resize=context.gen_scale
        base=recursos.base
        self.fondos=[]

        esc_pixel=3
        b=Background(base/"img/fondo.noche.l.png",True,False,mov*1.0,context,(30,24,48),y=context.camera.horizon,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/fondo.noche.c.png",True,True,mov*2.0,context,(30,24,48),y=context.camera.horizon,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)
        b=Background(base/"img/luna.png",False,False,mov*0.25,context,None,x=1060,y=170,resize=sprite_resize*esc_pixel,color_clave=True)
        self.fondos.append(b)

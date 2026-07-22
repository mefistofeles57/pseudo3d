import pygame
from ImageCache import ImageCache
from DefaultDrawer import DefaultDrawer

class Escenario:


    def __init__(self,LUTh,LUTm,LUTl):
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
#        self.lineas=[]
#        self.lineas.append({"name":"arcen izq","color":(102,102,102),"start":-self.half_width-0.15,"width":0.15,"offset":0,"freq":1})
#        self.lineas.append({"name":"arcen der","color":(102,102,102),"start":self.half_width,"width":0.15,"offset":0,"freq":1})
#        self.lineas.append({"name":"ext izquierda","color":(255,255,255),"start":-self.half_width,"width":0.01,"offset":0,"freq":1})
#        self.lineas.append({"name":"ext derecha","color":(255,255,255),"start":self.half_width-0.01,"width":0.01,"offset":0,"freq":1})
#        self.lineas.append({"name":"central","color":(255,255,255),"start":-0.0025,"width":0.005,"offset":0,"freq":2})

        #fondo
        self.f_img1=pygame.image.load("img/hills.png").convert_alpha()
        self.f_img2=pygame.transform.flip(self.f_img1, True, False)
        self.bgcolor=(28,40,52)

        #cache
        self.cache=ImageCache(LUTh,LUTm,LUTl)
        self.cache.addImage("signal.arrow","signal.arrow.png",ImageCache.HIGH,0.5)
        self.cache.addImage("arbol","arbol.png",ImageCache.HIGH,0.5)
        self.cache.addImage("arbusto","arbusto.png",ImageCache.HIGH,0.5)
        self.cache.addImage("farola","farola.png",ImageCache.HIGH,0.7)
        self.cache.addImage("palmera","palmera.png",ImageCache.HIGH,0.5)
        self.cache.addImage("piedra","piedra.png",ImageCache.HIGH,0.5)

        self.drawer=DefaultDrawer()

    def swapFondo(self):
        if self.f_img1!=None and self.f_img2!=None:
            aux=self.f_img1
            self.f_img1=self.f_img2
            self.f_img2=aux




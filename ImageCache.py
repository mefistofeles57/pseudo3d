import pygame
import math
from Point import Point
from Image import Image
from Rutas import BASE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class CacheConfig:
    def __init__(self,resize=1.0):
        self.num_samples=150
        self.scale_max=1500*resize
        self.scale_min=10*resize
        self.distancia_vuelo=7.5

class ImageCache:

    ANIMATION=0
    IMAGE=1

    @staticmethod
    def getPlayerConfig(distancia,resize=1.0):
        c=CacheConfig()
        #el tope de la tabla es la escala real del coche, que va siempre a esta distancia de la camara
        c.distancia_vuelo=distancia
        c.num_samples=2
        c.scale_min=80*resize
        return c
    
    @staticmethod
    def getHumoConfig(resize=1.0):
        c=CacheConfig()
        c.distancia_vuelo=None
        c.num_samples=20
        c.scale_max=1500*resize
        c.scale_min=20*resize
        return c


    def __init__(self,config:CacheConfig,context:"GameContext"):
        self.context=context
        if config==None:
            self.config=CacheConfig(resize=self.context.gen_scale)
        else:
            self.config=config
 

        self.scale_cache_max=self.config.scale_max
        if self.config.distancia_vuelo is not None:
            p=context.camera.project(Point(0.0,0.0,self.config.distancia_vuelo))
            self.scale_cache_max=p.z
        self.images={}
        self.animations={}
        self.metadata={}
        self.originales={}
        self.memo={}
        self.inv_log_ratio=0.0
        self.LUT=[]

        self.getScaleTable()

        self.base=BASE

    def addAnimation(self,name,file,anchor,ancho_mundo,flip=True,shadow=False,ancho=32,alto=32):
        img=pygame.image.load(str(self.base/"img"/file)).convert_alpha()
        frames=self.load_frames(img, ancho, alto)
        self.newAnimation(name,frames,anchor,shadow,ancho_mundo)
        if flip==True:
            img=pygame.image.load(str(self.base/"img"/file)).convert_alpha()
            img=pygame.transform.flip(img,True,False)
            frames=[]
            for item in reversed(self.load_frames(img, ancho, alto)):
                frames.append(item)
            anchor_x=anchor[0]
            anchor_y=anchor[1]
            self.newAnimation(name+".flip",frames,(1-anchor_x,anchor_y),shadow,ancho_mundo)


    def addImage(self,name,file,anchor,ancho_mundo,flip=True,shadow=False):
        img=pygame.image.load(str(self.base/"img"/file)).convert_alpha()
        self.newImage(name,img,anchor,shadow,ancho_mundo)
        if flip==True:
            img=pygame.transform.flip(img,True,False)
            anchor_x=anchor[0]
            anchor_y=anchor[1]
            self.newImage(name+".flip",img,(1-anchor_x,anchor_y),shadow,ancho_mundo)

    def newImage(self,name,img,anchor,shadow,ancho_mundo):
        for _ in self.generarImagen(name,img,anchor,shadow,ancho_mundo):
            pass

    def generarImagen(self,name,img,anchor,shadow,ancho_mundo):
        w=img.get_width()
        h=img.get_height()
        escalados=[]
        for scale in self.LUT:
            new_img=pygame.transform.scale(img,self.medida(w,h,ancho_mundo,scale))
            new_img.set_alpha(255, pygame.RLEACCEL)
            escalados.append(new_img)
            yield
        self.images[name]=escalados
        self.originales[name]=(img,w,h,ancho_mundo)
        self.metadata[name]=Image(name,anchor[0],anchor[1],shadow,ImageCache.IMAGE)

    def newAnimation(self,name,frames,anchor,shadow,ancho_mundo):
        for _ in self.generarAnimacion(name,frames,anchor,shadow,ancho_mundo):
            pass

    def generarAnimacion(self,name,frames,anchor,shadow,ancho_mundo):
        w=frames[0].get_width()
        h=frames[0].get_height()
        escalados=[]
        for scale in self.LUT:
            medida=self.medida(w,h,ancho_mundo,scale)
            nuevos=[]
            for frame in frames:
                nuevo=pygame.transform.scale(frame,medida)
                nuevo.set_alpha(255, pygame.RLEACCEL)
                nuevos.append(nuevo)
            escalados.append(nuevos)
            yield
        self.animations[name]=escalados
        self.originales[name]=(frames,w,h,ancho_mundo)
        metadata=Image(name,anchor[0],anchor[1],shadow,ImageCache.ANIMATION)
        metadata.frames=len(frames)
        self.metadata[name]=metadata


    #tamaño en pantalla de una imagen de w x h pixeles que mide ancho_mundo unidades, a la escala de proyeccion dada
    #el alto mantiene la proporcion de la imagen
    def medida(self,w,h,ancho_mundo,escala):
        ancho=ancho_mundo*escala
        return (int(ancho),int(ancho*h/w))
        
    def getScaleTable(self):
        num_samples=self.config.num_samples
        scale_max=self.scale_cache_max
        scale_min=self.config.scale_min
        ratio = (scale_max / scale_min) ** (1.0 / (num_samples - 1))
        self.inv_log_ratio = 1.0 / math.log(ratio)
        self.LUT.clear()
        for i in range(num_samples):
            scale = scale_min * ratio**i
            self.LUT.append(scale)

    def indice(self,escala):
        return round(math.log(escala/self.config.scale_min)*self.inv_log_ratio)

    def tamano(self,name,escala):
        (original,w,h,ancho_mundo)=self.originales[name]
        if escala>self.scale_cache_max:
            s=escala
        else:
            s=self.LUT[self.indice(escala)]
        return self.medida(w,h,ancho_mundo,s)

    def nuevoFrame(self):
        self.memo.clear()

    def getSprite(self,name,escala,frame,ancho,alto,vx0,vy0,vx1,vy1):
        # devuelve (superficie, dx, dy): qué pintar y su desplazamiento respecto a la esquina del objeto
        # vx0..vy1 es la parte visible del objeto, en píxeles de pantalla relativos a su esquina
        if escala<=self.scale_cache_max:
            if frame is None:
                return (self.images[name][self.indice(escala)],0,0)
            return (self.animations[name][self.indice(escala)][frame],0,0)
        (orig,w,h,escala_asset)=self.originales[name]
        if frame is not None:
            orig=orig[frame]
        if vx0==0 and vy0==0 and vx1==ancho and vy1==alto:
            clave=(name,frame,ancho,alto)
            img=self.memo.get(clave)
            if img is None:
                img=pygame.transform.scale(orig,(ancho,alto))
                self.memo[clave]=img
            return (img,0,0)
        # solo se ve una parte: se recorta del original lo que corresponde y se escala eso
        sx0=int(vx0*w/ancho)
        sy0=int(vy0*h/alto)
        sx1=min(w,math.ceil(vx1*w/ancho))
        sy1=min(h,math.ceil(vy1*h/alto))
        trozo=orig.subsurface((sx0,sy0,sx1-sx0,sy1-sy0))
        tw=max(1,round((sx1-sx0)*ancho/w))
        th=max(1,round((sy1-sy0)*alto/h))
        return (pygame.transform.scale(trozo,(tw,th)),sx0*ancho/w,sy0*alto/h)
        
    def load_frames(self, sheet, frame_width, frame_height):

        frames = []
        count = sheet.get_width() // frame_width

        for i in range(count):
            rect = pygame.Rect(
                i * frame_width,
                0,
                frame_width,
                frame_height
            )

            frames.append(sheet.subsurface(rect).copy())

        return frames

    def unload(self,name):
        self.unloadUno(name)
        self.unloadUno(name+".flip")

    def unloadUno(self,name):
        metadata=self.metadata.pop(name,None)
        if metadata is None:
            return
        if metadata.type==ImageCache.IMAGE:
            del self.images[name]
        else:
            del self.animations[name]
        del self.originales[name]

            
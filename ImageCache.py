import pygame
import math
from Point import Point
from Image import Image
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class CacheConfig:
    def __init__(self):
        self.num_samples=150
        self.scale_max=1500
        self.scale_min=80
        self.resize_at_1=1.5

class ImageCache:

    @staticmethod
    def getPlayerConfig():
        c=CacheConfig()
        c.num_samples=2
        c.scale_max=1500
        c.scale_min=80
        c.resize_at_1=3
        return c

    def __init__(self,config:CacheConfig,context:"GameContext"):
        self.context=context
        if config==None:
            self.config=CacheConfig()
        else:
            self.config=config
        self.images={}
        self.metadata={}
        self.inv_log_ratio=0.0
        self.LUT=[]
        self.getScaleTable()

        #resize factor
        #necesito la escala en (0,0,1)
        p=context.camera.project(Point(0.0,0.0,1.0))
        self.resizeFactor=p.z/self.config.resize_at_1

    def addImage(self,name,file,anchor,flip=True,shadow=False):
        img=pygame.image.load("img/"+file).convert_alpha()
        self.newImage(name,img,anchor,shadow)
        if flip==True:
            img=pygame.transform.flip(img,True,False)
            anchor_x=anchor[0]
            anchor_y=anchor[1]
            self.newImage(name+".flip",img,(1-anchor_x,anchor_y),shadow)

    def newImage(self,name,img,anchor,shadow):
        self.images[name]=[]
        metadata=Image(name,anchor[0],anchor[1],shadow)
        self.metadata[name]=metadata
        #escalados
        w = img.get_width()
        h = img.get_height()


        for scale in self.LUT:
            #resize = r_min + (scale - scale_min) * (r_max - r_min) / (scale_max - scale_min)
            resize=scale/self.resizeFactor
            #scale=item["scale"]/conversion
            new_img = pygame.transform.scale(img,(int(w * resize), int(h * resize)))
            self.images[name].append(new_img)


    def getScaleTable(self):
        num_samples=self.config.num_samples
        scale_max=self.config.scale_max
        scale_min=self.config.scale_min
        ratio = (scale_max / scale_min) ** (1.0 / (num_samples - 1))
        self.inv_log_ratio = 1.0 / math.log(ratio)
        self.LUT.clear()
        for i in range(num_samples):
            scale = scale_min * ratio**i
            self.LUT.append(scale)

    def getImage(self,name,escala):
        num_samples=self.config.num_samples
        scale_min=self.config.scale_min

        i =round(math.log(escala / scale_min) * self.inv_log_ratio)
        if i>=num_samples:
            return None

        return self.images[name][i]


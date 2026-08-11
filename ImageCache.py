import pygame
import math
from pathlib import Path
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

    ANIMATION=0
    IMAGE=1

    @staticmethod
    def getPlayerConfig():
        c=CacheConfig()
        c.num_samples=2
        c.scale_max=1500
        c.scale_min=80
        c.resize_at_1=3
        return c

    @staticmethod
    def getHumoConfig():
        c=CacheConfig()
        c.num_samples=20
        c.scale_max=1500
        c.scale_min=20
        c.resize_at_1=7
        return c


    def __init__(self,config:CacheConfig,context:"GameContext"):
        self.context=context
        if config==None:
            self.config=CacheConfig()
        else:
            self.config=config
        self.images={}
        self.animations={}
        self.metadata={}
        self.inv_log_ratio=0.0
        self.LUT=[]
        self.getScaleTable()

        #resize factor
        #necesito la escala en (0,0,1)
        p=context.camera.project(Point(0.0,0.0,1.0))
        self.resizeFactor=p.z/self.config.resize_at_1


        self.base = Path(__file__).resolve().parent


    def addAnimation(self,name,file,anchor,flip=True,shadow=False):
        img=pygame.image.load(self.base/"img"/file).convert_alpha()
        frames=self.load_frames(img, 32, 32)
        self.newAnimation(name,frames,anchor,shadow)
        if flip==True:
            img=pygame.image.load(self.base/"img"/file).convert_alpha()
            img=pygame.transform.flip(img,True,False)
            frames=[]
            for item in reversed(self.load_frames(img, 32, 32)):
                frames.append(item)
            anchor_x=anchor[0]
            anchor_y=anchor[1]
            self.newAnimation(name+".flip",frames,(1-anchor_x,anchor_y),shadow)


    def addImage(self,name,file,anchor,flip=True,shadow=False):
        img=pygame.image.load(self.base/"img"/file).convert_alpha()
        self.newImage(name,img,anchor,shadow)
        if flip==True:
            img=pygame.transform.flip(img,True,False)
            anchor_x=anchor[0]
            anchor_y=anchor[1]
            self.newImage(name+".flip",img,(1-anchor_x,anchor_y),shadow)

    def newImage(self,name,img,anchor,shadow):
        self.images[name]=[]
        metadata=Image(name,anchor[0],anchor[1],shadow,ImageCache.IMAGE)
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
    
    def newAnimation(self,name,frames,anchor,shadow):
        self.animations[name]=[]
        metadata=Image(name,anchor[0],anchor[1],shadow,ImageCache.ANIMATION)
        self.metadata[name]=metadata
        metadata.frames=len(frames)
        #escalados
        w = frames[0].get_width()
        h = frames[0].get_height()


        for scale in self.LUT:
            new_frames=[]
            for frame in frames:

                #resize = r_min + (scale - scale_min) * (r_max - r_min) / (scale_max - scale_min)
                resize=scale/self.resizeFactor
                #scale=item["scale"]/conversion
                new_frame = pygame.transform.scale(frame,(int(w * resize), int(h * resize)))
                new_frames.append(new_frame)
            self.animations[name].append(new_frames)

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

    def getAnimation(self,name,escala):
        num_samples=self.config.num_samples
        scale_min=self.config.scale_min

        i =round(math.log(escala / scale_min) * self.inv_log_ratio)
        if i>=num_samples:
            return None

        return self.animations[name][i]

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
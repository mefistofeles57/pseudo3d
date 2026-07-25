import pygame
import math
from Point import Point
from Image import Image
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class ImageCache:

    num_samples=100
    scale_max=1500
    scale_min=80
    resize_at_1=1.5

    def __init__(self,context:"GameContext"):
        self.images={}
        self.metadata={}
        self.inv_log_ratio=0.0
        self.LUT=[]
        self.getScaleTable()

        #resize factor
        #necesito la escala en (0,0,1)
        p=context.camera.project(Point(0.0,0.0,1.0))
        self.resizeFactor=p.z/ImageCache.resize_at_1

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




#    def getScaleTableOLD(self,numtramos):
#        escalas=[]
#        distancia=(self.h+(numtramos))-self.horizon
#        delta=distancia/numtramos
#
#        for i in range(numtramos):
#            y=(delta*(i))+self.horizon
#            #se usa la y del centro del tramo para minimizar el error
#            y_centro=(delta*(i+0.5))+self.horizon
#            z=self.unproject(y_centro)
#
#            if z>0.0:
#                p1=self.project(Point(0.0,0.0,z))
#                escalas.append({"index":i,"z":z,"y":y,"scale":p1.z})
#
#        return escalas

    def getScaleTable(self):
        num_samples=ImageCache.num_samples
        scale_max=ImageCache.scale_max
        scale_min=ImageCache.scale_min
        ratio = (scale_max / scale_min) ** (1.0 / (num_samples - 1))
        self.inv_log_ratio = 1.0 / math.log(ratio)
        self.LUT.clear()
        for i in range(num_samples):
            scale = scale_min * ratio**i
            self.LUT.append(scale)

    def getImage(self,name,escala):
        num_samples=ImageCache.num_samples
        scale_min=ImageCache.scale_min

        i =round(math.log(escala / scale_min) * self.inv_log_ratio)
        if i>=num_samples:
            i=num_samples-1

        return self.images[name][i]


#    def unproject(self,target_y):
#        z0=0
#        z1=self.view_distance
#
#        while z1-z0 > 0.001:
#            zm = (z0+z1) /2
#            if self.project(Point(0.0,0.0,zm)).y < target_y:
#                z1=zm
#            else:
#                z0=zm
#        return zm

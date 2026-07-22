import pygame

class ImageCache:

    HIGH=0
    MEDIUM=1
    LOW=2

    def __init__(self,LUTh,LUTm,LUTl):
        self.images={}
        self.scales={}
        self.anchor={}
        self.LUTh=LUTh
        self.LUTm=LUTm
        self.LUTl=LUTl

    def addImage(self,name,file,type,anchor,flip=True):
        img=pygame.image.load("img/"+file).convert_alpha()
        self.newImage(name,img,type,anchor)
        if flip==True:
            img=pygame.transform.flip(img,True,False)
            self.newImage(name+".flip",img,type,1-anchor)

    def newImage(self,name,img,type,anchor):
        self.images[name]=[]
        self.scales[name]=type
        self.anchor[name]=anchor
        #escalados
        w = img.get_width()
        h = img.get_height()
        #temporalmente hasta que tenga mejores imagenes
        #img= pygame.transform.scale(img,(int(w * 0.5), int(h * 0.5)))
        w = img.get_width()
        h = img.get_height()

        LUT=self.LUTh
        if type==ImageCache.MEDIUM:
            LUT=self.LUTm
        elif type==ImageCache.LOW:
            LUT=self.LUTl

        s_max=LUT[-1]["scale"]
        #s_min=self.LUT[0]["scale"]

        conversion=s_max

        for item in LUT:
            scale=item["scale"]/conversion
            new_img = pygame.transform.scale(img,(int(w * scale), int(h * scale)))
            self.images[name].append(new_img)


    def getImage(self,name,escala):
        #buscar escala
        type=self.scales[name]
        LUT=self.LUTh
        if type==ImageCache.MEDIUM:
            LUT=self.LUTm
        elif type==ImageCache.LOW:
            LUT=self.LUTl

        for item in LUT:
            if item["scale"]>escala:
                 return self.images[name][item["index"]]
        pass
        return self.images[name][LUT[-1]["index"]]
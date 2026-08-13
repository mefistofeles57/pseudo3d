import pygame
from MapGenerator import MapGenerator
from Escenario import Escenario
from Road import Road
from Road import Line
from Camera import Camera
from Player import Player
from VisualObjProfile import VisualObjProfile
from FrameData import FrameData

class GameContext:
    def __init__(self,screen:pygame.Surface):
        self.screen=screen
        self.road=Road()
        self.frame_data=FrameData()
        self.camera=Camera(self)
        self.player=Player(self)
        self.keys=None
        self.default_profile=None
        self.createMap()

    def createMap(self):
        objects=[]



        MapGenerator.setProfile(Escenario(self))

        default_profile=VisualObjProfile()
        self.default_profile=default_profile
        #sombra estrecha
        default_profile.shadow_color=(0,0,0)
        default_profile.shadow_alpha=60
        default_profile.shadow_width_factor=1.4
        default_profile.shadow_height=0.2

        poste_profile=VisualObjProfile()
        #sombra ancha
        poste_profile.shadow_color=(0,0,0)
        poste_profile.shadow_alpha=60
        poste_profile.shadow_width_factor=2.0
        poste_profile.shadow_height=0.2
        poste_profile.shadow_offset_z=-0.01

        MapGenerator.setObjProfile(default_profile)

        for _ in range(5):
            #recta
            self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,10))
            objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow.flip",2.5,0.5,1.3)
            objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow.flip",2.5,0.5,-1.3)
            #bajada
            #tramo1=MapGenerator.pattern(MapGenerator.HILL,0.02,20)
            #curva der
            #tramo2=MapGenerator.pattern(MapGenerator.CURVE,0.05,10)
            #self.road.add(MapGenerator.merge(tramo2,tramo1))
            self.road.add(MapGenerator.pattern(MapGenerator.CURVE,0.05,10))
            #farolas
            objects=MapGenerator.objects(objects,self.road.segments[-10:],"farola",4.0,0.6,1.5)
            objects=MapGenerator.objects(objects,self.road.segments[-10:],"farola.flip",4.0,0.6,-1.5)
            #quitamiedos
            objects=MapGenerator.objects(objects,self.road.segments[-10:],"quitamiedos",0.1,0.03,-1.3)
            objects=MapGenerator.objects(objects,self.road.segments[-10:],"quitamiedos",0.1,0.03,1.3)
            objects=MapGenerator.objects(objects,self.road.segments[-10:],"poste",1.0,0.1,-1.3,profile=poste_profile)
            objects=MapGenerator.objects(objects,self.road.segments[-10:],"poste",1.0,0.1,1.3,profile=poste_profile)
            #recta
            self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,10))
            objects=MapGenerator.objects(objects,self.road.segments[-10:],"arbol",2.5,0.6,1.5)
            objects=MapGenerator.objects(objects,self.road.segments[-10:],"arbol",2.5,0.6,-1.5)
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,2.0,0.5,0.5)
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-2.0,-0.5,0.5)
            #subida
            self.road.add(MapGenerator.pattern(MapGenerator.HILL,0.02,20))
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,1.5)
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-1.5)
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,2.0,0.5,0.5)
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-2.0,-0.5,0.5)
            #recta
            self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,10))
            objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow",2.5,0.5,1.3)
            objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow",2.5,0.5,-1.3)
            #curva izq
            self.road.add(MapGenerator.pattern(MapGenerator.CURVE,-0.05,50))
            #quitamiedos
            objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.1,0.03,-1.3)
            objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.1,0.03,1.3)
            objects=MapGenerator.objects(objects,self.road.segments[-50:],"poste",1.0,0.1,-1.3,profile=poste_profile)
            objects=MapGenerator.objects(objects,self.road.segments[-50:],"poste",1.0,0.1,1.3,profile=poste_profile)
            #map,count,image,step,offset,x
            #recta
            self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,20))
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,1.5)
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-1.5)
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,2.0,0.5,0.5)
            objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-2.0,-0.5,0.5)
            #bajada
            self.road.add(MapGenerator.pattern(MapGenerator.HILL,-0.01,20))
            #recta
            self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,20))
            objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow.flip",2.5,0.5,1.3)
            objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow.flip",2.5,0.5,-1.3)
            #curva der
            self.road.add(MapGenerator.pattern(MapGenerator.CURVE,0.05,50))
            #quitamiedos
            objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.1,0.03,-1.3)
            objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.1,0.03,1.3)
            objects=MapGenerator.objects(objects,self.road.segments[-50:],"poste",1.0,0.1,-1.3,profile=poste_profile)
            objects=MapGenerator.objects(objects,self.road.segments[-50:],"poste",1.0,0.1,1.3,profile=poste_profile)

        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,-2.0,-0.3,-0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,2.0,0.3,0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,-2.5,-0.3,-0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,2.5,0.3,0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,-3.0,-0.3,-0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,3.0,0.3,0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,-3.5,-0.3,-0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,3.5,0.3,0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,-4.0,-0.3,-0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,4.0,0.3,0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,-4.5,-0.3,-0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,4.5,0.3,0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,-5.0,-0.3,-0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,5.0,0.3,0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"piedra",10.0,0.1,-1.5,-0.3,-0.3)
        objects=MapGenerator.objects(objects,self.road.segments,"piedra.flip",10.0,0.4,1.5,0.3,0.3)
        self.road.objects=objects
            

        ##position,x,width,offset,freq,color
        l=Line(0.35,-0.0025,0.005,0,2,[(255,255,255),None])
        self.road.addLine(l,0,self.road.segments[-1].index)
        l=Line(-0.35,-0.0025,0.005,0,2,[(255,255,255),None])
        self.road.addLine(l,0,self.road.segments[-1].index)
        l=Line(-1.05,0.01,0.01,0,1,[(255,255,255)])
        self.road.addLine(l,0,self.road.segments[-1].index)
        l=Line(1.05,-0.01,-0.01,0,1,[(255,255,255)])
        self.road.addLine(l,0,self.road.segments[-1].index)



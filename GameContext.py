import pygame
from MapGenerator import MapGenerator
from Escenario import Escenario
from Road import Road
from Road import Line
from Camera import Camera
from Player import Player


class GameContext:
    def __init__(self,screen:pygame.Surface):
        self.screen=screen
        self.road=Road()
        self.camera=Camera(screen,self.road)
        self.player=Player()
        self.keys=None
        self.createMap(self.road)


    def createMap(self,road):
        objects=[]
        MapGenerator.setProfile(Escenario(self))
        for i in range(5):
            #recta
            road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,0,10,0))

            #bajada
            road.add(MapGenerator.pattern(MapGenerator.HILL,0.1,10,0,10))
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola",4.0,0.6,1.5)
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola.flip",4.0,0.6,-1.5)
            #colina
            road.add(MapGenerator.pattern(MapGenerator.HILL,-0.1,10,0,10))
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola",4.0,0.6,1.5)
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola.flip",4.0,0.6,-1.5)
            #quitamiedos
            objects=MapGenerator.objects(objects,road.segments[-48:],"quitamiedos",0.05,0.1,-1.3)
            objects=MapGenerator.objects(objects,road.segments[-48:],"quitamiedos",0.05,0.1,1.3)
            objects=MapGenerator.objects(objects,road.segments[-46:],"poste",5.0,0.5,-1.3)
            objects=MapGenerator.objects(objects,road.segments[-46:],"poste",5.0,0.5,1.3)
            #carteles de curva lado derecho
            #recta
            road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,0,10,0))
            objects=MapGenerator.objects(objects,road.segments[-10:],"arbol",2.5,0.6,1.5)
            objects=MapGenerator.objects(objects,road.segments[-10:],"arbol",2.5,0.6,-1.5)
            #curva izq
            road.add(MapGenerator.pattern(MapGenerator.CURVE,-0.5,50,0,50))
            #map,count,image,step,offset,x
            objects=MapGenerator.objects(objects,road.segments[-80:-70],"signal.arrow.flip",2.5,0.5,1.0)
            objects=MapGenerator.objects(objects,road.segments[-80:-70],"signal.arrow.flip",2.5,0.5,-1.0)
            #recta
            road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,0,20,0))
            objects=MapGenerator.objects(objects,road.segments[-20:],"arbol",2.5,0.6,1.5)
            objects=MapGenerator.objects(objects,road.segments[-20:],"arbol",2.5,0.6,-1.5)
            #bajada
            road.add(MapGenerator.pattern(MapGenerator.HILL,0.1,10,0,10))
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola",4.0,0.6,1.5)
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola.flip",4.0,0.6,-1.5)
            #recta
            road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,0,20,0))
            objects=MapGenerator.objects(objects,road.segments[-20:],"arbol",2.5,0.6,1.5)
            objects=MapGenerator.objects(objects,road.segments[-20:],"arbol",2.5,0.6,-1.5)
            #curva der
            road.add(MapGenerator.pattern(MapGenerator.CURVE,0.5,50,0,50))
            #map,count,image,step,offset,x
            objects=MapGenerator.objects(objects,road.segments[-80:-70],"signal.arrow",2.5,0.5,1.0)
            objects=MapGenerator.objects(objects,road.segments[-80:-70],"signal.arrow",2.5,0.5,-1.0)
            #arbustos
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,-1.5,-0.3,-0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,1.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto.flip",1.0,0.4,-2.0,-0.3,-0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto.flip",1.0,0.4,2.0,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,-2.5,-0.3,-0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,2.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto.flip",1.0,0.4,-3.0,-0.3,-0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto.flip",1.0,0.4,3.0,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,-3.5,-0.3,-0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,3.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,-4.0,-0.3,-0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,4.0,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"piedra",10.0,0.2,-1.5,-0.3,-0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"piedra.flip",10.0,0.3,1.5,0.3,0.3)

        ##position,x,width,offset,freq,color
        l=Line(0.35,-0.0025,0.005,0,2,[(255,255,255),None])
        road.addLine(l,0,road.segments[-1].index)
        l=Line(-0.35,-0.0025,0.005,0,2,[(255,255,255),None])
        road.addLine(l,0,road.segments[-1].index)
        l=Line(-1.05,0.01,0.01,0,1,[(255,255,255)])
        road.addLine(l,0,road.segments[-1].index)
        l=Line(1.05,-0.01,-0.01,0,1,[(255,255,255)])
        road.addLine(l,0,road.segments[-1].index)

        road.objects=objects

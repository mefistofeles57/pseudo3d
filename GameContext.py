import pygame
from MapGenerator import MapGenerator
from Escenario import Escenario
from Road import Road
from Road import Line
from Camera import Camera
from Player import Player
from VisualObjProfile import VisualObjProfile
from FrameData import FrameData
from Estados import *

class GameContext:


    def __init__(self,screen:pygame.Surface,root,gen_scale=1.0):
        self.gen_scale=gen_scale
        self.root=root
        self.screen=screen
        self.road=Road()
        self.frame_data=FrameData()
        self.camera=Camera(self)
        self.player=Player(self)
        self.keys=None
        self.default_profile=None
        self.escenario=Escenario(self)
        self.createMap(self.escenario)
        self.estado=STARTING
        #stuck
        self.stuck_time=0.0
        #inicio
        self.countdown=3.99
        #game data
        self.timer=0.0
        self.score=0
        self.stage=1

    def createMap(self,escenario):
        objects=[]



        MapGenerator.setProfile(escenario)

        default_profile=VisualObjProfile()
        self.default_profile=default_profile
        #sombra estrecha
        default_profile.shadow_color=(0,0,0)
        default_profile.shadow_alpha=80
        default_profile.shadow_width_factor=1.4
        default_profile.shadow_height=0.2
        default_profile.collide_radius=0.05
        default_profile.collide_radius2=0.05*0.05

        poste_profile=VisualObjProfile()
        #sombra ancha
        poste_profile.shadow_color=(0,0,0)
        poste_profile.shadow_alpha=80
        poste_profile.shadow_width_factor=2.0
        poste_profile.shadow_height=0.2
        poste_profile.shadow_offset_z=-0.01
        poste_profile.collide_radius=0.05
        poste_profile.collide_radius2=0.05*0.05

        piedra_profile=VisualObjProfile()
        piedra_profile.collide_radius=0.15
        piedra_profile.collide_radius2=0.15*0.15


        checkpoint_profile=VisualObjProfile()
        #sombra ancha
        checkpoint_profile.shadow_color=(0,0,0)
        checkpoint_profile.shadow_alpha=60
        checkpoint_profile.shadow_width_factor=1.3
        checkpoint_profile.shadow_height=0.3
        checkpoint_profile.shadow_offset_z=0.1

        MapGenerator.setObjProfile(default_profile)

        #recta inicio con decoración bonita
        #cartel de salida, gradas , farolas y marcas en el suelo
        self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,20))
        MapGenerator.addMark(self.road.segments[-18], "linea", x=-1.1, z=0.5, w=2.2, h=1.0)
        #pequeñas elevaciones
        self.road.add(MapGenerator.pattern(MapGenerator.HILL,0.02,3))
        self.road.add(MapGenerator.pattern(MapGenerator.HILL,-0.02,3))
        self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,2))
        self.road.add(MapGenerator.pattern(MapGenerator.HILL,0.03,3))
        self.road.add(MapGenerator.pattern(MapGenerator.HILL, -0.03, 3))
        
        #pequeña recta con flechas y señales de curva
        self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,5))
        objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow.flip",2.5,0.5,1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow.flip",2.5,0.5,-1.3)
        MapGenerator.addMark(self.road.segments[-1],"flecha.1",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-2],"flecha.2",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-1],"flecha.1",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-2],"flecha.2",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-1],"flecha.1",x=0.4,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-2],"flecha.2",x=0.4,z=0.0,w=0.5,h=1.0)

        MapGenerator.addEnemy(self.road.segments[-1],0.0, 0.0,8.0)
        MapGenerator.addEnemy(self.road.segments[-1],0.2, 0.5,11.0)
            #bajada
            #tramo1=MapGenerator.pattern(MapGenerator.HILL,0.02,20)
            #curva der
            #tramo2=MapGenerator.pattern(MapGenerator.CURVE,0.05,10)
            #self.road.add(MapGenerator.merge(tramo2,tramo1))
        #pequeña curva a la derecha con farolas y quitamiedos
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE,0.025,10))
        #farolas
        objects=MapGenerator.objects(objects,self.road.segments[-10:],"farola",4.0,0.6,1.5)
        objects=MapGenerator.objects(objects,self.road.segments[-10:],"farola.flip",4.0,0.6,-1.5)
        #quitamiedos
        objects=MapGenerator.objects(objects,self.road.segments[-10:-9],"piedra",10.0,0.0,-1.4,profile=piedra_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-10:-9],"piedra",10.0,0.0,1.4,profile=piedra_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-10:],"quitamiedos",0.1,0.03,-1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-10:],"quitamiedos",0.15,0.03,1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-10:],"poste",1.0,0.1,-1.3,profile=poste_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-10:],"poste",1.0,0.1,1.3,profile=poste_profile)
        #recta con arboles
        self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,10))
        objects=MapGenerator.objects(objects,self.road.segments[-10:],"arbol",2.5,0.6,1.5)
        objects=MapGenerator.objects(objects,self.road.segments[-10:],"arbol",2.5,0.6,-1.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,2.0,0.5,0.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-2.0,-0.5,0.5)
            #MapGenerator.addEnemy(self.road.segments[-5],0.3, -0.5,8.0)
        #subida con flechas y árboles
        self.road.add(MapGenerator.pattern(MapGenerator.HILL,0.02,20))
        MapGenerator.addMark(self.road.segments[-1],"flecha.1",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-2],"flecha.2",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-1],"flecha.1",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-2],"flecha.2",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-1],"flecha.1",x=0.4,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-2],"flecha.2",x=0.4,z=0.0,w=0.5,h=1.0)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,1.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-1.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,2.0,0.5,0.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-2.0,-0.5,0.5)
        #recta con señales
        self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,10))
        objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow",2.5,0.5,1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow",2.5,0.5,-1.3)
        #curva grande a la izquierda
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE,-0.05,50))
        #quitamiedos
        objects=MapGenerator.objects(objects,self.road.segments[-50:-49],"piedra",10.0,0.0,-1.4,profile=piedra_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-50:-49],"piedra",10.0,0.0,1.4,profile=piedra_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.15,0.03,-1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.1,0.03,1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"poste",1.0,0.1,-1.3,profile=poste_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"poste",1.0,0.1,1.3,profile=poste_profile)
        #curva grande a la derecha
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE,0.05,50))
        #quitamiedos
        objects=MapGenerator.objects(objects,self.road.segments[-50:-49],"piedra",10.0,0.0,-1.4,profile=piedra_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-50:-49],"piedra",10.0,0.0,1.4,profile=piedra_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.15,0.03,-1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.1,0.03,1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"poste",1.0,0.1,-1.3,profile=poste_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"poste",1.0,0.1,1.3,profile=poste_profile)
        #recta con árboles
        self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,20))
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,1.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-1.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,2.0,0.5,0.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-2.0,-0.5,0.5)
        #bajada con dibujos
        self.road.add(MapGenerator.pattern(MapGenerator.HILL,-0.01,20))
        MapGenerator.addMark(self.road.segments[-10],"flecha.1",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-11],"flecha.2",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-10],"flecha.1",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-11],"flecha.2",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-10],"flecha.1",x=0.4,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-11], "flecha.2", x=0.4, z=0.0, w=0.5, h=1.0)
        #elevaciones
        self.road.add(MapGenerator.pattern(MapGenerator.HILL,0.02,3))
        self.road.add(MapGenerator.pattern(MapGenerator.HILL,-0.02,3))
        self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,2))
        self.road.add(MapGenerator.pattern(MapGenerator.HILL,0.03,4))
        self.road.add(MapGenerator.pattern(MapGenerator.HILL, -0.03, 4))
        self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,2))
        self.road.add(MapGenerator.pattern(MapGenerator.HILL,0.02,1))
        self.road.add(MapGenerator.pattern(MapGenerator.HILL, -0.02, 1))
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,1.5,0.5,0.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-1.5,-0.5,0.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,2.0,0.5,0.5)
        objects=MapGenerator.objects(objects,self.road.segments[-20:],"arbol",2.5,0.6,-2.0,-0.5,0.5)
        #curva der
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE,0.07,50))
        #quitamiedos
        objects=MapGenerator.objects(objects,self.road.segments[-50:-49],"piedra",10.0,0.0,-1.4,profile=piedra_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-50:-49],"piedra",10.0,0.0,1.4,profile=piedra_profile)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.1,0.03,-1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"quitamiedos",0.15,0.03,1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-50:],"poste",1.0,0.1,-1.3,profile=poste_profile)
        objects = MapGenerator.objects(objects, self.road.segments[-50:], "poste", 1.0, 0.1, 1.3, profile=poste_profile)
        #recta con checkpoint y señales de curva
        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 100))
        MapGenerator.addMark(self.road.segments[-50],"flecha.1",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-51],"flecha.2",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-50],"flecha.1",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-51],"flecha.2",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-50],"flecha.1",x=0.4,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-51],"flecha.2",x=0.4,z=0.0,w=0.5,h=1.0)
        objects=MapGenerator.objects(objects,self.road.segments[-100:-30],"arbol",2.5,0.6,1.5,0.5,0.5)
        objects=MapGenerator.objects(objects,self.road.segments[-100:-30],"arbol",2.5,0.6,-1.5,-0.5,0.5)
        objects=MapGenerator.objects(objects,self.road.segments[-100:-30],"arbol",2.5,0.6,2.0,0.5,0.5)
        objects = MapGenerator.objects(objects, self.road.segments[-100:-30], "arbol", 2.5, 0.6, -2.0, -0.5, 0.5)

        objects=MapGenerator.objects(objects,self.road.segments[-30:-10],"farola",4.0,0.6,1.5)
        objects=MapGenerator.objects(objects,self.road.segments[-30:-10],"farola.flip",4.0,0.6,-1.5)

        objects=MapGenerator.objects(objects,self.road.segments[-5:-4],"checkpoint",step=1.0,offset=0.5,x=1.3,profile=checkpoint_profile)
        MapGenerator.addMark(self.road.segments[-5],"parrilla",x=-1.0,z=0.25,w=0.5,h=0.5)
        MapGenerator.addMark(self.road.segments[-5],"parrilla",x=-0.5,z=0.25,w=0.5,h=0.5)
        MapGenerator.addMark(self.road.segments[-5],"parrilla",x=0.0,z=0.25,w=0.5,h=0.5)
        MapGenerator.addMark(self.road.segments[-5],"parrilla",x=0.5,z=0.25,w=0.5,h=0.5)
        MapGenerator.addCheckpoint(self.road.segments[-5],0.5, 10.0)
        self.road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,20))
        objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow.flip",2.5,0.5,1.3)
        objects=MapGenerator.objects(objects,self.road.segments[-5:],"signal.arrow.flip",2.5,0.5,-1.3)

        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,-2.0,-0.3,-0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,2.0,0.3,0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,-2.5,-0.3,-0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,2.5,0.3,0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,-3.0,-0.3,-0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,3.0,0.3,0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,-3.5,-0.3,-0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,3.5,0.3,0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,-4.0,-0.3,-0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,4.0,0.3,0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,-4.5,-0.3,-0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto.flip",1.0,0.4,4.5,0.3,0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,-5.0,-0.3,-0.3,collidable=False)
        objects=MapGenerator.objects(objects,self.road.segments,"arbusto",1.0,0.4,5.0,0.3,0.3,collidable=False)
#        objects=MapGenerator.objects(objects,self.road.segments,"piedra",10.0,0.1,-1.5,-0.3,-0.3,profile=piedra_profile)
#        objects=MapGenerator.objects(objects,self.road.segments,"piedra.flip",10.0,0.4,1.5,0.3,0.3,profile=piedra_profile)
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


    def changeStatus(self,estado):
        if estado==STUCK:
            self.estado=estado
            self.player.reset()
            self.stuck_time=0.0
        else:
            self.estado=estado

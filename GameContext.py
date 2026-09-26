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
from CircuitParser import CircuitParser
import sys
from pathlib import Path

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
        self.checkpoints=None
        self.escenario=Escenario(self)
        self.createMap(self.escenario)
        self.estado=NONE
        #stuck
        self.stuck_time=0.0
        #inicio
        self.countdown=0.0
        #game data
        self.timer=60.0
        self.score=0
        self.stage=1

    def createMap(self, escenario):
        R = 0.05
        R_HARD = 0.07
        L = -0.05
        L_HARD = -0.07

        HILL = 0.01
        DOWN = -0.01
        HILL_HARD = 0.014
        DOWN_HARD = -0.014
        MapGenerator.setProfile(escenario)

        default_profile=VisualObjProfile()
        self.default_profile=default_profile
        #sombra estrecha
        default_profile.shadow_color=(0,0,0)
        default_profile.shadow_alpha=80
        default_profile.shadow_width_factor=1.4
        default_profile.shadow_height=0.2
        default_profile.collide_radius=0.07
        default_profile.collide_radius2=0.07*0.07

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
        checkpoint_profile.shadow_alpha=80
        checkpoint_profile.shadow_width_factor=1.3
        checkpoint_profile.shadow_height=0.3
        checkpoint_profile.shadow_offset_z=0.1

        MapGenerator.setObjProfile(default_profile)

        parser = CircuitParser(
            self,
            curves={"CR": R, "CL": L, "CHR": R_HARD, "CHL": L_HARD},
            heights={"H": HILL, "D": DOWN, "HH": HILL_HARD, "DH": DOWN_HARD},
            profiles={
                "default": default_profile,
                "poste": poste_profile,
                "piedra": piedra_profile,
                "checkpoint": checkpoint_profile,
            }
        )

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent
        parser.load(
            str(base/"circuits/circuit1.yaml")
        )

        objects = parser.objects
        self.checkpoints = parser.checkpoints

        MapGenerator.addFinish(
            self.road.segments[-1],
            0.5
        )

        objects.sort(key=lambda obj: obj.z)
        self.road.objects=objects
            

        ##position,x,width,offset,freq,color
        l=Line(0.35,-0.0025,-0.03,0,2,[(255,255,255),None])
        self.road.addLine(l,0,self.road.segments[-1].index)
        l=Line(-0.35,-0.0025,-0.03,0,2,[(255,255,255),None])
        self.road.addLine(l,0,self.road.segments[-1].index)
        l=Line(-1.05,0.01,0.02,0,1,[(255,255,255)])
        self.road.addLine(l,0,self.road.segments[-1].index)
        l=Line(1.05,-0.01,-0.02,0,1,[(255,255,255)])
        self.road.addLine(l,0,self.road.segments[-1].index)

    
    def changeStatus(self,estado):
        if estado == STUCK:
            self.root.sounds["crash"].play()
            self.player.reset()
            self.stuck_time=0.0
        elif estado == STARTING:
            self.countdown=3.00
            self.root.sounds["321go"].play()
        elif estado == GAMEOVER_FINAL:
            self.root.sounds["gameover"].play()
        elif estado == FINISH:
            self.player.reset()

        self.estado=estado

    def add_bumps(self, repeats=3, segments=4, slope=0.025):
        for _ in range(repeats):
            self.road.add(
                MapGenerator.pattern(0.0, slope, segments)
            )

            self.road.add(
                MapGenerator.pattern(0.0, -slope, segments)
            )


    def vegetacion(self,objects,tramo,x,step_x,step_z,offset_z,number,objeto,side=0):
            
        obj=objects
        for i in range(number):
            obj = MapGenerator.objects(
                obj,
                tramo,
                objeto,
                step=step_z, offset=offset_z, x=x+i*step_x
                ,collidable=False, side=side
            )
            obj = MapGenerator.objects(
                obj,
                tramo,
                objeto,
                step=step_z, offset=offset_z, x=-x-i*step_x
                ,collidable=False, side=side
            )
        return obj

    def bosque(
        self,
        objects,
        tramo,
        x,
        step_x=1.0,
        step_z=1.0,
        offset_z=0.0,
        number=1,
        objeto="",
        random_x=0.0,
        random_step=0.0,
        side=0
    ):
        obj = objects

        for i in range(number):
            obj = MapGenerator.objects(
                obj,
                tramo,
                objeto,
                step_z,
                offset_z,
                x + i * step_x,
                random_x=random_x,
                random_step=random_step,
                collidable=True,
                side=side
            )

            obj = MapGenerator.objects(
                obj,
                tramo,
                objeto,
                step_z,
                offset_z,
                -x - i * step_x,
                random_x=-random_x,
                random_step=random_step,
                collidable=True,
                side=side
            )

        return obj
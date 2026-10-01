import pygame
from MapGenerator import MapGenerator
from Escenario import RecursosEscenario,Bosque,DesiertoRoca,Pradera
from Road import Road,Line,LineProfile
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
        self.recursos_escenario=RecursosEscenario(self)
        self.escenarios={
            "bosque": Bosque(self,self.recursos_escenario),
            "desierto_roca": DesiertoRoca(self,self.recursos_escenario),
            "pradera": Pradera(self,self.recursos_escenario),
        }
        self.escenario=self.escenarios["bosque"]

        #circuit - hay que fijarlo antes de createMap, que ya lo usa
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            self.base_circuitos = Path(sys._MEIPASS)
        else:
            self.base_circuitos = Path(__file__).resolve().parent
        self.parser = None
        self.gen_circuito = None
        self.next_circuit = None

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
        self.escenario.streamer.actualizar(self.road,self.road.segments[0].z)
        self.escenario.streamer.procesarCompleto()


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

        discontinua_blanca = LineProfile(grosor=0.03, offset=0, freq=2, color=[(255,255,255),None])
        continua_blanca = LineProfile(grosor=0.02, offset=0, freq=1, color=[(255,255,255)])
        discontinua_arena = LineProfile(grosor=0.03, offset=0, freq=2, color=[(232,217,160),None])
        continua_arena = LineProfile(grosor=0.02, offset=0, freq=1, color=[(232,217,160)])

        parser = CircuitParser(
            self,
            curves={"CR": R, "CL": L, "CHR": R_HARD, "CHL": L_HARD},
            heights={"H": HILL, "D": DOWN, "HH": HILL_HARD, "DH": DOWN_HARD},
            profiles={
                "default": default_profile,
                "poste": poste_profile,
                "piedra": piedra_profile,
                "checkpoint": checkpoint_profile,
            },
            line_profiles={
                "discontinua_blanca": discontinua_blanca,
                "continua_blanca": continua_blanca,
                "discontinua_arena": discontinua_arena,
                "continua_arena": continua_arena,
            },
            scene_profiles=self.escenarios
        )
        self.parser=parser

        parser.load(str(self.base_circuitos / "circuits/circuit1.jsonl"))

        objects = parser.objects
        self.checkpoints = parser.checkpoints


        objects.sort(key=lambda obj: obj.z)
        self.road.objects=objects
            


    
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

    def add_bumps(self, repeats=3, segments=4, slope=0.025, w=1.0):
        for _ in range(repeats):
            self.road.add(
                MapGenerator.pattern(0.0, slope, segments, w, w)
            )

            self.road.add(
                MapGenerator.pattern(0.0, -slope, segments, w, w)
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


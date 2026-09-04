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
        self.estado=NONE
        #stuck
        self.stuck_time=0.0
        #inicio
        self.countdown=0.0
        #game data
        self.timer=0.0
        self.score=0
        self.stage=1

    def createMap(self, escenario):
        R = 0.05
        R_HARD = 0.07
        L = -0.05
        L_HARD = -0.07

        HILL = 0.01
        DOWN = -0.01

        objects=[]



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
        checkpoint_profile.shadow_alpha=60
        checkpoint_profile.shadow_width_factor=1.3
        checkpoint_profile.shadow_height=0.3
        checkpoint_profile.shadow_offset_z=0.1

        MapGenerator.setObjProfile(default_profile)

        # ============================================================
        # 0. SALIDA
        # ============================================================

        num_segs = 70

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        MapGenerator.addMark(
            self.road.segments[-num_segs + 2],
            "linea",
            x=-1.1, z=0.5, w=2.2, h=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[2:4],
            "start",
            10.0, 1.0, 0.0,collidable=False
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[2:4],
            "column",
            10.0, 1.0, 1.11,collidable=False
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[2:4],
            "column",
            10.0, 1.0, -1.11,collidable=False
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[:20],
            "quitamiedos",
            0.09, 0.03, 1.1
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[:20],
            "quitamiedos",
            0.09, 0.03, -1.1
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[:20],
            "quitamiedos.down",
            0.09, 0.03, 1.1
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[:20],
            "quitamiedos.down",
            0.09, 0.03, -1.1
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[7:17],
            "pitbox.1",
            10.0, 0.0, -2.0
            ,collidable=False
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[7:17],
            "pitbox.2",
            10.0, 3.5, -2.0
            ,collidable=False
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[7:17],
            "pitbox.3",
            10.0, 7.0, -2.0
            ,collidable=False
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[:5],
            "ruedas",
            10.0, 1.5, -0.5
            ,collidable=False
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[:5],
            "ruedas",
            10.0, 1.3, 0.5
            ,collidable=False
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[5:25],
            "grada",
            5.0, 0.0, 2.0
            ,collidable=False
        )


        objects=self.vegetacion(objects,self.road.segments[-40:-1],x=1.7,step_x=1.0,step_z=6.0,offset_z=0.0,number=3,objeto="vegetacion.1")
        objects=self.vegetacion(objects,self.road.segments[-40:-1],x=1.7,step_x=1.0,step_z=6.0,offset_z=3.0,number=3,objeto="vegetacion.2")

        # PENDIENTE:
        # - arco/cartel de salida
        # - ruedas
        # - starter
        # - pit box
        # - banderas/carteles


        # ============================================================
        # 1. PRIMERAS CURVAS
        # ============================================================

        # ------------------------------------------------------------
        # Primera curva derecha
        # AVENIDA: farolas + vegetacion baja
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "farola.flip",
            5.0, 0.0, -1.4,
            random_step=0.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "farola",
            5.0, 2.5, 1.4,
            random_step=0.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            0.5, 1.0, -1.55,
            random_x=-0.25,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            0.5, 2.0, 1.55,
            random_x=0.25,
            random_step=1.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Descanso
        # TRANSICION AVENIDA -> BOSQUE
        # ------------------------------------------------------------

        num_segs = 25

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        self.bosque(objects,self.road.segments[-num_segs:],x=1.5,step_x=0.0,step_z=20.0,offset_z=0.0,number=1,objeto="arbol")
        self.bosque(objects,self.road.segments[-num_segs:],x=1.5,step_x=0.0,step_z=20.0,offset_z=4.0,number=1,objeto="arbol.2")
        self.bosque(objects,self.road.segments[-num_segs:],x=1.5,step_x=0.0,step_z=20.0,offset_z=8.0,number=1,objeto="arbol.3")
        self.bosque(objects,self.road.segments[-num_segs:],x=1.5,step_x=0.0,step_z=20.0,offset_z=16.0,number=1,objeto="arbol.4")


        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.2,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.45,
            random_x=0.2,
            random_step=1.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Curva izquierda
        # BOSQUE
        # ------------------------------------------------------------

        num_segs = 55

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)
        )


        self.bosque(objects,self.road.segments[-num_segs:],x=1.5,step_x=0.7,step_z=8.0,offset_z=0.0,number=3,random_step=3.5,random_x=0.3,objeto="arbol")
        self.bosque(objects,self.road.segments[-num_segs:],x=1.5,step_x=0.7,step_z=8.0,offset_z=4.0,number=3,random_step=3.5,random_x=0.3,objeto="arbol.2")
        self.bosque(objects,self.road.segments[-num_segs:],x=1.5,step_x=0.7,step_z=8.0,offset_z=0.0,number=3,random_step=3.5,random_x=0.3,objeto="arbol.3")
        self.bosque(objects,self.road.segments[-num_segs:],x=1.5,step_x=0.7,step_z=8.0,offset_z=4.0,number=3,random_step=3.5,random_x=0.3,objeto="arbol.4")


        # Sotobosque
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            3.5, 0.0, -1.45,
            random_x=-0.2,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 2.0, 1.45,
            random_x=0.2,
            random_step=0.8,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta dentro del bosque
        # Bastante poblada
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            3.5, 0.0, -1.5,
            random_x=-0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            3.0, 2.0, 1.5,
            random_x=0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.3",
            4.5, 1.0, -1.8,
            random_x=-0.30,
            random_step=1.2
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            5.0, 3.0, 1.8,
            random_x=0.30,
            random_step=1.2
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 2.0, -2.15,
            random_x=-0.35,
            random_step=1.8
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            6.0, 5.0, 2.15,
            random_x=0.35,
            random_step=1.8
        )

        # Algunas piedras
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "piedra",
            13.0, 4.0, -1.5,
            random_x=-0.25,
            random_step=2.5,
            profile=piedra_profile
        )


        # ============================================================
        # ZONA PROTEGIDA
        #
        # Incluye:
        # - curva larga derecha
        # - recta
        # - enlazada R -> L
        #
        # Quitamiedos solamente en el exterior de cada curva.
        # ============================================================


        # ------------------------------------------------------------
        # Curva larga derecha
        # Exterior = izquierda
        # ------------------------------------------------------------

        num_segs = 70

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)
        )

        # Bosque de fondo
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.3",
            7.0, 0.0, -2.0,
            random_x=-0.3,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            7.5, 2.0, 2.0,
            random_x=0.3,
            random_step=1.5
        )

        # Piedra de entrada al quitamiedos
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:-num_segs + 1],
            "piedra",
            10.0, 0.0, -1.4,
            profile=piedra_profile
        )

        # Quitamiedos exterior
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "quitamiedos",
            0.1, 0.03, -1.3
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "poste",
            1.0, 0.1, -1.3,
            profile=poste_profile
        )

        # Farolas en segunda línea
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "farola.flip",
            7.0, 1.0, -1.65,
            random_step=0.5
        )


        # ------------------------------------------------------------
        # Recta entre curvas
        # Sin quitamiedos
        # ------------------------------------------------------------

        num_segs = 25

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 0.0, -1.7,
            random_x=-0.2,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.7,
            random_x=0.2,
            random_step=1.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Enlazada derecha
        # Exterior = izquierda
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            8.0, 0.0, -2.0,
            random_x=-0.3,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.3",
            8.5, 3.0, 2.0,
            random_x=0.3,
            random_step=1.5
        )

        # Piedra de entrada
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:-num_segs + 1],
            "piedra",
            10.0, 0.0, -1.4,
            profile=piedra_profile
        )

        # Quitamiedos exterior
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "quitamiedos",
            0.1, 0.03, -1.3
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "poste",
            1.0, 0.1, -1.3,
            profile=poste_profile
        )

        # Farolas detrás
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "farola.flip",
            7.0, 1.0, -1.65,
            random_step=0.5
        )


        # ------------------------------------------------------------
        # Enlazada izquierda
        # Exterior = derecha
        # ------------------------------------------------------------

        num_segs = 55

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            8.0, 1.0, -2.0,
            random_x=-0.3,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            8.5, 3.0, 2.0,
            random_x=0.3,
            random_step=1.5
        )

        # Piedra de entrada
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:-num_segs + 1],
            "piedra",
            10.0, 0.0, 1.4,
            profile=piedra_profile
        )

        # Quitamiedos exterior
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "quitamiedos",
            0.1, 0.03, 1.3
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "poste",
            1.0, 0.1, 1.3,
            profile=poste_profile
        )

        # Farolas detrás
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "farola",
            7.0, 1.0, 1.65,
            random_step=0.5
        )


        # ------------------------------------------------------------
        # Salida de la zona protegida / claro
        # ------------------------------------------------------------

        num_segs = 35

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        # ============================================================
        # FLECHAS DE FINAL DE TUTORIAL
        # ============================================================

        for x in (-0.9, -0.25, 0.4):
            MapGenerator.addMark(
                self.road.segments[-10],
                "flecha.1",
                x=x, z=0.0, w=0.5, h=1.0
            )

            MapGenerator.addMark(
                self.road.segments[-11],
                "flecha.2",
                x=x, z=0.0, w=0.5, h=1.0
            )


        # ============================================================
        # 2. PRIMERA SECCION DE ENLAZADAS
        # BOSQUE DENSO
        # ============================================================

        # ------------------------------------------------------------
        # Primera izquierda
        # ------------------------------------------------------------

        num_segs = 45
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L, num_segs))

        # Primera linea
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            4.5, 0.0, -1.45,
            random_x=-0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            5.5, 2.0, 1.45,
            random_x=0.25,
            random_step=1.0
        )

        # Segunda linea
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            6.5, 1.0, -1.75,
            random_x=-0.30,
            random_step=1.3
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            7.0, 3.0, 1.75,
            random_x=0.30,
            random_step=1.3
        )

        # Fondo
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            9.0, 3.0, -2.1,
            random_x=-0.35,
            random_step=1.8
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            10.0, 5.0, 2.1,
            random_x=0.35,
            random_step=1.8
        )

        # Sotobosque
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            3.5, 0.0, -1.4,
            random_x=-0.20,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 2.0, 1.4,
            random_x=0.20,
            random_step=0.8,
            collidable=False
        )


        # ------------------------------------------------------------
        # Derecha
        # Seguimos dentro del bosque pero cambiamos especies
        # ------------------------------------------------------------

        num_segs = 45
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, num_segs))

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            5.0, 0.0, -1.5,
            random_x=-0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            4.5, 2.0, 1.5,
            random_x=0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            7.0, 1.0, -1.8,
            random_x=-0.30,
            random_step=1.3
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            6.5, 3.0, 1.8,
            random_x=0.30,
            random_step=1.3
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "piedra",
            14.0, 4.0, 1.45,
            random_x=0.25,
            random_step=2.5,
            profile=piedra_profile
        )


        # ------------------------------------------------------------
        # Segunda derecha, corta
        # Un pequeño claro lateral rompe la continuidad del bosque
        # ------------------------------------------------------------

        num_segs = 35
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, num_segs))

        # Izquierda bastante poblada
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            4.5, 0.0, -1.45,
            random_x=-0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            6.5, 2.0, -1.8,
            random_x=-0.30,
            random_step=1.3
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            9.0, 4.0, -2.1,
            random_x=-0.35,
            random_step=1.8
        )

        # Derecha más abierta
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 0.0, 1.45,
            random_x=0.25,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            9.0, 3.0, 1.9,
            random_x=0.30,
            random_step=2.0
        )


        # ------------------------------------------------------------
        # Izquierda larga de salida
        # El bosque vuelve a cerrarse
        # ------------------------------------------------------------

        num_segs = 55
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L, num_segs))

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            4.5, 0.0, -1.5,
            random_x=-0.25,
            random_step=0.9
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            5.0, 2.0, 1.5,
            random_x=0.25,
            random_step=0.9
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            6.5, 1.0, -1.8,
            random_x=-0.30,
            random_step=1.2
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            7.0, 3.0, 1.8,
            random_x=0.30,
            random_step=1.2
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            9.0, 4.0, -2.1,
            random_x=-0.35,
            random_step=1.8
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            10.0, 6.0, 2.1,
            random_x=0.35,
            random_step=1.8
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            3.5, 1.0, -1.4,
            random_x=-0.2,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 2.0, 1.4,
            random_x=0.2,
            random_step=0.8,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta de salida
        # El bosque empieza a abrirse antes del checkpoint
        # ------------------------------------------------------------

        num_segs = 35
        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            7.0, 0.0, -1.7,
            random_x=-0.30,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            8.0, 3.0, 1.7,
            random_x=0.30,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.20,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.45,
            random_x=0.20,
            random_step=1.0,
            collidable=False
        )


        # ============================================================
        # 3. PRIMER CHECKPOINT
        # CLARO
        # ============================================================

        checkpoint_1 = len(self.road.segments)

        num_segs = 25
        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[checkpoint_1:checkpoint_1 + 1],
            "checkpoint",
            step=1.0,
            offset=0.5,
            x=1.3,
            profile=checkpoint_profile
        )

        MapGenerator.addCheckpoint(
            self.road.segments[checkpoint_1],
            0.25,
            55.0
        )

        for x in (-1.0, -0.5, 0.0, 0.5):
            MapGenerator.addMark(
                self.road.segments[checkpoint_1],
                "parrilla",
                x=x, z=0.25, w=0.5, h=0.5
            )

        # Muy poca vegetacion cerca del checkpoint.
        # Arboles retirados para que la torre destaque.
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            10.0, 4.0, -1.9,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            11.0, 6.0, 1.9,
            random_x=0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            5.0, 2.0, -1.5,
            random_x=-0.2,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            5.5, 3.0, 1.5,
            random_x=0.2,
            random_step=1.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta antes de los bumps
        # Transicion del claro a terreno mas abierto
        # ------------------------------------------------------------

        num_segs = 20
        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        # Aqui evitaria volver inmediatamente a cerrar el bosque.
        # Vegetacion baja + algunos arboles aislados.

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            3.5, 0.0, -1.45,
            random_x=-0.2,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.5, 1.45,
            random_x=0.2,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            9.0, 2.0, -1.8,
            random_x=-0.25,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            10.0, 5.0, 1.8,
            random_x=0.25,
            random_step=2.0
        )


        # ------------------------------------------------------------
        # Repechos
        # Las señales deben mandar visualmente
        # ------------------------------------------------------------

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "rasante",
            30.0, 0.0, -1.4,
            collidable=True
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "rasante",
            30.0, 0.0, 1.4,
            collidable=True
        )

        bumps_start = len(self.road.segments)

        self.add_bumps(
            repeats=3,
            segments=4,
            slope=0.025
        )

        bumps_end = len(self.road.segments)

        # Vegetacion baja solamente.
        # Los cambios de rasante son el protagonista.
        objects = MapGenerator.objects(
            objects,
            self.road.segments[bumps_start:bumps_end],
            "arbusto",
            3.5, 0.0, -1.5,
            random_x=-0.25,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[bumps_start:bumps_end],
            "arbusto",
            4.0, 2.0, 1.5,
            random_x=0.25,
            random_step=0.8,
            collidable=False
        )

        # ============================================================
        # 4. RASANTES + CURVAS
        # Zona ondulada / paisaje más abierto
        # ============================================================

        # ------------------------------------------------------------
        # Subida + curva derecha
        #
        # Venimos de los bumps. Mantenemos el paisaje abierto para
        # que se aprecie bien el cambio de altura.
        # ------------------------------------------------------------

        num_segs = 30

        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)

        self.road.add(MapGenerator.merge(curve, hill))

        # Vegetación baja cercana
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            3.5, 0.0, -1.45,
            random_x=-0.25,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.5, 1.45,
            random_x=0.25,
            random_step=0.8,
            collidable=False
        )

        # Árboles aislados, retirados
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            9.0, 2.0, -1.8,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.3",
            10.0, 5.0, 1.8,
            random_x=0.30,
            random_step=2.0
        )

        # Alguna piedra en primer plano
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "piedra",
            14.0, 4.0, -1.5,
            random_x=-0.20,
            random_step=2.5,
            profile=piedra_profile
        )


        # ------------------------------------------------------------
        # Bajada + curva izquierda
        #
        # Seguimos abiertos, pero cambia la distribución:
        # más masa a la derecha y fondo a la izquierda.
        # ------------------------------------------------------------

        num_segs = 25

        hill = MapGenerator.pattern(MapGenerator.HILL, DOWN, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)

        self.road.add(MapGenerator.merge(curve, hill))

        # Izquierda: baja y abierta
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            3.5, 0.0, -1.45,
            random_x=-0.20,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            9.0, 3.0, -1.9,
            random_x=-0.30,
            random_step=2.0
        )

        # Derecha: algo más poblada
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 0.0, 1.55,
            random_x=0.25,
            random_step=1.2
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            8.0, 2.0, 1.85,
            random_x=0.30,
            random_step=1.6
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, 1.45,
            random_x=0.20,
            random_step=0.8,
            collidable=False
        )

        # Piedra aislada
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "piedra",
            13.0, 4.0, 1.5,
            random_x=0.20,
            random_step=2.5,
            profile=piedra_profile
        )


        # ------------------------------------------------------------
        # Elevación larga + curva izquierda
        #
        # Aquí vuelve progresivamente el bosque.
        # No tan cerrado como antes del checkpoint.
        # ------------------------------------------------------------

        num_segs = 35

        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)

        self.road.add(MapGenerator.merge(curve, hill))

        # Primera línea
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            5.5, 0.0, -1.5,
            random_x=-0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 2.0, 1.5,
            random_x=0.25,
            random_step=1.0
        )

        # Segunda profundidad
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.3",
            7.5, 1.0, -1.8,
            random_x=-0.30,
            random_step=1.4
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            8.0, 3.0, 1.8,
            random_x=0.30,
            random_step=1.4
        )

        # Fondo más disperso
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            11.0, 4.0, -2.1,
            random_x=-0.35,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            12.0, 6.0, 2.1,
            random_x=0.35,
            random_step=2.0
        )

        # Sotobosque, pero menos denso que en el bosque anterior
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.5, 1.0, -1.4,
            random_x=-0.20,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            5.0, 2.5, 1.4,
            random_x=0.20,
            random_step=1.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta final
        #
        # Claro otra vez. Las flechas deben verse desde lejos.
        # ------------------------------------------------------------

        num_segs = 30

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        # Arbustos cercanos
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 0.0, -1.5,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.5,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )

        # Árboles sólo en segunda línea
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.3",
            9.0, 1.0, -1.9,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            10.0, 4.0, 1.9,
            random_x=0.30,
            random_step=2.0
        )

        for x in (-0.9, -0.25, 0.4):
            MapGenerator.addMark(
                self.road.segments[-10],
                "flecha.1",
                x=x, z=0.0, w=0.5, h=1.0
            )

            MapGenerator.addMark(
                self.road.segments[-11],
                "flecha.2",
                x=x, z=0.0, w=0.5, h=1.0
            )

        # ============================================================
        # 5. TRAMO RAPIDO
        # ============================================================

        # ------------------------------------------------------------
        # Curva derecha larga
        #
        # Salimos de la zona abierta y entramos otra vez en vegetacion,
        # pero sin llegar al bosque cerrado anterior.
        # ------------------------------------------------------------

        num_segs = 65

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)
        )

        # Primera linea
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            5.0, 0.0, -1.5,
            random_x=-0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            5.5, 2.0, 1.5,
            random_x=0.25,
            random_step=1.0
        )

        # Segunda profundidad
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.3",
            7.0, 1.0, -1.8,
            random_x=-0.30,
            random_step=1.4
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            7.5, 3.0, 1.8,
            random_x=0.30,
            random_step=1.4
        )

        # Fondo disperso
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            10.0, 4.0, -2.1,
            random_x=-0.35,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            11.0, 6.0, 2.1,
            random_x=0.35,
            random_step=2.0
        )

        # Sotobosque
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.4,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.5, 1.4,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta rapida
        #
        # AVENIDA DE FAROLAS.
        # Nada de arboles cerca: queremos una silueta limpia y repetitiva
        # que enfatice la velocidad.
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "farola.flip",
            4.5, 0.0, -1.4,
            random_step=0.4
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "farola",
            4.5, 2.25, 1.4,
            random_step=0.4
        )

        # Solo vegetacion baja.
        # No compite visualmente con las farolas.
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            5.0, 1.0, -1.65,
            random_x=-0.25,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            5.5, 3.0, 1.65,
            random_x=0.25,
            random_step=1.0,
            collidable=False
        )

        # Alguna piedra muy ocasional y retirada
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "piedra",
            18.0, 6.0, -1.8,
            random_x=-0.20,
            random_step=3.0,
            profile=piedra_profile
        )


        # ------------------------------------------------------------
        # Curva izquierda larga
        #
        # Termina la avenida y reaparece el bosque.
        # Hacemos la transicion bastante evidente.
        # ------------------------------------------------------------

        num_segs = 60

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)
        )

        # Arboles cercanos
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.3",
            4.5, 0.0, -1.5,
            random_x=-0.25,
            random_step=0.9
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            5.0, 2.0, 1.5,
            random_x=0.25,
            random_step=0.9
        )

        # Segunda linea
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.5, 1.0, -1.8,
            random_x=-0.30,
            random_step=1.3
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            7.0, 3.0, 1.8,
            random_x=0.30,
            random_step=1.3
        )

        # Fondo
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            9.0, 4.0, -2.1,
            random_x=-0.35,
            random_step=1.8
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            10.0, 6.0, 2.1,
            random_x=0.35,
            random_step=1.8
        )

        # Sotobosque
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            3.5, 0.0, -1.4,
            random_x=-0.20,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 2.0, 1.4,
            random_x=0.20,
            random_step=0.8,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta final
        #
        # El bosque se abre progresivamente.
        # No queremos otro corte brusco bosque -> claro.
        # ------------------------------------------------------------

        num_segs = 40

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        # Primera linea mas espaciada
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.2",
            7.0, 0.0, -1.55,
            random_x=-0.25,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.3",
            8.0, 3.0, 1.55,
            random_x=0.25,
            random_step=1.5
        )

        # Segunda linea aun mas dispersa
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol.4",
            10.0, 2.0, -1.9,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            11.0, 5.0, 1.9,
            random_x=0.30,
            random_step=2.0
        )

        # Vegetacion baja mantiene continuidad
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.5, 1.45,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )

        # ============================================================
        # 6. ZONA TRAMPA
        # ============================================================

        # Aviso de curvas sucesivas
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.s",
            30.0, 0.0, 1.3,
            collidable=True
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.s",
            30.0, 0.0, -1.3,
            collidable=True
        )


        # ------------------------------------------------------------
        # Subida + derecha
        # Terreno bastante abierto.
        # ------------------------------------------------------------

        num_segs = 18

        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)
        self.road.add(MapGenerator.merge(curve, hill))

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            3.5, 0.0, -1.45,
            random_x=-0.20,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.5, 1.45,
            random_x=0.20,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            9.0, 2.0, -1.9,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            10.0, 4.0, 1.9,
            random_x=0.30,
            random_step=2.0
        )


        # ------------------------------------------------------------
        # Bajada + izquierda
        # ------------------------------------------------------------

        num_segs = 18

        hill = MapGenerator.pattern(MapGenerator.HILL, DOWN, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)
        self.road.add(MapGenerator.merge(curve, hill))

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            3.5, 0.0, -1.45,
            random_x=-0.20,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 2.0, 1.45,
            random_x=0.20,
            random_step=0.8,
            collidable=False
        )

        # Cambiamos las masas lejanas de lado
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            8.0, 1.0, 1.85,
            random_x=0.30,
            random_step=1.8
        )


        # ------------------------------------------------------------
        # Nueva subida + derecha
        # ------------------------------------------------------------

        num_segs = 20

        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)
        self.road.add(MapGenerator.merge(curve, hill))

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            3.5, 0.0, -1.45,
            random_x=-0.20,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 2.0, 1.45,
            random_x=0.20,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "piedra",
            13.0, 3.0, -1.55,
            random_x=-0.20,
            random_step=2.5,
            profile=piedra_profile
        )


        # ------------------------------------------------------------
        # Pequeño respiro
        # Muy limpio para las flechas
        # ------------------------------------------------------------

        num_segs = 18

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 0.0, -1.55,
            random_x=-0.20,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            5.0, 2.0, 1.55,
            random_x=0.20,
            random_step=1.0,
            collidable=False
        )

        for x in (-0.9, -0.25, 0.4):
            MapGenerator.addMark(
                self.road.segments[-10],
                "flecha.1",
                x=x, z=0.0, w=0.5, h=1.0
            )
            MapGenerator.addMark(
                self.road.segments[-11],
                "flecha.2",
                x=x, z=0.0, w=0.5, h=1.0
            )


        # ------------------------------------------------------------
        # Ondulaciones
        # Aquí casi nada alto. La carretera tiene que dominar.
        # ------------------------------------------------------------

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "rasante",
            30.0, 0.0, -1.4,
            collidable=True
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "rasante",
            30.0, 0.0, 1.4,
            collidable=True
        )

        bumps_start = len(self.road.segments)

        self.add_bumps(
            repeats=4,
            segments=4,
            slope=0.03
        )

        bumps_end = len(self.road.segments)

        objects = MapGenerator.objects(
            objects,
            self.road.segments[bumps_start:bumps_end],
            "arbusto",
            3.5, 0.0, -1.5,
            random_x=-0.20,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[bumps_start:bumps_end],
            "arbusto",
            4.0, 2.0, 1.5,
            random_x=0.20,
            random_step=0.8,
            collidable=False
        )


        # ------------------------------------------------------------
        # Curva cerrada derecha
        #
        # Aquí SÍ pondría quitamiedos.
        # Es uno de los peligros importantes del circuito.
        # ------------------------------------------------------------

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva",
            30.0, 0.0, 1.3,
            collidable=True
        )

        guard_start = len(self.road.segments)

        num_segs = 45

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, R_HARD, num_segs)
        )

        guard_end = len(self.road.segments)

        guard_segments = self.road.segments[guard_start:guard_end]

        # Piedras de entrada
        objects = MapGenerator.objects(
            objects,
            self.road.segments[guard_start:guard_start + 1],
            "piedra",
            10.0, 0.0, -1.4,
            profile=piedra_profile
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[guard_start:guard_start + 1],
            "piedra",
            10.0, 0.0, 1.4,
            profile=piedra_profile
        )

        # Quitamiedos
        objects = MapGenerator.objects(
            objects,
            guard_segments,
            "quitamiedos",
            0.1, 0.03, -1.3
        )

        objects = MapGenerator.objects(
            objects,
            guard_segments,
            "quitamiedos",
            0.15, 0.03, 1.3
        )

        objects = MapGenerator.objects(
            objects,
            guard_segments,
            "poste",
            1.0, 0.1, -1.3,
            profile=poste_profile
        )

        objects = MapGenerator.objects(
            objects,
            guard_segments,
            "poste",
            1.0, 0.1, 1.3,
            profile=poste_profile
        )

        # Farolas detrás del guardarraíl
        objects = MapGenerator.objects(
            objects,
            guard_segments,
            "farola.flip",
            7.0, 1.0, -1.65,
            random_step=0.5
        )

        objects = MapGenerator.objects(
            objects,
            guard_segments,
            "farola",
            7.0, 4.5, 1.65,
            random_step=0.5
        )

        # Árboles retirados
        objects = MapGenerator.objects(
            objects,
            guard_segments,
            "arbol.3",
            10.0, 2.0, -2.0,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            guard_segments,
            "arbol.4",
            11.0, 5.0, 2.0,
            random_x=0.30,
            random_step=2.0
        )

        # Piedras de salida
        objects = MapGenerator.objects(
            objects,
            self.road.segments[guard_end - 1:guard_end],
            "piedra",
            10.0, 0.0, -1.4,
            profile=piedra_profile
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[guard_end - 1:guard_end],
            "piedra",
            10.0, 0.0, 1.4,
            profile=piedra_profile
        )


        # ------------------------------------------------------------
        # Recta después de la trampa
        # Descanso visual
        # ------------------------------------------------------------

        num_segs = 30

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 0.0, -1.5,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.5,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )


        # ============================================================
        # 7. SEGUNDA SECCION DE ENLAZADAS
        # Vuelta a bosque denso
        # ============================================================

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.s",
            30.0, 0.0, 1.3,
            collidable=True
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.s",
            30.0, 0.0, -1.3,
            collidable=True
        )


        # ------------------------------------------------------------
        # Izquierda
        # ------------------------------------------------------------

        num_segs = 50

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            4.5, 0.0, -1.5,
            random_x=-0.25,
            random_step=0.9
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            5.0, 2.0, 1.5,
            random_x=0.25,
            random_step=0.9
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            6.5, 1.0, -1.8,
            random_x=-0.30,
            random_step=1.3
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            7.0, 3.0, 1.8,
            random_x=0.30,
            random_step=1.3
        )


        # ------------------------------------------------------------
        # Derecha
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            4.5, 0.0, -1.5,
            random_x=-0.25,
            random_step=0.9
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            5.0, 2.0, 1.5,
            random_x=0.25,
            random_step=0.9
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            7.0, 1.0, -1.85,
            random_x=-0.30,
            random_step=1.3
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            7.5, 3.0, 1.85,
            random_x=0.30,
            random_step=1.3
        )


        # ------------------------------------------------------------
        # Curva cerrada izquierda
        # Señal ya existente.
        # Despejamos bastante alrededor.
        # ------------------------------------------------------------

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.flip",
            30.0, 0.0, -1.3,
            collidable=True
        )

        num_segs = 38

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, L_HARD, num_segs)
        )

        # Sólo vegetación retirada
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            8.0, 0.0, -1.9,
            random_x=-0.30,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            8.5, 2.0, 1.9,
            random_x=0.30,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.45,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta hacia checkpoint
        # El bosque se abre progresivamente.
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            7.0, 0.0, -1.65,
            random_x=-0.25,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            8.0, 3.0, 1.65,
            random_x=0.25,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.45,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )


        # ============================================================
        # 8. SEGUNDO CHECKPOINT
        # Otro claro fuerte
        # ============================================================

        checkpoint_2 = len(self.road.segments)

        num_segs = 25

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[checkpoint_2:checkpoint_2 + 1],
            "checkpoint",
            step=1.0,
            offset=0.5,
            x=1.3,
            profile=checkpoint_profile
        )

        MapGenerator.addCheckpoint(
            self.road.segments[checkpoint_2],
            0.25,
            40.0
        )

        for x in (-1.0, -0.5, 0.0, 0.5):
            MapGenerator.addMark(
                self.road.segments[checkpoint_2],
                "parrilla",
                x=x, z=0.25, w=0.5, h=0.5
            )

        # Vegetacion muy retirada
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            11.0, 4.0, -2.0,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            12.0, 6.0, 2.0,
            random_x=0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            5.0, 2.0, -1.5,
            random_x=-0.20,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            5.5, 3.0, 1.5,
            random_x=0.20,
            random_step=1.0,
            collidable=False
        )


        # ============================================================
        # 9. GRAN CURVA + CONTRACURVA
        #
        # Zona escenica. Vegetacion media y bastante profundidad.
        # ============================================================

        # ------------------------------------------------------------
        # Derecha + subida
        # ------------------------------------------------------------

        num_segs = 65

        curve = MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)
        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, num_segs)

        self.road.add(MapGenerator.merge(curve, hill))

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            6.0, 0.0, -1.6,
            random_x=-0.25,
            random_step=1.2
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            6.5, 2.0, 1.6,
            random_x=0.25,
            random_step=1.2
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            8.0, 1.0, -1.9,
            random_x=-0.30,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            8.5, 3.0, 1.9,
            random_x=0.30,
            random_step=1.5
        )


        # ------------------------------------------------------------
        # Izquierda + bajada
        # ------------------------------------------------------------

        num_segs = 70

        curve = MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)
        hill = MapGenerator.pattern(MapGenerator.HILL, DOWN, num_segs)

        self.road.add(MapGenerator.merge(curve, hill))

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            6.0, 0.0, -1.6,
            random_x=-0.25,
            random_step=1.2
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            6.5, 2.0, 1.6,
            random_x=0.25,
            random_step=1.2
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            8.0, 1.0, -1.9,
            random_x=-0.30,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            8.5, 3.0, 1.9,
            random_x=0.30,
            random_step=1.5
        )


        # ------------------------------------------------------------
        # Recta larga
        # Abrimos para las flechas
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 0.0, -1.5,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.5,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            10.0, 2.0, -2.0,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            11.0, 5.0, 2.0,
            random_x=0.30,
            random_step=2.0
        )

        for x in (-0.9, -0.25, 0.4):
            MapGenerator.addMark(
                self.road.segments[-20],
                "flecha.1",
                x=x, z=0.0, w=0.5, h=1.0
            )

            MapGenerator.addMark(
                self.road.segments[-21],
                "flecha.2",
                x=x, z=0.0, w=0.5, h=1.0
            )


        # ============================================================
        # 10. TRAMO FINAL
        # ============================================================

        # ------------------------------------------------------------
        # Curva derecha
        # El paisaje empieza a cerrarse.
        # ------------------------------------------------------------

        num_segs = 55

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            5.0, 0.0, -1.5,
            random_x=-0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            5.5, 2.0, 1.5,
            random_x=0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            7.0, 1.0, -1.85,
            random_x=-0.30,
            random_step=1.3
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            7.5, 3.0, 1.85,
            random_x=0.30,
            random_step=1.3
        )


        # ------------------------------------------------------------
        # Recta
        # ------------------------------------------------------------

        num_segs = 35

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 0.0, -1.45,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.45,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )


        # ------------------------------------------------------------
        # Subida + izquierda cerrada
        # Señal existente. Despejamos.
        # ------------------------------------------------------------

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.flip",
            30.0, 0.0, -1.3,
            collidable=True
        )

        num_segs = 25

        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, L_HARD, num_segs)

        self.road.add(MapGenerator.merge(curve, hill))

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 0.0, -1.5,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.5,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            9.0, 2.0, -2.0,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            10.0, 4.0, 2.0,
            random_x=0.30,
            random_step=2.0
        )


        # ------------------------------------------------------------
        # Recta
        # ------------------------------------------------------------

        num_segs = 40

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            7.0, 0.0, -1.7,
            random_x=-0.25,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            8.0, 3.0, 1.7,
            random_x=0.25,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.45,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )


        # ------------------------------------------------------------
        # Ultima derecha cerrada
        # Otra señal existente.
        # ------------------------------------------------------------

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva",
            30.0, 0.0, 1.3,
            collidable=True
        )

        num_segs = 40

        self.road.add(
            MapGenerator.pattern(MapGenerator.CURVE, R_HARD, num_segs)
        )

        # La hacemos visualmente intensa, pero sin quitamiedos otra vez.
        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol",
            5.5, 0.0, -1.55,
            random_x=-0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.2",
            6.0, 2.0, 1.55,
            random_x=0.25,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            7.5, 1.0, -1.9,
            random_x=-0.30,
            random_step=1.4
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            8.0, 3.0, 1.9,
            random_x=0.30,
            random_step=1.4
        )


        # ------------------------------------------------------------
        # Recta final
        # Empieza a abrirse hacia la meta.
        # ------------------------------------------------------------

        num_segs = 35

        self.road.add(
            MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs)
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.0, 0.0, -1.5,
            random_x=-0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbusto",
            4.5, 2.0, 1.5,
            random_x=0.20,
            random_step=0.9,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.3",
            10.0, 2.0, -2.0,
            random_x=-0.30,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects, self.road.segments[-num_segs:],
            "arbol.4",
            11.0, 5.0, 2.0,
            random_x=0.30,
            random_step=2.0
        )

        # ============================================================
        # 11. META / ÚLTIMO TRAMO
        # ============================================================

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L, 35))
        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 60))        
        MapGenerator.addMark(self.road.segments[-40],"flecha.1",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-41],"flecha.2",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-40],"flecha.1",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-41],"flecha.2",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-40],"flecha.1",x=0.4,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-41], "flecha.2", x=0.4, z=0.0, w=0.5, h=1.0)
        

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
            self.countdown=2.99
            self.root.sounds["321go"].play()
        elif estado == GAMEOVER_FINAL:
            self.root.sounds["gameover"].play()
        self.estado=estado

    def add_bumps(self, repeats=3, segments=4, slope=0.025):
        for _ in range(repeats):
            self.road.add(
                MapGenerator.pattern(
                    MapGenerator.HILL,
                    slope,
                    segments
                )
            )

            self.road.add(
                MapGenerator.pattern(
                    MapGenerator.HILL,
                    -slope,
                    segments
                )
            )


    def vegetacion(self,objects,tramo,x,step_x,step_z,offset_z,number,objeto):
            
        obj=objects
        for i in range(number):
            obj = MapGenerator.objects(
                obj,
                tramo,
                objeto,
                step_z, offset_z, x+i*step_x
                ,collidable=False
            )
            obj = MapGenerator.objects(
                obj,
                tramo,
                objeto,
                step_z, offset_z, -x-i*step_x
                ,collidable=False
            )
        return obj

    def bosque(self,objects,tramo,x,step_x=1.0,step_z=1.0,offset_z=0.0,number=1,objeto="",random_x=0.0,random_step=0.0):
        obj=objects
        for i in range(number):
            obj = MapGenerator.objects(
                obj,
                tramo,
                objeto,
                step_z, offset_z, x+i*step_x
                ,random_x=random_x
                ,random_step=random_step
                ,collidable=True
            )
            obj = MapGenerator.objects(
                obj,
                tramo,
                objeto,
                step_z, offset_z, -x-i*step_x
                ,random_x=random_x
                ,random_step=random_step
                ,collidable=True
            )
        return obj

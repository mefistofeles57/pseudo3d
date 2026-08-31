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

        # Farolas
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "farola.flip",
            8.0, 1.0, -1.4,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "farola",
            8.0, 5.0, 1.4,
            random_step=1.0
        )

        # Vegetacion baja
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            9.0, 2.0, -2.5,
            random_x=1.0,
            random_step=2.0,
            collidable=False
        )
        # ============================================================
        # 1. PRIMERAS CURVAS - fáciles, para entrar en ritmo
        # ============================================================

        # ------------------------------------------------------------
        # Primera curva derecha
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            9.0, 1.0, -1.6,
            random_x=-0.4,
            random_step=2.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            13.0, 4.0, 1.6,
            random_x=0.4,
            random_step=3.0
        )


        # ------------------------------------------------------------
        # Pequeño descanso
        # Vegetación baja, para cambiar la silueta
        # ------------------------------------------------------------

        num_segs = 25

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            6.0, 1.0, -1.5,
            random_x=-0.5,
            random_step=1.5,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            7.0, 3.0, 1.5,
            random_x=0.5,
            random_step=1.5,
            collidable=False
        )


        # ------------------------------------------------------------
        # Curva izquierda
        # Algo más arbolada que la primera
        # ------------------------------------------------------------

        num_segs = 55

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 0.0, -1.5,
            random_x=-0.5,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            9.0, 3.0, 1.5,
            random_x=0.5,
            random_step=2.5
        )

        # Algunos arbustos entre los árboles
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            11.0, 2.0, -1.45,
            random_x=-0.4,
            random_step=2.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            13.0, 5.0, 1.45,
            random_x=0.4,
            random_step=2.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta de descanso
        # Abrimos otra vez el paisaje
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            8.0, 1.0, -1.6,
            random_x=-0.5,
            random_step=2.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            10.0, 4.0, 1.6,
            random_x=0.5,
            random_step=2.5,
            collidable=False
        )


        # ------------------------------------------------------------
        # Curva larga derecha
        # Más cerrada visualmente para darle entidad propia
        # ------------------------------------------------------------

        num_segs = 70

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 0.0, -1.5,
            random_x=-0.5,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            8.0, 2.0, 1.5,
            random_x=0.5,
            random_step=2.0
        )

        # Algunas piedras en el exterior
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "piedra",
            16.0, 5.0, -1.45,
            random_x=-0.3,
            random_step=3.0,
            profile=piedra_profile
        )


        # ------------------------------------------------------------
        # Recta antes de las enlazadas sencillas
        # Bajamos otra vez la densidad
        # ------------------------------------------------------------

        num_segs = 25

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            7.0, 1.0, -1.5,
            random_x=-0.4,
            random_step=1.5,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            8.0, 3.0, 1.5,
            random_x=0.4,
            random_step=1.5,
            collidable=False
        )


        # ------------------------------------------------------------
        # Enlazadas sencillas R -> L
        # Vegetación continua para reforzar la sensación de movimiento
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 0.0, -1.5,
            random_x=-0.5,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            6.0, 2.0, 1.45,
            random_x=0.4,
            random_step=1.5,
            collidable=False
        )


        num_segs = 55

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 1.0, 1.5,
            random_x=0.5,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            6.0, 3.0, -1.45,
            random_x=-0.4,
            random_step=1.5,
            collidable=False
        )


        # ------------------------------------------------------------
        # Fin de la zona de aprendizaje
        # Abrimos la carretera y ponemos las flechas
        # ------------------------------------------------------------

        num_segs = 35

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            9.0, 0.0, -1.6,
            random_x=-0.4,
            random_step=2.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            10.0, 4.0, 1.6,
            random_x=0.4,
            random_step=2.0,
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


        # ============================================================
        # 2. PRIMERA SECCIÓN DE ENLAZADAS
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
        # Primera izquierda
        # Aquí empieza a sentirse algo más cerrado
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 0.0, -1.5,
            random_x=-0.5,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 2.0, 1.5,
            random_x=0.5,
            random_step=1.5
        )


        # ------------------------------------------------------------
        # Derecha
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 1.0, -1.5,
            random_x=-0.5,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            5.0, 0.0, 1.45,
            random_x=0.4,
            random_step=1.5,
            collidable=False
        )


        # ------------------------------------------------------------
        # Segunda derecha, corta
        # Mantenemos continuidad visual
        # ------------------------------------------------------------

        num_segs = 35

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 0.0, -1.5,
            random_x=-0.5,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            8.0, 3.0, 1.5,
            random_x=0.5,
            random_step=2.0
        )


        # ------------------------------------------------------------
        # Izquierda larga de salida
        # ------------------------------------------------------------

        num_segs = 55

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 1.0, -1.5,
            random_x=-0.5,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 3.0, 1.5,
            random_x=0.5,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            8.0, 2.0, -1.45,
            random_x=-0.4,
            random_step=2.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta de salida de la sección
        # Volvemos a abrir
        # ------------------------------------------------------------

        num_segs = 35

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            8.0, 0.0, -1.6,
            random_x=-0.5,
            random_step=2.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            9.0, 4.0, 1.6,
            random_x=0.5,
            random_step=2.0,
            collidable=False
        )


        # ============================================================
        # 3. PRIMER CHECKPOINT
        # ============================================================

        checkpoint_1 = len(self.road.segments)

        num_segs = 25
        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[checkpoint_1:checkpoint_1+1],
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

        # Vegetación alrededor, pero dejando respirar el checkpoint
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 3.0, -1.55,
            random_x=-0.45,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 5.0, 1.55,
            random_x=0.45,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 2.0, -1.45,
            random_x=-0.35,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            5.0, 4.0, 1.45,
            random_x=0.35,
            random_step=1.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Pequeño tramo recto antes de los bumps
        # ------------------------------------------------------------

        num_segs = 20
        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            5.0, 0.0, -1.55,
            random_x=-0.45,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 2.0, 1.55,
            random_x=0.45,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.3,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            4.5, 2.0, 1.45,
            random_x=0.3,
            random_step=1.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Repechos
        # Dejamos las señales muy visibles
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

        objects = MapGenerator.objects(
            objects,
            self.road.segments[bumps_start:bumps_end],
            "arbusto",
            4.0, 0.0, -1.5,
            random_x=-0.35,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[bumps_start:bumps_end],
            "arbusto.flip",
            4.5, 2.0, 1.5,
            random_x=0.35,
            random_step=1.0,
            collidable=False
        )


        # ============================================================
        # 4. RASANTES + CURVAS
        # ============================================================

        # ------------------------------------------------------------
        # Subida + curva derecha
        # ------------------------------------------------------------

        num_segs = 30

        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, R, num_segs)

        self.road.add(MapGenerator.merge(curve, hill))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            5.0, 0.0, -1.5,
            random_x=-0.5,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 2.0, 1.5,
            random_x=0.5,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.35,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            5.0, 3.0, 1.45,
            random_x=0.35,
            random_step=1.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Bajada + curva izquierda
        # ------------------------------------------------------------

        num_segs = 25

        hill = MapGenerator.pattern(MapGenerator.HILL, DOWN, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)

        self.road.add(MapGenerator.merge(curve, hill))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            5.0, 1.0, -1.5,
            random_x=-0.45,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            5.5, 0.0, 1.5,
            random_x=0.45,
            random_step=1.0
        )

        # Piedra ocasional para romper la pared vegetal
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "piedra",
            12.0, 4.0, 1.45,
            random_x=0.25,
            random_step=2.0,
            profile=piedra_profile
        )


        # ------------------------------------------------------------
        # Elevación larga + curva izquierda
        # Tramo bastante denso
        # ------------------------------------------------------------

        num_segs = 35

        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, num_segs)
        curve = MapGenerator.pattern(MapGenerator.CURVE, L, num_segs)

        self.road.add(MapGenerator.merge(curve, hill))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            4.5, 0.0, -1.5,
            random_x=-0.5,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            5.0, 2.0, 1.5,
            random_x=0.5,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.3,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            4.0, 3.0, 1.45,
            random_x=0.3,
            random_step=0.8,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta final de la sección
        # Abrimos algo para que las flechas destaquen
        # ------------------------------------------------------------

        num_segs = 30

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            8.0, 0.0, -1.6,
            random_x=-0.4,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            9.0, 4.0, 1.6,
            random_x=0.4,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            5.0, 2.0, -1.5,
            random_x=-0.3,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            6.0, 3.0, 1.5,
            random_x=0.3,
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


        # ============================================================
        # 5. TRAMO RÁPIDO
        # ============================================================

        # ------------------------------------------------------------
        # Curva derecha larga
        # Vegetación próxima = mucha sensación de velocidad
        # ------------------------------------------------------------

        num_segs = 65

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            5.0, 0.0, -1.5,
            random_x=-0.45,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            6.0, 2.0, 1.5,
            random_x=0.45,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.3,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            4.5, 3.0, 1.45,
            random_x=0.3,
            random_step=1.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta rápida
        # Farolas cercanas para enfatizar velocidad
        # ------------------------------------------------------------

        num_segs = 45

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

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

        # Vegetación por detrás de las farolas
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 1.0, -1.7,
            random_x=-0.35,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            8.0, 4.0, 1.7,
            random_x=0.35,
            random_step=1.5
        )


        # ------------------------------------------------------------
        # Curva izquierda larga
        # ------------------------------------------------------------

        num_segs = 60

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            5.0, 0.0, -1.5,
            random_x=-0.5,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            5.5, 2.0, 1.5,
            random_x=0.5,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            4.0, 1.0, -1.45,
            random_x=-0.3,
            random_step=0.8,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            4.0, 3.0, 1.45,
            random_x=0.3,
            random_step=0.8,
            collidable=False
        )


        # ------------------------------------------------------------
        # Recta final
        # Abrimos ligeramente después de tanta densidad
        # ------------------------------------------------------------

        num_segs = 40

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, num_segs))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            7.0, 0.0, -1.6,
            random_x=-0.4,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbol",
            8.0, 3.0, 1.6,
            random_x=0.4,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto",
            5.0, 1.0, -1.45,
            random_x=-0.3,
            random_step=1.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-num_segs:],
            "arbusto.flip",
            6.0, 4.0, 1.45,
            random_x=0.3,
            random_step=1.0,
            collidable=False
        )

        # ============================================================
        # 6. ZONA TRAMPA
        #
        # Varias pequeñas elevaciones para dificultar la lectura.
        # La última desemboca en una curva cerrada.
        # ============================================================

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.s",
            30.0,
            0.0,
            1.3,
            collidable=True
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.s",
            30.0,
            0.0,
            -1.3,
            collidable=True
        )
        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, 18)
        curve = MapGenerator.pattern(MapGenerator.CURVE, R, 18)
        self.road.add(MapGenerator.merge(curve, hill))

        hill = MapGenerator.pattern(MapGenerator.HILL, DOWN, 18)
        curve = MapGenerator.pattern(MapGenerator.CURVE, L, 18)
        self.road.add(MapGenerator.merge(curve, hill))

        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, 20)
        curve = MapGenerator.pattern(MapGenerator.CURVE, R, 20)
        self.road.add(MapGenerator.merge(curve, hill))

        # Pequeño respiro
        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 18))
        MapGenerator.addMark(self.road.segments[-10],"flecha.1",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-11],"flecha.2",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-10],"flecha.1",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-11],"flecha.2",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-10],"flecha.1",x=0.4,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-11],"flecha.2",x=0.4,z=0.0,w=0.5,h=1.0)

        #ondulaciones
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "rasante",
            30.0,
            0.0,
            -1.4,
            collidable=True
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "rasante",
            30.0,
            0.0,
            1.4,
            collidable=True
        )
        self.add_bumps(repeats=4, segments=4, slope=0.03)

        # Y ahora la sorpresa
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva",
            30.0,
            0.0,
            1.3,
            collidable=True
        )
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R_HARD, 45))

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 30))


        # ============================================================
        # 7. SEGUNDA SECCIÓN DE ENLAZADAS
        # ============================================================

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.s",
            30.0,
            0.0,
            1.3,
            collidable=True
        )
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.s",
            30.0,
            0.0,
            -1.3,
            collidable=True
        )
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L, 50))
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, 45))
        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.flip",
            30.0,
            0.0,
            -1.3,
            collidable=True
        )
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, L_HARD, 38))

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 45))


        # ============================================================
        # 8. SEGUNDO CHECKPOINT
        # ============================================================

        checkpoint_2 = len(self.road.segments)

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 25))

        objects=MapGenerator.objects(objects,self.road.segments[checkpoint_2:checkpoint_2+1],"checkpoint",step=1.0,offset=0.5,x=1.3,profile=checkpoint_profile)
        MapGenerator.addCheckpoint(
            self.road.segments[checkpoint_2],
            0.25,
            40.0
        )
        MapGenerator.addMark(self.road.segments[checkpoint_2],"parrilla",x=-1.0,z=0.25,w=0.5,h=0.5)
        MapGenerator.addMark(self.road.segments[checkpoint_2],"parrilla",x=-0.5,z=0.25,w=0.5,h=0.5)
        MapGenerator.addMark(self.road.segments[checkpoint_2],"parrilla",x=0.0,z=0.25,w=0.5,h=0.5)
        MapGenerator.addMark(self.road.segments[checkpoint_2],"parrilla",x=0.5,z=0.25,w=0.5,h=0.5)


        # ============================================================
        # 9. GRAN CURVA + CONTRACURVA
        # ============================================================

        curve = MapGenerator.pattern(MapGenerator.CURVE, R, 65)
        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, 65)
        self.road.add(MapGenerator.merge(curve, hill))

        curve = MapGenerator.pattern(MapGenerator.CURVE, L, 70)
        hill = MapGenerator.pattern(MapGenerator.HILL, DOWN, 70)
        self.road.add(MapGenerator.merge(curve, hill))

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 45))
        MapGenerator.addMark(self.road.segments[-20],"flecha.1",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-21],"flecha.2",x=-0.25,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-20],"flecha.1",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-21],"flecha.2",x=-0.9,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-20],"flecha.1",x=0.4,z=0.0,w=0.5,h=1.0)
        MapGenerator.addMark(self.road.segments[-21],"flecha.2",x=0.4,z=0.0,w=0.5,h=1.0)


        # ============================================================
        # 10. TRAMO FINAL - rápido pero con dos sorpresas
        # ============================================================

        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R, 55))
        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 35))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva.flip",
            30.0,
            0.0,
            -1.3,
            collidable=True
        )
        hill = MapGenerator.pattern(MapGenerator.HILL, HILL, 25)
        curve = MapGenerator.pattern(MapGenerator.CURVE, L_HARD, 25)
        self.road.add(MapGenerator.merge(curve, hill))

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 40))

        objects = MapGenerator.objects(
            objects,
            self.road.segments[-3:-2],
            "curva",
            30.0,
            0.0,
            1.3,
            collidable=True
        )
        self.road.add(MapGenerator.pattern(MapGenerator.CURVE, R_HARD, 40))

        self.road.add(MapGenerator.pattern(MapGenerator.NONE, 0.0, 35))


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
        MapGenerator.addMark(self.road.segments[-41],"flecha.2",x=0.4,z=0.0,w=0.5,h=1.0)
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

    def createMap2(self,escenario):
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


    def decoracion(self,objects,tutorial_start):
        # ============================================================
        # DECORACION - SALIDA / TUTORIAL
        # ============================================================

        # ------------------------------------------------------------
        # SALIDA
        # Limpia y abierta. Farolas para dar referencias de velocidad.
        # ------------------------------------------------------------

        objects = MapGenerator.objects(
            objects,
            self.road.segments[tutorial_start:tutorial_start + 70],
            "farola",
            8.0,
            1.0,
            -1.8,
            random_step=1.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[tutorial_start:tutorial_start + 70],
            "farola.flip",
            8.0,
            5.0,
            1.8,
            random_step=1.0
        )

        # Algunos arbustos bastante retirados.
        objects = MapGenerator.objects(
            objects,
            self.road.segments[tutorial_start:tutorial_start + 70],
            "arbusto",
            9.0,
            2.0,
            -2.5,
            random_x=1.0,
            random_step=2.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[tutorial_start:tutorial_start + 70],
            "arbusto.flip",
            11.0,
            5.0,
            2.5,
            random_x=1.0,
            random_step=2.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # PRIMERAS CURVAS
        # Empieza a aparecer vegetacion alta.
        # ------------------------------------------------------------

        zone_start = tutorial_start + 70
        zone_end   = zone_start + 45 + 25 + 55 + 45

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbol",
            9.0,
            1.0,
            -2.0,
            random_x=1.2,
            random_step=2.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbol",
            13.0,
            4.0,
            2.2,
            random_x=1.5,
            random_step=3.0
        )

        # Vegetacion baja para romper la regularidad.
        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbusto",
            7.0,
            0.0,
            -2.0,
            random_x=1.0,
            random_step=2.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbusto.flip",
            8.0,
            3.0,
            2.0,
            random_x=1.0,
            random_step=2.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # CURVA LARGA
        # Algo mas cerrada visualmente.
        # ------------------------------------------------------------

        zone_start = zone_end
        zone_end   = zone_start + 70

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbol",
            6.0,
            0.0,
            -1.8,
            random_x=0.8,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbol",
            10.0,
            3.0,
            2.0,
            random_x=1.2,
            random_step=2.0
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "piedra",
            18.0,
            5.0,
            1.7,
            random_x=0.5,
            random_step=3.0,
            profile="piedra_profile"
        )


        # ------------------------------------------------------------
        # ENLAZADAS DEL FINAL DEL TUTORIAL
        # Un poco mas densas para anunciar que empieza el juego serio.
        # ------------------------------------------------------------

        zone_start = zone_end + 25
        zone_end   = zone_start + 45 + 55

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbol",
            6.0,
            0.0,
            -1.8,
            random_x=1.0,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbol",
            7.0,
            2.0,
            1.8,
            random_x=1.0,
            random_step=1.5
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbusto",
            5.0,
            1.0,
            -2.2,
            random_x=1.2,
            random_step=2.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbusto.flip",
            6.0,
            3.0,
            2.2,
            random_x=1.2,
            random_step=2.0,
            collidable=False
        )


        # ------------------------------------------------------------
        # RECTA FINAL / FLECHAS
        # Abrir otra vez el paisaje para que las marcas respiren.
        # ------------------------------------------------------------

        zone_start = zone_end
        zone_end   = zone_start + 35

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbusto",
            8.0,
            1.0,
            -2.5,
            random_x=1.0,
            random_step=2.0,
            collidable=False
        )

        objects = MapGenerator.objects(
            objects,
            self.road.segments[zone_start:zone_end],
            "arbusto.flip",
            9.0,
            4.0,
            2.5,
            random_x=1.0,
            random_step=2.0,
            collidable=False
        )

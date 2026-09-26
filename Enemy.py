import math
from TempObject import TempObject
from Car import Car
from Object import Object
from VisualObjProfile import VisualObjProfile
from Road import Segment

class Enemy(TempObject,Car):
    def __init__(self, img, x_rel, z,speed,context,side=0):
        super().__init__(x_rel, z, img)
        self.collidable=True
        self.metadata=context.escenario.cache.metadata[img]
        self.numframes=self.metadata.frames
        self.frame=0
        self.shadow=True
        self.context=context
        profile=VisualObjProfile()
        profile.shadow_color=(0,0,0)
        profile.shadow_alpha=80
        profile.shadow_width_factor=1.4
        profile.shadow_height=0.15
        profile.shadow_offset_z=0.0
        profile.collide_radius=0.15
        profile.collide_radius2=0.15*0.15
        self.profile=profile
        #movimiento
        self.target_speed=speed
        self.speed=speed
        self.vx=0.0
        self.type=Object.CAR
        self.side=side

    def update(self, dt):
        if self.dead==False:
            self.sync_side(self.context)
            vs=self.getVS(self.context)
            player=self.context.player
            rama_jugador=player.side or player.last_side
            if self.last_side!=0 and rama_jugador!=0 and self.last_side!=rama_jugador:
                enemigo_dentro=vs is not None and vs.type==Segment.FORK
                jugador_fuera=player.side==0
                if (not enemigo_dentro) or jugador_fuera:
                    self.dead=True
                    return
            if vs!=None:
                curva=-vs.curve if self.side==-1 else vs.curve
                if curva<0.0:
                    self.frame=1
                elif curva>0.0:
                    self.frame=2
                else:
                    player=self.context.player
                    dx=(self.x_rel+self.x_shift_actual(self.context))-(player.x_rel+player.x_shift_actual(self.context))
                    dz=self.z-player.z
                    angulo=math.degrees(math.atan2(abs(dx),abs(dz)))
                    if angulo>30.0:
                        self.frame=2 if dx<0.0 else 1
                    else:
                        self.frame=0            #lateral
            self.vx *= 0.95 ** (dt * 60.0)

            if abs(self.vx) < 0.1:
                self.vx = 0.0

            #frontal
            if self.speed > self.target_speed:
                excess = self.speed - self.target_speed
                excess *= 0.98 ** (dt * 60.0)
                self.speed = self.target_speed + excess

            dz=self.speed*dt
            #colisiones
            self.collide(dz,self.vx*dt,self.context)
            #aplicar
            self.x_rel += self.vx * dt
            self.z+=self.speed*dt
            #muerte
            if self.z<self.context.camera.z-5.0 or self.z>self.context.camera.z+self.context.camera.view_distance+5.0:
                self.dead=True



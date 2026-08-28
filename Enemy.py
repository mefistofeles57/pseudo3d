import math
from TempObject import TempObject
from Car import Car
from Object import Object
from VisualObjProfile import VisualObjProfile

class Enemy(TempObject,Car):
    def __init__(self, x_rel, z,speed,context):
        img="enemigo.1"
        super().__init__(x_rel, z, img)
        self.collidable=True
        self.metadata=context.escenario.cache.metadata[img]
        self.numframes=self.metadata.frames
        self.frame=0
        self.shadow=True
        self.context=context
        profile=VisualObjProfile()
        profile.shadow_color=(74, 69, 64)
        profile.shadow_alpha=100
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

    def update(self, dt):
        if self.dead==False:
            vs=self.getVS(self.context)
            if vs!=None:
                if vs.curve<0.0:
                    self.frame=1
                elif vs.curve>0.0:
                    self.frame=2
                else:
                    self.frame=0
            #lateral
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



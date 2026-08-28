import math
from Object import Object
from Estados import STUCK
from abc import ABC, abstractmethod

class Car(Object,ABC):

#    LATERAL=0
#    FRONT=1
#    REAR=2

#    @abstractmethod
#    def action(self, other, tipo, col_dz, col_dx):
#        pass
#    @abstractmethod
#    def reaction(self, other, tipo, vz, vx):
#        pass


    def __init__(self):
        super().__init__()
        self.vx=0.0
        self.speed=0.0
        self.context=None

    def collide(self,dz,vx,context):
        inicio=self.z-0.5
        vs=self.getVS(context,1)
        if vs==None:
            return
        fin=vs.end.z

        x_min = min(self.x_rel, self.x_rel + vx) - self.profile.collide_radius
        x_max = max(self.x_rel, self.x_rel + vx) + self.profile.collide_radius

        z_min = self.z
        z_max = self.z + dz + self.profile.collide_radius

        collide_obj=None

        #buscar en el buffer los objetos
        for vsobj in context.frame_data.objbuffer:
            obj=vsobj.obj
            if not(obj is self) and obj.collidable and obj.z>=inicio and obj.z<=fin:
                if obj.x_rel + obj.profile.collide_radius >= x_min \
                    and obj.x_rel - obj.profile.collide_radius <= x_max \
                    and obj.z + obj.profile.collide_radius >= z_min \
                    and obj.z - obj.profile.collide_radius <= z_max:
                    #candidato a colision
                    #interpolación de posición
                    impact_dz=obj.z-self.z
                    if dz>0.0:
                        pct=impact_dz/dz
                    else:
                        pct=0.0
                    impact_dx=vx*pct
                    impact_z=obj.z
                    impact_x=self.x_rel+impact_dx
                    distance2=self.getDistance(self,impact_x,impact_z)
                    col_distance2=obj.profile.collide_radius2+self.profile.collide_radius2
                    #si está dentro del radio
                    if distance2<=col_distance2:
                        collide_obj=obj
                        #no se buscan más colisiones. No interesa contra que colisiona, con saber que colisiona es suficiente
                        break
            elif obj.z>fin:
                break

        if collide_obj!=None:
            self.resolve_collision(collide_obj)
            #tipo de colision
#            distance2=self.getDistance(self,collide_obj.x_rel,collide_obj.z)
#            col_dz=collide_obj.z-self.z
#            col_dx=collide_obj.x_rel-self.x_rel
#            ratio_z = col_dz * col_dz / distance2
#            lateral=False
#            if col_dz<0 and ratio_z>=0.5:
#                #choque trasero, no se detecta
#                return
#            elif col_dz<0 or ratio_z<0.5:
#                #lateral
#                lateral=True
#            if lateral:
#                tipo=Car.LATERAL
#            else:
#                tipo=Car.FRONT
#            self.action(collide_obj,tipo,col_dz,col_dx)

    def getDistance(self,obj1,x_rel,z):
        dx = x_rel - obj1.x_rel
        dz = z - obj1.z

        distance_squared = dx * dx + dz * dz

        return distance_squared

    def resolve_collision(self, other):
        if self.type==Car.CAR or self.type==Car.PLAYER:
            m1=1.0
            vx1 = self.vx
            vz1 = self.speed
        else:
            m1=vx1=vz1=0.0

        if other.type==Car.CAR or other.type==Car.PLAYER:
            m2=1.0
            vx2 = other.vx
            vz2 = other.speed
        else:
            m2=vx2=vz2=0.0
        # Vector entre centros
        dx = self.x_rel - other.x_rel
        dz = self.z - other.z

        dist = math.hypot(dx, dz)
        if dist < 1e-6:
            return

        # Normal del impacto
        nx = dx / dist
        nz = dz / dist

        # Velocidades relativas
        rvx = vx1 - vx2
        rvz = vz1 - vz2

        # Velocidad relativa sobre la normal
        vn = rvx * nx + rvz * nz

        # Ya se están separando
        if vn > 0.0:
            return

        #fuerza del impacto (para sonido o chispas)
        impact = -vn

        # Rebote:
        # 0 = totalmente inelástico
        # 1 = perfectamente elástico
        restitution = 0.5

        inv_mass_sum = m1 + m2
        if inv_mass_sum == 0.0:
            return

        # Impulso
        j = -(1.0 + restitution) * vn / inv_mass_sum

        impulse_x = j * nx
        impulse_z = j * nz

        # Aplicar a ambos
        vx1 += impulse_x * m1
        vz1 += impulse_z * m1


        vx2 -= impulse_x * m2
        vz2 -= impulse_z * m2

        # No existe marcha atrás
        vz1 = max(0.0, vz1)
        vz2 = max(0.0, vz2)        

        if self.type!=Car.NONE:
            self.speed=vz1
            self.vx=vx1

        if other.type!=Car.NONE:
            other.speed=vz2
            other.vx=vx2

        if self.type==Car.PLAYER and other.type==Car.NONE and self.speed<1e-6:
            if self.context!=None:
                self.context.changeStatus(STUCK)

        return impact
    
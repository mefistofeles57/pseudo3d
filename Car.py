import math
from Object import Object
from Estados import STUCK,NORMAL
from Road import Segment
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
        self.last_side=0
        

    def sync_side(self,context):
        vs=self.getVS(context)
        if vs is None:
            return
        if vs.type!=Segment.FORK:
            self.side=0
            return
                
        if self.side==0:
            self.side=1
            self.x_rel-=vs.w0

        d=vs.d_at(self.z)
        margen=self.profile.collide_radius

        elegido=self.side
        if self.side==1 and self.x_rel<-d-margen:
            elegido=-1
        elif self.side==-1 and self.x_rel>d+margen:
            elegido=1

        if elegido!=self.side:
            self.x_rel=self.x_rel-2*d*elegido
            self.side=elegido

        self.last_side=self.side


    def x_shift_actual(self,context):
        vs=self.getVS(context)
        if vs is None or vs.type!=Segment.FORK:
            return 0.0
        if self.side==-1:
            return vs.w0-2*vs.d_at(self.z)
        if self.side==1:
            return vs.w0
        return 0.0


    def collide(self,dz,vx,context):
        inicio=self.z-0.5
        vs=self.getVS(context,1)
        if vs==None:
            return
        fin=vs.end.z

        x_self=self.x_rel+self.x_shift_actual(context)
        x_min = min(x_self, x_self + vx) - self.profile.collide_radius
        x_max = max(x_self, x_self + vx) + self.profile.collide_radius

        z_min = self.z
        z_max = self.z + dz + self.profile.collide_radius

        collide_obj=None
        collide_vs=None

        #buscar en el buffer los objetos
        for vsobj in context.frame_data.objbuffer:
            obj=vsobj.obj
            if not(obj is self) and obj.collidable and obj.z>=inicio and obj.z<=fin:
                ox=obj.x_rel+vsobj.x_shift
                if ox + obj.profile.collide_radius >= x_min \
                    and ox - obj.profile.collide_radius <= x_max \
                    and obj.z + obj.profile.collide_radius >= z_min \
                    and obj.z - obj.profile.collide_radius <= z_max:
                    #candidato a colision
                    impact_dz=obj.z-self.z
                    if dz>0.0:
                        pct=impact_dz/dz
                    else:
                        pct=0.0
                    impact_dx=vx*pct
                    impact_z=obj.z
                    impact_x=x_self+impact_dx
                    distance2=self.getDistance(ox,obj.z,impact_x,impact_z)
                    col_distance2=(obj.profile.collide_radius+self.profile.collide_radius)**2
                    #si está dentro del radio
                    if distance2 <= col_distance2:
                        #se queda con la primera que encuentra
                        collide_obj=obj
                        collide_vs=vsobj
                        break
            elif obj.z>fin:
                break

        if collide_obj!=None:
            self.resolve_collision(collide_obj,x_self-(collide_obj.x_rel+collide_vs.x_shift))


    def getDistance(self,ox,oz,x,z):
        dx = x - ox
        dz = z - oz

        distance_squared = dx * dx + dz * dz

        return distance_squared

    def resolve_collision(self, other, dx):
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
        restitution = 0.3

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

        car2car_energy=2.0
        energy_loss=0.5

        if self.type!=Car.NONE and other.type!=Car.NONE:
            energy_loss=car2car_energy

        if self.type!=Car.NONE:
            self.speed=vz1
            self.vx=vx1*energy_loss

        if other.type!=Car.NONE:
            other.speed=vz2
            other.vx=vx2*energy_loss

        if self.type==Car.PLAYER and other.type==Car.NONE and self.speed<1e-6:
            if self.context != None and self.context.estado == NORMAL:
                self.context.root.playSound("crash")
                self.context.changeStatus(STUCK)
        else:
            self.context.root.playSound("choque",once=True)

        return impact
    
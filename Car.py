import math
from Object import Object
from Estados import STUCK,NORMAL
from Road import Segment
from abc import ABC, abstractmethod

class Car(Object,ABC):

    # reacciones
    EMPUJE_FIJO=2.0         # vx mínima con la que se separan dos objetos al chocar
    RECORTE_ALCANCE=0.3     # parte de su velocidad que pierde el que embiste por detrás a un coche
    EMPUJON_ALCANCE=0.5     # parte de la diferencia de velocidad que gana el embestido
    RECORTE_DECORADO=0.15   # parte de su velocidad que se pierde chocando de refilón con el decorado
    UMBRAL_STUCK=1.0        # por debajo de esta velocidad, un choque con el decorado deja al jugador parado
    FRACCION_FRONTAL=0.5    # golpe de frente si el desplazamiento lateral es menor que esta parte de la suma de radios
    RECORTE_LATERAL=0.15    # parte de su velocidad que pierde cada coche en un golpe lateral entre coches

    def __init__(self):
        super().__init__()
        self.vx=0.0
        self.speed=0.0
        self.context=None
        self.last_side=0
        self.masa=1.0
        self.target_x_rel=0.0
        

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
            self.target_x_rel-=vs.w0

        d=vs.d_at(self.z)
        margen=self.profile.collide_radius

        elegido=self.side
        if self.side==1 and self.x_rel<-d-margen:
            elegido=-1
        elif self.side==-1 and self.x_rel>d+margen:
            elegido=1

        if elegido!=self.side:
            self.x_rel=self.x_rel-2*d*elegido
            self.target_x_rel=self.target_x_rel-2*d*elegido
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

    def vel_lateral(self):
        return self.vx

    def es_coche(self,obj):
        return obj.type==Car.CAR or obj.type==Car.PLAYER

    def factor_masa(self,otro):
        # masa es la inversa de la masa: el que menos pesa (masa mayor) se lleva más
        suma=self.masa+otro.masa
        if suma==0.0:
            return 1.0
        return 2.0*self.masa/suma

    def resolve_collision(self, other, dx):
        # dx: posición lateral relativa (yo - otro) en coordenadas comunes
        dz=self.z-other.z
        if dx>0.0:
            lado=1
        elif dx<0.0:
            lado=-1
        elif self.vel_lateral()>=0.0:
            lado=1
        else:
            lado=-1
        radios=self.profile.collide_radius+other.profile.collide_radius
        de_frente=abs(dx)<self.FRACCION_FRONTAL*radios
        if self.es_coche(other):
            self.choque_coche(other,lado,dz,de_frente)
        else:
            self.choque_decorado(lado,dz,de_frente)

    def choque_coche(self,other,lado,dz,de_frente):
        v_yo=self.vel_lateral()
        v_otro=other.vel_lateral()
        if dz<0.0:
            detras=self
            delante=other
        else:
            detras=other
            delante=self
        se_acercan_x=(v_yo-v_otro)*lado<0.0
        alcance=de_frente and detras.speed>delante.speed
        if not se_acercan_x and not alcance:
            #ya se están separando (el otro coche también llama a collide en su update)
            return
        #separación lateral: parte fija + lo que el otro venía hacia mí + lo que yo ya me alejaba
        empuje_yo=self.EMPUJE_FIJO+max(0.0,v_otro*lado)+max(0.0,v_yo*lado)
        empuje_otro=self.EMPUJE_FIJO+max(0.0,-v_yo*lado)+max(0.0,-v_otro*lado)
        self.vx=lado*empuje_yo*self.factor_masa(other)
        other.vx=-lado*empuje_otro*other.factor_masa(self)
        #alcance: el de detrás pierde velocidad y el de delante recibe un empujón
        if alcance:
            dv=detras.speed-delante.speed
            recorte=min(1.0,self.RECORTE_ALCANCE*detras.factor_masa(delante))
            detras.speed=detras.speed*(1.0-recorte)
            delante.speed=delante.speed+self.EMPUJON_ALCANCE*dv*delante.factor_masa(detras)
        self.context.root.playSound("choque",once=True)
        #golpe lateral entre coches: los dos pierden algo de velocidad, el que menos pesa más
        if not alcance:
            self.speed=self.speed*(1.0-min(1.0,self.RECORTE_LATERAL*self.factor_masa(other)))
            other.speed=other.speed*(1.0-min(1.0,self.RECORTE_LATERAL*other.factor_masa(self)))

    def choque_decorado(self,lado,dz,de_frente):
        v_yo=self.vel_lateral()
        se_acercan_x=v_yo*lado<0.0
        se_acercan_z=dz<0.0 and self.speed>0.0
        if not se_acercan_x and not se_acercan_z:
            return
        if de_frente:
            self.speed=0.0
        else:
            self.speed=self.speed*(1.0-self.RECORTE_DECORADO)
            #el decorado no se mueve: solo cuenta la parte fija y lo que yo ya me alejaba
            self.vx=lado*(self.EMPUJE_FIJO+max(0.0,v_yo*lado))
        if self.type==Car.PLAYER and self.speed<self.UMBRAL_STUCK:
            if self.context!=None and self.context.estado==NORMAL:
                self.context.root.playSound("crash")
                self.context.changeStatus(STUCK)
                return
        self.context.root.playSound("choque",once=True)
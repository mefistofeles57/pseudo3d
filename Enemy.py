import math
import pygame
from TempObject import TempObject
from Car import Car
from Object import Object
from VisualObjProfile import VisualObjProfile
from Road import Segment


class Enemy(TempObject,Car):

    RUEDAS_VEL=3.0

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
        profile.shadow_offset_z=0.0
        profile.collide_radius=0.2
        profile.collide_radius2=0.2*0.2
        profile.sombra_suelo=True
        profile.sombra_atras=0.1
        profile.sombra_delante=0.2
        profile.shadow_height=0.3
        self.profile=profile
        #movimiento
        self.target_speed=speed
        self.speed=speed
        self.target_x_rel=x_rel
        self.vx=0.0
        self.type=Object.CAR
        self.side=side
        self.aceleracion=5.0
        self.freno=3.0
        self.volante=0.5
        self.v_volante=0.0
        #ruedas y freno
        self.ruedas_fase=0.0
        self.frenando=False

    def vel_lateral(self):
        return self.vx+self.v_volante

    def update(self, dt):
        if self.dead==False:
            #elegir lado en fork
            self.sync_side(self.context)
            vs=self.getVS(self.context)
            player=self.context.player
            #mata al enemigo si se termina la rama donde no está el player 
            rama_jugador=player.side or player.last_side
            if self.last_side!=0 and rama_jugador!=0 and self.last_side!=rama_jugador:
                enemigo_dentro=vs is not None and vs.type==Segment.FORK
                jugador_fuera=player.side==0
                if (not enemigo_dentro) or jugador_fuera:
                    self.dead=True
                    return
            
            if vs!=None:
                #selecciona frame
                curva=-vs.curve if self.side==-1 else vs.curve
                if curva<0.0:
                    self.frame=1
                elif curva>0.0:
                    self.frame=2
                else:
                    #elige el frame segun la posicion relativa con el juegador
                    player=self.context.player
                    dx=(self.x_rel+self.x_shift_actual(self.context))-(player.x_rel+player.x_shift_actual(self.context))
                    dz=self.z-player.z
                    angulo=math.degrees(math.atan2(abs(dx),abs(dz)))
                    if angulo>30.0:
                        self.frame=2 if dx<0.0 else 1
                    else:
                        self.frame=0

            #reduce la vx por el rozamiento
            self.vx *= 0.95 ** (dt * 60.0)
            if abs(self.vx) < 0.1:
                self.vx = 0.0

            #reduce vz progresivamente si se pasa
            if self.speed > self.target_speed:
                excess = self.speed - self.target_speed
                excess *= 0.98 ** (dt * 60.0)
                self.speed = self.target_speed + excess

            #detectar vehiculos en su camino

            min_dz=0.0
            max_dz=3.0
            max_dx=0.5
            #recorrer los objetos temporales
            frente=None
            lateral=None
            target_x_dif=self.x_rel-self.target_x_rel
            for item in self.context.frame_data.tempobjbuffer:
                #coche delante
                if item.dead==False and item.type==Object.CAR and item is not self and self.side==item.side:
                    ancho=self.profile.collide_radius+item.profile.collide_radius
                    if self.z+min_dz<item.z and self.z+max_dz>item.z and self.x_rel>item.x_rel-ancho and self.x_rel<item.x_rel+ancho:
                        if frente==None:
                            frente=item
                        elif frente.speed>item.speed:
                            frente=item
                    #coche en un lado
                    if lateral==None and self.side==item.side and self.x_rel!=self.target_x_rel and self.z>item.z-1.0 and self.z<item.z+1.0:
                        x_dif=self.x_rel-item.x_rel
                        
                        #si está dentro de la distancia en la direccion del objetivo x
                        if abs(self.x_rel-item.x_rel)<max_dx and x_dif*target_x_dif>0:
                            lateral=item


            #intenta alcanzar su velocidad objetivo
            #si hay un coche en frente trata de igualar la velocidad
            self.frenando=False
            if frente!=None and frente.speed<self.speed:
                self.frenando=True
                self.speed=max(frente.speed,self.speed-self.freno*dt)
            #si voy mas despacio pero mi velocidad objetivo supera a la del de delante solo acelero hasta la velocidad del de delante
            elif frente!=None and self.speed<self.target_speed and self.target_speed>frente.speed:
                self.speed=min(frente.speed,self.speed+self.aceleracion*dt)
            #no hay nadie y voy por debajo de mi velocidad acelero hasta el target
            elif self.speed<self.target_speed:
                self.speed=min(self.target_speed,self.speed+self.aceleracion*dt)
            
            #intenta situarse en un x_rel
            x_antes=self.x_rel
            if lateral==None:
                if target_x_dif<0:
                    self.x_rel=min(self.target_x_rel,self.x_rel+self.volante*dt)
                else:
                    self.x_rel=max(self.target_x_rel,self.x_rel-self.volante*dt)
            #velocidad lateral real del volante en este frame (0 si no se ha movido)
            self.v_volante=(self.x_rel-x_antes)/dt

            dz=self.speed*dt
            #colisiones
            self.collide(dz,self.vx*dt,self.context)
            #aplicar
            self.x_rel += self.vx * dt
            self.z+=self.speed*dt

            #freno y patron de ruedas

            capas=[]
            if self.frenando:
                capas.append(self.N_CUERPOS+self.frame)
            self.ruedas_fase+=self.speed*dt*self.RUEDAS_VEL
            fase=int(self.ruedas_fase)%self.N_RUEDAS
            capas.append(2*self.N_CUERPOS+self.frame*self.N_RUEDAS+fase)
            self.capas=tuple(capas)

            #si va por la otra rama y este avance lo saca del fork, muere ya:
            #en el siguiente dibujado ya no tendría el desplazamiento de su rama y aparecería en la del jugador
            vs=self.getVS(self.context)
            rama_jugador=player.side or player.last_side
            otra_rama=self.last_side!=0 and rama_jugador!=0 and self.last_side!=rama_jugador
            if otra_rama and vs!=None and vs.type==Segment.FORK and self.z>=vs.end.z:
                segmentos=self.context.road.segments
                i=vs.index+1
                if i>=len(segmentos) or segmentos[i].type!=Segment.FORK:
                    self.dead=True
                    return
            #muerte
            if self.z<self.context.camera.z-5.0 or self.z>self.context.camera.z+self.context.camera.view_distance+5.0:
                self.dead=True

class Deportivo(Enemy):
    N_CUERPOS=3
    N_RUEDAS=5

    def __init__(self, img, x_rel, z,speed,context,side=0):
        super().__init__(img, x_rel, z,speed,context,side)


class Camion(Enemy):
    N_CUERPOS=3
    N_RUEDAS=10

    def __init__(self, img, x_rel, z,speed,context,side=0):
        super().__init__(img, x_rel, z,speed,context,side)
        self.profile.collide_radius=0.25
        self.profile.collide_radius2=0.25*0.25
        self.profile.sombra_atras=0.045
        self.profile.sombra_delante=0.10
        self.profile.shadow_offset_z=0.0
        self.profile.shadow_height=1.0
        self.profile.shadow_width_factor=1.05
        self.masa=0.25
        self.aceleracion=3.0
        self.freno=2.0


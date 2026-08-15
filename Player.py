import pygame
import math
from ImageCache import ImageCache
from Object import Object,VisibleObject
from VisualObjProfile import VisualObjProfile
from TempObject import Humo
from Material import Material
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext


class Player(Object):

    NORMAL=0
    STARTING=1
    STUCK=2
    DESTUCKING=3

    def __init__(self,context:"GameContext"):
        self.context=context
        self.speed=0.0
        self.img="coche"
        self.metadata=None
        self.vs_index=-1
        #posicion
        self.x_rel=0.0
        self.vx=0.0
        self.c=0.0
        self.target_c=0.0
        self.z=0.0
        #posicion previa
        self.prev_z=0.0
        self.prev_x_rel=0.0
        self.prev_c=0.0
        #cache para el coche
        self.cache=ImageCache(ImageCache.getPlayerConfig(),context)
        self.cache.addImage("coche","coche.png",(0.5,1.0),False,True)
        self.load_metadata(self.cache)
        #propiedades
        self.estado=Player.STARTING
        self.stuck_time=0.0
        self.collidable=False
        profile=VisualObjProfile()
        profile.shadow_color=(74, 69, 64)
        profile.shadow_alpha=100
        profile.shadow_width_factor=1.2
        profile.shadow_height=0.5
        profile.shadow_offset_z=0.2
        profile.collide_radius=0.2
        profile.collide_radius2=0.2*0.2

        profile.cache=self.cache
        self.profile=profile

        #cache para el humo
        #animaciones
        self.cache_humo=ImageCache(ImageCache.getHumoConfig(),context)
        self.cache_humo.addAnimation("humo","humo.png",(0.0,1.0),True,False)
        profile=VisualObjProfile()
        profile.shadow_color=(0,0,0)
        profile.shadow_alpha=100
        profile.shadow_width_factor=1.0
        profile.shadow_height=0.1
        profile.cache=self.cache_humo
        self.profile_humo=profile


        #volante
        self.volante=0.0
        #ruedas
        self.stress_lateral=0.0
        self.stress_freno=0.0
        self.stress_salida=0.0
        #pedales
        self.p_acelerador=0.0
        self.p_freno=0.0
        #marchas (velocida,torque)
        self.marchas=[[8.0,2.5],[15.0,0.8]]
        self.marcha=0
        self.tecla_marcha=False
        #humo
        self.smoke_interval=0.1
        self.smoke_timer=0.0
        #params
        self.PENALIZACION_CURVA=3.0
        self.POTENCIA_MOTOR=7.0
        self.FUERZA_FRENADO=7.0
        self.RESISTENCIA_AIRE=0.0001
        self.FRENO_MOTOR=1.0
        self.INTENSIDAD_CURVA=30.0
        self.FUERZA_VOLANTE=5.0
        self.LIMITE_AGARRE=0.4


    def changeStatus(self,estado):
        if estado==Player.STUCK:
            self.estado=Player.STUCK
            self.stuck_time=0.0
        else:
            self.estado=estado

    def update(self,dt):
        if self.estado==Player.NORMAL:
            K_curva=8.0
            K_stress=3.0

            #dz con la vz del frame anterior
            dz=self.speed*dt

            #disipa algo de energía del movimiento lateral
            self.vx *= 0.95 ** (dt * 60.0)


            #material
            material=self.getMaterial()

            #acelerador/freno
            freno=self.get_freno(dt)*material.friccion_z
            acelerador=self.get_acelerador(dt)
            giro=self.get_volante(dt)####*material.agarre_x
            if self.context.keys[pygame.K_SPACE] and self.tecla_marcha==False:
                self.tecla_marcha=True
                self.cambio_marcha()
            elif self.context.keys[pygame.K_SPACE]==False:
                self.tecla_marcha=False


            #velocidad y torque
            (vmax_marcha,torque)=self.marchas[self.marcha]
            vmax=self.marchas[-1][0]
            factor_v=self.speed/vmax
            if self.speed<vmax_marcha:
                factor_v_marcha=self.speed/vmax_marcha
                eficiencia=max(0.0,1.0-factor_v_marcha*factor_v_marcha)
                fuerza_motor=self.POTENCIA_MOTOR*torque*eficiencia
            else:
                fuerza_motor=0.0

            #desnivel
            if self.getVS()!=None:
                pte=10*self.getVS().segment.height/self.getVS().segment.length
                if pte<-0.5:
                    pte=-0.5
                elif pte>0.5:
                    pte=0.5

                fuerza_pte=-pte*self.POTENCIA_MOTOR
            else:
                fuerza_pte=0.0


            #giro y fuerzas laterales
            dz_segura=max(0.001,dz)
            giro_player=giro*self.FUERZA_VOLANTE*dz_segura
            curva_pista=0.0
            if self.getVS()!=None:
                curva_pista=self.getVS().segment.curve
            centrifuga=curva_pista*factor_v*factor_v*self.INTENSIDAD_CURVA
            
            self.target_c=giro_player
            #si se suelta el acelerador el coche se agarra más
            if acelerador<0.1:
                K_curva_final=K_curva*4.0
            else:
                K_curva_final=K_curva
            self.c+=(self.target_c-self.c)*K_curva_final*dt


            #stress
            #curva
            demanda_lateral=(abs(giro)+abs(self.c))*factor_v*1.0
            self.stress_lateral+=(demanda_lateral-self.stress_lateral) * K_stress*dt

            if self.stress_lateral>=self.LIMITE_AGARRE:
                factor_humo_giro=(self.stress_lateral-self.LIMITE_AGARRE)/(1.0-self.LIMITE_AGARRE)
                factor_humo_giro=min(1.0,max(0.0,factor_humo_giro))
            else:
                factor_humo_giro=0.0
            #freno
            demanda_freno=0.0
            if freno<-self.FRENO_MOTOR and self.speed>3.0:
                demanda_freno=factor_v*2.0
            self.stress_freno+=(demanda_freno-self.stress_freno) * K_stress*dt
            if self.stress_freno>=self.LIMITE_AGARRE:
                factor_humo_freno=(self.stress_freno-self.LIMITE_AGARRE)/(1.0-self.LIMITE_AGARRE)
                factor_humo_freno=min(1.0,max(0.0,factor_humo_freno))
            else:
                factor_humo_freno=0.0
            #burnout
            demanda_salida=0.0
            if acelerador>0.3 and self.speed<3.0:
                demanda_salida=max(0.0,1.0-(self.speed/3.0))
                demanda_salida=fuerza_motor*acelerador*demanda_salida*0.5
            self.stress_salida+=(demanda_salida-self.stress_salida) * K_stress*dt
            if self.stress_salida>=self.LIMITE_AGARRE:
                factor_humo_salida=(self.stress_salida-self.LIMITE_AGARRE)/(1.0-self.LIMITE_AGARRE)
                factor_humo_salida=min(1.0,max(0.0,factor_humo_salida))
            else:
                factor_humo_salida=0.0
            #humo
            factor_humo=max(factor_humo_giro,factor_humo_freno,factor_humo_salida)
            if factor_humo>0.3:
                self.addHumo(dt)
            
            fuerza_z=0.0
            #potencia efectiva (transmision a ruedas)
            if acelerador>0.0:
                fuerza_base=acelerador*fuerza_motor*material.friccion_z
                fuerza_z+=fuerza_base*(1.0-factor_humo_salida*0.5)
            fuerza_z+=fuerza_pte
            # el material.freno_z no puede ser más del 50% de la fuerza_z
            fuerza_z-=min(material.freno_z,fuerza_z*0.5)
            fuerza_z+=freno
            #resistencia al viento
            r_aire=self.speed*self.speed*self.RESISTENCIA_AIRE
            fuerza_z-=r_aire
            #freno por curva
            r_curva=abs(self.c)*self.PENALIZACION_CURVA*factor_v
            fuerza_z-=r_curva
            #integracion fuerza
            self.speed+=fuerza_z*dt
            #limites
            if self.speed>vmax: self.speed=vmax
            if self.speed<0.0: self.speed=0.0
            if round(self.speed,2)==0.0:
                self.vx=0.0
            if self.getVS()!=None and abs(self.x_rel)>self.getVS().visualProfile.road_limit:
                self.x_rel=math.copysign(self.getVS().visualProfile.road_limit, self.x_rel)
                self.vx=0.0

            self.mueve_camera(material)

            dz=self.speed*dt
            self.vx+=self.c*dz#*factor_v
            self.vx-=centrifuga*dz

            self.collide(dz,self.vx)

            dz=self.speed*dt
            self.z+=dz
            self.x_rel+=self.vx*dt

            #posicion anterior
            self.prev_z=self.z
            self.prev_x_rel=self.x_rel
            self.prev_c=self.c
        elif self.estado==Player.STARTING:
            self.changeStatus(Player.NORMAL)
        elif self.estado==Player.STUCK:
            self.stuck_time+=dt
            if self.stuck_time>=2.0:
                self.changeStatus(Player.DESTUCKING)
        elif self.estado==Player.DESTUCKING:
            if self.x_rel!=0.0:
                center_speed=1.0
                direction = -1 if self.x_rel > 0 else 1
                self.x_rel += direction * center_speed * dt
                if abs(self.x_rel) <= center_speed * dt:
                    self.x_rel = 0.0
            else:
                self.changeStatus(Player.NORMAL)



    def get_freno(self,dt):
        K_pedal=6.0
        down_pressed=self.context.keys[pygame.K_DOWN]
        self.p_freno+=(down_pressed-self.p_freno)*K_pedal*dt
        fuerza_f=round(self.FUERZA_FRENADO*self.p_freno*-1,2)
        fuerza_fm=-self.FRENO_MOTOR
        return min(fuerza_f,fuerza_fm)

    def get_acelerador(self,dt):
        K_pedal=6.0
        up_pressed=self.context.keys[pygame.K_UP]
        self.p_acelerador+=(up_pressed-self.p_acelerador)*K_pedal*dt
        return self.p_acelerador

    def get_volante(self,dt):
        K_volante=10.0
        left_pressed=self.context.keys[pygame.K_LEFT]
        right_pressed=self.context.keys[pygame.K_RIGHT]
        
        i=0

        if left_pressed and not right_pressed:
            i=-1
        elif right_pressed and not left_pressed:
            i=1

        self.volante+=(i-self.volante)*K_volante*dt
        return round(self.volante,2)

    def addHumo(self,dt):
        self.smoke_timer += dt

        if self.smoke_timer >= self.smoke_interval:
            self.smoke_timer = 0.0
            cache=self.profile_humo.cache
            metadata1=cache.metadata["humo.flip"]
            metadata2=cache.metadata["humo"]
            h=Humo(self.x_rel-0.09,self.z-0.05,metadata1,flip=True)
            h.profile=self.profile_humo
            self.context.frame_data.tempobjbuffer.append(h)
            h=Humo(self.x_rel+0.09,self.z-0.05,metadata2)
            h.profile=self.profile_humo
            self.context.frame_data.tempobjbuffer.append(h)

    def cambio_marcha(self):
        if self.marcha==0:
            self.marcha=1
        else:
            self.marcha=0    

    def getMaterial(self):
        #material
        rueda_i=(self.x_rel-0.05)*-1
        rueda_d=self.x_rel+0.05
        profile=None
        if self.getVS()!=None:
            profile=self.getVS().visualProfile
        if profile==None:
            return Material()
        
        if rueda_i<profile.half_width:
            material_i=0
        elif rueda_i<profile.half_width+profile.arcen_width:
            material_i=1
        else:
            material_i=2
        if rueda_d<profile.half_width:
            material_d=0
        elif rueda_d<profile.half_width+profile.arcen_width:
            material_d=1
        else:
            material_d=2
        nummaterial=max(material_i,material_d)
        if nummaterial==0:
            material=profile.road_material
        elif nummaterial==1:
            material=profile.arcen_material
        else:
            material=profile.outside_material

        return material

    def mueve_camera(self,m:Material):
        mov=0.0

        mov=m.amplitud*math.sin(self.z*m.frecuencia)

        self.context.camera.move_camera(mov)

    def getVS(self,index=0):
        if self.vs_index==-1:
            return None
        return self.context.frame_data.buffer[self.vs_index+index]

    def getDistance(self,obj1,obj2):
        dx = obj2.x_rel - obj1.x_rel
        dz = obj2.z - obj1.z

        distance_squared = dx * dx + dz * dz

        return distance_squared


    def collide(self,dz,vx):
        inicio=self.z-0.5
        vs=self.getVS(1)
        if vs==None:
            return
        fin=vs.end.z

        x_min = min(self.x_rel, self.x_rel + vx) - self.profile.collide_radius
        x_max = max(self.x_rel, self.x_rel + vx) + self.profile.collide_radius

        z_min = self.z
        z_max = self.z + dz + self.profile.collide_radius

        collide_obj=None

        #buscar en el buffer los objetos
        for obj in self.context.frame_data.objbuffer:
            if obj.collidable and obj.z>=inicio and obj.z<=fin:
                if obj.x + obj.profile.collide_radius >= x_min \
                    and obj.x - obj.profile.collide_radius <= x_max \
                    and obj.z + obj.profile.collide_radius >= z_min \
                    and obj.z - obj.profile.collide_radius <= z_max:
                    #candidato a colision
                    distance2=self.getDistance(obj,self)
                    col_distance2=obj.profile.collide_radius2+self.profile.collide_radius2
                    #si está dentro del radio
                    if distance2<=col_distance2:
                        collide_obj=obj
                        #no se buscan más colisiones. No interesa contra que colisiona, con saber que colisiona es suficiente
                        break
            elif obj.z>fin:
                break

        if collide_obj!=None:
            #saca al coche de colisión
            self.x_rel=self.prev_x_rel
            self.z=self.prev_z
            #tipo de colision
            dz=collide_obj.z-self.z
            dx=collide_obj.x_rel-self.x_rel
            ratio_z = dz * dz / distance2
            lateral=False
            if dz<0 or ratio_z<0.5:
                #lateral
                #si el choque es fuera de la carretera por el lado exterior
                #se considera frontal
                profile=self.getVS().visualProfile
                offroad=abs(self.x_rel)>=profile.half_width+profile.arcen_width
                if offroad==False or -dx*self.x_rel<=0:
                    lateral=True

            if lateral==False:
                #frontal
                self.reset()
                #cambio de estado
                self.changeStatus(Player.STUCK)
                pass
            else:
                self.c = -math.copysign(abs(self.c), dx)
                self.vx = -math.copysign(abs(self.vx), dx)
                #self.c*=0.5
                self.speed*=0.85


    def reset(self):
        self.stress_salida=0.0
        self.stress_lateral=0.0
        self.stress_freno=0.0
        self.speed=0.0
        self.vx=0.0
        self.c=0.0
        self.p_freno=0.0
        self.p_acelerador=0.0
        self.volante=0.0

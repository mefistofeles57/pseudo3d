import pygame
from ImageCache import ImageCache
from Object import Object,VisibleObject
from VisualObjProfile import VisualObjProfile
from TempObject import Humo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext


class Player(Object):
    def __init__(self,context:"GameContext"):
        self.context=context
        self.speed=0.0
        self.img="coche"
        self.metadata=None
        self.vs=None
        self.x_rel=0.0
        self.vx=0.0
        self.c=0.0
        self.target_c=0.0
        self.z=0.0
        #cache para el coche
        self.cache=ImageCache(ImageCache.getPlayerConfig(),context)
        self.cache.addImage("coche","coche.png",(0.5,1.0),False,True)
        profile=VisualObjProfile()
        profile.shadow_color=(74, 69, 64)
        profile.shadow_alpha=100
        profile.shadow_width_factor=1.2
        profile.shadow_height=0.5
        profile.shadow_offset_z=0.2
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
        self.PENALIZACION_CURVA=5.0
        self.POTENCIA_MOTOR=7.0
        self.FUERZA_FRENADO=7.0
        self.RESISTENCIA_AIRE=0.0001
        self.FRENO_MOTOR=1.0
        self.INTENSIDAD_CURVA=12.0
        self.FUERZA_VOLANTE=2.0
        self.LIMITE_AGARRE=0.4
        self.AGILIDAD_PARADO=2.0



    def update(self,dt):
        K_curva=8.0
        K_stress=3.0

        #dz con la vz del frame anterior
        dz=self.speed*dt

        #disipa algo de energía del movimiento lateral
        self.vx*=0.95


        #acelerador/freno
        freno=self.get_freno(dt)
        acelerador=self.get_acelerador(dt)
        giro=self.get_volante(dt)
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

        #giro y fuerzas laterales
        factor_agilidad=self.AGILIDAD_PARADO-(self.AGILIDAD_PARADO-1.0)*factor_v
        dz_segura=max(0.001,dz)
        giro_player=giro*self.FUERZA_VOLANTE*dz_segura*factor_agilidad
        curva_pista=0.0
        if self.vs!=None:
            curva_pista=self.vs.curve*self.INTENSIDAD_CURVA
        self.target_c=giro_player-curva_pista
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
            fuerza_base=acelerador*fuerza_motor
            fuerza_z+=fuerza_base*(1.0-factor_humo_salida*0.5)
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



        dz=self.speed*dt
        self.z+=dz
        self.vx+=self.c*dz*factor_v
        if self.vx>0:
            pass
        self.x_rel+=self.vx*dt


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


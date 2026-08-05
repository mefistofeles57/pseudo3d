import pygame
from ImageCache import ImageCache
from Object import Object
from VisualObjProfile import VisualObjProfile
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
        self.cache=ImageCache(ImageCache.getPlayerConfig(),context)
        self.cache.addImage("coche","coche.png",(0.5,0.95),False,True)
        profile=VisualObjProfile()
        profile.shadow_color=(74, 69, 64)
        profile.shadow_alpha=100
        profile.shadow_width_factor=1.2
        profile.shadow_height=0.2
        profile.cache=self.cache
        self.profile=profile
        #ruedas
        self.stress_rueda=0.0
        self.factor_humo=0.0
        #params
        self.VELOCIDAD_MAXIMA=15.0
        self.PENALIZACION_CURVA=10.0
        self.POTENCIA_MOTOR=10.0
        self.FUERZA_FRENADO=5.0
        self.RESISTENCIA_AIRE=0.05
        self.FRENO_MOTOR=1.0
        self.INTENSIDAD_CURVA=10.0
        self.FUERZA_VOLANTE=5.0
        self.LIMITE_AGARRE=0.6



    def update(self,dt):
        K_curva=8.0
        K_stress=3.0

        #dz con la vz del frame anterior
        dz=self.speed*dt



        factor_v=self.speed/self.VELOCIDAD_MAXIMA
        #acelerador/freno
        freno=self.get_freno()
        acelerador=self.get_acelerador()
        fuerza_z=acelerador+freno
        #print("acelerador/freno: ",fuerza_z)
        #resistencia al viento
        r_aire=self.speed*self.speed*self.RESISTENCIA_AIRE
        #print("resistencia aire:",r_aire)
        fuerza_z-=r_aire
        #fuerzas laterales
        giro=self.get_volante()
        giro_player=giro*self.FUERZA_VOLANTE*dz
        curva_pista=0.0
        if self.vs!=None:
            curva_pista=self.vs.curve*self.INTENSIDAD_CURVA
        self.target_c=giro_player-curva_pista
        self.c+=(self.target_c-self.c)*K_curva*dt
        #stress
        demanda_lateral=abs(giro)*factor_v
        demanda_freno=0.0
        if freno<-self.FRENO_MOTOR and self.speed>3.0:
            demanda_freno=factor_v*2.0
            print("demanda_freno: ",demanda_freno)
        demanda_salida=0.0
        if acelerador>3.0 and self.speed<3.0:
            demanda_salida=(1.0-(self.speed/3.0))*5.0
        demanda_rueda=max(demanda_lateral,demanda_freno,demanda_salida)
        self.stress_rueda+=(demanda_rueda-self.stress_rueda)*K_stress*dt
        if self.stress_rueda>=self.LIMITE_AGARRE:
            self.factor_humo=(self.stress_rueda-self.LIMITE_AGARRE)/self.LIMITE_AGARRE
            self.factor_humo=min(1.0,max(0.0,self.factor_humo))
        else:
            self.factor_humo=0.0
        if round(self.stress_rueda,3)>0.0 or self.factor_humo>0.0:
            print("demanda rueda: ",demanda_rueda,"stress rueda: ",round(self.stress_rueda,3),"self.factor_humo: ",self.factor_humo)
            pass

        #freno por curva
        r_curva=abs(self.c)*self.PENALIZACION_CURVA*factor_v
        #print("resistencia curva:",r_curva)
        fuerza_z-=r_curva
        #integracion fuerza
        self.speed+=fuerza_z*dt
        #limites
        if self.speed>self.VELOCIDAD_MAXIMA: self.speed=self.VELOCIDAD_MAXIMA
        if self.speed<0.0: self.speed=0.0
        if round(self.speed,2)==0.0:
            self.vx=0.0



        dz=self.speed*dt
        self.z+=dz
        self.vx+=self.c*dz
        self.x_rel+=self.vx*dt
        self.vx*=0.95


    def get_freno(self):
        down_pressed=self.context.keys[pygame.K_DOWN]
        if down_pressed:
            return self.FUERZA_FRENADO*-1
        else:
            return -self.FRENO_MOTOR

    def get_acelerador(self):
        up_pressed=self.context.keys[pygame.K_UP]
        if up_pressed:
            return self.POTENCIA_MOTOR
        return 0.0

    def get_volante(self):
        left_pressed=self.context.keys[pygame.K_LEFT]
        right_pressed=self.context.keys[pygame.K_RIGHT]
        
        i=0

        if left_pressed and not right_pressed:
            i=-1
        elif right_pressed and not left_pressed:
            i=1

        return i

    


import pygame
import math
from pathlib import Path
from ImageCache import ImageCache
from Object import Object,VisibleObject
from VisualObjProfile import VisualObjProfile
from TempObject import Humo
from Material import Material
from Car import Car
from Sound import EngineSound
from Estados import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext


class Player(Car):

    def __init__(self,context:"GameContext"):
        super().__init__()
        self.context=context
        self.speed=0.0
        self.img="coche"
        #self.metadata=None
        #self.vs_index=-1
        #posicion
        #self.x_rel=0.0
        #self.vx=0.0
        self.c=0.0
        self.target_c=0.0
        self.rpm=0.0
        #self.z=0.0
        #posicion previa
        self.prev_z=0.0
        self.prev_x_rel=0.0
        self.prev_c=0.0
        #cache para el coche
        self.cache=ImageCache(ImageCache.getPlayerConfig(resize=self.context.gen_scale),context)
        #self.cache.addImage("coche","coche.png",(0.5,1.0),False,True)
        self.cache.addAnimation("coche","coche-anim.png",(0.5,1.0),False,True,ancho=64,alto=64)
        self.load_metadata(self.cache)
        #propiedades
        self.collidable=True
        profile=VisualObjProfile()
        profile.shadow_color=(0,0,0)
        profile.shadow_alpha=80
        profile.shadow_width_factor=1.4
        profile.shadow_height=0.20
        profile.shadow_offset_z=0.0
        profile.collide_radius=0.15
        profile.collide_radius2=0.15*0.15

        profile.cache=self.cache
        self.profile=profile

        #cache para el humo
        #animaciones
        self.cache_humo=ImageCache(ImageCache.getHumoConfig(resize=self.context.gen_scale),context)
        self.cache_humo.addAnimation("humo","humo.png",(0.0,1.0),True,False)
        profile=VisualObjProfile()
        profile.shadow_color=(0,0,0)
        profile.shadow_alpha=80
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
        self.PENALIZACION_CURVA=1.0
        self.POTENCIA_MOTOR=7.0
        self.FUERZA_FRENADO=7.0
        self.RESISTENCIA_AIRE=0.0001
        self.FRENO_MOTOR=1.0
        self.INTENSIDAD_CURVA=20.0
        self.FUERZA_VOLANTE=3.0
        self.LIMITE_AGARRE=0.6
        #object
        self.type=Object.PLAYER

        #sonido
        base = str(Path(__file__).resolve().parent)
        self.engine = EngineSound(base+"/sound/loop_5.wav")
        self.engine.start()

        #frame
        self.frame=0
        


    def update(self, dt):
        vs=self.getVS(self.context)
        if self.context.keys[pygame.K_SPACE] and self.tecla_marcha==False:
            self.tecla_marcha=True
            self.cambio_marcha()
        elif self.context.keys[pygame.K_SPACE]==False:
            self.tecla_marcha=False
        if self.context.estado==NORMAL or self.context.estado==STARTING or self.context.estado==GAMEOVER or self.context.estado==GAMEOVER_FINAL:

            if self.context.estado!=GAMEOVER and self.context.estado!=GAMEOVER_FINAL:
                k_freno=self.context.keys[pygame.K_DOWN]
                k_acel=self.context.keys[pygame.K_UP]
                k_vol_r=self.context.keys[pygame.K_RIGHT]
                k_vol_l=self.context.keys[pygame.K_LEFT]
            else:
                k_freno = True
                k_acel=k_vol_r=k_vol_l=False

            acelerador=self.get_acelerador(k_acel,dt)
            freno=self.get_freno(k_freno,dt)
            volante = self.get_volante(k_vol_l, k_vol_r, dt)

            if freno < -2.0 and self.speed > 2.0:
                self.context.root.playSound("freno")
            else:
                self.context.root.stopSound("freno")

            if k_vol_l and not k_vol_r and self.speed > 0.1:
                #izquierda
                self.frame = 2
            elif k_vol_r and not k_vol_l and self.speed > 0.1:
                #derecha
                self.frame = 1
            else:
                if vs!=None and vs.height > 0:
                    #subiendo
                    self.frame = 4
                elif vs!=None and vs.height < 0:
                    #bajando
                    self.frame = 3
                else:
                    self.frame = 0
                
            

            (vmax_marcha, _) = self.marchas[self.marcha]
            


            if self.context.estado==NORMAL or self.context.estado==GAMEOVER or self.context.estado==GAMEOVER_FINAL:
                self.physics(acelerador,freno,volante,dt)

                dz=self.speed*dt
                self.collide(dz,self.vx*dt,self.context)

                dz=self.speed*dt
                self.z+=dz
                self.x_rel+=self.vx*dt

                if self.context.estado==NORMAL:
                    self.context.score+=dz

            self.check_segment_events()

            #sonido
            rpm_from_speed = self.speed / vmax_marcha
            rpm_from_throttle = self.p_acelerador

            if self.context.estado==NORMAL:
                rpm_factor = (
                    rpm_from_speed * 0.85 +
                    rpm_from_throttle * 0.15
                )
            else:
                rpm_factor = rpm_from_throttle

            rpm_factor = max(0.0, min(1.0, rpm_factor))
            self.rpm=rpm_factor
            self.engine.set_pitch(1.5 + 2.0 * rpm_factor)


            #posicion anterior
            self.prev_z=self.z
            self.prev_x_rel=self.x_rel
            self.prev_c=self.c
        elif self.context.estado==STUCK:
            self.context.stuck_time+=dt
            if self.context.stuck_time>=2.0:
                self.context.changeStatus(DESTUCKING)
        elif self.context.estado==DESTUCKING:
            if self.x_rel!=0.0:
                center_speed=1.0
                direction = -1 if self.x_rel > 0 else 1
                self.x_rel += direction * center_speed * dt
                if abs(self.x_rel) <= center_speed * dt:
                    self.x_rel = 0.0
            else:
                self.engine.start()
                self.context.changeStatus(NORMAL)



    def get_freno(self,down_pressed,dt):
        K_pedal=6.0
        #down_pressed=self.context.keys[pygame.K_DOWN]
        self.p_freno+=(down_pressed-self.p_freno)*K_pedal*dt
        fuerza_f=round(self.FUERZA_FRENADO*self.p_freno*-1,2)
        fuerza_fm=-self.FRENO_MOTOR
        return min(fuerza_f,fuerza_fm)

    def get_acelerador(self,up_pressed,dt):
        K_pedal=6.0
        #up_pressed=self.context.keys[pygame.K_UP]
        self.p_acelerador+=(up_pressed-self.p_acelerador)*K_pedal*dt
        return self.p_acelerador

    def get_volante(self,left_pressed,right_pressed,dt):
        K_volante=10.0
        #left_pressed=self.context.keys[pygame.K_LEFT]
        #right_pressed=self.context.keys[pygame.K_RIGHT]
        
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
            h=Humo(self.x_rel-0.08,self.z-0.01,self.speed,self.vx,metadata1,flip=True)
            h.profile=self.profile_humo
            self.context.frame_data.tempobjbuffer.append(h)
            h=Humo(self.x_rel+0.08,self.z-0.01,self.speed,self.vx,metadata2)
            h.profile=self.profile_humo
            self.context.frame_data.tempobjbuffer.append(h)

    def cambio_marcha(self):
        self.context.root.sounds["marcha"].play()
        if self.marcha==0:
            self.marcha=1
        else:
            self.marcha=0    

    def getMaterial(self):
        #material
        rueda_i=(self.x_rel-0.05)*-1
        rueda_d=self.x_rel+0.05
        profile = None
        vs=self.getVS(self.context)
        if vs!=None:
            profile=vs.visualProfile
        if profile==None:
            return Material()
        
        if rueda_i<vs.half_width:
            material_i=0
        elif rueda_i<vs.half_width+profile.arcen_width:
            material_i=1
        else:
            material_i=2
        if rueda_d<vs.half_width:
            material_d=0
        elif rueda_d<vs.half_width+profile.arcen_width:
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

    def reset(self):
        self.stress_salida=0.0
        self.stress_lateral=0.0
        self.stress_freno=0.0
        self.speed=0.0
        self.vx=0.0
        self.c=0.0
        self.p_freno=0.0
        self.p_acelerador=0.0
        self.volante = 0.0
        self.context.root.stopSound("derrape")
        self.engine.stop()
    
    def soft_reset(self):
        self.speed=0.0
        self.vx=0.0
        self.c=0.0
        self.p_freno=0.0
        self.p_acelerador=0.0
        self.volante=0.0

    def check_segment_events(self):
        vs=self.getVS(self.context)
        if vs!=None:
            events=vs.events
            if events!=None:
                for event in events:
                    if event.enabled and self.z>=event.z+vs.start.z:
                        event.execute(self.context)

    def physics(self,i_acelerador,i_freno,i_volante,dt):
        K_curva=8.0
        K_stress = 2.0
        
        vs=self.getVS(self.context)

        #dz con la vz del frame anterior
        dz=self.speed*dt

        #disipa algo de energía del movimiento lateral
        self.vx *= 0.95 ** (dt * 60.0)


        #material
        material = self.getMaterial()
        if material.name == "hierba" and self.speed>2.0:
            self.context.root.playSound("hierba")
        else:
            self.context.root.stopSound("hierba")

        #acelerador/freno
        freno=i_freno
        acelerador=i_acelerador
        giro=i_volante


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
        if vs!=None:
            pte=10*vs.segment.height/vs.segment.length
            if pte<-0.5:
                pte=-0.5
            elif pte>0.5:
                pte=0.5

            fuerza_pte=-pte*self.POTENCIA_MOTOR
        else:
            fuerza_pte=0.0

        if vs!=None:
            #posicion relativa de la curva (0.0 = interior de la curva 1.0 - exterior)
            x_ratio = (self.x_rel + vs.half_width) / (2.0 * vs.half_width)
            x_ratio = max(0.0, min(1.0, x_ratio))

            if vs.curve > 1e-6:
                x_ratio = 1.0 - x_ratio
                
        else:
            x_ratio=0.0

        #giro y fuerzas laterales
        dz_segura=max(0.001,dz)
        giro_player=giro*self.FUERZA_VOLANTE*dz_segura
        curva_pista=0.0
        if self.getVS(self.context)!=None:
            curva_pista=self.getVS(self.context).segment.curve
        centrifuga=curva_pista*factor_v*factor_v*self.INTENSIDAD_CURVA


        #50% de la fuerza modificada por la trazada
        centrifuga=centrifuga*0.5+centrifuga*x_ratio*0.5
        
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
        if factor_humo > 0.5:
            self.context.root.playSound("derrape")
            self.addHumo(dt)
        else:
            self.context.root.stopSound("derrape")
        
        fuerza_z=0.0
        #potencia efectiva (transmision a ruedas)
        if acelerador>0.0:
            fuerza_base=acelerador*fuerza_motor*material.friccion_z
            fuerza_z+=fuerza_base*(1.0-factor_humo_salida*0.5)
        fuerza_z+=fuerza_pte
        fuerza_z+=freno
        #resistencia al viento
        r_aire=self.speed*self.speed*self.RESISTENCIA_AIRE
        fuerza_z-=r_aire
        #freno por curva
        r_curva=abs(self.c)*self.PENALIZACION_CURVA*factor_v
        fuerza_z-=r_curva
        #integracion fuerza
        self.speed += fuerza_z * dt
        
        #disminuye la velocidad según el material
        self.speed-=material.drag_z*factor_v*dt


        #limites
        if self.speed>vmax: self.speed=vmax
        if self.speed<0.0: self.speed=0.0
        if round(self.speed,2)==0.0:
            self.vx=0.0
        if self.getVS(self.context)!=None and abs(self.x_rel)>self.getVS(self.context).visualProfile.road_limit:
            self.x_rel=math.copysign(self.getVS(self.context).visualProfile.road_limit, self.x_rel)
            self.vx=0.0

        self.mueve_camera(material)

        dz=self.speed*dt
        self.vx+=self.c*dz#*factor_v
        self.vx-=centrifuga*dz


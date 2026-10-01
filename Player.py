import pygame
import math
import sys
from pathlib import Path
from ImageCache import ImageCache
from Object import Object,VisibleObject
from VisualObjProfile import VisualObjProfile
from TempObject import Humo
from Material import Material
from Car import Car
from SonidoMotor import SonidoMotor
from Road import Segment
from Estados import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext


FR_LLANO=0
FR_LLANO_CD1=1
FR_LLANO_CD2=2
FR_LLANO_CI1=3
FR_LLANO_CI2=4
FR_CAR=5
FR_CAR_CD1=6
FR_CAR_CD2=7
FR_CAR_CI1=8
FR_CAR_CI2=9
FR_CAB=10
FR_CAB_CD1=11
FR_CAB_CD2=12
FR_CAB_CI1=13
FR_CAB_CI2=14
FR_LUZ=15
FR_RUEDAS=16
FR_RUEDAS_NUM=5
FR_LUCES_BASE=15     # índice del primer frame de luces en la animación (después de los 15 cuerpos)
FR_RUEDAS_BASE=30    # índice del primer frame de ruedas (después de los 15 de luces)
FR_RUEDAS_VEL=3.0    # fases del patrón de ruedas por unidad recorrida
FR_GIRO_EXTREMO=15   # frames pulsando hasta llegar al extremo
FR_GIRO_MAX=20       # tope del contador: FR_GIRO_MAX-FR_GIRO_EXTREMO frames de giro suave al soltar
LUCES_DESPL=[
    (0,0),(-1,0),(-3,0),(1,0),(3,0),
    (0,-2),(0,-2),(0,-2),(0,-2),(0,-2),
    (0,1),(0,1),(0,1),(0,1),(0,1)
]
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
        #self.cache.addAnimation("coche","coche-anim.png",(0.5,1.0),False,True,ancho=64,alto=64)
        #self.load_metadata(self.cache)


        hoja=pygame.image.load(str(self.cache.base/"img"/"coche-anim.png")).convert_alpha()
        f=self.cache.load_frames(hoja,64,64)
        coches=f[0:15]
        luz=f[FR_LUZ]
        patrones=f[FR_RUEDAS:FR_RUEDAS+FR_RUEDAS_NUM]

        luces=[]
        for i in range(15):
            capa=pygame.Surface((64,64),pygame.SRCALPHA)
            capa.blit(luz,self.despl_luz(i))
            luces.append(capa)

        ruedas=[]
        for i in range(15):
            for k in range(FR_RUEDAS_NUM):
                dxi,dxd=self.despl_ruedas(i,k)
                capa=pygame.Surface((64,64),pygame.SRCALPHA)
                capa.blit(patrones[k],(dxi,0),(0,0,32,64))
                capa.blit(patrones[k],(32+dxd,0),(32,0,32,64))
                ruedas.append(capa)

        self.cache.newAnimation("coche",coches+luces+ruedas,(0.5,1.0),True)


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
        self.marchas=[[9.0,1.5],[16.0,0.8]]
        self.marcha=0
        self.tecla_marcha=False
        #humo
        self.smoke_interval=0.1
        self.smoke_timer=0.0
        #params
        self.PENALIZACION_CURVA=1.0
        self.POTENCIA_MOTOR=4.0
        self.FUERZA_FRENADO=6.0
        self.RESISTENCIA_AIRE=0.000015
        self.FRENO_MOTOR=0.6
        self.INTENSIDAD_CURVA=20.0
        self.FUERZA_VOLANTE=3.0
        self.LIMITE_AGARRE=0.6
        #object
        self.type=Object.PLAYER

        #sonido
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent
        self.engine = SonidoMotor(str(base/"sound/loop_5.wav"))

        #frame
        self.frame=FR_LLANO
        self.giro_frames=0
        self.ruedas_fase=0.0

        #road width
        self.cur_width=0.0
        


    def update(self, dt):
        self.sync_side(self.context)
        vs=self.getVS(self.context)

        if self.context.keys[pygame.K_SPACE] and self.tecla_marcha==False:
            self.tecla_marcha=True
            self.cambio_marcha()
        elif self.context.keys[pygame.K_SPACE]==False:
            self.tecla_marcha=False
        if self.context.estado==NORMAL or self.context.estado==STARTING or self.context.estado==GAMEOVER or self.context.estado==GAMEOVER_FINAL:

            if self.context.estado!=GAMEOVER and self.context.estado!=GAMEOVER_FINAL:
                k_freno=self.context.keys[pygame.K_x]
                k_acel=self.context.keys[pygame.K_z]
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

            # --- frame del coche ---
            # pendiente: bloque de frames (recto, CD1, CD2, CI1, CI2 dentro de cada bloque)
            if vs!=None and vs.segment.height > 0:
                base=FR_CAR
            elif vs!=None and vs.segment.height < 0:
                base=FR_CAB
            else:
                base=FR_LLANO

            # giro: contador con signo que sube pulsando y baja al soltar
            if k_vol_r and not k_vol_l:
                pulsa=1
            elif k_vol_l and not k_vol_r:
                pulsa=-1
            else:
                pulsa=0

            if self.speed<=0.1:
                self.giro_frames=0
            elif pulsa!=0:
                if self.giro_frames*pulsa<0:
                    self.giro_frames=0
                self.giro_frames=max(-FR_GIRO_MAX,min(FR_GIRO_MAX,self.giro_frames+pulsa))
            elif self.giro_frames>0:
                self.giro_frames-=1
            elif self.giro_frames<0:
                self.giro_frames+=1

            mag=abs(self.giro_frames)
            if self.giro_frames>0:
                direccion=1
            else:
                direccion=-1
            if self.speed<=0.1:
                nivel=0
            elif pulsa!=0:
                if mag>=FR_GIRO_EXTREMO:
                    nivel=2 
                else:
                    nivel=1
            else:
                if mag>=FR_GIRO_EXTREMO:
                    nivel=1
                else:
                    nivel=0

            if nivel==0:
                self.frame=base
            else:
                if direccion>0:
                    self.frame=base+nivel
                else:
                    self.frame=base+nivel+2                
            
            # capas: luces de freno y patrón de ruedas (frames extra de la misma animación)
            capas=[]
            if k_freno:
                capas.append(FR_LUCES_BASE+self.frame)
            self.ruedas_fase+=self.speed*dt*FR_RUEDAS_VEL
            fase=int(self.ruedas_fase)%FR_RUEDAS_NUM
            capas.append(FR_RUEDAS_BASE+self.frame*FR_RUEDAS_NUM+fase)
            self.capas=tuple(capas)


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
            h.side=self.side
            self.context.frame_data.tempobjbuffer.append(h)
            h=Humo(self.x_rel+0.08,self.z-0.01,self.speed,self.vx,metadata2)
            h.profile=self.profile_humo
            h.side=self.side
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

        if rueda_i<self.cur_width:
            material_i=0
        elif rueda_i<self.cur_width+profile.arcen_width:
            material_i=1
        else:
            material_i=2
        if rueda_d<self.cur_width:
            material_d=0
        elif rueda_d<self.cur_width+profile.arcen_width:
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

    def interpolar_ancho(self,w0, w1, length, z):
        if length == 0:
            return w0
        t = z / length
        t = max(0.0, min(1.0, t))  # clamp por si z se sale del rango
        return w0 + (w1 - w0) * t

    def physics(self,i_acelerador,i_freno,i_volante,dt):
        K_curva=8.0
        K_stress = 2.0
        
        vs=self.getVS(self.context)

        #interpolar vs en el punto z

        self.cur_width=self.interpolar_ancho(vs.w0,vs.w1,vs.length,self.z-vs.start.z)



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

        curva_pista=0.0
        if vs!=None:
            curva_pista=vs.segment.curve_for(self.side)

        if vs!=None:
            #posicion relativa de la curva (0.0 = interior de la curva 1.0 - exterior)
            x_ratio = (self.x_rel + self.cur_width) / (2.0 * self.cur_width)
            x_ratio = max(0.0, min(1.0, x_ratio))

            if curva_pista > 1e-6:
                x_ratio = 1.0 - x_ratio
                
        else:
            x_ratio=0.0

        #giro y fuerzas laterales
        dz_segura=max(0.001,dz)
        factor_giro = max(0.1, factor_v)
        giro_player=giro*self.FUERZA_VOLANTE*dz_segura*factor_giro/ max(factor_v, 0.001)
   
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

        vs_actual=self.getVS(self.context)
        if vs_actual!=None:
            margen=vs_actual.visualProfile.margin_limit
            lim_ext=self.cur_width+margen
            lim_int=lim_ext
            if vs_actual.type==Segment.FORK and self.side!=0:
                d=vs_actual.d_at(self.z)
                if 2*d<=margen+2*self.cur_width:
                    lim_int=2*d+self.cur_width+margen
            # side=1: el hueco queda a la izquierda (x_rel negativo); side=-1: a la derecha
            if self.side==1:
                lim_izq,lim_der=lim_int,lim_ext
            elif self.side==-1:
                lim_izq,lim_der=lim_ext,lim_int
            else:
                lim_izq,lim_der=lim_ext,lim_ext
            if self.x_rel<-lim_izq:
                self.x_rel=-lim_izq
                self.vx=0.0
            elif self.x_rel>lim_der:
                self.x_rel=lim_der
                self.vx=0.0

        self.mueve_camera(material)

        dz=self.speed*dt
        self.vx+=self.c*dz#*factor_v
        self.vx-=centrifuga*dz


    def despl_luz(self,i):
        return LUCES_DESPL[i]
    
    def despl_ruedas(self,i,fase):
        # desplazamiento del patrón según el giro. Las cuestas quedan a cero hasta que se dibujen sus giros
        if i>=FR_CAR:
            return (0,0)
        #nivel y sentido del giro según la posición del frame
        giro=i%5
        if giro==0:
            return (0,0)
        if giro<=2:
            sentido=-1
        else:
            sentido=1
        nivel=1
        if giro==2 or giro==4:
            if fase>0:
                nivel=2
        dx=sentido*nivel
        return (dx,dx)
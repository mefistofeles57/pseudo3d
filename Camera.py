import pygame
import math
import copy
import time
from Road import Road
from Road import VisibleSegment
from Point import Point
from Player import Player
from Object import VisibleObject
from FrameData import FrameData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class Follower:

    def __init__(self,acceleration=0.05,max_speed=0.5,damping=0.5):
        self.speed = 0.0

        self.acceleration = acceleration
        self.max_speed = max_speed
        #self.damping = 0.92
        self.damping = damping

    def update(self, current_position, target_position):

        error = target_position - current_position

        self.speed += error * self.acceleration

        self.speed = max(
            -self.max_speed,
            min(self.max_speed, self.speed)
        )

        new_position = current_position + self.speed

        self.speed *= self.damping

        return new_position

    def reset(self):
        self.speed=0


class Camera:

    near_plane=0.5

    def __init__(self,context:"GameContext"):
        self.x=0.0
        self.y=0.0
        self.z=0.0

        self.w=context.screen.get_width()
        self.h=context.screen.get_height()


        #self.pitch=-0.04
        self.pitch=-0.04
        self.fov=55.0
        self.view_distance=15.0
        self.height=0.3
        self.horizon=2*self.h/3
        self.lookahead=1.5
        self.bgahead=0.5

        self.focal=(self.w/2)/math.tan(math.radians(self.fov)/2)


        self.time_button=0

        #fondos
        self.fondo=None
        self.color_fondo_l=None
        self.color_fondo_d=None

        self.context=context
        self.frame_data=context.frame_data


        self.current_horizon=self.horizon

        self.player_z=1.5



    def update(self,dt):

        #ajuste de camara
        keys=self.context.keys

        current_time=time.time()
        last_time=self.time_button


        if current_time-last_time>=0.5:
            self.time_button=current_time
        #altura        
            if keys[pygame.K_1]:
                self.context.camera.height-=0.1
            elif keys[pygame.K_2]:
                self.context.camera.height+=0.1
    #pitch
            elif keys[pygame.K_3]:
                self.context.camera.pitch-=0.01
            elif keys[pygame.K_4]:
                self.context.camera.pitch+=0.01
    #fov
            elif keys[pygame.K_5]:
                self.context.camera.fov-=1.0
            elif keys[pygame.K_6]:
                self.context.camera.fov+=1.0
    #distance
            elif keys[pygame.K_7]:
                self.context.camera.view_distance-=1.0
            elif keys[pygame.K_8]:
                self.context.camera.view_distance+=1.0
    #horizon
            elif keys[pygame.K_9]:
                self.context.camera.horizon-=1.0
            elif keys[pygame.K_0]:
                self.context.camera.horizon+=1.0
            else:
                self.time_button=last_time


        ############################################

        #mover el coche
        self.context.player.update(dt)
        self.z=self.context.player.z-self.player_z
        self.x=self.context.player.x_rel
        self.y=self.height

        #actualizar objetos temporales
        for obj in self.context.frame_data.tempobjbuffer:
            obj.update(dt)

        #eliminar objetos temporales muertos
        self.remove_dead_objects()

        #construir el buffer de carreta
        offset=self.getBuffer(self.frame_data.buffer,self.z+self.near_plane,offset=self.context.player.z)

        if offset==None:
            return

        self.getBuffer(self.frame_data.buffer,self.z+self.near_plane,x=offset.x,y=offset.y)
        self.getObjBuffer(self.frame_data)

        if len(self.frame_data.buffer)<3:
            return
       

        #proyecto el ultimo segmento
        pn=self.project(self.frame_data.buffer[-1].end)
        f_y=pn.y
        if f_y<(self.horizon-50):
            f_y=self.horizon-50
        if f_y>(self.horizon+50):
            f_y=self.horizon+50

        for fondo in self.frame_data.buffer[-1].visualProfile.fondos:
            fondo.update(self.context.player.vs.curve,f_y)

        self.update_sky()

    def remove_dead_objects(self):
        alive_objects = []

        for obj in self.frame_data.tempobjbuffer:
            if not obj.dead:
                alive_objects.append(obj)

        self.frame_data.tempobjbuffer = alive_objects


    def clip(self,a:Point,b:Point,z_clip):
        t=(z_clip-a.z)/(b.z-a.z)
        return Point(
            x=a.x+(b.x-a.x)*t,
            y=a.y+(b.y-a.y)*t,
            z=z_clip
        )


    def getBuffer(self,buffer,frontera,offset=None,x=None,y=None):
        segments=self.context.road.segments[self.context.road.current_segment:]
        distancia=self.view_distance
        buffer.clear()

        fin=False

        vs_prev=None
        for s in segments:
            vs=VisibleSegment(copy.copy(s),vs_prev,playerx=x,playery=y)
            if vs.end.z<=frontera:
                continue

            if vs.start.z<frontera:
                #clipping cercano
                p=self.clip(vs.start,vs.end,frontera)
                vs.start.z=frontera
                vs.curve=vs.end.x-p.x
                vs.height=vs.end.y-p.y
                vs.end.x=vs.start.x+vs.curve
                vs.end.y=vs.start.y+vs.height
                vs.acum_curve=vs.curve
                vs.acum_height=vs.height

                #end x e y deben interpolarse

            elif vs.end.z>(self.z+distancia):
                #clipping lejano
                vs.end=self.clip(vs.start,vs.end,self.z+distancia)

                fin=True
            vs_prev=vs
            if offset!=None:
                if vs.start.z<=offset and vs.end.z>offset:
                    pct=(offset-vs.start.z)/(vs.end.z-vs.start.z)
                    p=Point(vs.start.x+pct*vs.curve,vs.start.y+pct*vs.height,offset)
                    return p
            buffer.append(vs)
            if fin:
                break

        if len(buffer)>0 and offset==None:
            self.context.road.current_segment=buffer[0].index






    def getObjBuffer(self,frame_data):
        objects=self.context.road.objects[self.context.road.current_object:]
        player=self.context.player
        frame_data.objbuffer.clear()

        #construyo el buffer haciendo merge de objetos del mapa, objetos temporales y coche del jugador
        #aprovecho la pasada para calcular sombras



        for vs in frame_data.buffer:
            #selecciono la parte del mapa a dibujar
            sublist1=[]
            for i,o in enumerate(objects):
                if o.z<vs.start.z:
                    if vs==frame_data.buffer[0]:
                        self.context.road.current_object+=1
                    continue
                if o.z>vs.end.z:
                    break
                sublist1.append(o)
            #selecciono los objetos temporales a dibujar
            sublist2=[]
            for i,o in enumerate(frame_data.tempobjbuffer):
                if o.z<vs.start.z:
                    continue
                if o.z>vs.end.z:
                    break
                sublist2.append(o)
            
            sublist2.sort(key=lambda obj: obj.z)

            #hay que recorrer todos los elementos en las listas
            sublist3=[]
            if player.z>=vs.start.z and player.z<vs.end.z:
                sublist3.append(player)

            listas=[sublist1,sublist2,sublist3]
            indices=[0,0,0]


            #buscar el menor de todas las listas y añadirlo al obj buffer
            finalizado=False
            while finalizado==False:
                min_indice=-1
                min_val=99999
                for i,lista in enumerate(listas):
                    if indices[i]<len(lista) and lista[indices[i]].z<min_val:
                        min_val=lista[indices[i]].z
                        min_indice=i
                if min_indice!=-1:
                    o=listas[min_indice][indices[min_indice]]
                    indices[min_indice]+=1
                    if o.img=="coche":
                        o.vs=vs
                    frame_data.objbuffer.append(VisibleObject(o,vs))
                #ver si se han recorrido todas las listas
                finalizado=True
                for i,lista in enumerate(listas):
                    if indices[i]<len(listas[i]):
                        finalizado=False
                        break




    def project(self,p:Point):
        dx=p.x-self.x
        dy=p.y-self.y
        dz=p.z-self.z
        y2=dy*math.cos(self.pitch) - dz*math.sin(self.pitch)
        z2=dy*math.sin(self.pitch) + dz*math.cos(self.pitch)
        scale=self.focal/z2

        screen_x=(self.w/2)+dx*scale
        screen_y=(self.horizon)-y2*scale
        return Point(screen_x,screen_y,scale)

#        dz=z-cam_z
#        focal=(screen_with/2)/tan(fov/2)
#        scale=focal/dz
#        screen_x=(screen_width/2)+(x-cam_x)
#        screen_y
#        screen_y+=pitch





    def draw(self,s:pygame.Surface):

            
        if self.fondo!=None:
            s.blit(self.fondo, (0, 0))

        if self.frame_data.buffer==None or len(self.frame_data.buffer)==0:
            return

        #parallax
        for fondo in self.frame_data.buffer[-1].visualProfile.fondos:
            fondo.draw(s)


        for vs in reversed(self.frame_data.buffer):
            pc1=self.project(vs.end)
            pc2=self.project(vs.start)


            #cuando hay líneas de grosor negativo no pinto porque es un polígono no visible
            if pc2.y-pc1.y<0:
                continue

            vs.visualProfile.drawer.draw(s,self,vs,pc1,pc2)


            #primero se pintan las sombras del vs. Cualquier objeto puede proyectar
            vs.visualProfile.drawer.clear_shadow_surface()
            for item in reversed(self.frame_data.objbuffer):
                p1=self.project(Point(item.x,item.y,item.z))
                profile=vs.visualProfile
                profile.drawer.drawShadow(s,p1,item,profile,vs,pc1,pc2)
            vs.visualProfile.drawer.blitShadows(s,pc1,pc2)
            #despues los objetos. Solo los que estén situados dentro del segmento
            for item in reversed(self.frame_data.objbuffer):
                if item.z>=vs.start.z and item.z<vs.end.z:
                    p1=self.project(Point(item.x,item.y,item.z))
                    profile=vs.visualProfile
                    profile.drawer.drawObj(s,p1,item,profile)





    def create_vertical_gradient(self,width, height, top_color, bottom_color):
        surface = pygame.Surface((width, height)).convert()

        r0, g0, b0 = top_color
        r1, g1, b1 = bottom_color

        for y in range(height):
            t = y / (height - 1)

            r = int(r0 + (r1 - r0) * t)
            g = int(g0 + (g1 - g0) * t)
            b = int(b0 + (b1 - b0) * t)

            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

        return surface

    def lerp(self,a, b, t):
        return a + (b - a) * t

    def lerp_color(self,c0, c1, t):
        return (
            int(self.lerp(c0[0], c1[0], t)),
            int(self.lerp(c0[1], c1[1], t)),
            int(self.lerp(c0[2], c1[2], t)),
        )

    def update_sky(self):
        #color del cielo
        #buscar los colores del cielo en el buffer
        if len(self.frame_data.buffer)==0:
            return
        num_primer_color=0
        primer_color_l=None
        primer_color_d=None
        num_segundo_color=0
        segundo_color_l=None
        segundo_color_d=None
        for item in reversed(self.frame_data.buffer):
            if num_segundo_color==0:
                if num_primer_color==0:
                    #primer color
                    primer_color_l=item.visualProfile.sky_light
                    primer_color_d=item.visualProfile.sky_dark
                    num_primer_color=1
                elif item.visualProfile.sky_light!=primer_color_l or item.visualProfile.sky_dark!=primer_color_d:
                    #segundo color
                    segundo_color_l=item.visualProfile.sky_light
                    segundo_color_d=item.visualProfile.sky_dark
                    num_segundo_color=1
                else:
                    num_primer_color+=1
            else:
                if item.vs.sky_light==segundo_color_l or item.vs.sky_dark==segundo_color_d:
                    break
                else:
                    num_segundo_color+=1
        if num_segundo_color>0:
            #hacer mezcla de colores
            t=num_segundo_color/(num_segundo_color+num_primer_color)
            color_l=self.lerp_color(primer_color_l,segundo_color_d,t)
            color_d=self.lerp_color(primer_color_d,segundo_color_d,t)
        else:
            #sin mezcla
            color_l=primer_color_l
            color_d=primer_color_d
        if self.color_fondo_l!=color_l or self.color_fondo_d!=color_d:
            self.color_fondo_l=color_l
            self.color_fondo_d=color_d
            self.fondo=self.create_vertical_gradient(self.w, int(self.horizon), color_d, color_l )


import pygame
import math
import copy
import time
from Road import Road
from Road import VisibleSegment
from Point import Point
from Player import Player
from Object import VisibleObject
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

        self.buffer=[]
        self.objbuffer=[]

        self.time_button=0

        #fondos
        self.fondo=None
        self.color_fondo_l=None
        self.color_fondo_d=None

        self.context=context

        self.current_horizon=self.horizon

        self.player_z=1.5
        self.x_follower=Follower()
        self.y_follower=Follower()



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


        #construir el buffer de carreta
        offset=self.getBuffer(self.buffer,self.z+self.near_plane,offset=self.context.player.z)

        if offset.x>0:
            pass

        self.getBuffer(self.buffer,self.z+self.near_plane,x=offset.x,y=offset.y)
        self.getObjBuffer(self.objbuffer,self.buffer)

        if len(self.buffer)<3:
            return
       
        road_y=0.0
        #encontrar el segmento sobre el que se apoya el coche para calcular dx en ese punto
        for i in range(len(self.buffer)-1):
            seg=self.buffer[i]


            #interpolar el frame actual
            if seg.start.z<=self.context.player.z and seg.end.z>self.context.player.z:
                #interpola x e y de la carretera
                pto=self.context.player.z-seg.start.z
                pct=pto/seg.segment.length
                y1=seg.start.y
                y2=seg.end.y
                road_y=y1+((y2-y1)*pct)

                #posicion en la carretera
                #self.y=road_y+self.height
                #self.context.player.road_heading=road_heading
                #self.context.player.vx-=seg.segment.curve*dt
                #print(self.context.player.vx,self.context.player.x_rel)
                break

        #proyecto el ultimo segmento
        pn=self.project(self.buffer[-1].end)
        f_y=pn.y
        if f_y<(self.horizon-50):
            f_y=self.horizon-50
        if f_y>(self.horizon+50):
            f_y=self.horizon+50

        for fondo in self.buffer[-1].visualProfile.fondos:
            fondo.update(0.0,f_y)

        self.update_sky()




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


    def getObjBuffer(self,buffer,road_buffer):
        objects=self.context.road.objects[self.context.road.current_object:]
        player=self.context.player
        buffer.clear()

        for vs in road_buffer:
            for o in objects:
                if o.z<=vs.start.z:
                    if vs==road_buffer[0]:
                        self.context.road.current_object+=1
                    continue
                if o.z>vs.end.z:
                    break
                buffer.append(VisibleObject(o,vs))
            if player.z>vs.start.z and player.z<=vs.end.z:
                vo=VisibleObject(player,vs)
                player.vs=vs

                buffer.append(vo)




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

        if self.buffer==None or len(self.buffer)==0:
            return

        #parallax
        for fondo in self.buffer[-1].visualProfile.fondos:
            fondo.draw(s)


        for vs in reversed(self.buffer):
            pc1=self.project(vs.end)
            pc2=self.project(vs.start)


            #cuando hay líneas de grosor negativo no pinto porque es un polígono no visible
            if pc2.y-pc1.y<0:
                continue

            vs.visualProfile.drawer.draw(s,self,vs,pc1,pc2)
            #para cada objeto visible en esa franja
            #surface:pygame.Surface,p1:Point,obj:Object,cache:ImageCache,vp:VisualProfile,shadow=False
                #p1=c.project(Point(obj.x,obj.y,obj.z))
                #cache=vs.visualProfile.cache

            for item in reversed(self.objbuffer):
                if item.z>=vs.start.z and item.z<vs.end.z:
                    p1=self.project(Point(item.x,item.y,item.z))
                    #if p1.z>self.z+self.near_plane:
                    profile=vs.visualProfile
                    profile.drawer.drawObj(s,p1,item,profile,True)
            for item in reversed(self.objbuffer):
                if item.z>=vs.start.z and item.z<vs.end.z:
                    p1=self.project(Point(item.x,item.y,item.z))
                    #if p1.z>self.z+self.near_plane:
                    profile=vs.visualProfile
                    profile.drawer.drawObj(s,p1,item,profile,False)


            #player draw
#            player=self.context.player
#            p1=self.project(Point(player.x,player.y,player.z))
            #if p1.z>self.z+self.near_plane:
#            profile=vs.visualProfile
#            profile.drawer.drawObj(s,p1,player,player.cache,profile,True)
#            profile.drawer.drawObj(s,p1,player,player.cache,profile,False)



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
        if len(self.buffer)==0:
            return
        num_primer_color=0
        primer_color_l=None
        primer_color_d=None
        num_segundo_color=0
        segundo_color_l=None
        segundo_color_d=None
        for item in reversed(self.buffer):
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


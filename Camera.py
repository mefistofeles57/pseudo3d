import pygame
import math
import copy
import time
from Juego import Player
from Juego import Juego
from Road import Road
from Road import VisibleSegment
from Point import Point



class Camera:
    def __init__(self,screen,road:Road):
        self.x=0.0
        self.y=0.5
        self.z=-0.1

        self.w=screen.get_width()
        self.h=screen.get_height()


        self.pitch=-0.04
        self.fov=55.0
        self.view_distance=15.0
        self.height=0.5
        self.horizon=2*self.h/3
        self.lookahead=1.5

        self.focal=(self.w/2)/math.tan(math.radians(self.fov)/2)

        self.LUTh=self.getScaleTable(150)
        self.LUTm=self.getScaleTable(100)
        self.LUTl=self.getScaleTable(50)
        self.buffer=[]
        self.objbuffer=[]

        self.time_button=0

        self.fondo=None
        self.color_fondo_l=None
        self.color_fondo_d=None
        self.pos_fondo1=0.0

        self.road=road



    def getScaleTable(self,numtramos):
        escalas=[]
        distancia=(self.h+(numtramos))-self.horizon
        delta=distancia/numtramos

        for i in range(numtramos):
            y=(delta*(i))+self.horizon
            #se usa la y del centro del tramo para minimizar el error
            y_centro=(delta*(i+0.5))+self.horizon
            z=self.unproject(y_centro)

            if z>0.0:
                p1=self.project(Point(0.0,0.0,z))
                escalas.append({"index":i,"z":z,"y":y,"scale":p1.z})

        return escalas

    def unproject(self,target_y):
        z0=0
        z1=self.view_distance

        while z1-z0 > 0.001:
            zm = (z0+z1) /2
            if self.project(Point(0.0,0.0,zm)).y < target_y:
                z1=zm
            else:
                z0=zm
        return zm


    def follow(self,car:Player):
        pass


    def update(self,dt,j:Juego):

        #ajuste de camara
        keys=j.keys

        current_time=time.time()
        last_time=self.time_button


        if current_time-last_time>=0.5:
            self.time_button=current_time
        #altura        
            if keys[pygame.K_1]:
                j.camera.height-=0.1
            elif keys[pygame.K_2]:
                j.camera.height+=0.1
    #pitch
            elif keys[pygame.K_3]:
                j.camera.pitch-=0.01
            elif keys[pygame.K_4]:
                j.camera.pitch+=0.01
    #fov
            elif keys[pygame.K_5]:
                j.camera.fov-=1.0
            elif keys[pygame.K_6]:
                j.camera.fov+=1.0
    #distance
            elif keys[pygame.K_7]:
                j.camera.view_distance-=1.0
            elif keys[pygame.K_8]:
                j.camera.view_distance+=1.0
    #horizon
            elif keys[pygame.K_9]:
                j.camera.horizon-=1.0
            elif keys[pygame.K_0]:
                j.camera.horizon+=1.0
            else:
                self.time_button=last_time


        #posicion de camara
        self.z+=j.player.speed*dt

        self.getBuffer(self.buffer,j.road)
        self.getObjBuffer(self.objbuffer,j.road)

        if len(self.buffer)==0:
            return
       
        p0=self.buffer[0]


        inicio=self.z
        #calcular posicion x del looking ahead para posicionar la camara
        for i in range(len(self.buffer)-1):
            seg=self.buffer[i]
            if seg.end.z-inicio>=self.lookahead:
                pto=inicio+self.lookahead-seg.start.z
                pct=pto/seg.length
                x1=seg.start.x
                x2=seg.end.x
                posx=x1+((x2-x1)*pct)
                break


        dif=posx-self.x
        self.pos_fondo1+=dif*-25
        img=self.buffer[-1].visualProfile.f_img1

        if self.pos_fondo1+img.get_width()<self.w:
            self.pos_fondo1+=img.get_width()
            self.buffer[-1].visualProfile.swapFondo()
        elif self.pos_fondo1-img.get_width()>0:
            self.pos_fondo1-=img.get_width()
            self.buffer[-1].visualProfile.swapFondo()
        self.x=posx

        self.y=p0.start.y+self.height

        self.update_sky()

        #self.fondo=j.fondo



    def clip(self,a:Point,b:Point,z_clip):
        t=(z_clip-a.z)/(b.z-a.z)
        return Point(
            x=a.x+(b.x-a.x)*t,
            y=a.y+(b.y-a.y)*t,
            z=z_clip
        )


    def getBuffer(self,buffer,road):


        segments=road.segments[road.current_segment:]
        distancia=self.view_distance
        buffer.clear()

        fin=False

        for s in segments:
            vs=VisibleSegment(copy.copy(s))
            if vs.end.z<=self.z:
                continue

            if vs.start.z<=self.z:
                #clipping cercano
                vs.start=self.clip(vs.start,vs.end,self.z)
            elif vs.end.z>(self.z+distancia):
                #clipping lejano
                vs.end=self.clip(vs.start,vs.end,self.z+distancia)
                fin=True
            buffer.append(vs)
            if fin:
                break
        if len(buffer)>0:
            road.current_segment=buffer[0].index


    def getObjBuffer(self,buffer,road):
        objects=road.objects[road.current_object:]
        distancia=self.view_distance
        buffer.clear()

        for o in objects:
            if o.z<=self.z:
                road.current_object+=1
                continue
            if o.z>(self.z+distancia):
                break
            buffer.append(o)


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

        #parallax
        if len(self.buffer)>0:
            fondo1=self.buffer[-1].visualProfile.f_img1
            fondo2=self.buffer[-1].visualProfile.f_img2
            posicion=self.pos_fondo1
            s.blit(fondo1, (posicion-fondo1.get_width(),self.horizon-fondo1.get_height()))
            s.blit(fondo2, (posicion,self.horizon-fondo2.get_height()))

        for vs in reversed(self.buffer):
            pc1=self.project(vs.end)
            pc2=self.project(vs.start)

            #cuando hay líneas de grosor negativo no pinto porque es un polígono no visible
            if pc2.y-pc1.y<0:
                continue

            vs.visualProfile.drawer.draw(s,self,vs,pc1,pc2)
            #para cada objeto visible en esa franja
            for item in reversed(self.objbuffer):
                if item.z>=vs.start.z and item.z<vs.end.z:
                    vs.visualProfile.drawer.drawObj(s,self,vs.visualProfile.cache,item)



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


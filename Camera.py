import pygame
import math
import time
from Road import Segment
from Road import VisibleSegment
from Point import Point
from Object import Object,VisibleObject
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext



class Camera:

    near_plane=0.5

    def __init__(self,context:"GameContext"):
        self.x=0.0
        self.y=0.0
        self.z=0.0

        self.w=context.screen.get_width()
        self.halfw=self.w/2
        self.h=context.screen.get_height()


        self.pitch=0.0
        self.sin_pitch = 0.0
        self.cos_pitch = 0.0
        self.setPitch(-0.05)
        self.fov=70.0
        self.view_distance=25.0
        self.height=0.35
        self.horizon=2*self.h/3
        self.y_move=0.0

        self.focal=(self.w/2)/math.tan(math.radians(self.fov)/2)


        self.time_button=0

        #fondos
        self.fondo=None
        self.color_fondo_l=None
        self.color_fondo_d=None
        self.perfil_fondos=None
        self.fase_fondos=0.0


        self.context=context
        self.frame_data=context.frame_data

        self.player_z=1.5


    def setPitch(self, pitch):
        self.pitch = pitch
        self.sin_pitch = math.sin(pitch)
        self.cos_pitch = math.cos(pitch)

    def update(self,dt):


        if self.context.root.DEBUG:
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
                    pitch=self.pitch
                    self.setPitch(pitch-0.01)
                elif keys[pygame.K_4]:
                    pitch=self.pitch
                    self.setPitch(pitch+0.01)
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

        #actualizar objetos en orden

        listaobjs = [self.context.player] + self.context.frame_data.tempobjbuffer
        listaobjs.sort(key=lambda obj: obj.z, reverse=True)

        for item in listaobjs:
            item.update(dt)

        #eliminar objetos temporales muertos
        self.remove_dead_objects()

        #mover la camara
        self.z=self.context.player.z-self.player_z
        self.x=self.context.player.x_rel

        pl=self.context.player
        self.side_anclaje=pl.side or pl.last_side or 1

        self.y=self.height+self.y_move

        #calcular el avance para actualizar el fondo
        dz=self.context.player.speed*dt

        #carga de assets
        streamer=self.context.escenario.streamer
        streamer.actualizar(self.context.road,self.context.player.z)

        #construir el buffer de carretera

        #primero calcula la posicion del coche con respecto a un inicio de buffer en x=0
        offset=self.getBuffer(self.frame_data.buffer,self.z+self.near_plane,offset=self.context.player.z)

        if offset==None:
            return

        #usa ese desplazamiento anterior para calcular el buffer de carretera y que el coche esté en el centro
        self.getBuffer(self.frame_data.buffer,self.z+self.near_plane,x=offset.x,y=offset.y)

        #calcula el buffer de objetos del frame
        self.getObjBuffer(self.frame_data)

        #si el coche está en un FORK calcula x según su side
        vs_jugador=self.context.player.getVS(self.context)
        if vs_jugador!=None and vs_jugador.type==Segment.FORK:
            if self.context.player.side==-1:
                self.x+=vs_jugador.w0-2*vs_jugador.d_at(self.context.player.z)
            elif self.context.player.side==1:
                self.x+=vs_jugador.w0

        #actualiza los objetos animados
        for item in self.frame_data.objbuffer:
            if item.isAnim:
                item.obj.update(dt)


        #proyecto el ultimo segmento para actualizar el fondo
        pn=self.project(self.frame_data.buffer[-1].end)
        f_y=pn.y
        if f_y<(self.horizon-50):
            f_y=self.horizon-50
        if f_y>(self.horizon+50):
            f_y=self.horizon+50

        self.update_sky()

        for fondo in self.perfil_fondos.fondos:
            fondo.update(self.context.player.getVS(self.context).segment.curve_for(self.context.player.side or 1)*dz,f_y)

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

    #construye el buffer con los segmentos de carretera que van a aparecer en el frame
    def getBuffer(self,buffer,frontera,offset=None,x=None,y=None):
        distancia=self.view_distance
        buffer.clear()

        fin=False

        vs_prev=None
        # para cada segmento del mapa empezando en self.context.road.current_segment
        for s_i in range(self.context.road.current_segment,len(self.context.road.segments)):
            s=self.context.road.segments[s_i]
            #convierte a VS y comprueba que esté más allá del near plane
            vs=VisibleSegment(s,vs_prev,playerx=x,playery=y,side=self.side_anclaje)
            if vs.end.z<=frontera:
                continue

            #si su inicio está anter del near plane hace el clipping cercano
            if vs.start.z<frontera:
                #clipping cercano
                d_clip=vs.d_at(frontera)
                p=self.clip(vs.start,vs.end,frontera)
                vs.start.z=frontera
                vs.curve=vs.end.x-p.x
                vs.height=vs.end.y-p.y
                vs.length=vs.end.z-p.z
                vs.end.x=vs.start.x+vs.curve
                vs.end.y=vs.start.y+vs.height
                vs.d=d_clip

            #si su fin está más allá de la distancia de dibujado hace el clipping lejano
            elif vs.end.z>(self.z+distancia):
                #clipping lejano
                vs.end=self.clip(vs.start,vs.end,self.z+distancia)
                vs.curve=vs.end.x-vs.start.x
                vs.height=vs.end.y-vs.start.y
                vs.length=vs.end.z-vs.start.z

                fin=True

            #si tenemos un offset (z) del coche devuelve su posicion para desplazar la carretera en una llamada posterior
            if offset!=None:
                if vs.start.z<=offset and vs.end.z>offset:
                    pct=(offset-vs.start.z)/(vs.end.z-vs.start.z)
                    p=Point(vs.start.x+pct*vs.curve,vs.start.y+pct*vs.height,offset)
                    return p
            #añade el segmento al buffer
            buffer.append(vs)
            vs_prev=vs
            if fin:
                break

        if len(buffer)>0 and offset==None:
            self.context.road.current_segment=buffer[0].index





    #construye el buffer de objetos. Selecciona los que van a aparecer en el frame
    #haciendo un merge del mapra de objetos, la lista de objetos temporales y el coche del player
    def getObjBuffer(self,frame_data):
        objects=self.context.road.objects
        player=self.context.player
        frame_data.objbuffer.clear()



        frame_data.tempobjbuffer.sort(key=lambda obj: obj.z)

        #construyo el buffer haciendo merge de objetos del mapa, objetos temporales y coche del jugador

        last_object_index=self.context.road.current_object

        for vs_index,vs in enumerate(frame_data.buffer):
            #selecciono la parte del mapa a dibujar
            sublist1=[]
            first_object_index=last_object_index
            for i in range(first_object_index,len(objects)):
                o=objects[i]
                if o.z<vs.start.z:
                    if vs==frame_data.buffer[0]:
                        self.context.road.current_object+=1
                    continue
                if o.z>vs.end.z:
                    last_object_index=i
                    break
                if vs_index>=o.lod_hasta:
                    continue
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

            #player
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
                    o.vs_index=vs_index
                    frame_data.objbuffer.append(VisibleObject(o,vs))
                #ver si se han recorrido todas las listas
                finalizado=True
                for i,lista in enumerate(listas):
                    if indices[i]<len(listas[i]):
                        finalizado=False
                        break


    #proyecta un punto tridimensional sobre la pantalla
    #devuelve sus coordenadas x,y y su escala en z 
    def project(self,p:Point):
        dx=p.x-self.x
        dy=p.y-self.y
        dz=p.z-self.z
        y2=dy*self.cos_pitch - dz*self.sin_pitch
        z2=dy*self.sin_pitch + dz*self.cos_pitch

        # Compresión adicional de perspectiva lejana
        #punto en el que se alcanza la maxima compresion
        MAX_Z = 25.0
        #cuanto comprime. distancia aparente en el horizonte es distancia*(1+strength)
        STRENGTH = 0.75
        #distancia a la empieza a notarse. 1 progresivo, 3 mitad, 5 lejos
        POWER = 3

        t = max(0.0, min(1.0, z2 / MAX_Z))
        z_visual = z2 * (1.0 + STRENGTH * t**POWER)


        scale = self.focal / z_visual
        



        screen_x=(self.halfw)+dx*scale
        screen_y=(self.horizon)-y2*scale
        return Point(screen_x,screen_y,scale)






    def draw(self,s:pygame.Surface):

        #primero se dibujan los fondos
        self.context.escenario.cache.nuevoFrame()

        if self.fondo!=None:
            s.blit(self.fondo, (0, 0))

        if self.frame_data.buffer==None or len(self.frame_data.buffer)==0:
            return

        #parallax
        if self.perfil_fondos!=None:
            for fondo in self.perfil_fondos.fondos:
                fondo.draw(s,self.fase_fondos)


        #calculo los indices del buffer sobre los que se proyecta la sombra de cada objeto
        #y lo guardo en una lista de sombras por segmento

        buffer=self.frame_data.buffer
        sombras=[]
        for _ in buffer:
            sombras.append([])
        for obj in self.frame_data.objbuffer:
            cache=Object.resolverCache(obj.profile)
            metadata=cache.metadata.get(obj.img)
            if metadata!=None and metadata.shadow:
                z=obj.z+obj.profile.shadow_offset_z
                h=obj.profile.shadow_height
                z_min=z-h
                z_max=z+h
                p1=self.project(Point(obj.x,obj.y,obj.z))
                #segmentos que pisa la sombra
                i=obj.vs_index
                while i>0 and buffer[i-1].end.z>=z_min:
                    i-=1
                while i<len(buffer) and buffer[i].start.z<=z_max:
                    if buffer[i].end.z>=z_min:
                        sombras[i].append((obj,p1))
                    i+=1

        cables=self.context.escenario.cables
        ultimos={}
        self.frame_data.faros=self.calcularFaros()
        manchas=self.calcularLuces()
        self.context.escenario.drawer.prepararLuces(manchas)
        last_obj_idx=len(self.frame_data.objbuffer)-1
        for i in range(len(buffer)-1,-1,-1):
            vs=buffer[i]
            pc1=self.project(vs.end)
            pc2=self.project(vs.start)


            #si la distancia entre lineas es negativa no pinto porque es un polígono no visible
            if pc2.y-pc1.y>=0:
                vs.visualProfile.drawer.draw(s,self,vs,pc1,pc2)

            #en las pantallas noecturas dibuja las luces
            if manchas and pc2.y-pc1.y>0:
                vs.visualProfile.drawer.drawLuces(s,vs,pc1,pc2,manchas)

            #primero se pintan las sombras del vs. Solo las que caen en este segmento
            vs.visualProfile.drawer.clear_shadow_surface(pc1,pc2)
            for item,p1 in reversed(sombras[i]):
                profile=vs.visualProfile
                profile.drawer.drawShadow(s,p1,item,profile,vs,pc1,pc2)
            vs.visualProfile.drawer.blitShadows(s,pc1,pc2)

            #despues los objetos. Solo los que estén situados dentro del segmento
            for j in range(last_obj_idx,-1,-1):
                item=self.frame_data.objbuffer[j]
                if item.z<vs.start.z:
                    break
                last_obj_idx=j-1
                if item.z<vs.end.z:
                    p1=self.project(Point(item.x,item.y,item.z))
                    profile=vs.visualProfile
                    profile.drawer.drawObj(s,p1,item,profile)
                    if cables and item.linea!=None:
                        lejano=ultimos.get(item.linea)
                        if lejano!=None:
                            self.drawCable(s,item.z,item.x_rel,lejano.z,lejano.x_rel,item.profile)
                        ultimos[item.linea]=item
        self.context.escenario.drawer.limpiarLuces()
        #por ultimo se dibujan los cables solo si están habilitados
        if cables:
            for linea,item in ultimos.items():
                if item.cable_inicio:
                    continue
                prof=item.profile
                self.drawCable(s,item.z-prof.cable_vano,item.x_rel,item.z,item.x_rel,prof)


    #crea el gradiente del fondo con lineas calculando los colores intermedios
    def create_vertical_gradient(self,width, height, top_color, bottom_color):
        #degradado en bandas de 3 pixeles: una columna con un pixel por banda, estirada
        banda=3
        n=(height+banda-1)//banda
        columna=pygame.Surface((1,n)).convert()
        r0, g0, b0 = top_color
        r1, g1, b1 = bottom_color
        for i in range(n):
            t=i/(n-1)
            r=int(r0+(r1-r0)*t)
            g=int(g0+(g1-g0)*t)
            b=int(b0+(b1-b0)*t)
            columna.set_at((0,i),(r,g,b))
        return pygame.transform.scale(columna,(width,height))

    def lerp(self,a, b, t):
        return a + (b - a) * t

    def lerp_color(self,c0, c1, t):
        return (
            int(self.lerp(c0[0], c1[0], t)),
            int(self.lerp(c0[1], c1[1], t)),
            int(self.lerp(c0[2], c1[2], t)),
        )

    #actualiza el color del cielo
    def update_sky(self):
        buffer=self.frame_data.buffer
        if len(buffer)==0:
            return
        actual=buffer[0].visualProfile
        color_l=actual.sky_light
        color_d=actual.sky_dark
        self.perfil_fondos=actual
        self.fase_fondos=0.0
        for vs in buffer:
            p=vs.visualProfile
            #busca en el buffer un cambio de profile (escenario)
            if p is not actual:
                # t=1 con la frontera en el horizonte, t=0 al llegar a ella
                t=(vs.start.z-self.z-self.near_plane)/(self.view_distance-self.near_plane)
                t=max(0.0,min(1.0,t))
                #calcula los nuevos colores light y dark mezclando los colores de los dos escenarios ponderando por t
                color_l=self.lerp_color(p.sky_light,actual.sky_light,t)
                color_d=self.lerp_color(p.sky_dark,actual.sky_dark,t)
                #calcula la fase de los fondos, para desvanecerlos o moverlos
                if t>=0.5:
                    self.fase_fondos=(1.0-t)*2.0
                else:
                    self.perfil_fondos=p
                    self.fase_fondos=t*2.0
                break
        #si el color cambia regenera el fondo
        if self.color_fondo_l!=color_l or self.color_fondo_d!=color_d:
            self.color_fondo_l=color_l
            self.color_fondo_d=color_d
            self.fondo=self.create_vertical_gradient(self.w, int(self.horizon), color_d, color_l)


    def move_camera(self,mov):
        self.y_move=mov


    #devuelve las coordenadas x,y de un punto z de la carretera
    #se usa para dibujar cables
    def puntoCarretera(self,z):
        buf=self.frame_data.buffer
        if len(buf)==0:
            return None
        for vs in buf:
            if vs.start.z<=z and z<vs.end.z:
                pct=(z-vs.start.z)/(vs.end.z-vs.start.z)
                return (vs.start.x+pct*vs.curve, vs.start.y+pct*vs.height)
        # fuera de lo visible: se prolonga el primer o el último segmento con longitud
        if z<buf[0].start.z:
            candidatos=buf
        else:
            candidatos=reversed(buf)
        for vs in candidatos:
            largo=vs.end.z-vs.start.z
            if largo>0:
                pct=(z-vs.start.z)/largo
                return (vs.start.x+pct*vs.curve, vs.start.y+pct*vs.height)
        return None


    #dibuja el cable entre postes
    def drawCable(self,s,a_z,a_x,b_z,b_x,profile):
        if a_z>b_z:
            a_z,b_z,a_x,b_x=b_z,a_z,b_x,a_x
        # el plano de corte es donde empieza el buffer: ahí desaparecen los postes
        z_cerca=self.z+self.near_plane
        if b_z<=z_cerca:
            return
        # extremo cercano detrás del plano: el cable se corta ahí, sobre la carretera en esa z
        if a_z<z_cerca:
            t=(z_cerca-a_z)/(b_z-a_z)
            a_x=a_x+(b_x-a_x)*t
            a_z=z_cerca
        pa=self.puntoCarretera(a_z)
        pb=self.puntoCarretera(b_z)
        if pa==None or pb==None:
            return
        xa=pa[0]+a_x
        ya=pa[1]+profile.cable_alto
        xb=pb[0]+b_x
        yb=pb[1]+profile.cable_alto
        N=12
        for dx in profile.cable_dx:
            p1=self.project(Point(xa+dx,ya,a_z))
            p2=self.project(Point(xb+dx,yb,b_z))
            caida=profile.cable_flecha*(p1.z+p2.z)/2
            puntos=[]
            for i in range(N+1):
                t=i/N
                puntos.append((p1.x+(p2.x-p1.x)*t, p1.y+(p2.y-p1.y)*t+caida*4*t*(1-t)))
            pygame.draw.lines(s,profile.cable_color,False,puntos,1)



    #calcula los circulos de las farolas
    def calcularLuces(self):
        #manchas de luz de las farolas: elipses en pantalla calculadas una vez por frame
        manchas=[]
        buffer=self.frame_data.buffer
        if len(buffer)==0:
            return manchas
        z_cerca=buffer[0].start.z+0.01
        z_min=self.z-2.0
        z_max=buffer[-1].end.z
        objetos=self.context.road.objects
        #tambien las farolas que ya han quedado un poco por detras de la camara
        k=self.context.road.current_object
        while k>0 and objetos[k-1].z>=z_min:
            k-=1
        while k<len(objetos) and objetos[k].z<=z_max:
            o=objetos[k]
            k+=1
            p=o.profile
            if p is None or not p.luz:
                continue
            lado=1.0
            if o.x_rel<0:
                lado=-1.0
            x_rel=o.x_rel-lado*p.luz_hacia_centro
            zc=o.z+p.luz_offset_z
            #la mancha se dibuja pegada a la farola: proporcional a su escala, como la sombra
            if zc<=z_cerca:
                continue
            (xc,yc)=self.puntoCarretera(zc)
            centro=self.project(Point(xc+x_rel,yc,zc))
            ancho=p.luz_ancho*centro.z
            alto=p.luz_alto*centro.z
            #rango de z que ocupa la mancha en pantalla: pixeles por unidad de carretera junto a la farola
            za=max(zc-0.5,z_cerca)
            zb=zc+0.5
            (xa,ya)=self.puntoCarretera(za)
            (xb,yb)=self.puntoCarretera(zb)
            pa=self.project(Point(xa+x_rel,ya,za))
            pb=self.project(Point(xb+x_rel,yb,zb))
            px_unidad=(pa.y-pb.y)/(zb-za)
            #carretera vista por detras (rasante): la mancha no se ve
            if px_unidad<=0:
                continue
            medio=(alto/2)/px_unidad*1.3+0.5
            elipses=[]
            for escala,fraccion in p.luz_escalones:
                w=ancho*escala
                h=alto*escala
                color=(int(p.luz_color[0]*fraccion),int(p.luz_color[1]*fraccion),int(p.luz_color[2]*fraccion))
                elipses.append(((centro.x-w/2,centro.y-h/2,w,h),color))
            manchas.append((elipses,zc-medio,zc+medio))
        return manchas



    #guarda en una lista los faros que hay en la carretera
    def calcularFaros(self):
        #z de los coches con faros, el jugador y los rivales vivos
        faros=[self.context.player.z]
        for o in self.frame_data.tempobjbuffer:
            if not o.dead and o.type==Object.CAR:
                faros.append(o.z)
        return faros
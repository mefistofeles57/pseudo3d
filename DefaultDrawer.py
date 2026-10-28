import pygame
import time
import math
import copy
from Camera import Camera
from Point import Point
from Road import Segment
from Road import VisibleSegment
from Object import Object,VisibleObject
from ImageCache import ImageCache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Escenario import Escenario


class DefaultDrawer:


    def __init__(self,context):
        # Superficie temporal reutilizable para sombras
        self.context=context
        self.shadow_surface = pygame.Surface(
            (context.screen.get_width(), context.screen.get_height()),
            pygame.SRCALPHA
        ).convert_alpha()
        # rectángulo de la superficie de sombras usado en el segmento actual
        self.sucio=None
        self.luz_surface=pygame.Surface((context.screen.get_width(),context.screen.get_height())).convert()
        self.luz_surface.fill((0,0,0))
        self.luz_sucio=None

    def clear_shadow_surface(self,p1:Point,p2:Point):
        # la superficie de sombras queda limpia al terminar cada segmento:
        # aquí solo se empieza a anotar lo que se dibuja
        self.sucio=None

    def blitShadows(self,s:pygame.Surface,pc1:Point,pc2:Point):
        if self.sucio is None:
            return
        y1 = pc1.y
        y2 = min(pc2.y,s.get_height())
        franja = pygame.Rect(
            0,
            y1,
            self.shadow_surface.get_width(),
            y2 - y1 +1
        )
        area = self.sucio.clip(franja)
        if area.width>0 and area.height>0:
            s.blit(self.shadow_surface, area.topleft, area)
        self.shadow_surface.fill((0, 0, 0, 0), self.sucio)
        self.sucio=None


    def brillo(self,distancia,max):
        min_brillo=1.0
        max_brillo=0.3
        min_distancia=0.0
        max_distancia=max

        #y = y₁ + (x - x₁) × (y₂ - y₁) / (x₂ - x₁)

        y=min_brillo +(((distancia-min_distancia)*(max_brillo-min_brillo))/(max_distancia-min_distancia))
        return y


    def draw(self,surface:pygame.Surface,c:Camera,vs:VisibleSegment,pc1,pc2):

        if vs.length<=0.0:
            return

        profile=vs.visualProfile
        #la coordenada z es la escala

        # se produce cierto jitter subpixel en la cuantización alrededor de la distancia 15. Se ha podido comprobar forzando la monotonía,
        # pero no es aplicable a otras geometrias, como las elevaciones

        num_rc=len(profile.road_colors)
        road_color=profile.road_colors[vs.index%num_rc]
        nivel=0
        if profile.luz_color!=None:
            nivel=self.nivelLuz(c,vs)
            if nivel>0:
                road_color=self.iluminar(road_color,nivel,profile)
        num_osc=len(profile.outside_colors)
        outside_color=profile.outside_colors[vs.index%num_osc]
        brillo=self.brillo(vs.start.z-c.z,c.view_distance)
        road_color=(
            min(255,road_color[0]*brillo),
            min(255,road_color[1]*brillo),
            min(255,road_color[2]*brillo)
        )
        outside_color=(
            min(255,outside_color[0]*brillo),
            min(255,outside_color[1]*brillo),
            min(255,outside_color[2]*brillo)
        )

        a=profile.arcen_width

        if vs.type==Segment.FORK:
            self.draw_exterior_fork(surface,c,vs,pc1,pc2,outside_color)
            #dibuja la seguna carretera desplazada d

            pc2_f = copy.copy(pc2)
            pc1_f = copy.copy(pc1)
            pc2_despl = copy.copy(pc2)
            pc1_despl = copy.copy(pc1)
            pc2_f.x -= 2*vs.d*pc2.z
            pc1_f.x -= 2*(vs.d+vs.curve)*pc1.z
            pc2_despl.x+=vs.w0*pc2.z
            pc1_despl.x+=vs.w1*pc1.z
            pc2_f.x+=vs.w0*pc2.z
            pc1_f.x+=vs.w1*pc1.z
            
            self.draw_road(surface,c,vs,pc1_despl,pc2_despl,road_color,brillo,(a,a),(a,a),nivel)
            self.draw_road(surface,c,vs,pc1_f,pc2_f,road_color,brillo,(a,a),(a,a),nivel)
        else:
            self.draw_exterior(surface,c,vs,pc1,pc2,outside_color)
            self.draw_road(surface,c,vs,pc1,pc2,road_color,brillo,(a,a),(a,a),nivel)

        #dibujos
        #solo no tiene clipping
        for marca in vs.road_marks:
            self.drawRoadMark(vs,marca)

    def draw_exterior(self,surface:pygame.Surface,c:Camera,vs:VisibleSegment,pc1,pc2,outside_color):
        borde_i=-1
        borde_d=c.w

        p1=Point( pc1.x-(vs.w1*pc1.z) , pc1.y )
        p2=Point( pc1.x+(vs.w1*pc1.z) , pc1.y )
        p3=Point( pc2.x-(vs.w0*pc2.z) , pc2.y )
        p4=Point( pc2.x+(vs.w0*pc2.z) , pc2.y )

        #dibuja el exterior izquierdo
        #solo si está dentro de la pantalla
        if p1.x>=0:
            puntos=((borde_i,p1.y),(p1.x,p1.y),(p3.x,p3.y),(borde_i,p3.y))
            self.pinta(surface,puntos,outside_color)
        #dibuja el exterior derecho
        if p2.x<c.w:
            puntos=((p2.x,p2.y),(borde_d,p2.y),(borde_d,p4.y),(p4.x,p4.y))
            self.pinta(surface,puntos,outside_color)

    def draw_exterior_fork(self,surface:pygame.Surface,c:Camera,vs:VisibleSegment,pc1,pc2,outside_color):
        borde_i=-1
        borde_d=c.w

        d_lejos=vs.d+vs.curve

        # izquierda (borde exterior en pc-2d)
        p1=Point( pc1.x-(2*d_lejos*pc1.z) , pc1.y )
        p3=Point( pc2.x-(2*vs.d*pc2.z) , pc2.y )
        # derecha (borde exterior en pc+2w, fijo)
        p2=Point( pc1.x+(2*vs.w1*pc1.z) , pc1.y )
        p4=Point( pc2.x+(2*vs.w0*pc2.z) , pc2.y )

        if p1.x>=0:
            puntos=((borde_i,p1.y),(p1.x,p1.y),(p3.x,p3.y),(borde_i,p3.y))
            self.pinta(surface,puntos,outside_color)
        if p2.x<c.w:
            puntos=((p2.x,p2.y),(borde_d,p2.y),(borde_d,p4.y),(p4.x,p4.y))
            self.pinta(surface,puntos,outside_color)

        #hueco entre las dos carreteras (solo se abre hacia la izquierda de pc)
        if vs.d>=vs.w0 and d_lejos>=vs.w1:
            g1=2*(d_lejos-vs.w1)*pc1.z
            g0=2*(vs.d-vs.w0)*pc2.z
            puntos=((pc1.x,pc1.y),(pc1.x-g1,pc1.y),(pc2.x-g0,pc2.y),(pc2.x,pc2.y))
            self.pinta(surface,puntos,outside_color)

    def draw_road(self,surface:pygame.Surface,c:Camera,vs:VisibleSegment,pc1,pc2,road_color,brillo,arcen_izq,arcen_der,nivel=0):
                
        profile=vs.visualProfile

        p1=Point( pc1.x-(vs.w1*pc1.z) , pc1.y )
        p2=Point( pc1.x+(vs.w1*pc1.z) , pc1.y )
        p3=Point( pc2.x-(vs.w0*pc2.z) , pc2.y )
        p4=Point( pc2.x+(vs.w0*pc2.z) , pc2.y )

        #dibuja el trapecio de la carretera
        if p1.y<c.h:
            puntos=((p1.x,p1.y),(p2.x,p2.y),(p4.x,p4.y),(p3.x,p3.y))
            self.pinta(surface,puntos,road_color)
        #arcenes
        if profile.arcen_width>0.0:
            mod=vs.index%profile.arcen_freq
            color_arcen=profile.arcen_color[mod]
            if color_arcen!=None:
                if nivel>0:
                    color_arcen=self.iluminar(color_arcen,nivel,profile)
                color_arcen=(
                    min(255,color_arcen[0]*brillo),
                    min(255,color_arcen[1]*brillo),
                    min(255,color_arcen[2]*brillo)
                )
                #izquierdo
                pl1=Point(pc1.x-((vs.w1+arcen_izq[0])*pc1.z),pc1.y)
                pl2=Point(pc1.x-((vs.w1)*pc1.z),pc1.y)
                pl4=Point(pc2.x-((vs.w0+arcen_izq[1])*pc2.z),pc2.y)
                pl3=Point(pc2.x-((vs.w0)*pc2.z),pc2.y)
                puntos=(pl1.list2d(),pl2.list2d(),pl3.list2d(),pl4.list2d())
                self.pinta(surface,puntos,color_arcen)
                #derecho
                pl1=Point(pc1.x+((vs.w1+arcen_der[0])*pc1.z),pc1.y)
                pl2=Point(pc1.x+((vs.w1)*pc1.z),pc1.y)
                pl4=Point(pc2.x+((vs.w0+arcen_der[1])*pc2.z),pc2.y)
                pl3=Point(pc2.x+((vs.w0)*pc2.z),pc2.y)
                puntos=(pl1.list2d(),pl2.list2d(),pl3.list2d(),pl4.list2d())
                self.pinta(surface,puntos,color_arcen)
        #lineas
        for linea in c.context.road.getLines(vs.index):
            item=linea.getPoints(vs,pc1,pc2)
            if item!=None:
                (puntos,color)=item
                if color!=None:
                    self.pinta(surface,puntos,color)


    def drawShadow(self,surface:pygame.Surface,p1:Point,obj:VisibleObject,p:"Escenario",vs:VisibleSegment,pc1:Point,pc2:Point):
        self.drawItem(surface,p1,obj,p,True,vs=vs,pc1=pc1,pc2=pc2)

    def drawObj(self,surface:pygame.Surface,p1:Point,obj:VisibleObject,p:"Escenario"):
        self.drawItem(surface,p1,obj,p,False)

    def drawItem(self,surface:pygame.Surface,p1:Point,obj:VisibleObject,p:"Escenario",shadow,vs=None,pc1=None,pc2=None):
        cache=Object.resolverCache(obj.profile)
        metadata=cache.metadata.get(obj.img)
        if metadata==None:
            return
        if p1.z>cache.config.scale_max:
            return
        (w,h)=cache.tamano(obj.img,p1.z)
        if shadow:
            if metadata.shadow:
                shadow_height=obj.profile.shadow_height
                shadow_offset_z=obj.profile.shadow_offset_z
                z=obj.z+shadow_offset_z
                if z+shadow_height>=vs.start.z and z-shadow_height<=vs.end.z:
                    if obj.profile.sombra_suelo:
                        self.drawSombraSuelo(w,h,p1,obj.profile,obj)
                    else:
                        self.drawItemShadow(surface,w,obj.profile,obj,vs,pc1,pc2)
            return
        x=p1.x-w*metadata.anchor_x
        y=p1.y-h*metadata.anchor_y
        sw=surface.get_width()
        sh=surface.get_height()
        if x>=sw or x+w<=0 or y>=sh or y+h<=0:
            return
        vx0=max(0,int(-x))
        vy0=max(0,int(-y))
        vx1=min(w,math.ceil(sw-x))
        vy1=min(h,math.ceil(sh-y))
        frame=None
        if metadata.type==ImageCache.ANIMATION:
            frame=obj.frame
        (img,dx,dy)=cache.getSprite(obj.img,p1.z,frame,w,h,vx0,vy0,vx1,vy1)
        surface.blit(img,(x+dx,y+dy))
        if frame is not None:
            for capa in obj.capas:
                (img,dx,dy)=cache.getSprite(obj.img,p1.z,capa,w,h,vx0,vy0,vx1,vy1)
                surface.blit(img,(x+dx,y+dy))



    def drawItemShadow(self,surface:pygame.Surface,ancho,profile:"Escenario",obj:VisibleObject,vs:VisibleSegment,pc1:Point,pc2:Point):
        #calcula el tamaño de la sombra en función al ancho del objeto y a un tamaño fijo
        #dibuja una elipse en el punto p con el ancho calculado y el color y alfa indicados en el vp
        shadow_color=profile.shadow_color
        shadow_alpha=profile.shadow_alpha
        shadow_width_factor=profile.shadow_width_factor
        shadow_height=profile.shadow_height
        shadow_offset_z=profile.shadow_offset_z

        #necesito proyectar 3 punto, el centro, el max z y el min z

        p1=Point(obj.x,obj.y,obj.z+shadow_offset_z)
        p2=Point(obj.x,obj.y,obj.z+shadow_offset_z-shadow_height)
        #p3=Point(obj.x,obj.y,obj.z+shadow_offset_z+shadow_height)

        pp1=self.context.camera.project(p1)
        pp2=self.context.camera.project(p2)
        #pl=self.context.camera.project(p3)


        z=obj.z+shadow_offset_z
        pp1=self.context.camera.project(Point(obj.x,obj.y,z))
        pp_cerca=self.context.camera.project(Point(obj.x,obj.y,z-shadow_height))
        pp_lejos=self.context.camera.project(Point(obj.x,obj.y,z+shadow_height))

        width=ancho*shadow_width_factor
        #la sombra no puede doblar la anchura, para que no se deforme
        max_h=width*0.5
        #extremos reales en pantalla: por la perspectiva la mitad cercana es más alta que la lejana
        y_lejos=pp_lejos.y
        y_cerca=pp_cerca.y
        height=max(2,y_cerca-y_lejos)
        y=y_lejos
        if height>max_h:
            #se recorta alrededor del centro sin salirse de los extremos
            height=max_h
            y=pp1.y-max_h/2
            if y<y_lejos:
                y=y_lejos
            if y+max_h>y_cerca:
                y=y_cerca-max_h

        x=pp1.x - width // 2
        pygame.draw.ellipse(
            self.shadow_surface,
            (shadow_color[0], shadow_color[1], shadow_color[2], shadow_alpha),      # RGBA
            (x, y, width, height)
        )
        # 1 px de margen para cubrir el redondeo de la elipse
        r=pygame.Rect(math.floor(x)-1, math.floor(y)-1, math.ceil(width)+3, math.ceil(height)+3)
        if self.sucio is None:
            self.sucio=r
        else:
            self.sucio.union_ip(r)



    def pinta(self,surface,puntos,color):
        pygame.draw.polygon(surface,color,puntos,0)

    def drawRoadMark(self,vs,road_mark):
        #numstripes según distancia
        vd=self.context.camera.view_distance
        
        n=vd/3

        if (vs.start.z-self.context.camera.z)>2*n:
            numstripes=4
        elif (vs.start.z-self.context.camera.z)>n:
            numstripes=8
        else:
            numstripes=16



        #parte la imagen en numstripstrozos
        stripesize=road_mark.height/numstripes
        #proyecta los puntos
        #punto de inicio
        #clip lejano

        p=Point(vs.start.x+road_mark.offset_x,vs.start.y,vs.start.z+road_mark.offset_z)
        p_ant=p
        
        for i in range(numstripes):
            #calcular los extremos (interpolar x e y)
            z=((i+1)*stripesize)
            pct=min((z+road_mark.offset_z)/vs.length,1.0)
            x=vs.curve*pct
            y=vs.height*pct

            #tiene que usar el inicio y fin sin clipping para calcular la posición de las franjas
            if (vs.start.z-self.context.camera.z)==Camera.near_plane:
                #primer vs con clipping cercano
                s_ini=Point(vs.end.x-vs.segment.curve_for(1),vs.end.y-vs.segment.height,vs.end.z-vs.segment.length)
            else:
                s_ini=vs.start

            p=Point(s_ini.x+road_mark.offset_x+x,s_ini.y+y,s_ini.z+road_mark.offset_z+z)
            #si el punto anterior está entre el inicio y el fin del segmento con clipping
            if p_ant.z>=vs.start.z and p_ant.z<=vs.end.z:
                #si tiene clipping lejano
                if p.z>vs.end.z:
                    p.x=vs.end.x
                    p.y=vs.end.y
                    p.z=vs.end.z
                #si el punto anterior está antes del actual
                if p.z>=p_ant.z:
                    #calcular ancho y alto
                    pc1=self.context.camera.project(p_ant)
                    pc2=self.context.camera.project(p)
                    y1=math.ceil(pc1.y)
                    y2=math.floor(pc2.y)
                    width=round(pc1.z*road_mark.width)
                    height=max(y1-y2,1)
                    #redimiensionar
                    img=vs.visualProfile.images[road_mark.img]
                    img_stripe=img.get_height()/numstripes
                    area = pygame.Rect(
                        0,
                        round(img_stripe*(numstripes-i-1)),
                        img.get_width(),
                        round(img_stripe)
                    )
                    stripe = img.subsurface(area)

                    stripe_redim=pygame.transform.scale(stripe, (width,height))
                    #dibujar en pantalla el fragmento de la imagen correspondiente a la franja

                    x=round(pc1.x)

                    self.context.screen.blit(stripe_redim,(x,y2))
            p_ant=p
            if p_ant.z>=vs.end.z:
                break


    def drawSombraSuelo(self,ancho,alto,p1,profile,obj):
        #sombra pegada al sprite: elipse proporcional a su tamaño en pantalla, apoyada en su base
        width=ancho*profile.shadow_width_factor
        x=p1.x-ancho*obj.metadata.anchor_x-(width-ancho)/2
        y=p1.y-profile.sombra_delante*alto
        height=(profile.sombra_delante+profile.sombra_atras)*alto
        c=profile.shadow_color
        pygame.draw.ellipse(self.shadow_surface,(c[0],c[1],c[2],profile.shadow_alpha),(x,y,width,height))
        r=pygame.Rect(math.floor(x)-1,math.floor(y)-1,math.ceil(width)+3,math.ceil(height)+3)
        r=r.clip(self.shadow_surface.get_rect())
        if r.width==0 or r.height==0:
            return
        if self.sucio is None:
            self.sucio=r
        else:
            self.sucio.union_ip(r)


    def prepararLuces(self,manchas):
        #todas las manchas del frame se pintan una sola vez; cada segmento solo copia su franja
        self.luz_sucio=None
        for i in range(len(manchas)):
            elipses,z_min,z_max=manchas[i]
            for rect,color in elipses:
                pygame.draw.ellipse(self.luz_surface,color,rect)
            r=pygame.Rect(elipses[0][0]).inflate(4,4)
            manchas[i]=(elipses,z_min,z_max,r)
            if self.luz_sucio is None:
                self.luz_sucio=r.copy()
            else:
                self.luz_sucio.union_ip(r)

    def drawLuces(self,surface,vs,pc1,pc2,manchas):
        sucio=None
        for elipses,z_min,z_max,r in manchas:
            if z_max<vs.start.z or z_min>vs.end.z:
                continue
            if sucio is None:
                sucio=r.copy()
            else:
                sucio.union_ip(r)
        if sucio is None:
            return
        y1=int(pc1.y)
        y2=int(min(pc2.y,surface.get_height()))
        franja=pygame.Rect(0,y1,self.luz_surface.get_width(),y2-y1+1)
        area=sucio.clip(franja)
        if area.width>0 and area.height>0:
            surface.blit(self.luz_surface,area.topleft,area,special_flags=pygame.BLEND_RGB_ADD)

    def limpiarLuces(self):
        if self.luz_sucio is not None:
            self.luz_surface.fill((0,0,0),self.luz_sucio.clip(self.luz_surface.get_rect()))
            self.luz_sucio=None


    def nivelLuz(self,c,vs):
        #luz de faros que recibe el centro del segmento, en escalones 0..len(umbrales)
        profile=vs.visualProfile
        zc=(vs.start.z+vs.end.z)/2
        luz=0.0
        for z in c.frame_data.faros:
            t=zc-z
            if t>profile.faro_inicio and t<profile.faro_fin:
                #sube hasta el pico y luego se apaga: lo mas cercano, que en pantalla es enorme, queda suave
                if t<profile.faro_pico:
                    f=(t-profile.faro_inicio)/(profile.faro_pico-profile.faro_inicio)
                else:
                    f=1.0-(t-profile.faro_pico)/(profile.faro_fin-profile.faro_pico)
                luz+=profile.faro_intensidad*f
        nivel=0
        for umbral in profile.luz_umbrales:
            if luz>=umbral:
                nivel+=1
        return nivel

    def iluminar(self,color,nivel,profile):
        #mezcla el color hacia el de la luz segun el nivel
        k=profile.luz_mezcla[nivel]
        lc=profile.luz_color
        return (color[0]+(lc[0]-color[0])*k,color[1]+(lc[1]-color[1])*k,color[2]+(lc[2]-color[2])*k)
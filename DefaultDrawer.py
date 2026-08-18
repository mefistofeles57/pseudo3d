import pygame
import time
import math
from Camera import Camera
from Point import Point
from Road import VisibleSegment
from Road import Road
from Object import VisibleObject
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


    def clear_shadow_surface(self,p1:Point,p2:Point):
        y1 = p1.y
        y2 = min(p2.y,self.shadow_surface.get_height())


        rect = pygame.Rect(
            0,
            y1,
            self.shadow_surface.get_width(),
            y2 - y1 +1
        )
        self.shadow_surface.fill((0, 0, 0, 0),rect)

    def blitShadows(self,s:pygame.Surface,pc1:Point,pc2:Point):
        y1 = pc1.y
        y2 = min(pc2.y,s.get_height())


        area = pygame.Rect(
            0,
            y1,
            self.shadow_surface.get_width(),
            y2 - y1 +1
        )

        s.blit(
            self.shadow_surface,
            (0, y1),
            area
        )

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

        borde_i=-1
        borde_d=c.w

        profile=vs.visualProfile
        #la coordenada z es la escala

        # se produce cierto jitter subpixel en la cuantización alrededor de la distancia 15. Se ha podido comprobar forzando la monotonía,
        # pero no es aplicable a otras geometrias, como las elevaciones

        p1=Point( pc1.x-(profile.half_width*pc1.z) , pc1.y )
        p2=Point( pc1.x+(profile.half_width*pc1.z) , pc1.y )
        p3=Point( pc2.x-(profile.half_width*pc2.z) , pc2.y )
        p4=Point( pc2.x+(profile.half_width*pc2.z) , pc2.y )

        #road_color=profile.road_colors[vs.index%2]
        #outside_color=profile.outside_colors[vs.index%2]
        road_color=profile.road_colors[0]
        outside_color=profile.outside_colors[0]
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


        #dibuja el exterior izquierdo
        #solo si está dentro de la pantalla
        if p1.x>=0:
            puntos=((borde_i,p1.y),(p1.x,p1.y),(p3.x,p3.y),(borde_i,p3.y))
            self.pinta(surface,puntos,outside_color)
        #dibuja el exterior derecho
        if p2.x<c.w:
            puntos=((p2.x,p2.y),(borde_d,p2.y),(borde_d,p4.y),(p4.x,p4.y))
            self.pinta(surface,puntos,outside_color)
        #dibuja el trapecio de la carretera
        if p1.y<c.h:
            puntos=((p1.x,p1.y),(p2.x,p2.y),(p4.x,p4.y),(p3.x,p3.y))
            self.pinta(surface,puntos,road_color)
        #arcenes
        if profile.arcen_width>0.0:
            mod=vs.index%profile.arcen_freq
            color_arcen=profile.arcen_color[mod]
            if color_arcen!=None:
                color_arcen=(
                    min(255,color_arcen[0]*brillo),
                    min(255,color_arcen[1]*brillo),
                    min(255,color_arcen[2]*brillo)
                )
                #izquierdo
                pl1=Point(pc1.x-((profile.half_width+profile.arcen_width)*pc1.z),pc1.y)
                pl2=Point(pc1.x-((profile.half_width)*pc1.z),pc1.y)
                pl4=Point(pc2.x-((profile.half_width+profile.arcen_width)*pc2.z),pc2.y)
                pl3=Point(pc2.x-((profile.half_width)*pc2.z),pc2.y)
                puntos=(pl1.list2d(),pl2.list2d(),pl3.list2d(),pl4.list2d())
                self.pinta(surface,puntos,color_arcen)
                #derecho
                pl1=Point(pc1.x+((profile.half_width+profile.arcen_width)*pc1.z),pc1.y)
                pl2=Point(pc1.x+((profile.half_width)*pc1.z),pc1.y)
                pl4=Point(pc2.x+((profile.half_width+profile.arcen_width)*pc2.z),pc2.y)
                pl3=Point(pc2.x+((profile.half_width)*pc2.z),pc2.y)
                puntos=(pl1.list2d(),pl2.list2d(),pl3.list2d(),pl4.list2d())
                self.pinta(surface,puntos,color_arcen)
        #lineas
        for linea in c.context.road.getLines(vs.index):
            item=linea.getPoints(vs,pc1,pc2)
            if item!=None:
                (puntos,color)=item
                if color!=None:
                    self.pinta(surface,puntos,color)
        #dibujos
        #solo no tiene clipping
        for marca in vs.road_marks:
            self.drawRoadMark(vs,marca)


    def drawShadow(self,surface:pygame.Surface,p1:Point,obj:VisibleObject,p:"Escenario",vs:VisibleSegment,pc1:Point,pc2:Point):
        self.drawItem(surface,p1,obj,p,True,vs=vs,pc1=pc1,pc2=pc2)

    def drawObj(self,surface:pygame.Surface,p1:Point,obj:VisibleObject,p:"Escenario"):
        self.drawItem(surface,p1,obj,p,False)

    def drawItem(self,surface:pygame.Surface,p1:Point,obj:VisibleObject,p:"Escenario",shadow,vs=None,pc1=None,pc2=None):
        #p1=c.project(Point(obj.x,obj.y,obj.z))
        #cache=vs.visualProfile.cache
        if  obj.profile==None or obj.profile.cache==None:
            cache=p.cache
        else:
            cache=obj.profile.cache
        #metadata=cache.metadata[obj.img]
        metadata=obj.metadata
        if metadata!=None:
            if metadata.type==ImageCache.IMAGE:
                img=cache.getImage(obj.img,p1.z)
            else:
                anim=cache.getAnimation(obj.img,p1.z)
                if anim!=None:
                    img=anim[obj.frame]
                else:
                    img=None
                #de momento ni alpha ni scale
            if img!=None:
                if shadow==False:
                    punto=(p1.x-(img.get_width()*metadata.anchor_x),p1.y-img.get_height()*metadata.anchor_y)
                    surface.blit(img,punto)
                elif metadata.shadow:
                    #filtrar por z
                    shadow_height=obj.profile.shadow_height
                    shadow_offset_z=obj.profile.shadow_offset_z
                    #calcular z de sombra
                    z=obj.z+shadow_offset_z
                    #if metadata.name=="coche" and vs.index<=4:
                    #    print(vs.index,z+shadow_height,">=",vs.start.z,vs.index,z+shadow_height>=vs.start.z,z-shadow_height,"<=",vs.end.z,z-shadow_height<=vs.end.z)
                    if z+shadow_height>=vs.start.z and z-shadow_height<=vs.end.z:
                        self.drawItemShadow(surface,img,obj.profile,obj,vs,pc1,pc2)

    def drawItemShadow(self,surface:pygame.Surface,img,profile:"Escenario",obj:VisibleObject,vs:VisibleSegment,pc1:Point,pc2:Point):
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

        p=self.context.camera.project(p1)
        pc=self.context.camera.project(p2)
        #pl=self.context.camera.project(p3)


        width=img.get_width()*shadow_width_factor
        #height=shadow_height*scale
        height=max(2,(pc.y-p.y)*2)

        #dibuja en la superfice

        #shadow = pygame.Surface((width, height), pygame.SRCALPHA)

#        if obj.img=="coche":
#            print("h2d: ",height,"h3d: ",shadow_height,"scale: ",scale)
#            print("h2d: ",pc2.y-pc1.y,"scale1: ",pc1.z,"scale2: ",pc2.z)


        pygame.draw.ellipse(
            self.shadow_surface,
            (shadow_color[0], shadow_color[1], shadow_color[2], shadow_alpha),      # RGBA
            (p.x - width // 2, p.y - height // 2, width, height)
        )
        #surface.blit(shadow, (p.x - width // 2, p.y - height // 2))




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
            pct=(z+road_mark.offset_z)/vs.length
            x=vs.curve*pct
            y=vs.height*pct

            #tiene que usar el inicio y fin sin clipping para calcular la posición de las franjas
            if (vs.start.z-self.context.camera.z)==Camera.near_plane:
                #primer vs con clipping cercano
                s_ini=Point(vs.end.x-vs.segment.curve,vs.end.y-vs.segment.height,vs.end.z-vs.segment.length)
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

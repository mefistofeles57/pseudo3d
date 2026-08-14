import random
from Road import Segment
from Object import Object

class MapGenerator:
    CURVE=0
    HILL=1
    NONE=0

    visualProfile=None
    visualObjProfile=None
    @staticmethod
    def setProfile(profile):
        MapGenerator.visualProfile=profile

    @staticmethod
    def setObjProfile(profile):
        MapGenerator.visualObjProfile=profile

    @staticmethod
    def genSegment(type,value):
        if type==MapGenerator.CURVE:
            s=Segment(1.0,value,0.0,profile=MapGenerator.visualProfile)
        if type==MapGenerator.HILL:
            s=Segment(1.0,0.0,value,profile=MapGenerator.visualProfile)
        return s

    @staticmethod
    def pattern(type,curvature,length):
        segments=[]
        for i in range(length):
            segments.append(MapGenerator.genSegment(type,curvature))
        return segments

    @staticmethod
    def values(max,length):
        values=[]
        at=0.0
        dt=1.0/length
        prev=0.0
        for i in range(length):
            at+=dt
            value=-max*MapGenerator.smoothstep(at)
            values.append(value-prev)
            prev=value
        return values


    @staticmethod
    def smoothstep(t):
        return (3*(t*t)) - (2*(t*t*t))
    
    @staticmethod
    def merge(curve,hill):
        base=curve
        sec=hill
        c2h=False
        if len(hill)>len(curve):
            base=hill
            sec=curve
            c2h=True
        for i in range(len(sec)-1):
            if c2h:
                base[i].curve=sec[i].curve
            else:
                base[i].height=sec[i].height
        return base

    @staticmethod
    def objects(objetos,tramo,image,step,offset,x,random_x=0.0,random_step=0.0,profile=None,collidable=True):
        objects=[]
        z_pos=tramo[0].z+offset
        if random_x!=0 or random_step!=0:
            rng=random.Random(z_pos)
        z_end=tramo[-1].z+tramo[-1].length
        obj_pointer=0
        while z_pos<z_end:
            #copiar en object todos los elementos de objetos anteriores a z_pos
            for item in objetos[obj_pointer:]:
                if item.z<=z_pos:
                    objects.append(item)
                    obj_pointer+=1
                else:
                    break
            #añadir el objeto en z_pos
            obj=Object()
            if profile==None:
                obj.profile=MapGenerator.visualObjProfile
            else:
                obj.profile=profile
            obj.img=image
            #posisiona aqui el objeto
            obj.z=z_pos
            obj.x_rel=x
            #añadir un random a la posicion z
            if random_step!=0:
                obj.z+=rng.uniform(0,random_step)
            if random_x!=0:
                obj.x_rel+=rng.uniform(0,random_x)
            obj.collidable=collidable

            objects.append(obj)

            z_pos+=step
        #añadir los objetos detras de z_end
        for item in objetos[obj_pointer:]:
            objects.append(item)
        return objects



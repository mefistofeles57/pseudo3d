import random
from RoadMark import RoadMark
from Road import Segment
from Object import Object
from Event import EnemySpawn,Checkpoint

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
        for _ in range(length):
            segments.append(MapGenerator.genSegment(type,curvature))
        return segments

    @staticmethod
    def values(max,length):
        values=[]
        at=0.0
        dt=1.0/length
        prev=0.0
        for _ in range(length):
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
        for i in range(len(sec)):
            if c2h:
                base[i].curve=sec[i].curve
            else:
                base[i].height=sec[i].height
        return base

    @staticmethod
    def objects(objetos,tramo,image,step,offset,x,random_x=0.0,random_step=0.0,profile=None,collidable=True):
        z_pos=tramo[0].z+offset
        if random_x!=0 or random_step!=0:
            rng=random.Random(z_pos)
        z_end=tramo[-1].z+tramo[-1].length
        while z_pos<z_end:
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
            #cargar los metadatos
            if obj.profile.cache!=None:
                cache=obj.profile.cache
            else:
                cache=MapGenerator.visualProfile.cache
            obj.metadata=cache.metadata[obj.img]

            objetos.append(obj)

            z_pos+=step
        #añadir los objetos detras de z_end
        return objetos

    @staticmethod
    def addMark(s:Segment,img,x,z,w,h):
        rm=RoadMark()
        rm.img=img
        rm.offset_x=x
        rm.offset_z=z
        rm.width=w
        rm.height=h
        s.road_marks.append(rm)

    @staticmethod
    def addEnemy(s:Segment,z_rel, x_rel,speed):
        e=EnemySpawn(z_rel,x_rel,speed)
        s.events.append(e)


    @staticmethod
    def addCheckpoint(s:Segment,z_rel, time):
        e=Checkpoint(z_rel,time)
        s.events.append(e)


from Road import VisibleSegment

class Object:

    NONE=0
    CAR=1
    PLAYER=2

    def __init__(self,anim=False,frametime=0.1):
        self.img=""
        self.metadata=None
        self.profile=None
        self.z=0.0
        self.x_rel=0.0
        self.collidable=True
        self.vs_index=-1
        self.type=Object.NONE
        self.isAnim=anim
        self.frametime=frametime
        self.age=0.0
        self.frame=0
        
    def load_metadata(self,cache):
        self.metadata=cache.metadata[self.img]

    def getVS(self, context, index=0):
        if self.vs_index==-1 or self.vs_index+index>len(context.frame_data.buffer)-1:
            return None
        return context.frame_data.buffer[self.vs_index+index]

    def update(self, dt):
        self.age += dt
        if self.age>self.frametime:
            self.frame+=1
            self.frame%=self.metadata.frames
            self.age-=self.frametime

class VisibleObject(Object):
    def __init__(self,obj: Object,seg: VisibleSegment):
        super().__init__()
        self.__dict__.update(obj.__dict__)
        self.obj=obj
        if obj.isAnim:
            self.frame=obj.frame


        #interpolar x e y
        z_pos=self.z
        x=self.x_rel
        
        length=seg.end.z-seg.start.z

        pct=(z_pos-seg.start.z)/length
        #dx=seg.start.x+((seg.end.x-seg.start.x)*pct)
        #self.x=x+dx
        #self.y=seg.start.y+((seg.end.y-seg.start.y)*pct)
        dx=seg.start.x+(pct*seg.curve)
        dy=seg.start.y+(pct*seg.height)
        self.x=x+dx
        self.y=dy




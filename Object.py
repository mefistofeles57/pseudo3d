from Road import VisibleSegment

class Object:
    def __init__(self):
        self.img=""
        self.metadata=None
        self.profile=None
        self.z=0.0
        self.x_rel=0.0
        self.collidable=True
        self.vs_index=-1
        
    def load_metadata(self,cache):
        self.metadata=cache.metadata[self.img]


class VisibleObject(Object):
    def __init__(self,obj: Object,seg: VisibleSegment):
        super().__init__()
        self.__dict__.update(obj.__dict__)
        self.obj=obj


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




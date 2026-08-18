import math
from Point import Point

class Segment:
    def __init__(self,length=0.0,curve=0.0,height=0.0,half_width=0.6,profile=None):
        self.length=length
        self.curve=curve
        self.height=height
        self.visualProfile=profile
        self.index=0
        self.z=0.0
        self.road_marks=[]
        #self.heading=math.atan2(curve,height)

class VisibleSegment:
    def __init__(self,s:Segment,origin,playerx=None,playery=None,vs_index=-1):
        if origin!=None:
            x=origin.end.x
            y=origin.end.y
            c=origin.curve
            h=origin.height
        else:
            x=y=c=h=0.0
            if playerx!=None:
                x=-playerx
            if playery!=None:
                y=-playery

        self.segment=s
        self.curve=c+s.curve
        self.height=h+s.height
        self.start=Point(x,y,s.z)
        self.end=Point(x+self.curve,y+self.height,s.z+s.length)
        self.visualProfile=s.visualProfile
        self.index=s.index
        self.length=self.end.z-self.start.z
        self.road_marks=s.road_marks
        self.vs_index=vs_index

class Line:
    def __init__(self,position,x,width,offset,freq,color):
        self.position=position
        self.x=x
        self.width=width
        self.offset=offset
        self.freq=freq
        self.color=color
        self.material=None

    def getPoints(self,vs:VisibleSegment,pc1:Point,pc2:Point):
        mod=(vs.index+self.offset)%self.freq
        if mod<len(self.color):
            color=self.color[mod]
        else:
            color=None
        if color!=None:
            width=vs.visualProfile.half_width
            x1=pc1.x+((self.position*width+self.x)*pc1.z)
            x4=pc2.x+((self.position*width+self.x)*pc2.z)
            x2=x1+(self.width*pc1.z)
            x3=x4+(self.width*pc2.z)
            y1=pc1.y
            y2=y1
            y3=pc2.y
            y4=y3
            puntos=((x1,y1),(x2,y2),(x3,y3),(x4,y4))
            return (puntos,color)




class Road:
    def __init__(self):
        self.segments=[]
        self.current_segment=0
        self.objects=[]
        self.current_object=0
        self.lines=[]
        self.line_bounds=[]

    def add(self,segments):
        for segment in segments:
            segment.index=len(self.segments)
            if segment.index>0:
                s_ant=self.segments[segment.index-1]
                segment.z=s_ant.z+segment.length
                #segment.start.z=s_ant.end.z
                #segment.start.x=s_ant.end.x
                #segment.start.y=s_ant.end.y
            #segment.end.x=segment.start.x+segment.curve
            #segment.end.y=segment.start.y+segment.height
            #segment.end.z=segment.start.z+segment.length
            
            self.segments.append(segment)

    def addLine(self,line:Line,firstIndex,lastIndex):
        self.lines.append(line)
        self.line_bounds.append((firstIndex,lastIndex))

    def getLines(self,index):
        lineas=[]
        for (i,item) in enumerate(self.line_bounds):
            if item[0]<=index and item[1]>=index:
                lineas.append(self.lines[i])
        return lineas


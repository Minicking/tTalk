import math,random
from PyQt5.QtCore import Qt,QBasicTimer
from PyQt5.QtGui import QPainter, QColor, QFont,QPen
class Position:
    def __init__(self,x,y):
        self.x=float(x)
        self.y=float(y)
    def __str__(self):
        return "(%.1f,%.1f)"%(self.x,self.y)
    def get(self):
        return (self.x,self.y)
    def set(self,x,y):
        self.x=x
        self.y=y
    def getDistance(self,p):
        return math.sqrt(math.pow(self.x-p.x,2)+math.pow(self.y-p.y,2))
class Vector:
    def __init__(self,x=0,y=0):
        pi=math.pi
        self.x=float(x)
        self.y=float(y)
    def getAngle(self):
        dis=self.getValue()
        if dis==0:
            return None
        sin=self.y/dis
        cos=self.x/dis
        return {'sin':sin,'cos':cos}
    def getValue(self):
        return math.sqrt(math.pow(self.x,2)+math.pow(self.y,2))
    def setValue(self,value):
        value1=self.getValue()
        if value1==0:
            self.x=0
            self.y=0
        else:
        # print("设置后前:",self.getValue())
            self.x=self.x/value1*value
            self.y=self.y/value1*value
        # print("设置后:",self.getValue())
    def __mul__(self,t):
        if type(t)==type(self):
        #向量的点乘
            return self.x*t.x+self.y*t.y
        else:
        #向量乘以常数
            return velocity(self.x*t,self.y*t)
    def getVecComponent(self,vec):
        '''
            获取此向量在向量vec所在方向上的的两个分量，f1vec方向的分量，为f2为
            垂直与vec方向的分量
        '''
        if self.getValue()>0:
            cos=self.getAngOfVector(vec)
            dis=self.getValue()*cos
            f1=Vector(vec.x,vec.y)
            f1.setValue(dis)
            f2=self-f1
            return f1,f2
        else:
            return velocity(0,0),velocity(0,0)
    def getAngOfVector(self,t):
        value1=self.getValue()
        value2=t.getValue()
        return self*t/(value1*value2)

class velocity(Vector):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
    def __add__(self,t):
        return velocity(self.x+t.x,self.y+t.y)
    def __sub__(self,t):
        return velocity(self.x-t.x,self.y-t.y)
    def __str__(self):
        return str((self.x,self.y))
    def getVecComponent(self,vec):
        '''
            获取此向量在向量vec所在方向上的的两个分量，f1vec方向的分量，为f2为
            垂直与vec方向的分量
        '''
        if self.getValue()>0:
            cos=self.getAngOfVector(vec)
            dis=self.getValue()*cos
            f1=velocity(vec.x,vec.y)
            f1.setValue(dis)
            f2=self-f1
            return f1,f2
        else:
            return velocity(0,0),velocity(0,0)
    def offset(self,vec):
        '''
            将此向量在vec向量上的分量设置为vec向量的方向
        '''
        if self.getValue()!=0:
            cos=self.getAngOfVector(vec)
            dis=self.getValue()*cos
            f1,f2=self.getVecComponent(vec)
            f3=velocity(f1.x,f1.y)
            f3.setValue(dis)
            new=f3+f2
            self.x=new.x
            self.y=new.y
class Impact:
    def __init__(self,obj1,obj2):
        if type(obj1)==Ball:
            if type(obj2)==Ball:
                dvec=velocity(obj1.position.x-obj2.position.x,obj1.position.y-obj2.position.y)
                #被撞圆的圆心指向撞击圆的圆心方向的向量，数值无意义
                xf1,xf2=obj1.velocity.getVecComponent(dvec)
                #获取到撞击圆在圆心连线方向上以及垂直于此方向的两个速度分量
                yf1,yf2=obj2.velocity.getVecComponent(dvec)
                #获取到被撞圆在圆心连线方向上以及垂直于此方向的两个速度分量
                nxf1=(xf1*(obj1.mass-obj2.mass)+yf1*2.0*obj2.mass)*(1.0/(obj1.mass+obj2.mass))
                nyf1=(yf1*(obj2.mass-obj1.mass)+xf1*2.0*obj1.mass)*(1.0/(obj1.mass+obj2.mass))
                #根据能量守恒和动量守恒计算得到两个圆在圆心连线方向对心碰撞后的碎度
                dvec.setValue(obj2.range)
                x0,y0=obj2.position.x+dvec.x,obj2.position.y+dvec.y
                dvec.setValue(-obj1.range)
                x1,y1=obj1.position.x+dvec.x,obj1.position.y+dvec.y

                x0,y0=(x0+x1)/2,(y0+y1)/2
                dvec.setValue(-obj1.range)
                obj1.position.x=x0+dvec.x
                obj1.position.y=y0+dvec.y
                dvec.setValue(-obj2.range)
                obj2.position.x=x0+dvec.x
                obj2.position.y=y0+dvec.y
                #在撞击碰撞触发时将两个圆的位置进行修正，避免同一次碰撞进行多次判定
                obj1.velocity=nxf1+xf2
                obj2.velocity=nyf1+yf2
                #根据计算得到的连线方向的碰撞后的速度和原本拥有的垂直圆心方向的分量进行矢量和得到最终的速度
class GameObject:
    def __init__(self,name='default',position=Position(0,0),mass=None):
        self.position=position
        self.mass=mass
        self.gameWorld=None
        self.name=name
    def draw(self):
        pass
    def checkPosition(self):
        pass
class FixedRoep(GameObject):#固定在一个点的一个定长绳子
    def __init__(self,obj,length,**args):
        super().__init__(args['name'],args['position'],args['mass'])
        self.length=length
        self.obj=obj
    def draw(self,qp):
        qp.drawLine(self.position.x+self.gameWorld.board[2],self.position.y+self.gameWorld.board[0],self.obj.position.x+self.gameWorld.board[2],self.obj.position.y+self.gameWorld.board[0])
    def checkPosition(self):
        if self.position.getDistance(self.obj.position)>self.length:
            t=velocity(self.obj.position.x-self.position.x,self.obj.position.y-self.position.y)
            f1,f2=self.obj.velocity.getVecComponent(t)
            self.obj.velocity=f2+f1*-0.8
            t.setValue(self.length)
            self.obj.position.set(self.position.x+t.x,self.position.y+t.y)
class Ball(GameObject):
    def __init__(self,range=10,velocity=velocity(0,0),**args):
        super().__init__(args['name'],args['position'],args['mass'])
        self.range=range
        self.velocity=velocity
        self.RGB=(random.randint(0,150),random.randint(0,150),random.randint(0,150))
    def __str__(self):
        s=''
        s+='name:%s\n'%(self.name)
        s+='(x,y):%s\n'%(str(self.position))
        s+='mass:%f\n'%(self.mass)
        s+='v(x,y):(%.1f,%.1f)\n'%(self.velocity.x,self.velocity.y)
        return s
    def draw(self,qp):
        qp.setPen(QPen(QColor(self.RGB[0],self.RGB[1],self.RGB[2]),1,Qt.SolidLine))
        x,y,d=self.position.x,self.position.y,self.range*2
        qp.drawText(x-d/2+self.gameWorld.board[2]+math.sqrt(0.5)*(d/2),y-d/2+self.gameWorld.board[0]+math.sqrt(0.5)*(d/2)+5,str(self.name))
        qp.drawEllipse(x-d/2+self.gameWorld.board[2],y-d/2+self.gameWorld.board[0],d,d)
    def getEnergy(self):
        if self.gameWorld.type=='plane':
            return self.mass*math.pow(self.velocity.getValue(),2)/2.0
        elif self.gameWorld.type=='vertical':
            h=self.gameWorld.size[1]-self.position.y
        # print("获取能量:",self.mass,self.velocity.getValue())
            return self.mass*math.pow(self.velocity.getValue(),2)/2.0+self.mass*self.gameWorld.g*h
    def setAttr(self,**args):
        if "x" in args:self.position.x=args["x"]
        if "y" in args:self.position.y=args["y"]
        if "range" in args:self.range=args["range"]
        if "velocity" in args:self.velocity=args["velocity"]
        if "mass" in args:self.mass=args["mass"]
        return self
    def checkPosition(self):
        x,y=self.position.x,self.position.y
        if x-self.range<0:#左碰撞
            self.velocity.offset(velocity(1,0))
            self.velocity.x=self.velocity.x*(1-self.gameWorld.frictional)
            self.position.x=1+self.range
        elif x+self.range>self.gameWorld.size[0]:#右碰撞
            self.velocity.offset(velocity(-1,0))
            self.velocity.x=self.velocity.x*(1-self.gameWorld.frictional)
            self.position.x=self.gameWorld.size[0]-self.range
        elif y-self.range<0:#上碰撞
            self.velocity.offset(velocity(0,1))
            self.position.y=1+self.range
        elif y+self.range>self.gameWorld.size[1]:#下碰撞
            self.velocity.offset(velocity(0,-1))
            self.velocity.y=self.velocity.y*(1-self.gameWorld.frictional)
            self.position.y=self.gameWorld.size[1]-self.range
    def physicalCalculation(self,dtime):
        # print(dtime,self.velocity.x*dtime,self.velocity.y*dtime)
        if self.gameWorld.type=='vertical':
            h=self.gameWorld.size[1]-self.position.y
            if h>0:
                dg=self.gameWorld.g*dtime
                self.velocity=self.velocity+velocity(0,dg)
        elif self.gameWorld.type=='plane':
            df=velocity(self.velocity.x,self.velocity.y)
            df.setValue(-self.gameWorld.frictional*self.gameWorld.g*dtime)
            self.velocity=self.velocity+df
        self.position.x+=self.velocity.x*dtime
        self.position.y+=self.velocity.y*dtime
    def getUsersDistance(self,ball):
        return math.sqrt(math.pow(self.position.x-ball.position.x,2)+math.pow(self.position.y-ball.position.y,2))
    def getUsersAngle(self,user):
        dis=self.getUsersDistance(user)
        dx=(user.position.x-self.position.x)
        dy=(user.position.y-self.position.y)
        if dis==0:
            return None
        sin=dy/dis
        cos=dx/dis
        return sin,cos
    def impactCheck(self,user):
        return self.getUsersDistance(user)<self.range+user.range
        
if __name__ == '__main__':
    t=FixedRoep(10,position=Position(10,10),mass=10)
    print(t.position,t.mass,t.length)
import sys,os
from PyQt5.QtWidgets import QWidget, QApplication,QTextEdit
from PyQt5.QtGui import QPainter, QColor, QFont,QPen
from PyQt5.QtCore import Qt,QBasicTimer
from gameClass import velocity
import random,math,time
class User():
    def __init__(self,name,**args):
        self.name=name
        self.gameWorld=None
        self.x=args['x'] if 'x' in args else 0
        self.y=args['y'] if 'y' in args else 0
        self.range=args['range'] if 'range' in args else 10
        self.force=args['force'] if 'force' in args else 0
        self.velocity=args['velocity'] if 'velocity' in args else velocity(0,0)
        self.mass=args['mass'] if 'mass' in args else 10
        # if "x" in args:self.x=args["x"] else:self.x=0
        # if "y" in args:self.y=args["y"] else:self.y=0
        # if "range" in args:self.range=args["range"] else:self.range=10
        # if "force" in args:self.force=args["force"] else:self.force=10
        # if "velocity" in args:self.velocity=args["velocity"] else:self.velocity=velocity(0,0)
        # if "mass" in args:self.mass=args["mass"] else:self.mass=10
        self.keyUpBool=False
        self.keyDownBool=False
        self.keyLeftBool=False
        self.keyRightBool=False
    def __str__(self):
        s=''
        s+='name:%s\n'%(self.name)
        s+='(x,y):(%f,%f)\n'%(self.x,self.y)
        s+='mass:%f\n'%(self.mass)
        s+='v(x,y):(%f,%f)\n'%(self.velocity.x,self.velocity.y)
        return s
    def getEnergy(self):
        if self.gameWorld.type=='plane':
            return self.mass*math.pow(self.velocity.getValue(),2)/2.0
        elif self.gameWorld.type=='vertical':
            h=self.gameWorld.size[1]-self.y
        # print("获取能量:",self.mass,self.velocity.getValue())
            return self.mass*math.pow(self.velocity.getValue(),2)/2.0+self.mass*self.gameWorld.g*h
    def setAttr(self,**args):
        if "x" in args:self.x=args["x"]
        if "y" in args:self.y=args["y"]
        if "range" in args:self.range=args["range"]
        if "force" in args:self.force=args["force"]
        if "velocity" in args:self.velocity=args["velocity"]
        if "mass" in args:self.mass=args["mass"]
        return self
    def checkUserPosition(self):
        x,y=self.x,self.y
        if x-self.range<0:#左碰撞
            self.velocity.offset(velocity(1,0))
            self.velocity.x=self.velocity.x*(1-self.gameWorld.frictional)
            self.x=1+self.range
        elif x+self.range>self.gameWorld.size[0]:#右碰撞
            self.velocity.offset(velocity(-1,0))
            self.velocity.x=self.velocity.x*(1-self.gameWorld.frictional)
            self.x=self.gameWorld.size[0]-self.range
        elif y-self.range<0:#上碰撞
            self.velocity.offset(velocity(0,1))
            self.y=1+self.range
        elif y+self.range>self.gameWorld.size[1]:#下碰撞
            self.velocity.offset(velocity(0,-1))
            self.velocity.y=self.velocity.y*(1-self.gameWorld.frictional)
            self.y=self.gameWorld.size[1]-self.range
    def physicalCalculation(self,dtime):
        # print(dtime,self.velocity.x*dtime,self.velocity.y*dtime)
        if self.gameWorld.type=='vertical':
            h=self.gameWorld.size[1]-self.y
            if h>0:
                dg=self.gameWorld.g*dtime
                self.velocity=self.velocity+velocity(0,dg)
        elif self.gameWorld.type=='plane':
        # if abs(self.velocity.x)<1:self.velocity.x=0
        # if abs(self.velocity.y)<1:self.velocity.y=0
            df=velocity(self.velocity.x,self.velocity.y)
            df.setValue(-self.gameWorld.frictional*self.gameWorld.g*dtime)
            self.velocity=self.velocity+df
        self.x+=self.velocity.x*dtime
        self.y+=self.velocity.y*dtime
    def getUsersDistance(self,user):
        return math.sqrt(math.pow(self.x-user.x,2)+math.pow(self.y-user.y,2))
    def getUsersAngle(self,user):
        dis=self.getUsersDistance(user)
        dx=(user.x-self.x)
        dy=(user.y-self.y)
        if dis==0:
            return None
        sin=dy/dis
        cos=dx/dis
        return sin,cos
    def impactCheck(self,user):
        return self.getUsersDistance(user)<self.range+user.range
    def impact(self,vt):
        dvec=velocity(self.x-vt.x,self.y-vt.y)
        #被撞圆的圆心指向撞击圆的圆心方向的向量，数值无意义
        xf1,xf2=self.velocity.getVecComponent(dvec)
        #获取到撞击圆在圆心连线方向上以及垂直于此方向的两个速度分量
        yf1,yf2=vt.velocity.getVecComponent(dvec)
        #获取到被撞圆在圆心连线方向上以及垂直于此方向的两个速度分量
        nxf1=(xf1*(self.mass-vt.mass)+yf1*2.0*vt.mass)*(1.0/(self.mass+vt.mass))
        nyf1=(yf1*(vt.mass-self.mass)+xf1*2.0*self.mass)*(1.0/(self.mass+vt.mass))
        #根据能量守恒和动量守恒计算得到两个圆在圆心连线方向对心碰撞后的碎度
        dvec.setValue(vt.range)
        x0,y0=vt.x+dvec.x,vt.y+dvec.y
        dvec.setValue(-self.range)
        x1,y1=self.x+dvec.x,self.y+dvec.y

        x0,y0=(x0+x1)/2,(y0+y1)/2
        dvec.setValue(-self.range)
        self.x=x0+dvec.x
        self.y=y0+dvec.y
        dvec.setValue(-vt.range)
        vt.x=x0+dvec.x
        vt.y=y0+dvec.y
        #在撞击碰撞触发时将两个圆的位置进行修正，避免同一次碰撞进行多次判定
        self.velocity=nxf1+xf2
        vt.velocity=nyf1+yf2
        #根据计算得到的连线方向的碰撞后的速度和原本拥有的垂直圆心方向的分量进行矢量和得到最终的速度
class GameBoard(QWidget):
    def __init__(self,tt,size,board,playRate,g,frictional,userList):
        super().__init__()
        # self.user.setAttr(range=20)
        self.type=tt
        self.size=size
        self.board=board
        self.playRate=playRate
        self.g=g
        self.frictional=frictional
        self.mainTimer=QBasicTimer()
        self.userList=[]
        for i in userList:
            self.addUser(i)
        # self.socreBoard.move(100,100)
        self.initUI()
    def initUI(self):
        self.setGeometry(100, 300, self.size[0]+self.board[2]+self.board[3]+125, self.size[1]+self.board[0]+self.board[1])
        self.setWindowTitle('Draw text')
        self.socreBoard=QTextEdit(self)
        self.socreBoard.move(self.board[2]+self.board[3]+self.size[0],self.board[0])
        self.socreBoard.resize(100,self.size[1])
        self.socreBoard.setFocusPolicy(Qt.NoFocus) 
        self.show()
        # time.sleep(5)
        self.ztime=time.time()
        self.mainTimer.start(10/self.playRate,self)
    def addUser(self,user):
        self.userList.append(user)
        user.gameWorld=self
        if user.mass<=0:user.mass=1
        if user.range<=0:user.range=1
    def flushScoreBoard(self):
        html="<p style='font-size:12px;text-align:center'>总球数(n):(%3d)</p>"%(len(self.userList))
        html+="<p style='font-size:12px;text-align:center'>帧数(fps):(%3d)</p>"%(self.zs)
        html+="<p style='font-size:12px;text-align:center'>重力加速度(g):(%.1f)</p>"%(self.g)
        html+="<p style='font-size:12px;text-align:center'>摩擦系数(μ):(%.1f)</p>"%(self.frictional)
        fff=0.0
        for i in self.userList:
            fff+=i.getEnergy()
        html+="<p style='font-size:12px;text-align:center'>系统内的总能量(q):(%.1f)</p>"%(fff)
        self.socreBoard.setHtml(html)
    def userImpact(self):
        tt=False
        for i in self.userList:
            for j in self.userList:
                if i is not j:
                    if i.impactCheck(j):
                        # print(i.name,"碰撞",j.name)
                        i.impact(j)
                        # tt=True
        if tt:
            self.mainTimer.stop()
            time.sleep(1)
            self.mainTimer.start(10/self.playRate,self)
            tt=False

        # pass

    def timerEvent(self,e):
        
        nowtime=time.time()
        jg=nowtime-self.ztime
        print(jg)
        self.zs=1//jg
        self.ztime=nowtime
        for i in self.userList:
            # i.checkPress()
            i.physicalCalculation(dtime=jg)
            i.checkUserPosition()
        self.userImpact()
        self.flushScoreBoard()
        self.repaint()
        # print("到期",e)
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawBoard(event,qp)
        qp.end()
        # self.user.setAttr(x=user.x+dx,y=user.y+dy)
    def drawBoard(self, event, qp):
        pen=QPen(QColor(0,0,0),1,Qt.SolidLine)
        qp.setPen(pen)
        # qp.drawRect(self.board[2],self.board[0],self.size[0]-self.board[3],self.size[1]-self.board[1])
        # qp.drawEllipse(self.user.x+self.board[2]-self.user.range/2,self.user.y+self.board[0]-self.user.range/2,self.user.range,self.user.range)
        qp.drawRect(self.board[2],self.board[0],self.size[0],self.size[1])
        for i in self.userList:
            self.drawUser(i,qp)
    def drawUser(self,user,qp):
        x,y,a1,a2=user.x,user.y,user.range*2,user.range*2
        qp.drawText(x-a1/2+self.board[2]+math.sqrt(0.5)*(a1/2),y-a2/2+self.board[0]+math.sqrt(0.5)*(a2/2)+5,str(user.name))
        qp.drawEllipse(x-a1/2+self.board[2],y-a2/2+self.board[0],a1,a2)
    def keyPressEvent(self,event):
        # self.keyPressEvent(self,event)
        key=event.key()
        if key == Qt.Key_Up: self.userList[0].keyUpBool=True
        elif key == Qt.Key_Down:self.userList[0].keyDownBool=True
        elif key == Qt.Key_Left:self.userList[0].keyLeftBool=True
        elif key == Qt.Key_Right:self.userList[0].keyRightBool=True
    def mousePressEvent(self,event):
        x=event.x()-self.board[2]
        y=event.y()-self.board[0]
        if x>0 and x<self.size[0] and y>0 and y<self.size[1]:
            self.addUser(User(0,x=x,y=y,range=10,mass=10,velocity=velocity(500,0)))
        print(x,y)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    userList=[]
    for i in range(5):
        userList.append(User(i,x=200,y=i*20,range=10,mass=10))
    #tt:vertical plane
    ex = GameBoard(tt='vertical',size=(400,800),board=(25,25,25,25),playRate=1.0,g=0,frictional=0.2,userList=userList)
    sys.exit(app.exec_())
    
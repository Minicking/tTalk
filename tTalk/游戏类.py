import sys,os
from PyQt5.QtWidgets import QWidget, QApplication,QTextEdit
from PyQt5.QtGui import QPainter, QColor, QFont,QPen
from PyQt5.QtCore import Qt,QBasicTimer,QUrl
from PyQt5.QtMultimedia import QSound,QSoundEffect
from gameClass import velocity,Ball,FixedRoep,Impact,Position
import random,math,time
from threading import Thread
class GameBoard(QWidget):
    def __init__(self,tt,size,board,playRate,g,frictional):
        super().__init__()
        # self.user.setAttr(range=20)
        self.type=tt
        self.size=size
        self.board=board
        self.playRate=playRate
        self.g=g
        self.frictional=frictional
        self.mainTimer=QBasicTimer()
        self.objPool=[]
        self.sceneObjPool=[]
        # self.socreBoard.move(100,100)
        self.initUI()
        self.player=QSoundEffect()
        # print(dir(self.player))
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
        self.mainTimer.start(1,self)
    # def addObject(self,obj):
    def addObject(self,obj):
        if type(obj)==FixedRoep:
            self.sceneObjPool.append(obj)
            self.objPool.append(obj.obj)
            obj.obj.gameWorld=self
        else:
            self.objPool.append(obj)
        obj.gameWorld=self
    def flushScoreBoard(self):
        html="<p style='font-size:12px;text-align:center'>总球数(n):(%3d)</p>"%(len(self.objPool))
        html+="<p style='font-size:12px;text-align:center'>帧数(fps):(%3d)</p>"%(self.zs)
        html+="<p style='font-size:12px;text-align:center'>重力加速度(g):(%.1f)</p>"%(self.g)
        html+="<p style='font-size:12px;text-align:center'>摩擦系数(μ):(%.1f)</p>"%(self.frictional)
        fff=0.0
        for i in self.objPool:
            fff+=i.getEnergy()
        html+="<p style='font-size:12px;text-align:center'>系统内的总能量(q):(%.1f)</p>"%(fff)
        self.socreBoard.setHtml(html)
    def playImpactMusic(self):
        self.player.setSource(QUrl.fromLocalFile('source/music/impact.wav'))
        self.player.setLoopCount(1)
        self.player.setVolume(0.1)
        self.player.play()
    def objPoolImpact(self):
        # tt=False
        for i in self.objPool:
            for j in self.objPool:
                if i is not j:
                    if i.impactCheck(j):
                        # thr=Thread(target=self.playImpactMusic,args=())
                        # thr.setDaemon(True)
                        # thr.start()
                        Impact(i,j)

                        # tt=True
        # if tt:
        #     self.mainTimer.stop()
        #     time.sleep(1)
        #     self.mainTimer.start(10,self)
        #     tt=False
    def timerEvent(self,e):
        nowtime=time.time()
        jg=(nowtime-self.ztime)
        self.zs=1//jg
        self.ztime=nowtime
        for i in self.objPool:
            i.physicalCalculation(dtime=jg)
            i.checkPosition()
        self.objPoolImpact()
        for i in self.sceneObjPool:
            i.checkPosition()
        self.flushScoreBoard()
        self.repaint()
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawBoard(event,qp)
        qp.end()
    def drawBoard(self, event, qp):
        pen=QPen(QColor(0,0,0),1,Qt.SolidLine)
        qp.setPen(pen)
        qp.drawRect(self.board[2],self.board[0],self.size[0],self.size[1])
        for i in self.objPool:
            i.draw(qp)
        for i in self.sceneObjPool:
            i.draw(qp)
    
    def keyPressEvent(self,event):
        pass
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            x,y=event.x()-self.board[2],event.y()-self.board[0]
            
            if x>0 and x<self.size[0] and y>0 and y<self.size[1]:
                self.clickPosition=Position(x,y) 
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.LeftButton:
            x=event.x()-self.board[2]
            y=event.y()-self.board[0]
            if x>0 and x<self.size[0] and y>0 and y<self.size[1]:
                np=Position(x,y)
                nv=velocity(self.clickPosition.x-x,self.clickPosition.y-y)*5
                print(nv.getValue())
                self.addObject(Ball(10,nv,name='b',position=Position(self.clickPosition.x,self.clickPosition.y),mass=10))
def ObjectInit(ex):
    pass
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #tt:vertical plane
    ex = GameBoard(tt='vertical',size=(400,800),board=(25,25,25,25),playRate=0.2,g=600,frictional=0.1)
    ObjectInit(ex)
    sys.exit(app.exec_())
    
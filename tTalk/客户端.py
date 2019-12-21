import sys
import time
import threading
import socket
import json
import os
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QMainWindow,QGridLayout,QTextEdit,QLineEdit,QWidget, QMessageBox, QApplication,QLabel,QPushButton,QHBoxLayout,QVBoxLayout
from PyQt5.QtCore import Qt,QTimer,QObject,pyqtSignal
from ClientClass import *
class memberSignal(QObject):
	sendSignal=pyqtSignal()
class program(QMainWindow):
	def __init__(self):
		super().__init__()
		self.dirlist={
		"document":"C:"+os.environ.get("HOMEPATH")+r"\Documents\tTalk"
		}
		# self.targetAddr="127.0.0.1"
		self.targetAddr="112.124.13.95"
		self.initUI()  
		self.loginTimer=QTimer(self)
		self.loginTimer.setSingleShot(True)

		self.loginTimer.timeout.connect(self.openLoginDia)

		self.loginTimer.start(1)
	def initUI(self):               
	    self.bt_send=QPushButton("发送",self)
	    self.edit_input=myEdit(self)
	    self.text_display=QTextEdit(self)
	    self.member_list=QTextEdit(self)
	    self.member_label=QLabel("在线成员",self)

	    self.edit_input.resize(400,100)
	    self.edit_input.move(25,200)

	    self.text_display.resize(400,200)
	    self.text_display.setFocusPolicy(Qt.NoFocus) 
	    self.text_display.move(25,0)

	    self.member_label.move(435,0)
	    self.member_label.resize(100,30)

	    self.member_list.resize(100,200)
	    self.member_list.move(435,30)
	    self.member_list.setFocusPolicy(Qt.NoFocus) 

	    self.bt_send.resize(75,30)
	    self.bt_send.move(350,300)
	    self.setGeometry(0, 0, 550, 350)        
	    self.setWindowTitle('聊天室')   
	def openLoginDia(self):
		acc,pas=loginDialog.getResult(self)
		if acc!=None and pas!=None:
			self.account=acc
			self.password=pas
			self.show()
			self.initSocket(acc,pas)
		else:
			self.close()
	def connectServer(self):
		if "socket" in dir(self):
			self.socket.close()
		self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			self.socket.connect((self.targetAddr,8000))
		except ConnectionRefusedError as e:
			return False
		else:
			return True
	def initMainEvent(self):
		self.bt_send.clicked.connect(self.buttonCLicked)
		self.memberFlushSingle=memberSignal()
		self.memberFlushSingle.sendSignal.connect(self.flushMemberList)
	def initSocket(self,account,password):
		if self.connectServer():
			self.addText("已连接上服务器！")
			self.addText("正在进行用户验证...")
			self.acceptMesTask=threading.Thread(target=self.listenTask,args=())
			self.acceptMesTask.setDaemon(True)
			self.acceptMesTask.start()
			data=json.dumps({"type":0,"account":self.account,"password":self.password})
			try:
				self.socket.send(data.encode("utf-8"))
			except ConnectionResetError as e:
				self.addText("与服务器的连接已中断！")
				self.addText("无法进行用户验证！请确认网络状态再重新登录。")
			else:
				self.edit_input.clear()
		else:
			self.addText("无法连接服务器！")
			self.addText("无法进行用户验证！请确认网络状态再重新登录。")
			# reSocket=threading.Thread(target=self.resocket,args=())
			# reSocket.setDaemon(True)
			# reSocket.start()
	def flushMemberList(self):
		self.member_list.clear()
		for i in self.memberList:
			self.member_list.append(i)
	def addText(self,text):
		self.text_display.append(text)
	def sendMessage(self,mes):
		try:
			self.socket.send(json.dumps(mes.getMessage()).encode("utf-8"))
		except ConnectionResetError as e:
			return False
		else:
			return True
	def talk(self):
		data=self.edit_input.toPlainText()
		# data={"type":1,"text":data,"token":self.token}
		mes=message(clientMessageType.talk,text=data,token=self.token)
		if self.sendMessage(mes):
			self.edit_input.clear()
		else:
			self.addText("与聊天室的连接已经中断,无法发送消息...")
	def closeEvent(self,event):
		pass
	def keyPressEvent(self,e):
		if e.key()==Qt.Key_Escape:
			self.close()
	def buttonCLicked(self):
		sender=self.sender()
		self.talk()
	def resocket(self):
		while not self.connectServer():
			self.addText("自动重连：无法连接服务器...")
			time.sleep(1)
		self.addText("自动重连：服务器重连成功！")
		self.acceptMesTask=threading.Thread(target=self.listenTask,args=())
		self.acceptMesTask.setDaemon(True)
		self.acceptMesTask.start()
		print("监听socket线程重启成功")
	def listenTask(self):
		try:
			print("等待登录确认的发送：")
			data = self.socket.recv(1024).decode("utf-8")#监听首次开启，等待登录信息的发送
		except Exception as e:
			print("登录确认信息获取错误，连接中断！")
		else:
			data=json.loads(data)
			print("接收到的登录确认消息:",data,type(data))
			if data['type']==serverMessageType.loginConfirm:
				if data['confirm']==1:
					self.addText("登录成功！")
					self.token=data['token']
					self.memberList=data['memberList']
					self.initMainEvent()
					self.memberFlushSingle.sendSignal.emit()
					confirm=True
					print("登录验证成功，开启监听循环")
				else:
					self.addText("登录失败!账号或密码错误.请退出客户端...")
					confirm=False
					print("登录验证失败，连接中断")
			else:
				self.socket.close()
				print("消息不合法，连接强制中断(期望接收到的消息类别为  登录验证消息0，实际接收到的消息为%d)"%(data['type']))
				return 
		while confirm:
			try:
				acceptData=self.socket.recv(1024)
			except ConnectionResetError as e:
				self.addText("与聊天室的连接已中断！")
				self.socket.close()
				# reSocket=threading.Thread(target=self.resocket,args=())
				# reSocket.setDaemon(True)
				# reSocket.start()
				# print("开启重启socket线程")
				break
			else:
				# print("接收消息：",acceptData,type(acceptData))
				try:
					data=json.loads(acceptData.decode("utf-8"))
				except json.decoder.JSONDecodeError as e:
					self.addText("服务器已关闭！连接中断！")
					self.socket.close()
					# reSocket=threading.Thread(target=self.resocket,args=())
					# reSocket.setDaemon(True)
					# reSocket.start()
					# print("开启重启socket线程")
				else:
					print("接收到从服务器发来的数据：",data,type(data))
					if data['type']==serverMessageType.broadcast:
						s="[%s]%s:%s"%(data['time'],data['name'],data['text'])
						if not os.path.exists(self.dirlist['document']):
							os.mkdir(self.dirlist['document'])
						else:
							with open(self.dirlist['document']+r"\chartRecord.cr","a") as f:
							    f.write(s+"\n")
						self.addText(s)
					elif data['type']==serverMessageType.enter:
						self.memberList.append(data['name'])
						self.memberFlushSingle.sendSignal.emit()
						self.addText("<p style='color:red'>[%s]%s进入了聊天室</p>"%(data['time'],data['name']))
					elif data['type']==serverMessageType.exit:
						self.memberList.remove(data['name'])
						self.memberFlushSingle.sendSignal.emit()
						self.addText("<p style='color:#888'>[%s]%s离开了聊天室</p>"%(data['time'],data['name']))
					else:
						print("消息不合法，连接强制中断(期望接收到的消息类别为  广播消息1或者2，实际接收到的消息为%d)"%(data['type']))
# if __name__ == '__main__':
app = QApplication(sys.argv)
ex = program()
sys.exit(app.exec_())
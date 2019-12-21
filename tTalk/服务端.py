import  socket
import threading
import time
import json
import pymysql
from ServerClass import *
class Server:
	def __init__(self):
		print("初始化:初始化服务器....")
		self.serverSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.serverSocket.bind(("0.0.0.0",8000))
		print("初始化:服务器端口设定...")
		self.serverListener=threading.Thread(target=self.serverListener,args=())
		print("初始化:初始化监听线程...")
		self.db=pymysql.connect("localhost","root","123456","tTalk")
		print("初始化:数据库开启...")
		self.clientList=[]
		print("初始化:初始化客户端池...")
	def start(self):
		self.serverSocket.listen()
		print("初始化:打开服务器监听...")
		self.serverListener.start()
		print("初始化:服务器开启完成！!!")
	def serverListener(self):
		'''
			服务器监听线程，用来监听客户端发起的连接请求
		'''
		while True:
		    sock, addr = self.serverSocket.accept()     #接受不同client 端的sock .
		    print("来自%s的用户与服务器进行了连接！"%(str(addr)))
		    client_thread=threading.Thread(target=self.clientListener,args=(sock,addr))  #把sock 加入线程内
		    client_thread.start()  #启动线程
	def sendMessage(self,mes,sock):
		sock.send(json.dumps(mes.getMessage()).encode("utf-8"))
	def Broadcast(self,mes,ignore=None):
		'''
			广播方法，用来广播用户发送的聊天消息给所有已连接的socket连接。
		'''
		print("广播消息:",mes)
		cursor=self.db.cursor()
		if mes.type==1:
			try:
				cursor.execute("insert into chatRecord(cr_text,cr_Date,user_id) values(%s,%s,%s)",(mes.text,mes.time,mes.user_id))
			except Exception as e:
				print("执行插入出错：",str(cursor))
				print(e)
			else:
				self.db.commit()
		for i in self.clientList:
			if ignore!=i:
				self.sendMessage(mes,i.sock)
	def clientListener(self,sock,addr):
	# '''
	# 	客户端监听线程，每一个连接到服务器的客户端单独开启一个监听线程，用来监听客户端发送过来的所有信息，包括各类请求信息和聊天信息。
	# '''
		try:
			print("等待登录信息的发送：")
			data = sock.recv(1024).decode("utf-8")#监听首次开启，等待登录信息的发送
		except Exception as e:
			print("登录信息获取错误，连接中断！")
			sock.close()
		else:
			data=json.loads(data)
			data['loginIP']=addr
			nUser=self.dataProcesser(data=data,sock=sock)
		if nUser and nUser.confirm:
			print("登录信息验证成功，开始消息监听循环")
			mesEnter=message(serverMessageType.enter,name=nUser.name)
			self.Broadcast(mesEnter,nUser)
		else:
			print("登录信息验证失败，sock中断")
			sock.close()
		while nUser.confirm:	
			try:
			    data = sock.recv(1024).decode("utf-8")
			except Exception as e:
				print('%s的连接已中断！'%(str(addr)))
				sock.close()
				self.clientList.remove(nUser)
				print("当前服务器中已连接的用户：",self.clientList)
				mesExit=message(serverMessageType.exit,name=nUser.name)
				self.Broadcast(mesExit)
				break
			else:
				data=json.loads(data)
				print("来自客户端的消息:",data,type(data))
				if data['token']==nUser.token:
					print("token一致",nUser.token)
				else:
					print("token不一致",nUser.token,data['token'])
				data['text']=data['text'].replace('\n',"").replace(" ","")
				self.dataProcesser(data=data,user=nUser)
	def dataProcesser(self,data,sock=None,user=None):
		'''
			信息处理方法，用来处理客户端发送过来的信息，根据不同信息做出不同的处理
			type=0：信息属于登录请求信息，发送过来的数据{"type":0,"account":账号,"password":密码}
			        返回数据为登录验证结果信息{"type":0,"confirm":1或者0,"token":"xxxxxx"}
			type=1:信息属于聊天消息，发送过来的数据{"type":1,"text":聊天信息,"token":身份令牌}
		'''
		if data["type"]==0:
			nUser=User()
			nUser.loginConfirm(self.db,data["account"],data["password"])
			if nUser.confirm:
				nowTime=time.localtime()
				nowTime="%s-%s-%s %s:%s:%s"%(nowTime.tm_year,nowTime.tm_mon,nowTime.tm_mday,nowTime.tm_hour,nowTime.tm_min,nowTime.tm_sec)
				nUser.lastIP="%s:%d"%(data['loginIP'][0],data['loginIP'][1])
				nUser.sock=sock
				nUser.lastDate=nowTime
				nUser.createToken()
				nUser.infoSave(self.db)
				self.clientList.append(nUser)
				print("当前服务器中已连接的用户：",self.clientList)
				# rdata={"type":0,"confirm":1,"token":"xxxxxx"}
				memberList=[]
				for i in self.clientList:
					memberList.append(i.name)
				mes=message(serverMessageType.loginConfirm,confirm=1,memberList=memberList,token=nUser.token)
				self.sendMessage(mes,sock)
			else:
				# rdata={"type":0,"confirm":0}
				mes=message(serverMessageType.loginConfirm,confirm=0,memberList=None)
				self.sendMessage(mes,sock)
			return nUser
		if data['type']==1:
			# rdata={"type":1,"text":data['text'],'name':user.name,'user_id':user.id}
			# self.sendMessage(rdata,sock)
			mes=message(serverMessageType.broadcast,text=data['text'],name=user.name,user_id=user.id)
			user.messageCount+=1
			user.infoSave(self.db)
			self.Broadcast(mes)
			return
	
if __name__ == '__main__':
	server=Server()
	server.start()
	

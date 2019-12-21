import time
class serverMessageType:
	loginConfirm=0
	broadcast=1
	enter=2
	exit=3
class message():
	'''
type字段的含义:0 服务端发出确认登录信息 {"type":0,"confirm":1或者0,"token":"xxxxxx"} 1为验证成功，0为验证失败,token为验证成功后发给客户端的令牌
             :1 通过广播发出的普通聊天信息 {"type":1,"text":data['text'],'name':user.name,'user_id':user.id}
             :2 新的用户进入聊天室的系统提示{"type":2,'name':user.name}
             :3 用户离开聊天室的系统提示{"type":3,'name':user.name}
	'''
	def __init__(self,mType,**args):
		nowTime=time.localtime()
		nowTime="%s-%s-%s %s:%s:%s"%(nowTime.tm_year,nowTime.tm_mon,nowTime.tm_mday,nowTime.tm_hour,nowTime.tm_min,nowTime.tm_sec)
		self.type=mType
		self.time=nowTime
		if mType==serverMessageType.loginConfirm:
			self.confirm=args['confirm']
			self.memberList=args['memberList']
			if 'token' in args:
				self.token=args['token']
		elif mType==serverMessageType.broadcast:
			self.text=args['text']
			self.name=args['name']
			self.user_id=args['user_id']
		elif mType==serverMessageType.enter or mType==serverMessageType.exit:
			self.name=args['name']
	def getMessage(self):
		s={'type':self.type,'time':self.time}
		if self.type==serverMessageType.loginConfirm:
			s['confirm']=self.confirm
			s['memberList']=self.memberList
			if 'token' in dir(self):
				s['token']=self.token
		elif self.type==serverMessageType.broadcast:
			s['text']=self.text
			s['name']=self.name
			s['user_id']=self.user_id
		elif self.type==serverMessageType.enter or self.type==serverMessageType.exit:
			s['name']=self.name
		return s
	def __str__(self):
		return str(self.getMessage())
class User:
	def __init__(self,**kwargs):
		if 'id' in kwargs:
			self.id=int(kwargs['id'])
			self.name=kwargs['name']
			self.account=kwargs['account']
			self.password=kwargs['password']
			self.regDate=kwargs['regDate']
			self.lastDate=kwargs['lastDate']
			self.messageCount=int(kwargs['messageCount'])
			self.lastIP=kwargs['lastIP']
			self.messageStyle=kwargs['messageStyle']
		self.confirm=False
		self.sock=None
	def loginConfirm(self,db,account,password):
		cursor=db.cursor()
		cursor.execute("select * from user where user_account=%s",(account,))
		r=cursor.fetchall()
		print("r=",r)
		if r==():
			self.confirm=False
		else:		
			self.id=int(r[0][0])
			self.name=r[0][1]
			self.account=r[0][2]
			self.password=r[0][3]
			self.regDate=r[0][4]
			self.lastDate=r[0][5]
			self.messageCount=int(r[0][6])
			self.lastIP=r[0][7]
			self.messageStyle=r[0][8]
			self.confirm=password==self.password
			print("self.confirm:",self.confirm)
	def infoSave(self,db):
		cursor=db.cursor()
		cursor.execute("update user set user_messageCount=%s,user_lastDate=%s,user_lastIP=%s where user_id=%s",(str(self.messageCount),str(self.lastDate),str(self.lastIP),str(self.id)))
		db.commit()
	def createToken(self):
		self.token=self.account+self.password
	def __str__(self):
		s=''
		s+="ID[%d]\n"%(self.id)
		s+="名称[%s]\n"%(self.name)
		s+="账号[%s]\n"%(self.account)
		s+="密码[%s]\n"%(self.password)
		s+="注册时间[%s]\n"%(self.regDate)
		s+="最后登录时间[%s]\n"%(self.lastDate)
		s+="发送消息数量[%s]\n"%(self.messageCount)
		s+="最后一次登录IP[%s]\n"%(str(self.lastIP))
		s+="消息样式[%d]\n"%(str(self.messageStyle))
		return s
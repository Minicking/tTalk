class messageType:
	loginConfirm=1
	broadcast=2
	enter=3
	exit=4
class message():
	'''
type字段的含义:0 服务端发出确认登录信息 {"type":0,"confirm":1或者0,"token":"xxxxxx"} 1为验证成功，0为验证失败,token为验证成功后发给客户端的令牌
             :1 通过广播发出的普通聊天信息 {"type":1,"text":data['text'],'name':user.name,'user_id':user.id}
             :2 新的用户进入聊天室的系统提示{"type":2,'name':user.name}
             :3 用户离开聊天室的系统提示{"type":3,'name':user.name}
	'''
	def __init__(self,mType,**args):
		self.type=mType
		if mType==messageType.loginConfirm:
			self.confirm=args['confirm']
			self.token=args['token']
		elif mType==messageType.broadcast:
			self.text=args['text']
			self.name=args['name']
			self.user_id=args['user_id']
		elif mType==messageType.enter or mType==messageType.exit:
			self.name=args['name']
	def getMessage(self):
		s={'type':self.type}
		if self.type==messageType.loginConfirm:
			s['confirm']=self.confirm
			s['token']=self.token
		elif self.type==messageType.broadcast:
			s['text']=self.text
			s['name']=self.name
			s['user_id']=self.user_id
		elif self.type==messageType.enter or self.type==messageType.exit:
			s['name']=self.name
		return s
	def __str__(self):
		return str(self.getMessage())
x=message(messageType.loginConfirm,confirm=1,token='abcd')
print(x)
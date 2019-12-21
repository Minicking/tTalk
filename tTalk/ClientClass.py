from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QMainWindow,QGridLayout,QTextEdit,QLineEdit,QWidget, QMessageBox, QApplication,QLabel,QPushButton,QHBoxLayout,QVBoxLayout
from PyQt5.QtCore import Qt,QTimer
import time
class loginDialog(QDialog):
	def __init__(self,parent=None):
	    super(loginDialog, self).__init__(parent)
	    print("parent2:",parent)
	    self.parent=parent
	    self.resize(200,200)
	    self.setWindowTitle("登录")
	    labelAccount=QLabel("账号",self)
	    labelPassword=QLabel("密码",self)
	    self.account=QLineEdit(self)
	    self.password=QLineEdit(self)
	    labelAccount.move(10,10)
	    labelPassword.move(10,60)
	    self.account.move(50,10)
	    self.password.move(50,60)
	    self.loginButton=QPushButton("登录",self)
	    self.cancelButton=QPushButton("退出",self)
	    self.loginButton.move(10,100)
	    self.cancelButton.move(100,100)
	    self.loginButton.clicked.connect(self.clickLogin)
	    self.cancelButton.clicked.connect(self.clickCancel)
	def clickLogin(self):
		print("点击登录")
		account=self.account.text()
		password=self.password.text()
		self.close()
	def clickCancel(self):
		print("点击退出")
		self.account.setText("\n\n")
		self.close()
	@staticmethod
	def getResult(parent):
		print("parent1:",parent)
		dialog=loginDialog(parent)
		result=dialog.exec_()
		print(type(result))
		# print(result)
		account=dialog.account.text()
		password=dialog.password.text()
		if account=="\n\n":
			return(None,None)
		return (account,password)
class myEdit(QTextEdit):
	def __init__(self,parent):
		super().__init__(parent)
		self.parent = parent
	def keyPressEvent(self,event):
		QTextEdit.keyPressEvent(self,event)
		print('press',event)
		if event.key() == Qt.Key_Return: #如果是Enter 按钮
			self.parent.talk()
class clientMessageType:
	loginConfirm=0
	talk=1
class serverMessageType:
	loginConfirm=0
	broadcast=1
	enter=2
	exit=3
class message():
	'''
type字段的含义:0 客户端发出登录请求 {"type":0,"account":"tzf","password":"123456"}
              1 客户端发送聊天信息 {"type":1,"text":"哈哈哈","token":"xxxxx"}
	'''
	def __init__(self,mType,**args):
		self.type=mType
		if mType==clientMessageType.loginConfirm:
			self.confirm=args['confirm']
			self.token=args['token']
		elif mType==clientMessageType.talk:
			self.text=args['text']
			self.token=args['token']
	def getMessage(self):
		s={'type':self.type}
		if self.type==clientMessageType.loginConfirm:
			s['confirm']=self.confirm
			s['token']=self.token
		elif self.type==clientMessageType.talk:
			s['text']=self.text
			s['token']=self.token
		return s
	def __str__(self):
		return str(self.getMessage())
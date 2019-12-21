from pynput import mouse,keyboard
import threading
import json
import time
DIR={}
nowtime=time.localtime()
filename="%d_%d_%d"%(nowtime.tm_year,nowtime.tm_mon,nowtime.tm_mday)
# print(filename)
def keyPress(key):
    key=str(key)
    if key in DIR:
        DIR[key]+=1
    else:
        DIR[key]=1
    with open("%s.txt"%(filename),'w') as f:
        for i in DIR:
            f.write("%s:%d\n"%(i,DIR[i]))
def keyboardListener():
    with keyboard.Listener(on_press=keyPress,on_release=None) as listener:
        listener.join()
if __name__ == '__main__':
    a=threading.Thread(target=keyboardListener,args=())
    a.start()

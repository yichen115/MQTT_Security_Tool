from paho.mqtt import client as mqtt_client
import uuid
from pyfiglet import Figlet
import os,argparse,sys,time,json

############### params #################
broker = "192.168.127.137"
port = 1883
userfile = "./user.txt"
passfile = "./pass.txt"
########################################

usernames = []
passwords = []
output = {"unauth":False,"weakpass":False,"username":"","password":""}

def on_connect_unauth(client, userdata, flags, rc):
    if rc == 0:
        output["unauth"] = True
        print("[√]发现匿名登陆!!")
        client.disconnect()
        client.loop_stop()
        return True
    else:
        client.disconnect()
        client.loop_stop()
        return True

def on_connect_brute(client, userdata, flags, rc):
    if rc == 0:
        output["weakpass"] = True
        print("[√]暴力破解连接成功！")
        client.disconnect()
        client.loop_stop()
        return True
    else:
        client.disconnect()
        client.loop_stop()
        return True

def unauthaccess(broker, port):
    client = mqtt_client.Client(str(uuid.uuid4()))
    client.on_connect = on_connect_unauth
    client.connect(broker, port)
    client.loop_start()
    time.sleep(0.5)

def brute(broker, port, userfile, passfile, usernames, passwords):
    if((os.path.exists(userfile)!= True) or (os.path.exists(passfile)!= True)):
        print("[X]字典路径不存在！！")
        return False

    user_file = open(userfile,'r')
    for user_name in user_file:
        usernames.append(user_name[:-1])
    pass_file = open(passfile,'r')
    for pass_name in pass_file:
        passwords.append(pass_name[:-1])
    
    for user in usernames:
        for passwd in passwords:
            client = mqtt_client.Client(str(uuid.uuid4()))
            client.on_connect = on_connect_brute
            print("[+]正在测试: username:"+user+" "+"password:"+passwd)
            client.username_pw_set(username=user, password=passwd)
            client.connect(broker, port)
            time.sleep(0.5)
            client.loop_start()
            if output["weakpass"] == True:
                output["username"] = user
                output["password"] = passwd
                return 

f = Figlet(font="slant", width=100)
print(f.renderText("MQTT Security Tool"))

print("[+]正在测试匿名登陆...")
unauthaccess(broker, port)
if (output["unauth"] == False):
    print("[X]不存在匿名登陆，正在暴力破解用户名和密码...")
    brute(broker, port, userfile, passfile, usernames, passwords)
data = json.dumps({'result':output})
print(data)
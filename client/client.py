import socket
import json
import server_const


s = socket.socket()         # 创建 socket 对象
host = '127.0.0.1'          # 获取本地主机名
port = 8080                 # 设置端口号

data = {"token":server_const.__TOKN__,
    "name":"DiannaoJun",
    "pass":server_const.__TOKN__}

s.connect((host, port))
getd = s.recv(1024).decode('utf-8')
if getd!="HELO":
    print("con error!");
    s.close()
    exit()
s.send(json.dumps(data).encode('utf-8'))
getd = s.recv(1024).decode('utf-8')
if getd!="HELO":
    print("con error!");
    s.close()
    exit()
data = {"opt":"send","to":1,"txt":"HELLO WORLD!"}
s.send(json.dumps(data).encode('utf-8'))
data = {"opt":"list"}
s.send(json.dumps(data).encode('utf-8'))

getd = s.recv(1024).decode('utf-8')
print(getd);

s.close()
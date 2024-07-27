# -*- coding: UTF-8 -*-
import socket
import os, sys
import sqlite3
import json
import server_const
import threading

bool_newdb = not os.path.isfile(server_const.__DBPT__)

con = sqlite3.connect(server_const.__DBPT__)

def obje(x,y):
    try:
        if x==y: return True
        else: return False
    except: return False
def loaduser(u,p):
    con = sqlite3.connect(server_const.__DBPT__)
    c = con.cursor()
    result = c.execute("SELECT * FROM USR WHERE NAME = ?;", tuple([u]))
    for row in result:
        if row[2].lower() == p.lower():
            ret = {}
            ret["id"]=row[0]
            ret["name"]=row[1]
            ret["addr"]=row[3]
            ret["level"]=row[4]
            return ret
    return None
def sendmsg(frm,to,dat):
    con = sqlite3.connect(server_const.__DBPT__)
    try:
        c = con.cursor()
        arg = (frm,int(to),str(dat))
        c.execute("INSERT INTO MSG (FRM_ID, TO_ID, SDTM, DATA) VALUES (?,?,strftime('%Y-%m-%d %H:%M:%f','now'),?);",arg)
        con.commit()
    except:
        pass
def getmsg(cfg,cnt=10):
    con = sqlite3.connect(server_const.__DBPT__)
    c = con.cursor()
    ret = []
    result = []
    result = c.execute("SELECT * FROM MSG;")
    for row in result:
        bf = {}
        if cfg["level"]<=1 or row[1] == cfg["id"] or row[2] == cfg["id"]:
            bf["id"] = row[0]
            bf["frm"] = row[1]
            bf["to"] = row[2]
            bf["tm"] = row[3]
            bf["dat"] = row[4]
            ret.append(bf)
    if len(ret) > cnt:
        ret = ret[-cnt:]
    return ret
class ServerThread:
    def __init__(self, ipaddr, port, num):
        self.ipaddr = ipaddr
        self.port = port
        self.num = num
        self.lq = [True for _ in range(self.num)]
        self.cfg = [None for _ in range(self.num)]
    def server_link(self, conn, addr, cid):
        conn.send("HELO".encode())
        print(f"link  {cid}");
        while True:
            self.cfg[cid]=None
            try:
                data = conn.recv(1024)
                if data:
                    text = json.loads(data.decode('utf-8'))
                    print(text)
                    if type(text) == str:
                        print(f"Bad connection from {addr} : Format Error!");
                        conn.close()
                        break
                    if not obje(text.get("token",None),server_const.__TOKN__):
                        print(f"Bad connection from {addr} : Token Error!");
                        conn.close()
                        break
                    usr = loaduser(text["name"], text["pass"])
                    if type(usr) == type(None):
                        print(f"Bad connection from {addr} : User Error!");
                        conn.close()
                        break
                    self.cfg[cid]=usr
                    conn.send("HELO".encode())
            except Exception as ex:
                print(f"Bad connection from {addr} : Unknown Error! {ex}");
                conn.close()
            else:
                print(f"Success connect from {addr}")
            if self.cfg[cid]==None:
                return
            break
        while True:
            try:
                data=conn.recv(1024)
                if data:
                    text = json.loads(data.decode('utf-8'))
                    if type(text) == str:
                        continue
                    cmd = text.get("opt","")
                    print("CMD:",cmd)
                    match(cmd):
                        case "send":
                            sendmsg(self.cfg[cid]["id"],text.get("to",0),text.get("txt",""))
                        case "list":
                            ret = getmsg(self.cfg[cid])
                            ret = json.dumps(ret)
                            ret = ret.encode('utf-8')
                            conn.sendall(ret)
                        case _:
                            pass
                    print("OK")
            except Exception as ex:
            	print(ex)
        self.cfg[cid]=None

    def server_start(self):
        s_pro = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_pro.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_pro.bind((self.ipaddr, self.port))
        s_pro.listen(self.num)
        print('Waiting link...')
        while True:
            cid = 0
            while cid < self.num:
                if self.lq[cid]:
                    self.lq[cid]=False
                    break
                cid+=1
            if cid < self.num:
                conn, addr = s_pro.accept()
                p = threading.Thread(target=self.server_link, args=(conn, addr, cid))
                p.start()
                self.lq[cid]=True

def PM__init__ ():
    c = con.cursor()
    c.execute("DROP TABLE IF EXISTS MSG")
    c.execute("""CREATE TABLE MSG
        ( MSG_ID  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        FRM_ID    INTEGER NOT NULL,
        TO_ID     INTEGER NOT NULL,
        SDTM      TEXT NOT NULL,
        DATA      TEXT);""")
    c.execute("DROP TABLE IF EXISTS USR")
    c.execute("""CREATE TABLE USR
        ( ID      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        NAME      TEXT NOT NULL,
        PASS      TEXT NOT NULL,
        ADDR      TEXT,
        PRIORITY  INTEGER NOT NULL);""")
    arg = ('DiannaoJun', server_const.__TOKN__, 'aheiwuchang@163.com', 0) 
    c.execute("INSERT INTO USR (NAME, PASS, ADDR, PRIORITY) VALUES (?,?,?,?);", arg)
    con.commit()

if __name__ == "__main__":
    if bool_newdb:
        PM__init__()
    s = ServerThread('127.0.0.1',8080, server_const.__MX_LSTN__)
    s.server_start()
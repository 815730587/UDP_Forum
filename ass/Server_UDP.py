import time
from socket import *
import threading
import sys
import queue
import json
from itertools import islice
import os


def packet(username, command, code, password='', step=0, message='', message_dict=None, thread_title='', file_name=''):
    if message_dict is None:
        message_dict = {}
    packet_message = {
        "username": username,
        "password": password,
        "step": step,
        "command": command,
        "code": code,
        "message": message,
        "thread_title": thread_title,
        "file_name": file_name,
        "message_dict":message_dict
    }
    return json.dumps(packet_message).encode()


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.state = 0

    def login(self, password):
        if password == self.password:
            self.state = 1
            return 3
        else:
            return 4

    def log_out(self, username):
        if self.username == username:
            self.state = 0


class UserManager:
    def __init__(self, file="credentials.txt"):
        self.file = file
        self.user_dict = {}
        with open(file, "r") as fp:
            for line in fp.readlines():
                un, pw = line.split()
                user = User(un, pw)
                self.user_dict[un] = user

    def wirtefile(self):
        with open(self.file, "w+") as txt:
            for user in self.user_dict:
                user_info = self.user_dict[user]
                line_data = "{} {}\n".format(user_info.username, user_info.password)
                txt.write(line_data)

    def login_prev(self, username):

        if username not in self.user_dict:
            return 1
        if self.user_dict[username].state == 1:
            return 2
        return 0

    def login(selfs, username, password):
        user = selfs.user_dict[username]
        return user.login(password)


class Threa:
    def __init__(self, title, username):
        self.title = title
        self.username = username
        with open(self.title, "w+") as fp:
            fp.write(self.username + "\n")


class Th_Manager:
    def __init__(self):
        self.th_dict = {}

    def create_thread(self, title, username):
        if title in self.th_dict:
            return 1
        self.th_dict[title] = Threa(title, username)
        return 0


class file_trans:
    def __init__(self, username, threadtitle, filename):
        self.username = username
        self.filename = filename
        self.threadtitle = threadtitle


class file_trans_manage:
    def __init__(self):
        self.file_trans = {}

    def write_to_file(self, username, threadtitle, filename):
        with open(threadtitle, "a+") as th:
            th.writelines(username + " uploded " + filename + "\n")

    def create_transfile(self, username, threadtitle, filename):
        if username+threadtitle+filename in self.file_trans :
            return 1
        self.file_trans[username+threadtitle + filename] = file_trans(username, threadtitle, filename)
        self.write_to_file(username, threadtitle, filename)
        return 0


class Server:
    def __init__(self, port):
        self.port = port
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', self.port))
        self.client_info = {}
        self.client_queue = {}
        self.UserManager = UserManager()
        self.Th_M = Th_Manager()
        self.file_trans_ma = file_trans_manage()

    def TCP_filetrans(self, threadtitle, filename,username, address):
        file_trans_socket = socket(AF_INET, SOCK_STREAM)
        file_trans_socket.bind(('127.0.0.1', self.port))
        file_trans_socket.listen(10)
        file_username, file_useraddr = file_trans_socket.accept()
        with open(f"{username}_{threadtitle}_{filename}", "wb") as file:
            while True:
                data = file_username.recv(1024)
                if not data:
                    break
                file.write(data)
        file_username.close()
        file_trans_socket.close()

    def DWN_file(self, filename, address):
        dwn_file_socket = socket(AF_INET, SOCK_STREAM)
        dwn_file_socket.connect(('127.0.0.1', self.port))
        try:
            with open(filename, "rb") as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    dwn_file_socket.send(data)
            dwn_file_socket.close()
        except Exception:
            dwn_file_socket.close()
            return True


    def write_to_th(self, threadname, message):
        i = 0
        with open(threadname, "r") as th:
            for line in islice(th, 1, None):
                data = line.split()
                if data[0].isdigit():
                    i = int(data[0])
        with open(threadname, "a+") as th_w:
            th_w.writelines(str(i + 1) + " " + message + "\n")

    def delete_message(self, threadname, message):
        message_dic = {}
        i = 0

        with open(threadname, "r") as th:
            for line in th.readlines():
                message_dic[i] = line
                i += 1
        for x in range(1, i):
            data = message_dic[x].split()
            if data[0] == message:
                message_dic.pop(x)
        j = 1
        for n in range(1, i):
            if n != int(message):
                data, mes = message_dic[n].split(" ", 1)
                if data.isdigit():
                    message_dic[n] = str(j) + " " + mes
                    j += 1
        with open(threadname, "w") as th_w:
            for me in message_dic:
                if message_dic[me] != "":
                    th_w.write(message_dic[me])

    def User_rights(self, threadname, message, username):
        h_flag = 1
        if threadname in self.Th_M.th_dict:
            with open(threadname, "r") as th_weight:
                for line in islice(th_weight, 1, None):
                    data = line.split()
                    if data[0] == message:
                        h_flag = 0
                        break
                if h_flag == 1:
                    return 2
            th = open(threadname, "r")
            for line in islice(th, 1, None):
                data = line.split()
                if data[0] == message and data[1] == username:
                    th.close()
                    return 1
            return 0
        else:
            return 3


    def Edit_file(self, threadname, message, num):
        message_dic = {}
        i = 0
        with open(threadname, "r") as th:
            for line in th.readlines():
                message_dic[i] = line
                i += 1

        for n in range(1, i):
            data = message_dic[n].split()
            if data[0] == num:
                message_dic[n] = num + " " + message + "\n"
                break

        with open(threadname, "w+") as th_w:
            for n in range(0, i):
                th_w.write(message_dic[n])

    def server_c(self, addr):
        self.client_queue[addr] = queue.Queue()
        que = self.client_queue[addr]
        pu_flag = 0
        while True:
            data, addr = que.get()
            req = json.loads(data.decode())
            if req["command"] == "login" and req["step"] == 0 and req["right_username"]==1:
                if pu_flag == 0:
                    print("Client authenticating")
                username = req["username"]
                code = self.UserManager.login_prev(username)
                self.socket.sendto(packet(username,req["command"],code), addr)
            elif req["command"] == "login" and req["step"] == 1 and req["right_password"]==1:
                username = req["username"]
                password = req["password"]
                flag = self.UserManager.login_prev(username)
                if flag == 1:
                    self.UserManager.user_dict[username] = User(username, password)
                    self.UserManager.wirtefile()
                code = self.UserManager.login(username, password)
                if code == 3:
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" "+username + " successful login")
                self.socket.sendto(packet(username,req["command"],code,step=1), addr)
            elif req["command"] == "XIT" and req["step"] == 2:
                command = req["command"]
                username = req["username"]
                time_now=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                self.UserManager.user_dict[username].log_out(username)
                print(username + " exited")
                print("Waiting for clients")
                break
            elif req["command"] == "CRT" and req["step"] == 2:
                title = req["thread_title"]
                username = req["username"]
                command = req["command"]
                time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                code = self.Th_M.create_thread(title, username)
                self.socket.sendto(packet(username,req["command"],code,step=2), addr)
            elif req["command"] == "UPD" and req["step"] == 2:
                threanname = req["thread_title"]
                filename = req["file_name"]
                username = req["username"]
                command = req["command"]
                have_file=req["have_file"]
                time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                if threanname in self.Th_M.th_dict and have_file==0:
                    self.socket.sendto(packet(username, req["command"], code=0, step=2), addr)
                    if self.file_trans_ma.create_transfile(username, threanname, filename) == 0:
                        self.socket.sendto(packet(username, req["command"], code=0, step=2), addr)
                        self.TCP_filetrans(threanname, filename,username, addr)
                    else:
                        self.socket.sendto(packet(username, req["command"], code=1, step=2), addr)
                else:
                    if threanname not in self.Th_M.th_dict:
                        self.socket.sendto(packet(username, req["command"], code=2, step=2), addr)
                    elif have_file==1:
                        self.socket.sendto(packet(username, req["command"], code=3, step=2), addr)

            elif req["command"] == "MSG" and req["step"] == 2:
                title = req["thread_title"]
                message = req["message"]
                username = req["username"]
                command = req["command"]
                time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                if title in self.Th_M.th_dict:
                    data = username + " " + message
                    self.write_to_th(title, data)
                    code = 0
                else:
                    code = 1
                self.socket.sendto(packet(username, req["command"], code=code, step=2), addr)
            elif req["command"] == "DLT" and req["step"] == 2:
                title = req["thread_title"]
                message = req["message"]
                username = req["username"]
                command = req["command"]
                time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                rights_user=self.User_rights(title, message, username)
                if title in self.Th_M.th_dict and rights_user==1:
                    self.delete_message(title, message)
                    code = 0
                    self.socket.sendto(packet(username, req["command"], code=code, step=2), addr)
                else:
                    code = 0
                    if rights_user == 0:
                        code = 1
                    elif rights_user == 2:
                        code = 3
                    if title not in self.Th_M.th_dict:
                        code = 2
                    self.socket.sendto(packet(username, req["command"], code=code, step=2), addr)
            elif req["command"] == "EDT" and req["step"] == 2:
                title = req["thread_title"]
                message = req["message"]
                username = req["username"]
                command = req["command"]
                time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                index = req["index"]
                rights_user = self.User_rights(title,index, username)
                if title in self.Th_M.th_dict and rights_user==1:
                    data = username + " " + message
                    self.Edit_file(title, data, index)
                    code = 0
                    self.socket.sendto(packet(username, req["command"], code=code, step=2), addr)
                else:
                    code = 0
                    if rights_user == 0:
                        code = 1
                    elif rights_user == 2:
                        code = 3
                    if title not in self.Th_M.th_dict:
                        code = 2
                    self.socket.sendto(packet(username, req["command"], code=code, step=2), addr)
            elif req["command"] == "LST" and req["step"] == 2:
                username = req["username"]
                command = req["command"]
                time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                thread_dict = {}
                i = 0
                if self.Th_M.th_dict:
                    for user in self.Th_M.th_dict:
                        thread = self.Th_M.th_dict[user]
                        thread_dict[i] = thread.title
                        i += 1
                    code = 0
                    self.socket.sendto(packet(username, req["command"],message_dict=thread_dict, code=code, step=2), addr)
                else:
                    code = 1
                    self.socket.sendto(packet(username, req["command"], code=code, step=2), addr)

            elif req["command"] == "RDT" and req["step"] == 2:
                username = req["username"]
                thread_title = req["thread_title"]
                command = req["command"]
                time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                message_dict = {}
                if thread_title in self.Th_M.th_dict:
                    with open(thread_title, "r") as txt:
                        i = 0
                        for line in txt.readlines():
                            message_dict[i] = line
                            i += 1
                        message_dict.pop(0)
                    if message_dict:
                        code = 0
                    else:
                        code = 1
                    self.socket.sendto(packet(username, req["command"], message_dict=message_dict, code=code, step=2),
                                       addr)
                else:
                    code=2
                    self.socket.sendto(packet(username, req["command"], message_dict=message_dict, code=code, step=2), addr)

            elif req["command"] == "RMV" and req["step"] == 2:
                username = req["username"]
                thread_title = req["thread_title"]
                command = req["command"]
                time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                if thread_title in self.Th_M.th_dict:
                    thread = self.Th_M.th_dict[thread_title]
                    if thread.username == username:
                        self.Th_M.th_dict.pop(thread_title)
                        os.remove(thread_title)
                        code = 0
                    else:
                        code = 1
                else:
                    code=2
                self.socket.sendto(packet(username, req["command"], code=code, step=2), addr)

            elif req["command"] == "DWN" and req["step"] == 2:
                threadname = req["thread_title"]
                filename = req["file_name"]
                username = req["username"]
                command = req["command"]
                time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{time_now} {username} issued {command} command")
                code = 1
                with open(threadname, "r") as th:
                    for line in islice(th, 1, None):
                        data = line.split()
                        if not data[0].isdigit() and filename == data[2]:
                            code = 0
                            break

                if code == 0:
                    self.socket.sendto(packet(username, req["command"], code=code, step=2), addr)
                    self.DWN_file(f"{username}_{threadname}_{filename}", addr)
                else:
                    self.socket.sendto(packet(username, req["command"], code=code, step=2), addr)

            pu_flag += 1

    def run(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            if addr not in self.client_info:
                new_c_th = threading.Thread(target=self.server_c, args=(addr,))
                new_c_th.setDaemon(True)
                new_c_th.start()
                self.client_info[addr] = new_c_th
            self.client_queue[addr].put((data, addr))


print("Waiting for clients")
if __name__ == '__main__':
    port = int(sys.argv[1])
    cli = Server(port)
    cli.run()

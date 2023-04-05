import time
from socket import *
import threading
import sys
import queue
import json


def packet(username, command, password='', step=0, message='', thread_title='', file_name='', right_username=1,
           right_password=1, index='',have_file=0):
    packet_message = {
        "username": username,
        "password": password,
        "step": step,
        "command": command,
        "message": message,
        "thread_title": thread_title,
        "file_name": file_name,
        "index": index,
        "right_username": right_username,
        "right_password": right_password,
        "have_file":have_file
    }
    return json.dumps(packet_message).encode()


class Client:
    def __init__(self, port):
        self.port = port
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.username = ""
        self.user_stat = 0

    def tranfile_TCP(self, filename):
        trans_file_socket = socket(AF_INET, SOCK_STREAM)
        trans_file_socket.connect(('127.0.0.1', self.port))
        try:
            with open(filename, "rb") as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    trans_file_socket.send(data)
            trans_file_socket.close()
        except Exception:
            trans_file_socket.close()
            return True

    def DWN_file(self, filename):
        file_trans_socket = socket(AF_INET, SOCK_STREAM)
        file_trans_socket.bind(('127.0.0.1', self.port))
        file_trans_socket.listen(10)
        file_username, file_useraddr = file_trans_socket.accept()
        with open(f"download_{filename}", "wb") as file:
            while True:
                data = file_username.recv(1024)
                if not data:
                    break
                file.write(data)
        file_username.close()
        file_trans_socket.close()

    def Right_username_and_password(self, input_str):
        str_c = "(~!@#$%^&*_-+=`|\()[]:;" + '"' + "'" + "<>,.?/)"
        if " " not in input_str and input_str != '':
            for i in range(0, len(input_str)):
                if input_str[i] != " " and (
                        (input_str[i] in str_c) or input_str[i].isdigit() or input_str[i].isalpha()):
                    continue
                else:
                    return False
            return True
        else:
            return False

    def run(self):
        while True:
            if self.user_stat == 0:
                username = input("Enter username: ")
                if self.Right_username_and_password(username):
                    self.socket.sendto(packet(username, command="login"), ('127.0.0.1', self.port))
                    packet_data, addr = self.socket.recvfrom(1024)
                    res = json.loads(packet_data.decode())
                    if res["code"] == 0:
                        password = input("Enter password: ")
                        self.socket.sendto(packet(username, command="login", password=password, step=1),
                                           ('127.0.0.1', self.port))
                        packet_data, addr = self.socket.recvfrom(1024)
                        res = json.loads(packet_data.decode())
                        if res["code"] == 3:
                            self.username = username
                            self.user_stat = 1
                            print("Welcome to the forum")
                        if res["code"] == 4:
                            print("Invalid password")

                    if res["code"] == 2:
                        print(username + " " + "has already  logged in")
                    if res["code"] == 1:
                        password = input("New user, enter password: ")
                        if self.Right_username_and_password(password):
                            self.socket.sendto(packet(username, command="login", password=password, step=1),
                                               ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            if res["code"] == 3:
                                self.username = username
                                self.user_stat = 1
                                print("Welcome to the forum")
                        else:
                            self.socket.sendto(packet(username, command="login", right_username=0),
                                               ('127.0.0.1', self.port))
                            print("Invalid password")

                else:
                    self.socket.sendto(packet(username, command="login", right_username=0), ('127.0.0.1', self.port))
                    print("Invalid username")

            else:
                command_in = input(
                    "Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT: ")
                command = ''
                message = ''
                if " " in command_in:
                    command, message = command_in.split(" ", 1)
                else:
                    command = command_in
                if command in {"CRT", "MSG", "DLT", "EDT", "LST", "RDT", "UPD", "DWN", "RMV", "XIT"}:

                    if command == "CRT":
                        if " " not in message and message != "":
                            self.socket.sendto(packet(self.username, command, step=2, thread_title=message),
                                               ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            result = message
                            if res["code"] == 0:
                                print(f"Thread {result} created")
                            else:
                                print(f"Thread {result} exists")
                        else:
                            print(f"Incorrect syntax for {command}")
                    elif command == "UPD":
                        try:
                            k1, k2 = message.split()
                        except Exception:
                            k1 = {}
                            k2 = {}

                        if (message != '') and k1 and k2:
                            title, filename = message.split()
                            try:
                                file = open(filename, "r")
                                file.close()
                                self.socket.sendto(
                                    packet(self.username, command, step=2, thread_title=title, file_name=filename),
                                    ('127.0.0.1', self.port))
                            except Exception:
                                self.socket.sendto(
                                    packet(self.username, command, step=2, thread_title=title, file_name=filename,have_file=1),
                                    ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            if res["code"] == 0:
                                packet_data, addr = self.socket.recvfrom(1024)
                                res = json.loads(packet_data.decode())
                                if res["code"] == 0:
                                    self.tranfile_TCP(filename)
                                    print(f"{filename} uploaded to {title} thread")
                                elif res["code"] == 1:
                                    print(f"{filename} exist {title} thread")
                            elif res["code"] == 2:
                                print(f"Thread {title} not exist  ")
                            elif res["code"] == 3:
                                print(f"No such file or directory: {filename}")
                        else:
                            print(f"Incorrect syntax for {command}")

                    elif command == "MSG":
                        try:
                            k1, k2 = message.split(" ", 1)
                        except Exception:
                            k1 = {}
                            k2 = {}
                        if (message != '') and k1 and k2:
                            title, data = message.split(" ", 1)
                            self.socket.sendto(packet(self.username, command, step=2, thread_title=title, message=data),
                                               ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            if res["code"] == 0:
                                print(f"Message posted to {title} thread")
                            else:
                                print(f"Thread {title} not exist")
                        else:
                            print(f"Incorrect syntax for {command}")
                    elif command == "DLT":
                        try:
                            k1, k2 = message.split(" ", 1)
                        except Exception:
                            k1 = {}
                            k2 = {}
                        if (message != '') and k1.isdigit() and k2:
                            title, data = message.split(" ", 1)
                            self.socket.sendto(packet(self.username, command, step=2, thread_title=title, message=data),
                                               ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            if res["code"] == 0:
                                print("The message has been deleted")
                            elif res["code"] == 1:
                                print("The message belongs to another user and cannot be edited")
                            elif res["code"] == 2:
                                print(f"Thread {title} not exist")
                            elif res["code"] == 3:
                                print(f"No message match for thread {title}")
                        else:
                            print(f"Incorrect syntax for {command}")
                    elif command == "EDT":
                        try:
                            k1, k2 = message.split(" ", 1)
                            k3, k4 = k2.split(" ", 1)
                        except Exception:
                            k1 = {}
                            k2 = {}
                            k3 = {}
                            k4 = {}
                        if (message != '') and k1 and k2 and k3.isdigit() and k4:
                            title, data = message.split(" ", 1)
                            index, data_m = data.split(" ", 1)
                            self.socket.sendto(
                                packet(self.username, command, index=index, step=2, thread_title=title, message=data_m),
                                ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            if res["code"] == 0:
                                print("The message has been edited")
                            elif res["code"] == 1:
                                print("The message belongs to another user and cannot be edited")
                            elif res["code"] == 2:
                                print(f"Thread {title} not exist")
                            else:
                                print(f"No message match for thread {title}")
                        else:
                            print(f"Incorrect syntax for {command}")

                    elif command == "LST":
                        if message == '':
                            self.socket.sendto(
                                packet(self.username, command, step=2),
                                ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            if res["code"] == 0:
                                thread_dict = res["message_dict"]
                                print("The list of active threads:")
                                for i in thread_dict:
                                    print(thread_dict[i])
                            else:
                                print("No threads to list")
                        else:
                            print(f"Incorrect syntax for {command}")

                    elif command == "RDT":
                        if message != '' and " " not in message:
                            self.socket.sendto(
                                packet(self.username, command, step=2, thread_title=message),
                                ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            if res["code"] == 0:
                                message_dict = res["message_dict"]
                                for i in message_dict:
                                    print(message_dict[i], end='')
                            elif res["code"] == 2:
                                print(f"Thread {message} does not exist")
                            else:
                                print(f"Thread {message} is empty")
                        else:
                            print(f"Incorrect syntax for {command}")

                    elif command == "RMV":
                        if message != '' and " " not in message:
                            self.socket.sendto(
                                packet(self.username, command, step=2, thread_title=message),
                                ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            if res["code"] == 0:
                                print(f"Thread {message} removed")
                            else:
                                print("The thread was created by another user and cannot be removed")
                        else:
                            print(f"Incorrect syntax for {command}")

                    elif command == "DWN":
                        try:
                            k1, k2 = message.split(" ", 1)
                        except Exception:
                            k1 = {}
                            k2 = {}
                        if (message != '') and k1 and k2:
                            title, data = message.split(" ", 1)
                            self.socket.sendto(
                                packet(self.username, command, step=2, thread_title=title, file_name=data),
                                ('127.0.0.1', self.port))
                            packet_data, addr = self.socket.recvfrom(1024)
                            res = json.loads(packet_data.decode())
                            if res["code"] == 0:
                                self.DWN_file(data)
                                print(f"{data} successfully downloaded")
                            else:
                                print(f"File does not exist in Thread{title}")
                        else:
                            print(f"Incorrect syntax for {command}")




                    elif command == "XIT":
                        if message == '':
                            self.socket.sendto(
                                packet(self.username, command, step=2),
                                ('127.0.0.1', self.port))
                            print("GOOD_BYE")
                            break
                        else:
                            print(f"Incorrect syntax for {command}")
                else:
                    print("Invalid command")

            #     ...


if __name__ == '__main__':
    port = int(sys.argv[1])
    cli = Client(port)
    cli.run()

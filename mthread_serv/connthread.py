from distutils.log import Log
from msilib.schema import File
from pickle import FALSE
import threading
from threading import Thread
import json

CONNECTION_POOL = []    
LOCK = threading.Lock()
LOG = None

class SocketConnectionThread(Thread):
    username = None  
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.connection = conn
        self.address = addr

    def run(self):
        while True:
            try:
                data = self.connection.recv(1024)  
                data_json = json.loads(data.decode('utf-8'))    
                data_str = data_json['text']   

                data_from = data_json['from']
                
                if self.username is None:
                    if self.check_username(data_from) == False:
                        break
                data_to = data_json['to']
                print(f"FROM {data_from} TO {data_to}: {data_str}") 

                if data_str == "exit" or data_str == "close":
                    print(f"User {self.username} has gone offline!\n") 
                    break  

                elif data_to == '' or data_to == 'all':
                    if data_str != '':
                        self.send_all(data_str)
                        self.get_clients_data(data_str, data_to)

                elif data_str != '':
                        if self.send_direct(data_str, data_to) == True:
                            self.get_clients_data(data_str, data_to)
                else:
                    response = f"SERVER RESPONSE: MESSAGE RECEIVED FROM {data_from}"    
                    print(response)
            except Exception as error:
                print(self.name, error)
                print(f"User {self.username} has been disconnected\n") 
                self.get_clients_data("has gone\n", '')
                break
        self.connection.close()  
        self.remove_connection_from_pool()  
    
    def send_all(self, text):
        msg = json.dumps({'to': "all", 'from': self.username, 'text': f"BROADCAST MESSAGE: {text}"})
        for thread in CONNECTION_POOL:
            thread.connection.send(msg.encode('utf-8'))

    def remove_connection_from_pool(self):
        for i, thread in enumerate(CONNECTION_POOL):
            if thread.ident == self.ident:  
                del CONNECTION_POOL[i]

    def send_direct(self, text, data_to):
        for thread in CONNECTION_POOL:
            if thread.username == data_to:
                msg = json.dumps({'to': thread.username, 'from': self.username, 'text': f"DIRECT MESSAGE: {text}"})
                thread.connection.send(msg.encode('utf-8'))
                self.connection.send(msg.encode('utf-8'))
                return True
        msg = json.dumps({'to': self.username, 'from': "SERVER", 'text': "There's no such user"})
        self.connection.send(msg.encode('utf-8'))
        return False
 
    def get_clients_data(self, text, data_to):
        LOCK.acquire()
        LOG = open ("Log.txt", 'a+')
        if data_to == '' or data_to == 'all':
            line = f"{self.username}: {text}\n"
        else:
           line = f"{self.username} TO {data_to}: {text}\n" 
        LOG.write(line)
        LOG.close()
        LOCK.release()

    def check_username(self, name):
        for thread in CONNECTION_POOL:
            if thread.username == name:
                msg = json.dumps({'to': "CLIENT", 'from': "SERVER", 'text': "This username already exists, try another one"})
                self.connection.send(msg.encode('utf-8'))
                return False
        self.username = name
        msg = json.dumps({'to': "CLIENT", 'from': "SERVER", 'text': "You may start to chat now"})
        self.connection.send(msg.encode('utf-8'))
        return True

    
def clean_log():  
    LOG = open("Log.txt", 'w')
    LOG.write("")
    LOG.close()
    


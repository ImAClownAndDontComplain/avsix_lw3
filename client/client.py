import socket
import json
import re  
from threading import Thread


HOST = '192.168.0.101'   
PORT = 5000          
CLIENTNAME = None    

WRITE_THREAD = None
READ_THREAD = None

def send_msg(conn):
    conn.send(json.dumps({'to': "all", 'from': CLIENTNAME, 'text': f"User {CLIENTNAME} has come online!"}).encode('utf-8'))
    while True:
        data = input() 
        
        user_match = re.match(r'\[(\w+)\]', data)
        
        if user_match is not None:
            to_user = user_match.group(1)
            msg = {'to': to_user, 'from': CLIENTNAME, 'text': data} 
        else:
            msg = {'to': "all", 'from': CLIENTNAME, 'text': data}   
        conn.send(json.dumps(msg).encode('utf-8'))
        
        if data == "exit" or data == "close":
            conn.close()
            print('Connection closed.')
            break


def recv_msg(conn):
    while True:
        try:
            response = conn.recv(1024).decode('utf-8')  
            data_json = json.loads(response)  
            data_str = data_json['text']    
            data_from = data_json['from']    
            print(f"FROM {data_from}: {data_str}")
        except Exception:
            print('Listener disconnected.')
            break

if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0) 
    if client is not None:
        client.connect((HOST, PORT))    
        CLIENTNAME = input("Enter your name: ")  
        WRITE_THREAD = Thread(target=send_msg, args=(client,)).start()
        READ_THREAD = Thread(target=recv_msg, args=(client,)).start()

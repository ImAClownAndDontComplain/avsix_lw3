
import socket
import time
import threading
from connthread import SocketConnectionThread, CONNECTION_POOL, clean_log


HOST = ''        
PORT = 5000       
CLIENTS = 5  
#def check_username(new_thread):
#    for i in CONNECTION_POOL:
#        if i.username == new_thread.username:
#            print(f"This username already exists, try another one") 
#            time.sleep(0.1)
#            return False
#    return True

if __name__ == '__main__':
    clean_log()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)  
    sock.bind((HOST, PORT))  
    print(f"Server is running on {HOST}:{PORT}, please, press ctrl+c to stop")
    while True:
        sock.listen(CLIENTS)  
        try:
            conn, addr = sock.accept() 
            print(f"Client connected: {addr}") 
            new_thread = SocketConnectionThread(conn, addr) 
            new_thread.start()  
            CONNECTION_POOL.append(new_thread) 
        except Exception as error:
            print(error)
        print(f"Connections count: {threading.activeCount() - 1}") 
        time.sleep(0.1)

    
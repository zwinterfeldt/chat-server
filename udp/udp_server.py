import socket
import threading
import queue

messages=queue.Queue()
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('localhost', 12500))

def receive():
    while True:
        try:
            data, addr = server.recvfrom(1024)
            messages.put((data, addr))
        except:
            pass

def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            print(message.decode())
            if addr not in clients:
                clients.append(addr)
            for client in clients:
                try: 
                    if message.decode().startswith('WELCOME_TO_NOT_DISCORD:'):
                        name = messages.decode()[message.decode().index(':')+1:] 
                        server.sendto(f'{name} has joined the chat'.encode(), client)
                    else:
                        server.sendto(message, client)
                except:
                    clients.remove(client)




t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)
t1.start()
t2.start()
import socket
import threading
import random
import sys

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(('localhost', random.randint(10000, 13000)))

name = input("Enter your name: ")

def receive():
    while True:
        try:
            data, addr = client.recvfrom(1024)
            print(addr, data.decode())
        except:
            pass
t= threading.Thread(target=receive)
t.start()

client.sendto(f"WELCOME_TO_NOT_DISCORD:{name}".encode(), ('localhost', 12500))
while True:
    message = input("")

    if message == "status":
        client.sendto(f"STATUS {name} online".encode(), ('localhost', 12500))

    elif message == 'exit':
        client.sendto(f"{name} has left the chat".encode(), ('localhost', 12500))
        client.sendto(f"STATUS {name} offline".encode(), ('localhost', 12500))
        print("Goodbye!")
        sys.exit()
    else:
        client.sendto(f"{name}: {message}".encode(), ('localhost', 12500))
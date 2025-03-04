import threading
import socket

host = '127.0.0.1'
port = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()


clients = []
usernames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} has left the chat'.encode('utf-8'))
            usernames.remove(username)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')
        client.send('USERNAME'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
        clients.append(client)

        print(f'Username of the client is {username}')
        broadcast(f'Welcome {username}'.encode('utf-8'))
        broadcast(f'{username} has joined the chat \n'.encode('utf-8'))
        client.send('Connected to the server'.encode('utf-8'))


        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print("Server is running...")
receive()

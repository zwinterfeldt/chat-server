import socket
import threading

# Server configuration
TCP_PORT = 12345
UDP_PORT = 12346
HOST = '0.0.0.0'

# Store connected clients
clients = []

# TCP server
def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, TCP_PORT))
    server.listen(5)
    print(f"TCP server listening on port {TCP_PORT}...")

    while True:
        client_socket, addr = server.accept()
        print(f"New connection from {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_tcp_client, args=(client_socket,)).start()

# Handle TCP client
def handle_tcp_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received: {message}")
            broadcast(message, client_socket)
        except:
            clients.remove(client_socket)
            client_socket.close()
            break

# UDP server
def udp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, UDP_PORT))
    print(f"UDP server listening on port {UDP_PORT}...")

    while True:
        message, addr = server.recvfrom(1024)
        print(f"Received UDP message: {message.decode('utf-8')}")
        broadcast(message, None)

# Broadcast messages to all clients
def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8') if isinstance(message, str) else message)
            except:
                clients.remove(client)
                client.close()

# Start servers
threading.Thread(target=tcp_server).start()
threading.Thread(target=udp_server).start()
import socket
import threading

# Server configuration
TCP_PORT = 12345
UDP_PORT = 12346
HOST = '127.0.0.1'

# TCP client
def tcp_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, TCP_PORT))

    # Send username
    username = input("Enter your username: ")
    client.send(username.encode('utf-8'))

    # Receive messages
    def receive():
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                print(message)
            except:
                print("Connection closed.")
                client.close()
                break

    threading.Thread(target=receive).start()

    # Send messages
    while True:
        message = input()
        client.send(message.encode('utf-8'))

# UDP client
def udp_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(('0.0.0.0', 0))

    # Send status updates
    while True:
        status = input("Enter status: ")
        client.sendto(f"STATUS:{status}".encode('utf-8'), (HOST, UDP_PORT))

# Start clients
threading.Thread(target=tcp_client).start()
threading.Thread(target=udp_client).start()
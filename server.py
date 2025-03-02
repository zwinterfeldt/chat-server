import socket
import threading

HOST = '0.0.0.0'
TCP_PORT = 5555
UDP_PORT = 5556

def handle_tcp_client(client_socket, addr):
    # This function will parse incoming messages from one client
    # and handle them (CONNECT, MSG, BROADCAST, DISCONNECT).

    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            # parse data and handle commands here
            print(f"Received: {data} from {addr}")
        except ConnectionResetError:
            break

    # Cleanup logic when the client disconnects
    client_socket.close()

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, TCP_PORT))
    server_socket.listen()
    print(f"TCP server listening on port {TCP_PORT}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"New connection: {addr}")
        threading.Thread(target=handle_tcp_client, args=(client_socket, addr)).start()

def start_udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    print(f"UDP server listening on port {UDP_PORT}...")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        message = data.decode('utf-8')
        # parse the message (e.g. STATUS <username> <online/offline>)
        print(f"UDP from {addr}: {message}")

if __name__ == "__main__":
    threading.Thread(target=start_tcp_server).start()
    threading.Thread(target=start_udp_server).start()

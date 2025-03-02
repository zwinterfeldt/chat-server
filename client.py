import socket
import threading

SERVER_HOST = '127.0.0.1'
TCP_PORT = 6091
UDP_PORT = 6092

def tcp_receive(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print("From Server:", data.decode('utf-8'))

def main():
    # Connect via TCP
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((SERVER_HOST, TCP_PORT))

    # Start a thread to listen for server messages
    threading.Thread(target=tcp_receive, args=(tcp_socket,)).start()

    # For sending UDP
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Simple user input loop
    while True:
        message = input(">>> ")
        if message.startswith("UDP "):
            # e.g. "UDP STATUS myUser online"
            udp_msg = message[4:]
            udp_socket.sendto(udp_msg.encode('utf-8'), (SERVER_HOST, UDP_PORT))
        else:
            # For TCP commands
            tcp_socket.sendall(message.encode('utf-8'))

if __name__ == "__main__":
    main()

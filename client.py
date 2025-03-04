import socket
import threading

# Client configuration
TCP_IP = '127.0.0.1'
TCP_PORT = 12345
UDP_IP = '127.0.0.1'
UDP_PORT = 12346

def tcp_receive(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print("TCP:", data.decode().strip())

def main():
    username = input("Enter your username: ")
    
    # Setup TCP connection
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((TCP_IP, TCP_PORT))
    # Send CONNECT command
    tcp_socket.send(f"CONNECT {username}\n".encode())
    print("Sent CONNECT command over TCP")
    
    # Start thread to receive messages over TCP
    threading.Thread(target=tcp_receive, args=(tcp_socket,), daemon=True).start()
    
    # Setup UDP socket (no separate thread for UDP sending anymore)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Display available commands for both protocols
    print("\nAvailable commands:")
    print("TCP Commands:")
    print("  MSG <username> <message>       → Send a private message")
    print("  BROADCAST <message>            → Send a message to all users")
    print("  DISCONNECT                     → Disconnect from the chat")
    print("UDP Commands:")
    print("  STATUS <username> <online/offline>  → Update your status")
    print("  TYPING <username>              → Indicate that you are typing")
    print("------------------------------------------------------------")
    
    # Main loop for sending commands (both TCP and UDP)
    while True:
        cmd = input("Enter your command: ").strip()
        if not cmd:
            continue
        
        # Determine protocol based on command prefix
        if cmd.startswith("STATUS") or cmd.startswith("TYPING"):
            udp_socket.sendto(cmd.encode(), (UDP_IP, UDP_PORT))
        else:
            tcp_socket.send(f"{cmd}\n".encode())
            if cmd.startswith("DISCONNECT"):
                break

if __name__ == "__main__":
    main()

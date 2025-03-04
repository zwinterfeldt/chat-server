import socket
import threading

# Server configuration
TCP_IP = '127.0.0.1'
TCP_PORT = 5000
UDP_IP = '127.0.0.1'
UDP_PORT = 5001

# A dictionary to track connected users: username -> (tcp_conn, address, user_id)
clients = {}
user_id_counter = 1
lock = threading.Lock()

def handle_tcp_client(conn, addr):
    global user_id_counter
    username = None
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            data_str = data.decode().strip()
            # Process TCP commands
            if data_str.startswith("CONNECT"):
                # Example: CONNECT Alice
                parts = data_str.split()
                if len(parts) == 2:
                    username = parts[1]
                    with lock:
                        user_id = user_id_counter
                        user_id_counter += 1
                        clients[username] = (conn, addr, user_id)
                    conn.send(f"CONNECTED {username} {user_id}\n".encode())
                    print(f"{username} connected with id {user_id}")
            elif data_str.startswith("MSG"):
                # Example: MSG Bob Hello there!
                parts = data_str.split(maxsplit=2)
                if len(parts) < 3:
                    conn.send("ERROR Invalid MSG format\n".encode())
                    continue
                target_username = parts[1]
                message = parts[2]
                if target_username in clients:
                    target_conn = clients[target_username][0]
                    target_conn.send(f"MSG from {username}: {message}\n".encode())
                else:
                    conn.send("ERROR User not found\n".encode())
            elif data_str.startswith("BROADCAST"):
                message = data_str[len("BROADCAST "):]
                with lock:
                    for user, (client_conn, client_addr, uid) in clients.items():
                        if client_conn != conn:
                            client_conn.send(f"BROADCAST from {username}: {message}\n".encode())
            elif data_str.startswith("DISCONNECT"):
                conn.send("DISCONNECTING\n".encode())
                break
            else:
                conn.send("ERROR Unknown command\n".encode())
    except Exception as e:
        print("TCP client error:", e)
    finally:
        if username:
            with lock:
                if username in clients:
                    del clients[username]
            print(f"{username} disconnected")
        conn.close()

def tcp_listener():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((TCP_IP, TCP_PORT))
    tcp_socket.listen(5)
    print("TCP server listening on", TCP_IP, TCP_PORT)
    while True:
        conn, addr = tcp_socket.accept()
        threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()

def udp_listener():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP, UDP_PORT))
    print("UDP server listening on", UDP_IP, UDP_PORT)
    while True:
        data, addr = udp_socket.recvfrom(1024)
        data_str = data.decode().strip()
        # Process UDP commands
        if data_str.startswith("STATUS"):
            # Example: STATUS Alice online
            parts = data_str.split()
            if len(parts) == 3:
                username = parts[1]
                status = parts[2]
                print(f"Status update: {username} is {status}")
        elif data_str.startswith("TYPING"):
            # Example: TYPING Alice
            parts = data_str.split()
            if len(parts) == 2:
                username = parts[1]
                print(f"{username} is typing...")
        else:
            print("Unknown UDP command from", addr, ":", data_str)

if __name__ == "__main__":
    # Start TCP and UDP listener threads
    threading.Thread(target=tcp_listener, daemon=True).start()
    threading.Thread(target=udp_listener, daemon=True).start()
    
    # Prevent the main thread from exiting
    while True:
        pass
 
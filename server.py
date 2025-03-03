import socket
import threading
import time

HOST = '127.0.0.1'
TCP_PORT = 6091
UDP_PORT = 6092
online_users = {}  
TIMEOUT = 300 

# Dictionary to keep track of connected clients: { username: socket }
connected_clients = {}

def handle_tcp_client(client_socket, addr):
    global connected_clients
    username = None

    # We'll keep a buffer for partial reads
    buffer = ""

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                # Client closed the connection
                break

            # Decode the newly-received data
            buffer += data.decode('utf-8')

            # Keep processing as long as there's a newline in the buffer
            while '\n' in buffer:
                # Split up to the first newline
                line, buffer = buffer.split('\n', 1)
                line = line.strip()  # remove trailing spaces

                if not line:
                    continue

                print(f"Received from {addr}: {line}")

                # Now parse and handle the line
                parts = line.split(' ', 2)
                cmd = parts[0].upper()

                if cmd == "CONNECT":
                    # ... your CONNECT handling
                    if len(parts) < 2:
                        client_socket.sendall(b"ERROR: Username not provided.\n")
                        continue

                    requested_username = parts[1]
                    if requested_username in connected_clients:
                        client_socket.sendall(b"ERROR: Username already in use.\n")
                    else:
                        username = requested_username
                        connected_clients[username] = client_socket
                        client_socket.sendall(f"WELCOME {username}\n".encode('utf-8'))

                elif cmd == "MSG":
                    # ... your MSG handling
                    if len(parts) < 3:
                        client_socket.sendall(b"ERROR: Invalid MSG command.\n")
                        continue
                    if username is None:
                        client_socket.sendall(b"ERROR: You must CONNECT first.\n")
                        continue
                    recipient = parts[1]
                    message_body = parts[2]
                    if recipient in connected_clients:
                        recipient_socket = connected_clients[recipient]
                        forward_msg = f"MSG from {username}: {message_body}\n"
                        recipient_socket.sendall(forward_msg.encode('utf-8'))
                    else:
                        client_socket.sendall(b"ERROR: Recipient not found.\n")

                elif cmd == "BROADCAST":
                    # ... your BROADCAST handling
                    if len(parts) < 2:
                        client_socket.sendall(b"ERROR: No broadcast message.\n")
                        continue
                    if username is None:
                        client_socket.sendall(b"ERROR: You must CONNECT first.\n")
                        continue
                    message_body = parts[1]
                    broadcast_msg = f"BROADCAST from {username}: {message_body}\n"
                    for user, sock in connected_clients.items():
                        sock.sendall(broadcast_msg.encode('utf-8'))

                elif cmd == "DISCONNECT":
                    # ... your DISCONNECT handling
                    if username in connected_clients:
                        del connected_clients[username]
                    client_socket.sendall(b"GOODBYE\n")
                    break  # exit while loop to close socket

                elif cmd == "STATUS":
                    handle_udp_client()

                else:
                    client_socket.sendall(b"ERROR: Unknown command.\n")

        except ConnectionResetError:
            break
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break

    # Cleanup
    client_socket.close()
    if username and username in connected_clients:
        del connected_clients[username]
    print(f"Connection closed: {addr}")


    # When the client exits the loop (disconnect), close socket and remove if needed
    client_socket.close()
    if username and username in connected_clients:
        del connected_clients[username]
    print(f"Connection closed: {addr}")


def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, TCP_PORT))
    server_socket.listen()
    print(f"TCP server listening on port {TCP_PORT}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"New connection: {addr}")
        threading.Thread(target=handle_tcp_client, args=(client_socket, addr)).start()

def handle_udp_client():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    print(f"UDP server listening on port {UDP_PORT}...")

    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)  # Receive message and sender address
            message = data.decode('utf-8').strip()
            print(f"Received UDP from {addr}: {message}")

            if not message:
                continue

            parts = message.split(' ', 2)
            cmd = parts[0].upper()

            if cmd == "STATUS" and len(parts) == 1:
                # Request for online users list
                remove_inactive_users()
                response = "Online users: " + ", ".join(online_users.keys()) if online_users else "No users online."
                udp_socket.sendto(response.encode('utf-8'), addr)

            elif cmd == "STATUS" and len(parts) == 3:
                # Update user status
                username, status = parts[1], parts[2].lower()
                if status == "online":
                    online_users[username] = time.time()  # Update timestamp
                    udp_socket.sendto(f"{username} is now online.".encode('utf-8'), addr)
                elif status == "offline":
                    online_users.pop(username, None)  # Remove from online list
                    udp_socket.sendto(f"{username} is now offline.".encode('utf-8'), addr)
                else:
                    udp_socket.sendto("ERROR: Invalid status. Use 'online' or 'offline'.".encode('utf-8'), addr)

            else:
                udp_socket.sendto("ERROR: Unknown command.".encode('utf-8'), addr)

        except Exception as e:
            print(f"Error handling UDP client {addr}: {e}")

def start_udp_server():
    # This minimal UDP server just prints incoming messages
    # You can add parsing similar to handle_tcp_client if needed
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    print(f"UDP server listening on port {UDP_PORT}...")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        message = data.decode('utf-8').strip()
        print(f"UDP from {addr}: {message}")
        # For example, parse if it’s "STATUS <username> <online/offline>"
        # Or handle additional logic as desired.
        handle_udp_client()
       

def remove_inactive_users():
    """Remove users who have been inactive for more than TIMEOUT seconds."""
    current_time = time.time()
    inactive_users = [user for user, last_seen in online_users.items() if current_time - last_seen > TIMEOUT]
    for user in inactive_users:
        del online_users[user]



if __name__ == "__main__":
    threading.Thread(target=start_tcp_server).start()
    threading.Thread(target=start_udp_server).start()

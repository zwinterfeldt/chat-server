import socket
import threading

username = input("Enter your username: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 12345))   


def receive():
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if data == "USERNAME":
                client.send(username.encode('utf-8'))
            else:
                print(data)
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    while True:
        message = f'{username}: {input("")}'
        client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
write_thread = threading.Thread(target=write)
receive_thread.start()
write_thread.start()
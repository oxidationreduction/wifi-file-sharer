import socket
import os
import time


def client_program():
    host = 'localhost'
    port = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port))

    files_to_send = ['client.py']

    for file_name in files_to_send:
        size = os.path.getsize(file_name)

        # Send the size of the file and the filename
        client_socket.sendall(f'{size}\n{file_name}\n'.encode())

        with open(file_name, 'rb') as file_to_send:
            for data in file_to_send:
                client_socket.sendall(data)

    time.sleep(0.5)
    client_socket.close()


if __name__ == '__main__':
    client_program()

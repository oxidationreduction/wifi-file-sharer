import os
import socket
import selectors
import types


def accept_wrapper(sock):
    conn, addr = sock.accept()
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask, size=None, filename=None):
    sock = key.fileobj
    data = key.data
    try:
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024).decode()
            if '\n' in recv_data:  # check if we received the size and filename
                recv_data_list = recv_data.split('\n')
                print(recv_data_list)
                global info_received
                if not info_received:
                    size, filename = recv_data_list[:2]
                    size = int(size)
                    info_received = True
                data.outb = b''
            else:
                if len(recv_data) == size:  # check if we received the entire file
                    with open(os.path.join(save_path, filename), 'wb') as f:
                        f.write(recv_data.encode())
                    print('received', repr(recv_data), 'from', data.addr)
                    print('sending confirmation to', data.addr)
                    data.outb = b"File received successfully."  # confirmation message
                    sock.send(data.outb)  # send confirmation
                    info_received = False
                    data.outb = b''  # clear output buffer
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print('echoing', repr(data.outb), 'to', data.addr)
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]
    except ConnectionResetError:
        print('ConnectionResetError for', data.addr)
        sel.unregister(sock)
        info_received = False
        sock.close()
    except Exception as e:
        print(f'Error for {data.addr}: {str(e)}')
        sel.unregister(sock)
        info_received = False
        sock.close()


if __name__ == '__main__':
    host = 'localhost'
    port = 5000
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print('listening on', (host, port))
    lsock.setblocking(False)

    sel = selectors.DefaultSelector()
    sel.register(lsock, selectors.EVENT_READ, data=None)

    save_path = 'files'  # The path to save received files
    info_received = False

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print('caught keyboard interrupt, exiting')
    finally:
        sel.close()

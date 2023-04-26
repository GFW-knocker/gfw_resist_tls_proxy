import os
import socket
import time
import threading


listen_PORT = 2500  # pyprox listening to 127.0.0.1:listen_PORT

Cloudflare_IP = '162.159.135.42'  # plos.org (can be any dirty cloudflare ip)
Cloudflare_port = 443

L_fragment = 77  # length of fragments of Client Hello packet (L_fragment Byte in each chunk)
fragment_sleep = 0.2  # sleep between each fragment to make GFW-cache full so it forget previous chunks. LOL.

# ignore description below, its for old code, just leave it intact.
my_socket_timeout = 60  # default for google is ~21 sec , recommend 60 sec unless you have low ram and need close soon
first_time_sleep = 0.01  # speed control, avoid server crash if huge number of users flooding (default 0.1)
accept_time_sleep = 0.01  # avoid server crash on flooding request -> max 100 sockets per second


def endstream(backend_sock, client_sock, reason=None):
    # print(reason)
    time.sleep(2)  # wait two second for another thread to flush
    client_sock.close()
    backend_sock.close()


def downstream(backend_sock, client_sock):
    try:
        data = backend_sock.recv(16384)
        if not data: raise Exception('backend pipe close at first')
        client_sock.sendall(data)

        while True:
            data = backend_sock.recv(4096)
            if not data: raise Exception('backend pipe close')
            client_sock.sendall(data)
    except Exception as e:
        endstream(backend_sock, client_sock, reason=f'downstream: {repr(e)}')


def upstream(client_sock):
    backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    backend_sock.settimeout(my_socket_timeout)
    time.sleep(first_time_sleep)  # speed control + waiting for packet to fully recieve

    try:
        data = client_sock.recv(16384)
        # print('len data -> ',str(len(data)))
        # print('user talk :')
        if not data: raise Exception('cli syn close')
        backend_sock.connect((Cloudflare_IP, Cloudflare_port))
        thread_down = threading.Thread(target=downstream, args=(backend_sock, client_sock), daemon=True)
        thread_down.start()
        # backend_sock.sendall(data)

        # send data in delayed fragments:
        for i in range(0, len(data), L_fragment):
            fragment_data = data[i: i + L_fragment]
            print(f'send {len(fragment_data)} bytes')
            # backend_sock.send(fragment_data)
            backend_sock.sendall(fragment_data)
            time.sleep(fragment_sleep)
        print('----------finish------------')

        while True:
            data = client_sock.recv(4096)
            if not data: raise Exception('cli pipe close')
            backend_sock.sendall(data)
    except Exception as e:
        endstream(backend_sock, client_sock, reason=f'upstream: {repr(e)}')


def listen(host, port):
    if os.name == 'posix':
        import resource
        print('[linux] set max_num_open_socket from 1024 to 128k')
        resource.setrlimit(resource.RLIMIT_NOFILE, (127000, 128000))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    print(f"Now listening at {host or '127.0.0.1'}:{listen_PORT}")

    sock.listen(128)  # up to 128 concurrent unaccepted socket queued , the more is refused untill accepting those.
    while True:
        client_sock, _ = sock.accept()
        client_sock.settimeout(my_socket_timeout)

        # print('someone connected')
        time.sleep(accept_time_sleep)  # avoid server crash on flooding request
        # avoid memory leak by telling os its belong to main program , its not a separate program , so gc collect it when thread finish
        thread_up = threading.Thread(target=upstream, args=(client_sock,), daemon=True)
        thread_up.start()


if __name__ == '__main__':
    listen('', listen_PORT)

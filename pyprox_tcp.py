#!/usr/bin/env python3

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


# Main method: lets make handshake (the only way GFW can detect) costly.
def handshake(backend_sock, client_sock):
    data = client_sock.recv(16384)
    if not data: raise Exception('syn close')
    backend_sock.connect((Cloudflare_IP, Cloudflare_port))

    # print(f'{len(data)}B client hello recevied, lets send {L_fragment}B per {fragment_sleep} seconds to CF.')
    for i in range(0, len(data), L_fragment):
        fragment_data = data[i: i + L_fragment]
        print(f'sending {len(fragment_data)} bytes')
        backend_sock.sendall(fragment_data)
        time.sleep(fragment_sleep)
    print('----------finish------------')

    data = backend_sock.recv(16384)
    if not data: raise Exception('syn-ack close')
    client_sock.sendall(data)
    # print(f'{len(data)}B hello response moved to client.')


def stream(recv_sock, send_sock):
    try:
        while True:
            data = recv_sock.recv(4096)
            if not data: raise Exception('pipe close')
            send_sock.sendall(data)
    except Exception as e:
        # print(f'{threading.current_thread().name}: {repr(e)}')
        time.sleep(2)  # wait two second for another thread to flush
        send_sock.close()
        recv_sock.close()


def tunnel(backend_sock, client_sock):
    time.sleep(first_time_sleep)  # speed control + waiting for packet to fully recieve

    try: handshake(backend_sock, client_sock)
    except Exception as e:
        # print(f'Handshake: {repr(e)}')
        time.sleep(2)  # wait two second for another thread to flush
        backend_sock.close()
        client_sock.close()

    thread_down = threading.Thread(target=stream, args=(backend_sock, client_sock), daemon=True, name='backend')
    thread_down.start()
    stream(client_sock, backend_sock)


def listen(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    print(f"Now listening at {host or '127.0.0.1'}:{listen_PORT}")

    sock.listen(128)  # up to 128 concurrent unaccepted socket queued , the more is refused untill accepting those.
    while True:
        client_sock, _ = sock.accept()
        client_sock.settimeout(my_socket_timeout)
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_sock.settimeout(my_socket_timeout)

        # print('someone connected')
        time.sleep(accept_time_sleep)  # avoid server crash on flooding request
        # avoid memory leak by telling os its belong to main program, so gc collect it when thread finish
        thread_up = threading.Thread(target=tunnel, args=(backend_sock, client_sock), daemon=True, name='client')
        thread_up.start()


if __name__ == '__main__':
    if os.name == 'posix':
        import resource
        print('[linux] set max_num_open_socket from 1024 to 128k')
        resource.setrlimit(resource.RLIMIT_NOFILE, (127000, 128000))

    listen('', listen_PORT)

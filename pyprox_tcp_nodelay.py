#!/usr/bin/env python3

import os
import socket
import time
import threading

listen_PORT = 2500  # pyprox listening to 127.0.0.1:listen_PORT

Cloudflare_IP = '162.159.135.42'  # plos.org (can be any dirty cloudflare ip)
Cloudflare_port = 443

GFW_FRAGS_LIMIT = 3  # minimum fragments limit for the GFW that will pass if the count of fragments more than it
# ignore description below, its for old code, just leave it intact.
my_socket_timeout = 60  # default for google is ~21 sec , recommend 60 sec unless you have low ram and need close soon
first_time_sleep = 0.01  # speed control, avoid server crash if huge number of users flooding (default 0.1)
accept_time_sleep = 0.01  # avoid server crash on flooding request -> max 100 sockets per second
CHUNK_SIZE = 16384  # read and receive chunks in sockets.


# Can be used to rotating IPs
def backend_connect(backend):
    backend.connect((Cloudflare_IP, Cloudflare_port))


# Main method: lets make handshake (the only way GFW can detect) costly.
def handshake(backend, client):
    try:
        data = client.recv(CHUNK_SIZE)
        if not data: raise Exception('syn close')

        # connect to backend after received client hello
        backend_connect(backend)

        length = len(data)
        L_fragment, mod = divmod(length, GFW_FRAGS_LIMIT)
        if mod: L_fragment += 1
        print(f'{len(data)}B client hello recevied, lets send as {GFW_FRAGS_LIMIT} x {L_fragment}B fragments to CF.')
        for i in range(0, length, L_fragment):
            fragment_data = data[i: i + L_fragment]
            backend.sendall(fragment_data)
        print('----------finish------------')

        data = backend.recv(CHUNK_SIZE)
        if not data: raise Exception('syn-ack close')
        client.sendall(data)
        print(f'{len(data)}B hello response moved to client.')
        return True
    except Exception as e:
        print(f'Handshake: {repr(e)}')
        time.sleep(2)  # wait two second for another thread to flush
        backend.close()
        client.close()


def stream(reader, writer):
    try:
        while True:
            data = reader.recv(CHUNK_SIZE)
            if not data: raise Exception('pipe close')
            writer.sendall(data)
    except Exception as e:
        print(f'{threading.current_thread().name}: {repr(e)}')
        time.sleep(2)  # wait two second for another thread to flush
        writer.close()
        reader.close()


def tunnel(backend, client):
    time.sleep(first_time_sleep)  # speed control + waiting for packet to fully recieve
    if not handshake(backend, client): return

    thread_down = threading.Thread(target=stream, args=(backend, client), daemon=True, name='backend')
    thread_down.start()
    stream(client, backend)


def run_proxy(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # try to reuse port is if it already in use.
    sock.bind((host, port))
    print(f"Now listening at {host or '127.0.0.1'}:{listen_PORT}")

    sock.listen(128)  # up to 128 concurrent unaccepted socket queued , the more is refused untill accepting those.
    while True:
        client, _ = sock.accept()
        client.settimeout(my_socket_timeout)
        # create backend for this connected client
        backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend.settimeout(my_socket_timeout)
        # force localhost kernel to send TCP packet immediately (idea: @free_the_internet)
        # avoid OS cache of continuous fragments sent immediately
        backend.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # print('someone connected')
        time.sleep(accept_time_sleep)  # avoid server crash on flooding request
        # avoid memory leak by telling os its belong to main program, so gc collect it when thread finish
        thread_up = threading.Thread(target=tunnel, args=(backend, client), daemon=True, name='client')
        thread_up.start()


if __name__ == '__main__':
    if os.name == 'posix':
        import resource
        print('[linux] set max_num_open_socket from 1024 to 128k')
        resource.setrlimit(resource.RLIMIT_NOFILE, (127000, 128000))

    run_proxy('', listen_PORT)

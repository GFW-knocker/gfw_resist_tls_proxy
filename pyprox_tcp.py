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


def backend_connect(backend):
    # Can be used to rotating IPs here
    backend.connect((Cloudflare_IP, Cloudflare_port))


# Main method: lets make handshake (the only way GFW can detect) costly.
def handshake(backend, client):
    try:
        data = client.recv(16384)
        if not data: raise Exception('syn close')

        # connect to backend after received client hello
        backend_connect(backend)

        # print(f'{len(data)}B client hello recevied, lets send {L_fragment}B per {fragment_sleep} seconds to CF.')
        for i in range(0, len(data), L_fragment):
            fragment_data = data[i: i + L_fragment]
            print(f'sending {len(fragment_data)} bytes')
            backend.sendall(fragment_data)
            time.sleep(fragment_sleep)
        print('----------finish------------')

        data = backend.recv(16384)
        if not data: raise Exception('syn-ack close')
        client.sendall(data)
        # print(f'{len(data)}B hello response moved to client.')
        return True
    except Exception as e:
        # print(f'Handshake: {repr(e)}')
        time.sleep(2)  # wait two second for another thread to flush
        backend.close()
        client.close()


def stream(reader, writer):
    try:
        while True:
            data = reader.recv(4096)
            if not data: raise Exception('pipe close')
            writer.sendall(data)
    except Exception as e:
        # print(f'{threading.current_thread().name}: {repr(e)}')
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
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    print(f"Now listening at {host or '127.0.0.1'}:{listen_PORT}")

    sock.listen(128)  # up to 128 concurrent unaccepted socket queued , the more is refused untill accepting those.
    while True:
        client, _ = sock.accept()
        client.settimeout(my_socket_timeout)
        # create backend for this connected client
        backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend.settimeout(my_socket_timeout)

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

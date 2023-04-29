#!/usr/bin/env python3
import socket
import threading
import random
import time

NUM_FRAGMENT = 27
FRAGMENT_SLEEP = 0.001
GOOGLE_IP = '216.239.38.120'
GOOGLEVIDEO_IP = '74.125.98.10'
SOCKET_TIMEOUT = 60
FIRST_TIME_SLEEP = 0.1
ACCEPT_TIME_SLEEP = 0.01
LISTEN_PORT_GOOGLE = 2500
LISTEN_PORT_YOUTUBE = 2501


class ThreadedServer:
    def __init__(self, host, port1, port2):
        self.host = host
        self.sock_web = self.create_and_bind_socket(port1)
        self.sock_video = self.create_and_bind_socket(port2)

    @staticmethod
    def create_and_bind_socket(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        sock.listen(128)
        return sock

    def multi_listen(self):
        thread_web = threading.Thread(target=self.listen, args=(self.sock_web, GOOGLE_IP))
        thread_web.start()
        thread_video = threading.Thread(target=self.listen, args=(self.sock_video, GOOGLEVIDEO_IP))
        thread_video.start()

    @staticmethod
    def upstream(client_sock, remote_ip):
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_sock.settimeout(SOCKET_TIMEOUT)
        backend_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        try:
            data = client_sock.recv(16384)
            if not data:
                raise Exception('cli syn close')
            backend_sock.connect((remote_ip, 443))
            thread_down = threading.Thread(target=ThreadedServer.downstream,
                                           args=(backend_sock, client_sock))
            thread_down.daemon = True
            thread_down.start()
            send_data_in_fragment(data, backend_sock)

            while True:
                data = client_sock.recv(16384)
                if not data:
                    raise Exception('cli pipe close')
                backend_sock.sendall(data)

        except Exception:
            time.sleep(2)
            client_sock.close()
            backend_sock.close()
            return False

    @staticmethod
    def downstream(backend_sock, client_sock):
        first_flag = True
        while True:
            try:
                if first_flag:
                    first_flag = False
                    data = backend_sock.recv(16384)
                    if data:
                        client_sock.sendall(data)
                    else:
                        raise Exception('backend pipe close at first')

                else:
                    data = backend_sock.recv(4096)
                    if data:
                        client_sock.sendall(data)
                    else:
                        raise Exception('backend pipe close')

            except Exception:
                time.sleep(2)
                backend_sock.close()
                client_sock.close()
                return False

    def listen(self, sock, remote_ip):
        while True:
            client_sock, _ = sock.accept()
            client_sock.settimeout(SOCKET_TIMEOUT)
            time.sleep(ACCEPT_TIME_SLEEP)
            thread_up = threading.Thread(target=self.upstream, args=(client_sock, remote_ip))
            thread_up.daemon = True
            thread_up.start()


def send_data_in_fragment(data, sock):
    data_len = len(data)
    fragment_indices = random.sample(range(1, data_len), min(NUM_FRAGMENT - 1, data_len - 1))
    fragment_indices.sort()

    i_pre = 0
    for i in fragment_indices:
        fragment_data = data[i_pre:i]
        if len(fragment_data) > 0:
            sock.sendall(fragment_data)
            time.sleep(FRAGMENT_SLEEP)
        i_pre = i

    fragment_data = data[i_pre:data_len]
    if len(fragment_data) > 0:
        sock.sendall(fragment_data)


ThreadedServer('', LISTEN_PORT_GOOGLE, LISTEN_PORT_YOUTUBE).multi_listen()
print(f"Now listening at: 127.0.0.1:{LISTEN_PORT_GOOGLE} for web")
print(f"Now listening at: 127.0.0.1:{LISTEN_PORT_YOUTUBE} for video")

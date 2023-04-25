#!/usr/bin/env python3

import socket
import threading
import ipaddress
import itertools
from pathlib import Path
import os
import copy
import time
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

def load_dotenv(dotenv_path):
    if not os.path.exists(dotenv_path):
        return

    with open(dotenv_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            name, value = line.split('=', 1)
            os.environ[name] = value

# Load environment variables from .env file if it exists
dotenv_path = '.env'
load_dotenv(dotenv_path)


if os.name == 'posix':
    print('os is linux')
    import resource   # ( -> pip install python-resources )
    # set linux max_num_open_socket from 1024 to 128k
    resource.setrlimit(resource.RLIMIT_NOFILE, (127000, 128000))



listen_PORT = int(os.environ.get('PORT', 2500))   # pyprox listening to 127.0.0.1:listen_PORT

Cloudflare_IPs = os.environ.get('CLOUDFLARE_IPS', '23.227.39.0/32')  # plos.org (can be any dirty cloudflare ip)
Cloudflare_port = int(os.environ.get('CLOUDFLARE_PORT', 443))

L_fragment = int(os.environ.get('L_FRAGMENT', 77))   # length of fragments of Client Hello packet (L_fragment Byte in each chunk)
fragment_sleep = float(os.environ.get('FRAGMENT_SLEEP', 0.2))  # sleep between each fragment to make GFW-cache full so it forget previous chunks. LOL.



# ignore description below , its for old code , just leave it intact.
my_socket_timeout = int(os.environ.get('MY_SOCKET_TIMEOUT', 60)) # default for google is ~21 sec , recommend 60 sec unless you have low ram and need close soon
first_time_sleep = float(os.environ.get('FIRST_TIME_SLEEP', 0.01)) # speed control , avoid server crash if huge number of users flooding (default 0.1)
accept_time_sleep = float(os.environ.get('ACCEPT_TIME_SLEEP', 0.01)) # avoid server crash on flooding request -> max 100 sockets per second

Cloudflare_IPs = [str(ip) for subnet in Cloudflare_IPs.split(',') for ip in ipaddress.IPv4Network(subnet, strict=False)]

# Define an iterator for round-robin load balancing
cloudflare_ips_iterator = itertools.cycle(Cloudflare_IPs)


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(128)  # up to 128 concurrent unaccepted socket queued , the more is refused untill accepting those.
        while True:
            client_sock , client_addr = self.sock.accept()                    
            client_sock.settimeout(my_socket_timeout)
            
            #print('someone connected')
            time.sleep(accept_time_sleep)   # avoid server crash on flooding request
            thread_up = threading.Thread(target = self.my_upstream , args =(client_sock,) )
            thread_up.daemon = True   #avoid memory leak by telling os its belong to main program , its not a separate program , so gc collect it when thread finish
            thread_up.start()
            

    def my_upstream(self, client_sock):
        first_flag = True
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_sock.settimeout(my_socket_timeout)
        while True:
            try:
                if( first_flag == True ):                        
                    first_flag = False

                    time.sleep(first_time_sleep)   # speed control + waiting for packet to fully recieve
                    data = client_sock.recv(16384)
                    #print('len data -> ',str(len(data)))                
                    #print('user talk :')
                    
                    Cloudflare_IP = next(cloudflare_ips_iterator)

                    if data:                                                                    
                        backend_sock.connect((Cloudflare_IP,Cloudflare_port))
                        thread_down = threading.Thread(target = self.my_downstream , args = (backend_sock , client_sock) )
                        thread_down.daemon = True
                        thread_down.start()
                        # backend_sock.sendall(data)    
                        send_data_in_fragment(data,backend_sock,Cloudflare_IP)

                    else:                   
                        raise Exception('cli syn close')

                else:
                    data = client_sock.recv(4096)
                    if data:
                        backend_sock.sendall(data)
                    else:
                        raise Exception('cli pipe close')
                    
            except Exception as e:
                #print('upstream : '+ repr(e) )
                time.sleep(2) # wait two second for another thread to flush
                client_sock.close()
                backend_sock.close()
                return False



            
    def my_downstream(self, backend_sock , client_sock):
        first_flag = True
        while True:
            try:
                if( first_flag == True ):
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
            
            except Exception as e:
                #print('downstream '+backend_name +' : '+ repr(e)) 
                time.sleep(2) # wait two second for another thread to flush
                backend_sock.close()
                client_sock.close()
                return False


def send_data_in_fragment(data , sock, ip):
    for i in range(0, len(data), L_fragment):
        fragment_data = data[i:i+L_fragment]
        print('send ',len(fragment_data),' bytes on ', ip)                        
        
        # sock.send(fragment_data)
        sock.sendall(fragment_data)

        time.sleep(fragment_sleep)

    print('----------finish------------')


print ("Now listening at: 127.0.0.1:"+str(listen_PORT))
ThreadedServer('',listen_PORT).listen()



    

#!/usr/bin/env python3

# Impoerts
import copy
import datetime
import logging
import os
import socket
import threading
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from random import choice

import ipcalc
import requests

# Codes here

if os.name == 'posix':
    print('os is linux')
    import resource  # ( -> pip install python-resources )

    # set linux max_num_open_socket from 1024 to 128k
    resource.setrlimit(resource.RLIMIT_NOFILE, (127000, 128000))



LISTEN_PORT = 2500    # pyprox listening to 127.0.0.1:LISTEN_PORT



CLOUDFLARE_IP_SUBNETS = tuple(requests.get("https://www.cloudflare.com/ips-v4").text.split("\n"))
CLOUDFLARE_IP_LIST = []
for cloud_flare_ip in CLOUDFLARE_IP_SUBNETS:
    for ip in ipcalc.Network(cloud_flare_ip):
        CLOUDFLARE_IP_LIST.append(ip.ip)
print(f"There is {len(CLOUDFLARE_IP_LIST)} cloudflare IP(s) found")




CLOUDFLARE_IP = '162.159.135.42'   # plos.org (can be any dirty cloudflare ip)
CLOUDFLARE_PORT = 443

L_FRAGMENT = 77   # length of fragments of Client Hello packet (L_FRAGMENT Byte in each chunk)
FRAGMENT_SLEEP = 0.2  # sleep between each fragment to make GFW-cache full so it forget previous chunks. LOL.



# ignore description below , its for old code , just leave it intact.
MY_SOCKET_TIMEOUT = 60 # default for google is ~21 sec , recommend 60 sec unless you have low ram and need close soon
FIRST_TIME_SLEEP = 0.01 # speed control , avoid server crash if huge number of users flooding (default 0.1)
ACCEPT_TIME_SLEEP = 0.01 # avoid server crash on flooding request -> max 100 sockets per second



class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host # There is no need to host any more
        self.port = port
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = socket.create_server(("", self.port)) # Create server on all interfaces ("127.0.0.1", "192.168.1.1", etc)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(128)  # up to 128 concurrent unaccepted socket queued , the more is refused untill accepting those.
        while True:
            client_sock , client_addr = self.sock.accept()                    
            client_sock.settimeout(MY_SOCKET_TIMEOUT)
            
            #print('someone connected')
            time.sleep(ACCEPT_TIME_SLEEP)   # avoid server crash on flooding request
            thread_up = threading.Thread(target = self.my_upstream , args =(client_sock,) )
            thread_up.daemon = True   #avoid memory leak by telling os its belong to main program , its not a separate program , so gc collect it when thread finish
            thread_up.start()
            

    def my_upstream(self, client_sock):
        first_flag = True
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_sock.settimeout(MY_SOCKET_TIMEOUT)
        backend_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)   #force localhost kernel to send TCP packet immediately (idea: @free_the_internet)

        while True:
            try:
                if( first_flag == True ):                        
                    first_flag = False

                    time.sleep(FIRST_TIME_SLEEP)   # speed control + waiting for packet to fully recieve
                    data = client_sock.recv(16384)
                    #print('len data -> ',str(len(data)))                
                    #print('user talk :')

                    if data:                                                                    
                        backend_sock.connect((CLOUDFLARE_IP,CLOUDFLARE_PORT))
                        thread_down = threading.Thread(target = self.my_downstream , args = (backend_sock , client_sock) )
                        thread_down.daemon = True
                        thread_down.start()
                        # backend_sock.sendall(data)    
                        send_data_in_fragment(data,backend_sock)

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


def send_data_in_fragment(data , sock):
    
    for i in range(0, len(data), L_FRAGMENT):
        fragment_data = data[i:i+L_FRAGMENT]
        print('send ',len(fragment_data),' bytes')                        
        
        # sock.send(fragment_data)
        sock.sendall(fragment_data)

        time.sleep(FRAGMENT_SLEEP)

    print('----------finish------------')




if __name__ == "__main__":
    print ("Now listening at: 127.0.0.1:"+str(LISTEN_PORT))
    ThreadedServer('',LISTEN_PORT).listen()


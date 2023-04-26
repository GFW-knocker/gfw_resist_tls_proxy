#!/usr/bin/env python3

import socket
import threading
from pathlib import Path
import os
import copy
import time
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import random

if os.name == 'posix':
    print('os is linux')
    import resource   # ( -> pip install python-resources )
    # set linux max_num_open_socket from 1024 to 128k
    resource.setrlimit(resource.RLIMIT_NOFILE, (127000, 128000))



listen_PORT = 2500    # pyprox listening to 127.0.0.1:listen_PORT

Cloudflare_IP = [
    {
        'ip': '104.20.176.67',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.20.173.46',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.20.176.165',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.22.50.19',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.26.15.45',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.23.107.230',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.22.50.169',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.21.97.235',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.26.15.40',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.21.54.169',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.20.194.219',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.22.50.28',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.23.107.40',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.20.176.153',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.22.50.50',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.26.15.79',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.22.50.22',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.23.107.98',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.20.173.34',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.26.15.56',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.22.50.16',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.26.15.50',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.22.50.247',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.22.50.37',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.23.107.130',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.19.96.249',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.17.122.243',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.17.232.131',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.19.96.194',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.17.232.11',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.19.96.177',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.19.96.215',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.19.96.155',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.17.232.168',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.17.122.15',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.17.122.41',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.17.232.127',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.16.240.74',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.16.240.35',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    },
    {
        'ip': '104.17.122.0',
        'connectCount': 0,
        'sumTime': 0,
        'average': 0,
        'errcount': 0
    }
]
curip = 0

Cloudflare_port = 443

L_fragment = 77   # length of fragments of Client Hello packet (L_fragment Byte in each chunk)
fragment_sleep = 0.2  # sleep between each fragment to make GFW-cache full so it forget previous chunks. LOL.



# ignore description below , its for old code , just leave it intact.
my_socket_timeout = 60 # default for google is ~21 sec , recommend 60 sec unless you have low ram and need close soon
first_time_sleep = 0.01 # speed control , avoid server crash if huge number of users flooding (default 0.1)
accept_time_sleep = 0.01 # avoid server crash on flooding request -> max 100 sockets per second


lastPacketTime = time.time()


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
        global curip
        global lastPacketTime
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

                    if data:                                                                    
                        befip = curip
                        curip = Cloudflare_IP.index(min(Cloudflare_IP,key=lambda x:x['average']))
                        if(befip==curip and (lastPacketTime+20<time.time())):
                            Cloudflare_IP[curip]['errcount'] += 250
                            Cloudflare_IP[curip]['average'] += 500
                        backend_sock.connect((Cloudflare_IP[curip]['ip'],Cloudflare_port))
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
                Cloudflare_IP[curip]['errcount']+=1
                # print('upstream : '+ repr(e) + "\n")
                time.sleep(0.2) # wait two second for another thread to flush
                client_sock.close()
                backend_sock.close()
                return False



            
    def my_downstream(self, backend_sock , client_sock):
        global curip
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
                Cloudflare_IP[curip]['errcount']+=1
                # print('downstream : '+ repr(e) + "\n") 
                time.sleep(0.2) # wait two second for another thread to flush
                backend_sock.close()
                client_sock.close()
                return False
            


def send_data_in_fragment(data , sock):
    global curip
    global lastPacketTime
    connectTime = time.time()
    for i in range(0, len(data), L_fragment):
        fragment_data = data[i:i+L_fragment]
        print('   send ',len(fragment_data),' bytes with ', Cloudflare_IP[curip]['ip']," (",curip,")                ")                        
        
        # sock.send(fragment_data)
        sock.sendall(fragment_data)

        time.sleep(fragment_sleep)
    lastPacketTime = time.time()
    Cloudflare_IP[curip]['connectCount'] += len(data)
    Cloudflare_IP[curip]['sumTime'] += time.time() - connectTime
    Cloudflare_IP[curip]['average'] = Cloudflare_IP[curip]['connectCount'] / (Cloudflare_IP[curip]['sumTime'] + (Cloudflare_IP[curip]['errcount'] * 5))
    # print('----------finish------------')


print ("    Now listening at: 127.0.0.1:"+str(listen_PORT) + "\n\n")
ThreadedServer('',listen_PORT).listen()


#!/usr/bin/env python3

import socket
import threading
from pathlib import Path
import os
import copy
import time
import datetime
import logging
import random
from logging.handlers import TimedRotatingFileHandler




num_fragment = 27  # total number of chunks that ClientHello devided into (chunks with random size)
fragment_sleep = 0.001  # sleep between each fragment to make GFW-cache full so it forget previous chunks. LOL.


Google_IP = '216.239.38.120'   # ( www.google.com IP)
googlevideo_IP = '74.125.98.10'
# '180.150.1.14'  
# '173.194.182.234'  rr5---sn-4g5e6nsz.googlevideo.com
# '74.125.98.10'     rr5---sn-hju7enll.googlevideo.com
# '110.50.80.143'    google Edge CDN
# '63.64.3.14'       google Edge CDN
# '172.253.122.100'  suggestqueries-clients6.youtube.com
# '142.251.16.91'    youtube-ui.l.google.com , www.youtube.com
# '134.0.218.206'    rr3.sn-vh5ouxa-hjuz.googlevideo.com
# '172.253.122.132'  lh3.googleusercontent.com
# '142.251.167.94'   ssl.gstatic.com
# '142.251.16.119'   i.ytimg.com
# '142.251.16.95'    jnn-pa.googleapis.com




listen_PORT_google = 2500    # (if you change the port , you need to change port in youtube_config.json too , in section outbound -> freedom -> reverseTLS -> "redirect": "127.0.0.1:2500")  
listen_PORT_youtube = 2501    # (if you change the port , you need to change port in youtube_config.json too , in section outbound -> freedom -> reverseTLS -> "redirect": "127.0.0.1:2501")  



# ignore description below , its for old code , just leave it intact.
my_socket_timeout = 21 # default for google is ~21 sec , recommend 60 sec unless you have low ram and need close soon
first_time_sleep = 0.1 # speed control , avoid server crash if huge number of users flooding
accept_time_sleep = 0.01 # avoid server crash on flooding request -> max 100 sockets per second



class ThreadedServer(object):
    def __init__(self, host, port1 , port2 ):
        self.host = host
    
        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock1.bind((host, port1))

        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock2.bind((host, port2))


    def multi_listen(self):
        thread_web = threading.Thread(target = self.listen , args = (self.sock1,Google_IP) )
        # thread_web.daemon = True
        thread_web.start()
        thread_video = threading.Thread(target = self.listen , args = (self.sock2,googlevideo_IP) )
        # thread_video.daemon = True
        thread_video.start()


    def listen(self , sock , remote_ip):
        sock.listen(128)  # up to 128 concurrent unaccepted socket queued , the more is refused untill accepting those.
        while True:
            client_sock , client_addr = sock.accept()                    
            client_sock.settimeout(my_socket_timeout)
            
            #print('someone connected')
            time.sleep(accept_time_sleep)   # avoid server crash on flooding request
            thread_up = threading.Thread(target = self.my_upstream , args =(client_sock,remote_ip) )
            thread_up.daemon = True   #avoid memory leak by telling os its belong to main program , its not a separate program , so gc collect it when thread finish
            thread_up.start()
            

    def my_upstream(self, client_sock,remote_ip):
        first_flag = True
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_sock.settimeout(my_socket_timeout)
        backend_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)   #force localhost kernel to send TCP packet immediately (idea: @free_the_internet)

        while True:
            try:
                if( first_flag == True ):                        
                    first_flag = False

                    time.sleep(first_time_sleep)   # speed control + waiting for packet to fully recieve
                    data = client_sock.recv(16384)
                    #print('len data -> ',str(len(data)))                
                    #print('user talk :')

                    if data:                                                                    
                        backend_sock.connect((remote_ip,443))
                        thread_down = threading.Thread(target = self.my_downstream , args = (backend_sock , client_sock) )
                        thread_down.daemon = True
                        thread_down.start()
                        # backend_sock.sendall(data)    
                        send_data_in_fragment(data,backend_sock)

                    else:                   
                        raise Exception('cli syn close')

                else:
                    data = client_sock.recv(16384)
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
    L_data = len(data)
    indices = random.sample(range(1,L_data-1), num_fragment-1)
    indices.sort()
    print('indices=',indices)

    i_pre=0
    for i in indices:
        fragment_data = data[i_pre:i]
        i_pre=i
        # print('send ',len(fragment_data),' bytes')                        
        
        # sock.send(fragment_data)
        sock.sendall(fragment_data)
        
        time.sleep(fragment_sleep)
    
    fragment_data = data[i_pre:L_data]
    sock.sendall(fragment_data)
    print('----------finish------------')


ThreadedServer('',listen_PORT_google,listen_PORT_youtube).multi_listen()
print ("now listening at: 127.0.0.1:"+str(listen_PORT_google),' for web')
print ("Now listening at: 127.0.0.1:"+str(listen_PORT_youtube),' for video')




    

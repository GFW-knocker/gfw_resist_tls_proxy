#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import socket
import random
import threading
from pathlib import Path
import os
import copy
import time
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import json

def choose_random_ip_with_operator(json_data, operator_code):
    # Decode JSON data
    data = json.loads(json_data)

    # Search for IPv4 addresses with the specified operator code
    matching_ips = []
    for ipv4_address in data["ipv4"]:
        if ipv4_address["operator"] == operator_code:
            matching_ips.append(ipv4_address["ip"])

    # Count how many IPv4 addresses have the operator code
    matching_count = len(matching_ips)

    # If there are any matching IPs, choose one at random and return it
    if matching_count > 0:
        random_index = random.randint(0, matching_count - 1)
        random_ip = matching_ips[random_index]
        return random_ip
    else:
        return None


if os.name == 'posix':
    print('os is linux')
    import resource   # ( -> pip install python-resources )
    # به صورت خودکار با شناسایی ماکزیمم لیمیت اقدام به تنظیم آن روی سیستم های لینوکسی میکند.
    soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))
    
# با این پورت به 127.0.0.1 گوش می دهد
listen_PORT = int(input("Port Listening  khodeton ro vared konid : "))

# آیپی تمیز یا کثیف کلودفلر
Cloudflare_IP = input("agar IP tamiz Cloudflare darid vared konid : ")
if Cloudflare_IP == "":
    response = requests.get("https://raw.githubusercontent.com/yebekhe/cf-clean-ip-resolver/main/list.json")
    json_data = response.content
    
    print("1. Automatic")
    print("2. Hamrah aval")
    print("3. Irancell")
    print("4. Rightel")
    print("5. Mokhaberat")
    print("6. HiWeb")
    print("7. Asiatek")
    print("8. Shatel")
    print("9. ParsOnline")
    print("10. MobinNet")
    print("11. AndisheSabzKhazar")
    print("12. Respina")
    print("13. AfraNet")
    print("14. ZiTel")
    print("15. Pishgaman")
    print("16. Arax")
    print("17. SamanTel")
    print("18. FanAva")
    print("19. DidebanNet")
    print("20. UpTel")
    print("21. FanupTelecom")
    print("22. RayNet")
    choice = input("Adad Operator khodetun ro vared konid: ")
    
    if choice == "1":
        Cloudflare_IP = '162.159.36.93'
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "2":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "MCI")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "3":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "MTN")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "4":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "RTL")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "5":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "MKH")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "6":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "HWB")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "7":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "AST")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "8":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "SHT")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "9":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "PRS")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "10":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "MBT")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "11":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "ASK")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "12":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "RSP")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "13":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "AFN")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "14":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "ZTL")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "15":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "PSM")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "16":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "ARX")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "17":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "SMT")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "18":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "FNV")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "19":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "DBN")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "20":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "APT")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "21":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "FNP")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    elif choice == "22":
        Cloudflare_IP = choose_random_ip_with_operator(json_data, "RYN")
        print(f"IP tamiz shoma : {Cloudflare_IP}")
    else:
        print("Lotfan yeki az Operator ha ro entekhab konid!")

Cloudflare_port = int(input("Port Config Xray khodeton ro vared konid : "))

#اگر سیستم ضعیف دارید مقدار 60 رو کمتر قرار بدید
my_socket_timeout = 60
first_time_sleep = 0.01 # کنترل سرعت، جلوگیری از خرابی سرور در صورت فلود کردن تعداد زیادی از کاربران (پیش‌فرض 0.01)
accept_time_sleep = 0.01 # جلوگیری از خرابی سرور در صورت فلود شدن درخواست ها -> حداکثر 100 سوکت در ثانیه



class ThreadedServer(object):                        
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(128) 
        
        while True:
            client_sock , client_addr = self.sock.accept()                   
            client_sock.settimeout(my_socket_timeout)
            
            time.sleep(accept_time_sleep) 
            thread_up = threading.Thread(target = self.my_upstream , args =(client_sock,) )
            thread_up.daemon = True 
            thread_up.start()
            

    def my_upstream(self, client_sock):
        first_flag = True
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_sock.settimeout(my_socket_timeout)
        while True:
            try:
                if( first_flag == True ):                        
                    first_flag = False

                    time.sleep(first_time_sleep)   # کنترل سرعت + انتظار برای دریافت کامل بسته
                    data = client_sock.recv(16384)

                    if data:                                                                    
                        backend_sock.connect((Cloudflare_IP,Cloudflare_port))
                        thread_down = threading.Thread(target = self.my_downstream , args = (backend_sock , client_sock) )
                        thread_down.daemon = True
                        thread_down.start()
                        # تنظیم خودکار L_fragment و fragment_sleep  
                        data_len = len(data)
                        L_fragment = random.randint(25, data_len // 3)
                        fragment_sleep = 0.0025974025974026 * L_fragment
                        send_data_in_fragment(data,backend_sock,L_fragment,fragment_sleep)

                    else:                   
                        raise Exception('cli syn close')

                else:
                    data = client_sock.recv(4096)
                    if data:
                        backend_sock.sendall(data)
                    else:
                        raise Exception('cli pipe close')
                    
            except Exception as e:
                time.sleep(2)
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
                time.sleep(2)
                backend_sock.close()
                client_sock.close()
                return False


def send_data_in_fragment(data , sock , L_fragment , fragment_sleep):
    for i in range(0, len(data), L_fragment):
        fragment_data = data[i:i+L_fragment]
        print('send ',len(fragment_data),' bytes')                        
        
        # sock.send(fragment_data)
        sock.sendall(fragment_data)

        time.sleep(fragment_sleep)

    print('----------finish------------')


print ("Now listening at: 127.0.0.1:"+str(listen_PORT))
ThreadedServer('',listen_PORT).listen()

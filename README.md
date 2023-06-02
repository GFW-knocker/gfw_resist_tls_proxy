# load balancer with multiple cloudflare ip 
improve upload and download speed by connecting to multiple cloudflare server

# for pyprox_tcp_randchunk.py
set in config.ini
- your list of cloudflare_ip
- num_fragment between 1 to 100
- fragment_sleep between 0.001 to 0.01

# for pyprox_tcp.py
set in config.ini
- your list of cloudflare_ip
- L_fragment = 77
- L_fragment_sleep = 0.2



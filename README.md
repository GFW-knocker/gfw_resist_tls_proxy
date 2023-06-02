# load balancer with multiple cloudflare ip 
load balancing idea by <a href="https://github.com/nvv1d">nvv1d</a><br>
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

# update 1402-3-12
- add randchunk
- add tcp-no-delay
- fix round robin issue
- remove invalid ips from config

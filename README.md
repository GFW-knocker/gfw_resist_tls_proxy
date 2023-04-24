# gfw_resist_tls_proxy
# internet for everyone or no one
سلام گرم به همه دوستانی که برای حق اولیه و ابتدایی شهروندی ، برای دسترسی به اینترنت ، تلاش میکنند
<br>
سلام به هیدیفای،باشسیز،سگارو،آی آر سی اف ، پروژه امید، یوتیوبرها و همه عزیزان دوست داشتنی
<br>
روش این پیج یک زخم عمیق بر پیکر  GFW  می گذارد که تا سالها سوزش آن در ماتحت فیلترچیان دنیا باقی خواهد ماند
<br>
<br>
# goodbye SNI filtering & goodbye GFW mf'er
<img src="/asset/meme1.jpg?raw=true" width="300" >
<br><br>

# main Idea:
in TLS protocol (even latest v1.3)  SNI transfered in plain-text<br>
GFW find it and when SNI is not in whitelist reply with TCP-RST<br>
so it filter cloudflare-ip , based on SNI , such that some popular sites<br>
like plos.org is open , and all other sites closed , through that ip<br>
so we need to hide SNI from GFW<br>
we fragment TLS "client Hello" packet into chunks in a simple manner<br>
we show that it pass the firewall<br>
more importantly we show that GFW cant fix it because its nearly impossible<br>
to cache TBs of data in high speed router , so they MUST give up or break the whole network<br>
<br>
<img src="/asset/slide1.png?raw=true" width="600" >
<br><br>


# about SNI , ESNI & ECH (skip if you want)
leaking domain name (SNI) is the old famous bug of tls protocol which is not fixed yet as of 2023<br>
some attempt started few years ago , was trying to encrypt sni called ESNI which is deprecated today<br>
cloudflare stop supporting esni in summer 2022<br>
another way is Encrypted Client Hello (ECH) which is in draft version and well-documented<br>
i make much effort to use ECH but its too complex and still is in development<br>
also its based on DNS-over-HTTPS which is already filtered by GFW<br>

# about GFW SNI filtering on cloudflare IPs (skip if you want)
cloudflare IPs are high traffic and 30% of web is behind them<br>
so GFW cant simply block them by traffic volume<br>
and all traffic is encrypted except client hello which leak server name (SNI)<br>
<br><br>
so GFW extract sni from client hello and when SNI is in white list it pass<br><br>
![Alt text](/asset/plos-not-filtered.png?raw=true "plos.org is in whitelist")
<br><br>
otherwise it send TCP-RST to terminate tcp socket<br><br>
![Alt text](/asset/youtube-filtered.png?raw=true "youtube is in backlist")
<br><br>

# about packet fragment (skip if you want)
we hide sni by fragmenting client hello packet into several chunk.<br>
but GFW already know this and try to assemble those chunk to find SNI! LOL<br>
but we add time delay between fragment. LOL<br>
since cloudflare IPs have too much traffic , GFW cant wait too long. LOL<br>
GFW high-speed cache is limited so it cant cache TBs of data looking for a tiny tcp fragment. LOL<br>
so it forget those fragments after a second. LOL<br>
its impossible to looking at huge traffic for a packet didnt know when or where it arrive. LOL<br>
so it forced to Give up. LOL<br>

# how to run
1. assume that you have cv2ray config {websocket+tls+Cloudflare}<br>
2. setup your pyprox listen port and cloudflare ip<br>
<img src="/asset/pyprox_tcp_setup.png?raw=true" width="400" ><br>
3. setup your v2ray client to forward to 127.0.0.1:listen_port<br>
<img src="/asset/v2rayng_setup.png?raw=true" width="400" ><br>
4. on your local machine run<br>
<code>python pyprox_tcp.py</code><br>
5. monitor traffic by wireshark or microsoft network monitor<br>
6. adjast fragment_size & fragment_sleep<br>
typical Client Hello packet is ~300 byte<br>
we split 300 into {77+77+77+69} and send each by delay of 0.2 second<br>
<code>fragment_size=77 byte  ,  fragment_sleep=0.2 sec -> moderate packet size with moderate delay -> work good</code><br>
another setup might be:<br>
<code>fragment_size=17 byte  ,  fragment_sleep=0.03 sec -> too small chunk with less delay -> work good</code><br>
<code>too big chunk -> assembled by GFW -> TCP-RST recieved</code><br>
<code>too small delay  -> assembled by GFW -> TCP-RST recieved</code><br>


# we are working on it to adjast parameters better
stay tuned!


# gfw_resist_tls_proxy
# internet for everyone or no one
سلام گرم به همه دوستانی که برای حق اولیه و ابتدایی شهروندی ، برای دسترسی به اینترنت ، تلاش میکنند
<br>
سلام به هیدیفای،باشسیز،سگارو،آی آر سی اف ، پروژه امید،ثنایی،هگزا، یوتیوبرها و همه عزیزان دوست داشتنی
<br><br>
روش این پیج یک زخم عمیق بر پیکر  GFW  می گذارد که تا سالها سوزش آن در ماتحت فیلترچیان دنیا باقی خواهد ماند
<br>
<br>
خلاصه کار به فارسی:<br>
روترهای gfw تلاش میکنند اما نمیتوانند همه packet های fragment را سرهم کنند زمانی که delay بین پکت ها باشد<br>
چرا؟ چون کل ترافیک کشور ازشون عبور میکنه و براشون سخته و cache  محدود دارند و باید سریع باشند<br>
از طرفی gfw نمیتونه پکت های فرگمنت رو reject کنه چون اولا fragmet جزو اصول شبکه هست ثانیا در خیلی از نت های ضعیف packet ها تکه میشوند<br>
در صورت reject کردن نت بسیاری از گوشی های قدیمی و خطوط ضعیف مختل میشه<br>
همچنین در مسیر روترهای پرسرعت fragmentation اتفاق می افته<br>
و اینو gfw میدونه بنابراین سعی میکنه اسمبل کنه و اگر نتونه عبور میده<br> 
سرورها ولی موظف به سرهم کردن fragment ها هستند چون در پروتکل ip قید شده و سرشون به اندازه gfw شلوغ نیست<br>
سرورهای کلودفلر به خوبی این کارو میکنن<br>
باور کنید یا نکنید کار gfw ساختست<br>
الان عمده ترافیک TLS هست و تنها با تحلیل SNI میتونه ترافیک TLS رو تفکیک کنه<br>
و ما کار رو براش پردازش بر و هزینه بر میکنیم<br>
یا باید کل cloudflare رو با همه سایت هاش ببنده و عملا نت جهانی رو قطع کنه<br>
 یا باید فرگمنت رو drop کنه که در هر صورت سیستم های خودشون هم دچار اختلال میشه<br>
این سیستم تست شده و کار میکنه<br>
با اندکی تنظیمات ، سرعت handshake اول هم بالا خواهد رفت<br>
اینترنت برای همه یا برای هیچکس<br>


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
leaking domain name (SNI) is the old famous bug of TLS protocol which is not fixed yet as of 2023<br>
some attempt started few years ago , was trying to encrypt sni called ESNI which is deprecated today<br>
cloudflare stop supporting esni in summer 2022<br>
another way is Encrypted Client Hello (ECH) which is in draft version and not well-documented<br>
i made much effort to use ECH but its too complex and still is in development<br>
also its based on DNS-over-HTTPS which is already filtered by GFW<br>

# about GFW SNI filtering on cloudflare IPs (skip if you want)
cloudflare IPs are high traffic and 30% of web is behind them<br>
so GFW cant simply block them by traffic volume<br>
and all traffic is encrypted except client hello which leak server name (SNI)<br>
<br><br>
so GFW extract sni from client hello and when SNI is in white list it pass<br><br>
![Alt text](/asset/plos-not-filtered.png?raw=true "plos.org is in whitelist")
<br><br>
if SNI in in blacklist , GFW send TCP-RST to terminate tcp socket<br><br>
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
1. assume that you have v2ray config {websocket+tls+Cloudflare}<br>
2. setup pyprox listen_port and cloudflare_dirty_ip<br>
<img src="/asset/pyprox_tcp_setup.png?raw=true" ><br>
3. setup your v2ray client to forward to 127.0.0.1:listen_port<br>
<img src="/asset/v2rayng_setup.png?raw=true" ><br>
4. on your local machine run<br>
<code>python pyprox_tcp.py</code><br>
5. monitor traffic by wireshark or microsoft network monitor<br>
6. adjast fragment_size & fragment_sleep<br>
typical Client Hello packet is ~300 byte<br>
we split 300 into {77+77+77+69} and send each by delay of 0.3 second<br>
<code>fragment_size=77 byte  ,  fragment_sleep=0.3 sec -> moderate packet size with moderate delay -> work good</code><br>
another setup might be:<br>
<code>fragment_size=77 byte  ,  fragment_sleep=0.2 sec -> moderate packet size with moderate delay -> work nice</code><br>
<code>fragment_size=17 byte  ,  fragment_sleep=0.03 sec -> too small chunk with less delay -> work good</code><br>
<code>too big chunk -> assembled by GFW -> TCP-RST recieved</code><br>
<code>too small delay  -> assembled by GFW -> TCP-RST recieved</code><br>
7. just surf the web using your filtered sni and a dirty cloudflare IP !<br>

# we are working on it to adjast parameters better
it might be slow at initiating tls handshake<br>
but we make it better by setting up persistent TLS<br>
stay tuned!<br>

# need help to implement it into v2ray clients or xray-core
any ideas are welcome<br>



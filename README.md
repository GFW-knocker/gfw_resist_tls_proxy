# gfw_resist_tls_proxy
# internet for everyone or no one
سلام گرم به همه دوستانی که برای حق اولیه و ابتدایی شهروندی، دسترسی به اینترنت، تلاش می‌کنند.
<br>
سلام به هیدیفای، باشسیز، سگارو، آی آر سی اف، پروژه امید، ثنایی، هگزا، وحید، صفا، اردشیر، ایمان، امین، حسین، یوتیوبرها و همه‌ی عزیزان دوست داشتنی!
<br><br>
روش این پیج، یک زخم عمیق بر پیکر  GFW  می‌گذارد که تا سال‌ها سوزش آن در ماتحت فیلترچیان دنیا باقی خواهد ماند. 😁	
<br>
<br>
خلاصه‌ی کار به فارسی:<br>
روترهای gfw تلاش می‌کنن، اما نمی‌تونن همه‌ی packet های fragment را زمانی که delay بین پکت ها باشه سرهم کنن. <br>
چرا؟ چون کل ترافیک کشور ازشون عبور می‌کنه و براشون سخته؛ همچنین، cache  محدود دارن و باید سریع باشن.<br>
از طرفی، gfw نمی‌تونه پکت‌های فرگمنت رو reject کنه چون اولاً fragmet جزو اصول شبکه هست؛<br>
ثانیاً در خیلی از نت های ضعیف، packet ها تکه می‌شن.<br>
در صورت reject کردن، نت بسیاری از گوشی‌های قدیمی و خطوط ضعیف مختل می‌شه.<br>
همچنین، در مسیر روترهای پرسرعت fragmentation اتفاق می‌افته.<br>
و gfw این رو می‌دونه؛ بنابراین سعی می‌کنه اسمبل کنه و اگه نتونه، عبور می‌ده.<br> 
سرورها اما، موظف به سرهم کردن fragment ها هستن؛ چون در پروتکل اینترنت (ip) قید شده و سرشون به اندازه‌ی gfw شلوغ نیست.<br>
سرورهای کلودفلر به خوبی این کار رو می‌کنن.<br>
باور کنید یا نه، کار gfw ساخته‌ست!<br>
در حال حاضر عمده‌ی ترافیک TLS هست و تنها با تحلیل SNI می‌تونه ترافیک TLS رو تفکیک کنه؛<br>
و ما کار رو براش هزینه‌بر و پر پردازش می‌کنیم.<br>
یا باید کل cloudflare رو با همه‌ی سایت‌هاش ببنده و عملاً نت جهانی رو قطع کنه،<br>
یا باید فرگمنت رو drop کنه؛ که در هر صورت سیستم‌های خودشون هم دچار اختلال می‌شه.<br>
*این سیستم تست شده و کار میکنه*<br>
شما با domain فیلتر شده و با ip کثیف cloudflare می‌تونید از gfw عبور کنید.<br>
با تنظیمات اندک، سرعت handshake اول هم بالا خواهد رفت.<br>
اینترنت برای همه یا برای هیچکس!<br>


# goodbye SNI filtering & goodbye GFW mf'er
<img src="/asset/meme1.jpg?raw=true" width="300" >
<br><br>

# main Idea:
in TLS protocol (even latest v1.3)  SNI is transfered in plain-text.<br>
GFW finds it and when SNI is not in whitelist, replies with TCP-RST.<br>
So that filters cloudflare-ip, based on the SNI, such that some popular sites<br>
like plos.org is open; and all other sites are closed through that ip.<br>
Therefore, we need to hide SNI from GFW.<br>
We fragment TLS "client Hello" packet into chunks in a simple manner.<br>
We show that it'll pass the firewall;<br>
more importantly, we show that GFW can't fix it. Because its nearly impossible<br>
to cache TBs of data in high speed router. Hence, they MUST give up or break the whole network.<br>
<br>
<img src="/asset/slide1.png?raw=true" width="600" >
<br><br>


# about SNI, ESNI & ECH (skip if you want)
leaking domain name (SNI) is the old famous bug of TLS protocol which is not fixed yet as of 2023.<br>
Some attempts started few years ago, trying to encrypt SNI in a project called ESNI which is deprecated today.<br>
cloudflare stopped supporting ESNI in summer 2022.<br>
Another way is the Encrypted Client Hello (ECH) which is in draft version and not well-documented.<br>
I made so much effort to use ECH, but its too complex and still in development.<br>
Also, it's based on DNS-over-HTTPS which is already filtered by GFW.<br>

# about GFW SNI filtering on cloudflare IPs (skip if you want)
cloudflare IPs are high traffic and 30% of web is behind them;<br>
So GFW can't simply block them by traffic volume.<br>
Plus, all the traffic is encrypted except for client hello which leaks the server name (SNI).<br>
<br><br>
So GFW extracts SNI from client hello and when SNI is in white list, it passes.<br><br>
![Alt text](/asset/plos-not-filtered.png?raw=true "plos.org is in whitelist")
<br><br>
But if SNI is in blacklist, GFW sends TCP-RST to terminate the tcp socket.<br><br>
![Alt text](/asset/youtube-filtered.png?raw=true "youtube is in backlist")
<br><br>

# about packet fragment (skip if you want)
We hide SNI by fragmenting client hello packet into several chunks.<br>
But GFW already knew this and tries to assemble those chunks to find SNI!<br>
So, we add a time delay between fragment. LOL.<br>
Since cloudflare IPs have too much traffic, GFW is not able to wait too long. LOL<br>
GFW high-speed cache is limited so it doesn't have the ability to cache TBs of data looking for a tiny tcp fragment. LOL<br>
And that's why, it forgets those fragments after a second. LOL<br>
It's impossible to looking at huge traffic for a packet not knowing when or where it has arrived. LOL<br>
So it's forced to give up! 😁<br>

# how to run
1. Assume that you have v2ray config {websocket+tls+Cloudflare}.<br>
2. Setup pyprox listen_port and cloudflare_dirty_ip.<br>
<img src="/asset/pyprox_tcp_setup.png?raw=true" ><br>
3. Setup your v2ray client to forward to 127.0.0.1:listen_port<br>
<img src="/asset/v2rayng_setup.png?raw=true".><br>
4. Nn your local machine, run<br>
<code>python pyprox_tcp.py</code.><br>
5. Monitor traffic by Wireshark or Microsoft Network Monitor.<br>
6. Adjust fragment_size & fragment_sleep.<br>
Typical Client Hello packet is ~300 byte.<br>
We split 300 into {77+77+77+69} and send each by delay of 0.3 second.<br>
<code>fragment_size=77 byte  ,  fragment_sleep=0.3 sec -> moderate packet sizes with moderated delays -> works good</code><br>
another setup might be:<br>
<code>fragment_size=77 byte  ,  fragment_sleep=0.2 sec -> moderate packet sizes with moderated delays -> works nice</code><br>
<code>fragment_size=17 byte  ,  fragment_sleep=0.03 sec -> very small chunk with less delay -> works good</code><br>
<code>very big chunk -> assembled by GFW -> TCP-RST recieved</code><br>
<code>too small delay  -> assembled by GFW -> TCP-RST recieved</code><br>
7. Just surf the web using your filtered SNI and a dirty cloudflare IP!<br>

# we are working on it to adjust parameters better
it might be slow at initiating tls handshake;<br>
but we make it better by setting up persistent TLS.<br>
Stay tuned!<br>

# TO DO NEXT
1. Implement this method into v2ray clients or xray-core -> Client Hello Fragmentation option.<br>
2. Setting up persistent TLS (thus one handshake is enough for everything).<br>
3. Sending TCP packets in reverse time order.<br>
4. All your ideas are welcome!<br>




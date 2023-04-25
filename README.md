# gfw_resist_tls_proxy
# آپدیت
رو ایرانسل پکت با موفقیت رد میشه ولی شدید کنده تحت بررسیه<br>
این محصول نهایی نیست یه اسکریپت پایتونه جهت اثبات ادعا<br>
بزارید به نقطه پایدار برسیم بعد برا کلاینت v2ray پیاده میشه<br>
الان متخصص حرفه ای شبکه و برنامه نویس c لازم داریم جهت تبادل اطلاعات<br>


# internet for everyone or no one
سلام گرم به همه دوستانی که برای حق اولیه و ابتدایی شهروندی ، برای دسترسی به اینترنت ، تلاش میکنند
<br>
سلام به هیدیفای،باشسیز،سگارو،آی آر سی اف،پروژه امید،ثنایی،هگزا،وحید،صفا،اردشیر،ایمان،امین،حسین، یوتیوبرها و همه عزیزان دوست داشتنی
<br><br>
روش این پیج یک زخم عمیق بر پیکر  GFW  می گذارد که تا سالها سوزش آن در ماتحت فیلترچیان دنیا باقی خواهد ماند
<br>
<br>
خلاصه کار به فارسی:<br>
روترهای gfw تلاش میکنند اما نمیتوانند همه packet های fragment را سرهم کنند زمانی که delay بین پکت ها باشد<br>
چرا؟ چون کل ترافیک کشور ازشون عبور میکنه و براشون سخته و cache  محدود دارند و باید سریع باشند<br>
از طرفی gfw نمیتونه پکت های فرگمنت رو reject کنه چون اولا fragmet جزو اصول شبکه هست<br>
ثانیا در خیلی از نت های ضعیف packet ها تکه میشوند<br>
در صورت reject کردن نت بسیاری از گوشی های قدیمی و خطوط ضعیف مختل میشه<br>
همچنین در مسیر روترهای پرسرعت fragmentation اتفاق می افته<br>
و اینو gfw میدونه بنابراین سعی میکنه اسمبل کنه و اگر نتونه عبور میده<br> 
سرورها ولی موظف به سرهم کردن fragment ها هستند چون در پروتکل ip قید شده و سرشون به اندازه gfw شلوغ نیست<br>
سرورهای کلودفلر به خوبی این کارو میکنن<br>
باور کنید یا نکنید کار gfw ساختست<br>
الان عمده ترافیک TLS هست و تنها با تحلیل SNI میتونه ترافیک TLS رو تفکیک کنه<br>
و ما کار رو براش هزینه بر و پردازش بر میکنیم<br>
یا باید کل cloudflare رو با همه سایت هاش ببنده و عملا نت جهانی رو قطع کنه<br>
 یا باید فرگمنت رو drop کنه که در هر صورت سیستم های خودشون هم دچار اختلال میشه<br>
این سیستم تست شده و کار میکنه<br>
و شما با domain فیلتر شده و با ip کثیف cloudflare میتوانید از gfw عبور کنید<br>
با اندکی تنظیمات ، سرعت handshake اول هم بالا خواهد رفت<br>
اینترنت برای همه یا برای هیچکس<br>


# goodbye SNI filtering & goodbye GFW mf'er
<img src="/asset/meme1.jpg?raw=true" width="300" >
<br><br>

# main Idea:
in TLS protocol (even latest v1.3)  SNI transferred in plain-text<br>
GFW finds it, and when SNI is not in the whitelist, replies with TCP-RST<br>
so it filter cloudflare-ip, based on SNI, such that some popular sites<br>
like plos.org is open, and all other sites closed, through that ip<br>
so we need to hide SNI from GFW<br>
we fragment TLS "client Hello" packet into chunks in a simple manner<br>
we show that it passes the firewall<br>
more importantly, we show that GFW can't fix it because its nearly impossible<br>
to cache TBs of data in high-speed router, so they MUST give up or break the whole network<br>
<br>
<img src="/asset/slide1.png?raw=true" width="600" >
<br><br>


# about SNI, ESNI & ECH (skip if you want)
leaking domain name (SNI) is the famous old bug of TLS protocol which is not fixed yet as of 2023<br>
some attempt started a few years ago trying to encrypt SNI called ESNI, which is deprecated today<br>
Cloudflare stopped supporting ESNI in the summer of 2022<br>
another way is Encrypted Client Hello (ECH), which is in draft version and not well-documented<br>
I made many efforts to use ECH, but its too complex and still is in development<br>
also its based on DNS-over-HTTPS which is already filtered by GFW<br>

# about GFW SNI filtering on Cloudflare IPs (skip if you want)
Cloudflare IPs are high traffic, and 30% of the web is behind them<br>
so GFW can't simply block them by traffic volume<br>
and all traffic is encrypted except client hello, which leaks server name (SNI)<br>
<br><br>
so GFW extracts SNI from client hello, and when SNI is in the whitelist, it passes <br><br>
![Alt text](/asset/plos-not-filtered.png?raw=true "plos.org is in whitelist")
<br><br>
if SNI is in the blacklist, GFW sends TCP-RST to terminate TCP socket<br><br>
![Alt text](/asset/youtube-filtered.png?raw=true "youtube is in backlist")
<br><br>

# about packet fragment (skip if you want)
we hide SNI by fragmenting client hello packet into several chunks.<br>
but GFW already knows this and tries assembling those chunks to find SNI! LOL<br>
but we add a time delay between fragments. LOL<br>
since Cloudflare IPs have too much traffic, GFW can't wait too long. LOL<br>
GFW high-speed cache is limited, so it can't cache TBs of data looking for a tiny TCP fragment. LOL<br>
so it forgets those fragments after a second. LOL<br>
it's impossible to look at huge traffic for a packet that don't know when or where it arrives. LOL<br>
so it's forced to Give up. LOL<br>

# How to run
1. assume that you have v2ray config {websocket+tls+Cloudflare}<br>
2. setup pyprox listen_port and cloudflare_dirty_ip<br>
<img src="/asset/pyprox_tcp_setup.png?raw=true" ><br>
3. setup your v2ray client to forward to 127.0.0.1:listen_port<br>
<img src="/asset/v2rayng_setup.png?raw=true" ><br>
4. on your local machine, run<br>
<code>python pyprox_tcp.py</code><br>
5. monitor traffic by Wireshark or Microsoft Network Monitor<br>
6. adjust fragment_size & fragment_sleep<br>
typical Client Hello packet is ~300 byte<br>
we split 300 into {77+77+77+69} and send each by delay of 0.3 second<br>
<code>fragment_size=77 byte  ,  fragment_sleep=0.3 sec -> moderate packet size with moderate delay -> work good</code><br>
another setup might be:<br>
<code>fragment_size=77 byte  ,  fragment_sleep=0.2 sec -> moderate packet size with moderate delay -> work nice</code><br>
<code>fragment_size=17 byte  ,  fragment_sleep=0.03 sec -> too small chunk with less delay -> work good</code><br>
<code>too big chunk -> assembled by GFW -> TCP-RST recieved</code><br>
<code>too small delay  -> assembled by GFW -> TCP-RST recieved</code><br>
7. just surf the web using your filtered SNI and a dirty Cloudflare IP !<br>

# We are working on it to adjust parameters better
it might be slow at initiating TLS handshake<br>
but we make it better by setting up persistent TLS<br>
stay tuned!<br>

# TO DO NEXT
1. implement into v2ray clients or xray-core -> Client Hello Fragmentation option<br>
2. setup persistent TLS (thus one handshake is enough for everything)<br>
3. sending TCP packet in reverse time order<br>
4. your ideas are welcome<br>



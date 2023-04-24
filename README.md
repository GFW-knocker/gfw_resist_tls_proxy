# gfw_resist_tls_proxy
# internet for everyone or no one
سلام گرم به همه دوستانی که برای حق اولیه و ابتدایی شهروندی ، برای دسترسی به اینترنت ، تلاش میکنند
<br>
سلام به هیدیفای،باشسیز،سگارو،آی آر سی اف ، پروژه امید، یوتیوبرها و همه عزیزان دوست داشتنی
<br>
روش این پیج یک زخم عمیق بر پیکر  GFW  می گذارد که تا سالها سوزش آن در ماتحت فیلترچیان دنیا باقی خواهد ماند
<br>

# main Idea:
in TLS protocol (even latest v1.3)  SNI transfered in plain-text<br>
GFW find it and when SNI is not in whitelist reply with TCP-RST<br>
so it filter cloudflare ip based on SNI such that some popular sites<br>
like plos.org be open and all others closed through that ip<br>
so we need to hide SNI from GFW<br>
we fragment TLS client Hello packet into chunks in a simple manner<br>
we show that it pass the firewall<br>
more importantly we show that GFW cant fix it because its nearly impossible <br>
to cache TBs of data in high speed router so they MUST give up or break the whole network<br>



# about SNI , ESNI & ECH (skip if you want)
leaking domain name (SNI) is the old famous bug of tls protocol which is not fixed yet as of 2023<br>
some attempt started few years ago is try to encrypt sni called ESNI which is deprecated today<br>
cloudflare stop supporting esni in summer 2022<br>
another way is Encrypted Client Hello (ECH) which is in draft version and well-documented<br>
i make much effort to use ECH but its too complex and still is in development<br>
also its based on DNS-over-HTTPS which is already filtered by GFW<br>

# about GFW SNI filtering on cloudflare IPs (skip if you want)
cloudflare IPs are high traffic and 30% of web is behind them<br>
so GFW cant simply block them by traffic volume<br>
and all traffic is encrypted except client hello which leak server name (SNI)<br>
so GFW extract sni from client hello and when SNI is in white list it pass<br>
otherwise it send TCP-RST to terminate tcp socket<br>

![Alt text](/asset/youtube-filtered.png?raw=true "youtube is in backlist")
<br>
![Alt text](/asset/plos-not-filtered.png?raw=true "plos.org is in whitelist")
<br>


# required for test
python 3<br>
wireshark or microsoft network monitor<br>



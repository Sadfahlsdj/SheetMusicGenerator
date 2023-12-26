import requests
from random import *
import json
from bs4 import BeautifulSoup
from LinkGenerator import get_permlinks

permlinks = get_permlinks()

# relevant html:
# <a rel="nofollow" class="external text" href="https://imslp.org/wiki/Special:ImageFromIndex/693320/hfpn"> == $0
# use the div class "we_file_download plainlinks"

"""
TODO:
It appears that after 10(?) downloads the website forces a 15 second wait period
Need to get around this
"""
def get_user_agent_list():
  response = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=' + "0c881a51-cebc-42fe-8e56-5910c43997fc")
  json_response = response.json()
  return json_response.get('result', [])

def get_random_user_agent(user_agent_list):
  random_index = randint(0, len(user_agent_list) - 1)
  return user_agent_list[random_index]

user_agent_list = get_user_agent_list()

"""
notes: proxyscrape sucks ass, it's fast(lol) but nearly all the proxies are broken
can load from proxies.txt for very very very slow process

try this later: https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/storage/#wiki_proxy_lists
"""
def get_proxies():
    url = ("https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt")
    # documentation: https://github.com/proxy4parsing
    # with this one, disregard the first element because it has some weird attachments

    response = requests.get(url)

    proxies = str(response.content).split('\\n')

    return [p.strip() for p in proxies]

proxies = get_proxies()[1:]
"""header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    }"""

"""
used for testing if proxies work; takes a LONG time so I gave up
for p in proxies[400:]:
    print(p)
    try:
        # https://ipecho.net/plain returns the ip address
        # of the current session if a GET request is sent.
        page = requests.get('https://ipecho.net/plain',
                            proxies={"http": p.strip(), "https": p.strip()}, headers=header, verify=False)
        print("Status OK, Output:", page.text)
    except OSError as e:
        print(e)
        proxies.remove(p)

for p in proxies:
    print(p)
    """
add_to_proxy_index = 0
def get_pdf(i):
    global add_to_proxy_index
    global user_agent_list

    proxyIndex = (i + add_to_proxy_index) % (len(proxies) - 1)
    proxy = proxies[proxyIndex]

    user_agent = get_random_user_agent(user_agent_list)
    header = {'User-Agent': user_agent}

    url = permlinks[i].strip() # should run on each permlink, i is the index
    try:
        page = requests.get(url,
                        proxies={"http": proxy.strip(), "https": proxy.strip()}, headers=header, verify=False)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="tabScore1")  # id that is closest to the link I want

        pdfurl = ""  # declaration to change later

        if type(results) is not None:  # does this even work?
            links = results.find_all('a', href=True)  # <a signifies links
            pdfurl = links[0]['href']
            # index 0 is the one we want, just happens to be the first href link in this id
            # takes us to disclaimer page

        # note: links have disclaimer pages, need to take steps to get around them
        pdfpage = requests.get(pdfurl,
                            proxies={"http": proxy.strip(), "https": proxy.strip()}, headers=header, verify=False)
        pdfsoup = BeautifulSoup(pdfpage.content, "html.parser")
        pdfresults = pdfsoup.find(id="wiki-body")

        if type(pdfresults) is not None:
            links = pdfresults.find_all('a', href=True)
            final_link = "https://imslp.org" + links[0]['href']
            with open("pdflinks.txt", 'w+', encoding='utf-8') as f:
                f.write(final_link + "\n")
            print(f"wrote {final_link}")
            # first link on the disclaimer page is the pdf link, need to add https to make it work

        """
        # code block for writing link contents to pdf, will save for later
        response = requests.get(final_link,
                               proxies={"http": proxy.strip(), "https": proxy.strip()}, headers=header, verify=False)
        pdfname = "pdf" + str(i) + ".pdf"  # naming convention
        with open(pdfname, 'wb') as pdf:
            pdf.write(response.content)  # writing to pdf on my own machine
        print(f"finished writing {pdfname}")
        """
    except:
        print(f"something went wrong with the proxy {proxy}")
        add_to_proxy_index += 1



for i in range(len(permlinks)):
    get_pdf(i)



import requests
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

def get_pdf(i):
    url = permlinks[i].strip() # should run on each permlink, i is the index
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="tabScore1") # id that is closest to the link I want

    pdfurl = "" # declaration to change later

    if type(results) is not None: # does this even work?
        links = results.find_all('a', href=True) # <a signifies links
        pdfurl = links[0]['href']
        # index 0 is the one we want, just happens to be the first href link in this id
        # takes us to disclaimer page

    # note: links have disclaimer pages, need to take steps to get around them
    pdfpage = requests.get(pdfurl)
    pdfsoup = BeautifulSoup(pdfpage.content, "html.parser")
    pdfresults = pdfsoup.find(id="wiki-body")

    if type(pdfresults) is not None:
        links = pdfresults.find_all('a', href=True)
        final_link = "https://imslp.org" + links[0]['href']
        with open("pdflinks.txt", 'w+', encoding='utf-8') as f:
            f.write(final_link + "\n")
        # first link on the disclaimer page is the pdf link, need to add https to make it work

    response = requests.get(final_link)
    pdfname = "pdf" + str(i) + ".pdf" # naming convention
    pdf = open(pdfname, 'wb')
    pdf.write(response.content) # writing to pdf on my own machine
    pdf.close()
    print(f"finished writing {pdfname}")

for i in range(len(permlinks)):
    get_pdf(i)
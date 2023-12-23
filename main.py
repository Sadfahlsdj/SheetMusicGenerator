import requests
import json
from bs4 import BeautifulSoup
from LinkGenerator import get_permlinks

linksTest = get_permlinks()
print(linksTest)
# replace the start value with something else to access a different entry
# retformat can be pretty, json, php, or wddx
api_url = ("https://imslp.org/imslpscripts/API.ISCR.php?account=worklist/disclaimer=accepted/"
           "sort=id/type=2/start=60000/retformat=json")

bad_query_message = "response code was not 200, something went 2 shit"

permlinks = []

def get_music():
    url = api_url
    response = requests.get(url)

    if response.status_code == 200: # the good response code
        return json.loads(response.content.decode('utf-8'))
        # return response.content.decode('utf-8')
    else:
        return bad_query_message

music = get_music()

if music != bad_query_message:
    print("query successful")

# keys of inner dicts are id, type, parent, intvals, permlink
for key, value in music.items():
    if key != 'metadata' and key != '':
        # keys go from 0-999 and have a "metadata" and a "[]" at the end, these are different ignore them
        permlinks.append(music[key]['permlink'])

# print(permlinks) # list of all the permlinks we will be scraping pdfs from

# relevant html:
# <a rel="nofollow" class="external text" href="https://imslp.org/wiki/Special:ImageFromIndex/693320/hfpn"> == $0
# use the div class "we_file_download plainlinks"

def get_pdf(i):
    url = permlinks[i] # should run on each permlink, i is the index
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
        # first link on the disclaimer page is the pdf link, need to add https to make it work

    response = requests.get(final_link)
    pdfname = "pdf" + str(i) + ".pdf" # naming convention
    pdf = open(pdfname, 'wb')
    pdf.write(response.content) # writing to pdf on my own machine
    pdf.close()
    print(f"finished writing {pdfname}")

for i in range(len(permlinks)):
    get_pdf(i)


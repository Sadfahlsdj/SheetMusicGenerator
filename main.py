import requests
import json
from bs4 import BeautifulSoup

# replace the start value with something else to access a different entry
# retformat can be pretty, json, php, or wddx
api_url = ("https://imslp.org/imslpscripts/API.ISCR.php?account=worklist/disclaimer=accepted/"
           "sort=id/type=2/start=0/retformat=json")

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

print(permlinks) # list of all the permlinks we will be scraping pdfs from

# relevant html:
# <a rel="nofollow" class="external text" href="https://imslp.org/wiki/Special:ImageFromIndex/693320/hfpn"> == $0

def get_pdf():
    url = permlinks[0]
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    # print(soup.text)

get_pdf()



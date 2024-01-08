import grequests
import requests
from random import *
import json
from bs4 import BeautifulSoup

from LinkGenerator import get_permlinks

permlinks = get_permlinks()

class Test:
    def __init__(self):
        self.urls = [p.strip() for p in permlinks[10:20]]

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))

    def a(self):
        results = grequests.map((grequests.get(u) for u in self.urls), exception_handler=self.exception, size=10)
        soup = [BeautifulSoup(res.text, 'html.parser') for res in results]

        results2 = [s.find(id="tabScore1") for s in soup]
        links = []
        for r in results2:
            try:
                links.append([r.find_all('a', href=True) for r in results2])
            except:
                print(f"something went wrong, the statement that r is none is: {r is None}")
        pdfurls = [l[0]['href'] for l in links]

        pdfresults = grequests.map((grequests.get(u) for u in pdfurls), exception_handler=self.exception, size=10)
        pdfsoup = [BeautifulSoup(p.content, "html.parser") for p in pdfresults]
        pdfresponses = [p.find(id="wiki-body") for p in pdfsoup]

        for p in pdfresponses:
            links = p.find_all('a', href=True)
            final_link = "https://imslp.org" + links[0]['href']
            with open("pdflinks.txt", 'w+', encoding='utf-8') as f:
                f.write(final_link + "\n")
            print(f"wrote {final_link}")


test = Test()
test.a()
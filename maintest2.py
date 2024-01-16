import grequests
import requests
from time import sleep
from random import *
import json
from bs4 import BeautifulSoup
import warnings
from LinkGenerator import get_permlinks
import os
import threading

def write_file(pdfname, response):
    with open(os.path.join('./pdfs', pdfname), 'wb') as pdf:  # ./ is for relative filepath
        # os.set_blocking(pdf.fileno(), False) this doesn't work
        pdf.write(response.content)  # writing to pdf on my own machine
    print(f"finished writing {pdfname}")
class Test:
    def __init__(self, start, stop, permlinks):
        self.start = start
        self.stop = stop
        self.urls = [p.strip() for p in permlinks[start:stop]]
        self.threads = abs(stop - start)

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))

    def a(self):
        start = self.start
        t = self.threads
        done = False
        tryCount = 0
        try:
            """ # next code block is for proxies
            while not done and tryCount < 3:
                try:
                    rs = (grequests.get(u) for u in self.urls)
                    results = grequests.map(rs, size=t, exception_handler=self.exception)
                    soup = [BeautifulSoup(res.text, 'html.parser') for res in results]
                    # print(soup[0])
                    done = True
                except:
                    print("connection refused on step 1, waiting 5 seconds")
                    sleep(5)
                    tryCount += 1
                    if tryCount == 3:
                        print("reached 3 tries, terminating")
                        return False"""
            rs = (grequests.get(u) for u in self.urls)
            results = grequests.map(rs, size=t, exception_handler=self.exception)
            soup = [BeautifulSoup(res.text, 'html.parser') for res in results]
        except:
            print(f"something went wrong with the second step, assume that soup is none")
            return False

        try:
            results2 = [s.find(id="tabScore1") for s in soup]
            links = []
            for r in results2:
                try:
                    links.append(r.find_all('a', href=True))
                    # print(r.find_all('a', href=True))
                except:
                    print(f"something went wrong with the second step, the statement that r is none is: {r is None}")
                    return False

            pdfurls = [l[0]['href'] for l in links]
            print(pdfurls)

            done = False
            tryCount = 0
            print(f"reached step 3")
            """# next code block is for proxies
                while not done and tryCount < 3:
                try:
                    next code block is for proxies
                    rs2 = (grequests.get(u) for u in pdfurls)
                    pdfresults = grequests.map(rs2, size=t, exception_handler=self.exception)
                    pdfsoup = [BeautifulSoup(p.content, "html.parser") for p in pdfresults]
                    pdfresponses = [p.find(id="wiki-body") for p in pdfsoup]
                    done = True
                except:
                    print("connection refused on step 3, waiting 5 seconds")
                    sleep(5)
                    tryCount += 1
                    if tryCount == 3:
                        print("reached 3 tries, terminating")
                        return False"""
            rs2 = (grequests.get(u) for u in pdfurls)
            pdfresults = grequests.map(rs2, size=t, exception_handler=self.exception)
            pdfsoup = [BeautifulSoup(p.content, "html.parser") for p in pdfresults]
            pdfresponses = [p.find(id="wiki-body") for p in pdfsoup]

            final_links = []
            for p in pdfresponses:
                try:
                    links = p.find_all('a', href=True)
                    final_link = "https://imslp.org" + links[0]['href']

                    final_links.append(final_link)
                    index = start + final_links.index(final_link)
                    with open("pdflinks.txt", 'a+', encoding='utf-8') as f:
                        f.write(str(index) + ": " + final_link + "\n")
                    print(f"wrote {final_link}")

                except:
                    print(f"something went wrong with the third step, the statement that p is none is: {p is None}")
                    return False

            """try:
                for final_link in final_links:
                    response = requests.get(final_link)
                    pdfname = "pdf" + str(start + final_links.index(final_link)) + ".pdf"  # naming convention
                    write_file(pdfname, response)

            except:
                print("something went wrong with the printing process")
                """

        except:
            print(f"catch-all error in case i forgot something tbh")
            return False
        return True

def get_proxies():
    # proxies.txt generated with this:
    # curl https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt -o http.txt
    with open('proxies.txt') as file:
        proxies = [line.strip() for line in file]
    return proxies

def main():
    permlinks = get_permlinks()
    open('pdflinks.txt', 'w').close()  # i use append so clear file on each iteration
    warnings.filterwarnings("ignore") # LIVING ON A PRAYER
    proxies = get_proxies()

    i = 9720
    proxyi = 80
    proxy = proxies[proxyi].strip()

    while i < len(permlinks):
        threads = 10 # higher than 10 gets banned
        cooldown = 20 # lower than 20 gets banned
        print(f"trying with starting i as {i}")
        test = Test(i, i + threads, permlinks)
        succeeded = test.a()  # returns true if it worked, false if it didn't

        i += threads
        if succeeded:
            print(f"succeeded, forcing {cooldown} sec timeout")
        else:
            print(f"something failed, moving on to the next bunch after {cooldown} seconds")
        sleep(cooldown)

if __name__ == "__main__":
    main()
import grequests
import requests
from time import sleep
from random import *
import json
from bs4 import BeautifulSoup
import warnings
from LinkGenerator import get_permlinks

class Test:
    def __init__(self, start, stop, permlinks):
        self.start = start
        self.stop = stop
        self.urls = [p.strip() for p in permlinks[start:stop]]
        self.threads = abs(stop - start)

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))

    def a(self, proxy):
        t = self.threads
        done = False
        tryCount = 0
        try:
            while not done and tryCount < 3:
                try:
                    rs = (grequests.get(u,proxies={"http": proxy, "https": proxy}, verify=False) for u in self.urls)
                    results = grequests.map(rs, size=t, exception_handler=self.exception)
                    soup = [BeautifulSoup(res.text, 'html.parser') for res in results]
                    print(soup[0])
                    done = True
                except:
                    print("connection refused on step 1, waiting 5 seconds")
                    sleep(5)
                    tryCount += 1
                    if tryCount == 3:
                        print("reached 3 tries, terminating")
                        return False
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

            done = False
            tryCount = 0
            print(f"reached step 3")
            while not done and tryCount < 3:
                try:
                    rs2 = (grequests.get(u, proxies={"http": proxy, "https": proxy}, verify=False) for u in pdfurls)
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
                        return False

            for p in pdfresponses:
                try:
                    links = p.find_all('a', href=True)
                    final_link = "https://imslp.org" + links[0]['href']
                    with open("pdflinks_sample.txt", 'a+', encoding='utf-8') as f:
                        f.write(final_link + "\n")
                    print(f"wrote {final_link}")
                    return True
                except:
                    print(f"something went wrong with the third step, the statement that p is none is: {p is None}")
                    return False
        except:
            print(f"catch-all error in case i forgot something tbh")

def get_proxies():
    # proxies.txt generated with this:
    # curl https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt -o http.txt
    with open('proxies.txt') as file:
        proxies = [line.strip() for line in file]
    return proxies

def main():
    permlinks = get_permlinks()
    open('pdflinks_sample.txt', 'w').close()  # i use append so clear file on each iteration
    warnings.filterwarnings("ignore") # LIVING ON A PRAYER
    proxies = get_proxies()

    i = 10
    proxyi = 80

    while i < len(permlinks):
        proxy = proxies[proxyi].strip()
        print(f"trying with proxy index {proxyi}")
        test = Test(i, i+8, permlinks) # probably capped to 8 threads because any more gets a proxy banned
        succeeded = test.a(proxy) # returns true if it worked, false if it didn't
        proxyi += 1
        if succeeded:
            i += 8

if __name__ == "__main__":
    main()
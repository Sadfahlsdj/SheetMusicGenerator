from playwright.sync_api import Playwright, sync_playwright, expect
import os
from bs4 import BeautifulSoup
import requests


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch_persistent_context(user_dir, headless=False)
    # above line makes the browser launch in non incognito
    page = browser.new_page()
    # request_context = context.request
    page.goto("https://imslp.org/wiki/Special:IMSLPImageHandler/43455")
    print("step 1")
    # page.get_by_text("Accept all & visit the site").click()
    # print("step 2")
    # print(page.content())
    pdfresults = page.content()
    pdfsoup = BeautifulSoup(pdfresults, "html.parser")
    pdfresponses = pdfsoup.find(id="wiki-body")

    links = pdfresponses.find_all('a', href=True)
    final_link = "https://imslp.org" + links[0]['href']

    with open("testpdf.pdf", "wb") as p:
        p.write()
    # page.get_by_role("link", name="Click here to continue your").click()
    print("step 2")


    page.close()

    # ---------------------
    # context.close()
    browser.close()

user_dir = '/tmp/playwright'

if not os.path.exists(user_dir):
  os.makedirs(user_dir)

with sync_playwright() as playwright:
    run(playwright)

from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import requests

def get_pdflinks(): # so other files in the program can read the links
    with open("pdflinks_saved.txt", 'r', encoding='utf-8') as file:
        p = [l.split(" ")[1].strip() for l in file]
    return p

def run(i, playwright: Playwright) -> None:
    pdflinks = get_pdflinks()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(pdflinks[i])
    page.get_by_text("Accept all & visit the site").click()
    # page.get_by_text("I accept this disclaimer").click()
    url = page.url
    print(url)


    # print(span)
    # page.pause()

    locator = page.get_by_role("link", name="Click here to continue your")
    locator.hover()
    print("found link")
    result = page.content()
    # print(result)
    soup = BeautifulSoup(result, 'html.parser')
    span = soup.find(id='wiki-body')
    links = span.find_all('a', href=True)
    final_link = links[0]['href']

    response = requests.get(final_link)
    pdf_name = "testpdf" + str(i) + ".pdf"

    with open(pdf_name, "wb") as p:
        p.write(response.content)
    print(f"pdf number {i} was written")
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    for i in range(10):
        run(i + 16, playwright)

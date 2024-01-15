from playwright.sync_api import Playwright, sync_playwright, expect

import os
from LinkGenerator import *

with open("pdf_final_links.txt", 'w') as pdf:
    pdf.write("")
def run(playwright: Playwright, link) -> None:
    sanitized_link = link.replace("\"", "%22")
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(sanitized_link)
    # page.get_by_text("✕").click()
    page.get_by_text("Accept all & visit the site").click()
    # document.querySelector('div#tabScore1').querySelectorAll('[href*="Special:ImagefromIndex"]');
    # try using this to make playwright more exact, some pages are weird and "complete score" won't work
    page.get_by_role("link", name="Complete Score", exact=True).click()
    page.get_by_role("link", name="I accept this disclaimer,")
    pdf_final_url = page.url + "\n"

    with open("pdf_final_links.txt", 'a+') as pdf:  # ./ is for relative filepath
        # os.set_blocking(pdf.fileno(), False) this doesn't work
        pdf.write(pdf_final_url)  # writing to pdf on my own machine
    print(f"wrote {pdf_final_url}")

    page.close()

    # ---------------------
    context.close()
    browser.close()

def main():
    links = get_permlinks()
    for l in links:
        with sync_playwright() as playwright:
            run(playwright, l)

if __name__ == "__main__":
    main()

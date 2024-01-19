import os
from bs4 import BeautifulSoup
import time

# works for pages where the countdown occurs, does not for pages where it goes straight to pdf
# solution, just directly wget those pages i guess
# this is in pdfs folder because the stupid ass -O tag won't work for me

def get_pdflinks():
    with open('pdflinks_saved.txt', 'r') as f:
        p = [l for l in f]
    return p # do not use directly, returns index with link
def input_parser(line):
    index = line.split(":")[0].strip()
    link = line.split(" ")[1].strip()
    return [index, link]
def get_final_link(index, link):
    try:
        command_to_use = f'wget -q {link} -O temp.html'
        os.system(command_to_use)
        html = open('temp.html', 'r').read()
        soup = BeautifulSoup(html, 'html.parser')

        first_link = soup.find('a', href=True)
        if '/files/imglnks' in str(first_link): # if it is a petrucci link or a eu link
            if '/files/imglnks/eu' in str(first_link):
                final_link = 'imslp.eu/' + first_link['href']
            else:
                final_link = 'https://petruccimusiclibrary.ca/' + first_link['href']
            with open('pdf_final_links.txt', 'a+') as f:
                f.write(index + ": " + final_link + "\n")
            print(f"wrote {final_link}, it is a Petrucci/EU server link")

            command2 = f'wget -O ./pdfs/pdf{index}.pdf -q \"{final_link}\"'
            os.system(command2)
            print(f"saved index {index} to pdf")

        else: # if it is a regular imslp link
            span = soup.find(id='sm_dl_wait')
            final_link = str(span).split("\"")[1]

            link_to_write = f'{index}: {final_link}'

            with open('pdf_final_links.txt', 'a+') as f:
                f.write(link_to_write + "\n")
            print(f"wrote {link_to_write}")

            command2 = f'wget -O ./pdfs/pdf{index}.pdf -q \"{final_link}\"'
            os.system(command2)
            print(f"saved index {index} to pdf")
    except: # this SHOULD trigger if the link goes directly to pdf, or if something weird happens
        print("something went wrong, likely because this link resolves directly to pdf")
        command_to_use = f'wget -O ./pdfs/pdf{index}.pdf -q \"{link}\"'
        os.system(command_to_use)
        # print(command_to_use)
        print(f"saved index {index} to pdf")

def main():
    # index 247 works usually for pdf acquisition, try that to test code
    # 122 currently broken
    with open('pdf_final_links.txt', 'w+') as f: # clears the file
        f.write(" ")
    pdf_links = get_pdflinks()
    for i in range(len(pdf_links)):
        index, link = input_parser(pdf_links[i])
        get_final_link(index, link)
        time.sleep(1) # SET TO 2 SECONDS FOR NEU SERVERS, THEY ARE FASTER SO NEED MORE TIMEOUT
    """index, link = input_parser(pdf_links[122]) # use this & next line to test individual ones
    get_final_link(index, link)"""
    # print(f"{index} {link}")


if __name__ == "__main__":
    main()



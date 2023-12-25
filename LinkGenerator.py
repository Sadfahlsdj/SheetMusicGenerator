import requests
import json
from bs4 import BeautifulSoup

permlinks = []
permlinks_no_ascii = []

def get_links(i):
    bad_query_message = "response code was not 200, something went 2 shit"

    # replace the start value with something else to access a different entry, skip 1000 at a time
    # retformat can be pretty, json, php, or wddx
    url = ("https://imslp.org/imslpscripts/API.ISCR.php?account=worklist/disclaimer=accepted/"
           "sort=id/type=2/start=" + str(i) + "/retformat=json")
    response = requests.get(url)

    if response.status_code == 200: # the good response code
        music = json.loads(response.content.decode('utf-8'))
        # return response.content.decode('utf-8')
    else:
        music = bad_query_message
        return "failed"

    if music != bad_query_message:
        for key, value in music.items():
            if key != 'metadata' and key != '':
                # keys go from 0-999 and have a "metadata" and a "[]" at the end, these are different ignore them
                permlinks.append(music[key]['permlink'])
    # keys of inner dicts are id, type, parent, intvals, permlink
    print(f"appended permlinks for index {i}")
    return "succeeded"

def main():
    i = 0
    failed = False
    while not failed:
        print(f"getting music for index {i}")
        result = get_links(i)
        print(f"finished getting music for index {i}")
        i += 1000 # each api call only returns 1000 entries at a time

        if result == "failed" or i > 100000: # have i > n here as an upper bound
            failed = True

    with open("permlinks.txt", 'w+', encoding='utf-8') as f:
        for p in permlinks:
            str_to_append = p + "\n"
            f.write(str_to_append)

    if len(permlinks) != len(set(permlinks)):
        print("duplicates are present, something is wrong")
    else:
        print("no duplicates present")

    a = get_permlinks()
    print(a)

def get_permlinks(): # so other files in the program can read the links
    with open("permlinks100000.txt", 'r', encoding='utf-8') as file:
        p = [l for l in file]
    return p

if __name__ == "__main__":
    main()



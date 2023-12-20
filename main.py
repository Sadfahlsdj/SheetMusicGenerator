import requests
import json

api_token = "is this needed"

# replace the start value with something else to access a different entry
# retformat can be pretty, json, php, or wddx
api_url = ("https://imslp.org/imslpscripts/API.ISCR.php?account=worklist/disclaimer=accepted/"
           "sort=id/type=2/start=0/retformat=json")

api_url_test = ("http://imslp.org/imslpscripts/API.ISCR.php?account=worklist/disclaimer=accepted"
                "/sort=id/type=1/start=0/retformat=<pretty|json|php|wddx>")

bad_query_message = "response code was not 200, something went 2 shit"

permlinks = []

def get_music():
    url = api_url
    response = requests.get(url)

    if response.status_code == 200:
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

print(permlinks)


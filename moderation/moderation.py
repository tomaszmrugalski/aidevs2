# This is a solution to the moderation task from aidevs2 course
# See https://zadania.aidevs.pl/ for details

import requests
import json
import yaml
import os.path

def load_apikey():
    """Loads the aidevs API key from ~/.aidevs2"""
    with open(os.path.expanduser('~/.aidevs2'), 'r') as file:
        api_key = yaml.safe_load(file)
    return api_key['APIKEY']

def load_openai_key():
    """Loads the openai API key from ~/.aidevs2"""
    with open(os.path.expanduser('~/.aidevs2'), 'r') as file:
        api_key = yaml.safe_load(file)
    return api_key['OPENAI_KEY']


BASE_URL = 'https://zadania.aidevs.pl'
APIKEY = load_apikey()
OPENAI_KEY = load_openai_key()
TASK = 'moderation'

# STEP 1: Get the token from aidevs
url = BASE_URL + '/token/' + TASK
print(f'Getting {url}, sending {APIKEY}')
page = requests.post(url, json={ "apikey": APIKEY })
data = json.loads(page.text)
token = data['token']
print(f"My token is {token}")

# STEP 2: Get the task: list of strings to moderate
url = BASE_URL + '/task/' + token

page2 = requests.get(url)
data2 = json.loads(page2.text)
print(f"/task/token returned {data2}")

input_to_be_moderated = data2['input']
print(f"Input to be moderated: {input_to_be_moderated}")


# Run this content through the moderation API
moderation_url = 'https://api.openai.com/v1/moderations'

body = { "input": input_to_be_moderated }
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }

resp3 = requests.post(moderation_url, json=body, headers=headers)
mod_resp = json.loads(resp3.text)
print(f"Moderation API returned {mod_resp['results']}")

# Ok, this is extremely naive and could be done much better with filtering, but it's more
# tricky to read it for less experienced programmers. So let's keep it simple.
# mod_result = list(map(lambda i: 1 if i['flagged'] else 0, mod_resp['results']))

mod_result = []
for i in mod_resp['results']:
    if i['flagged'] == True:
        mod_result.append(1)
    else:
        mod_result.append(0)

print(f"Parsed moderation result: {mod_result}")

# STEP 3: Send the answer
url = BASE_URL + '/answer/' + token
print(f'Getting {url}, sending {mod_result}')
page3 = requests.post(url, json={ "answer": mod_result })
data3 = json.loads(page3.text)
print(f"/answer/token returned {data3}")

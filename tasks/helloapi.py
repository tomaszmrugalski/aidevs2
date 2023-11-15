import requests
import json
import yaml
import os.path

def load_apikey():
    with open(os.path.expanduser('~/.aidevs2'), 'r') as file:
        api_key = yaml.safe_load(file)
    return api_key['APIKEY']

BASE_URL = 'https://zadania.aidevs.pl'
APIKEY = load_apikey()
TASK = 'helloapi'

# STEP 1: Get the token
url = BASE_URL + '/token/' + TASK
print(f'Getting {url}, sending {APIKEY}')
page = requests.post(url, json={ "apikey": APIKEY })
data = json.loads(page.text)
token = data['token']
print(f"My token is {token}")

# STEP 2: Get the task
url = BASE_URL + '/task/' + token

page2 = requests.get(url)
data2 = json.loads(page2.text)
print(f"/task/token returned {data2}")
cookie = data2['cookie']

# STEP 3: Send the answer
url = BASE_URL + '/answer/' + token
print(f'Getting {url}, sending {cookie}')
page3 = requests.post(url, json={ "answer": cookie })
data3 = json.loads(page3.text)
print(f"/answer/token returned {data3}")

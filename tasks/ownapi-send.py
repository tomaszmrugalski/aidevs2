# This is a script that will send the URL to my own hosted api (location where ownapi.py is run) task from aidevs2 course
# See https://zadania.aidevs.pl/ for details
#
# The overall goal is to:
# 1. Get a token from aidevs
# 2. Get the task from aidevs -
# 3. Send my own API url to aidevs
# 4. Wait for aidevs to interrogate my API, send response.
# 5. Profit!

import requests
import json
import yaml
import os
import sys

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
TASK = 'ownapi'

OWNAPI_URL = 'https://svarog.space:2137/v1/knowledge'

# STEP 1: Get the token from aidevs
url = BASE_URL + '/token/' + TASK
print(f'aidevs: Getting {url}, sending {APIKEY}')
response1 = requests.post(url, json={ "apikey": APIKEY })
resp = json.loads(response1.text)
token = resp['token']
print(f"aidevs: My token is {token}")

# STEP 2: Get the task from aidevs
url = BASE_URL + '/task/' + token
query={  }
print(f"aidevs: Sending {query} to {url}")
response2 = requests.post(url, data=query)
data2 = json.loads(response2.text)
print(f"aidevs: response: {data2}")


# STEP 6: Send the answer to aidevs
url = BASE_URL + '/answer/' + token
print(f'aidevs: Getting {url}, sending {OWNAPI_URL}')
response3 = requests.post(url, json = { "answer": OWNAPI_URL })
data3 = json.loads(response3.text)
print(f"aidevs: /answer/token returned {data3}")

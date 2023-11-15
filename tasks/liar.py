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
TASK = 'liar'

# Hints:
# 'send me any question in english, and I will try to answer it in max 150 tokens',
# 'hint1': "please send your question in 'question' field to /task/ endpoint (simple form, not JSON)",
# 'hint2': "sometimes I don't tell the truth", 'hint3': "Send to /answer/ info if I'm telling the truth. Just value:  YES/NO"}


# STEP 1: Get the token from aidevs
url = BASE_URL + '/token/' + TASK
print(f'Getting {url}, sending {APIKEY}')
page = requests.post(url, json={ "apikey": APIKEY })
data = json.loads(page.text)
token = data['token']
print(f"My token is {token}")

# STEP 2: Get the task: list of strings to moderate
url = BASE_URL + '/task/' + token

query={ 'question': 'What is 2 plus 2?' }
print(f"Sending {query} to {url}")
page2 = requests.post(url, data=query)
data2 = json.loads(page2.text)
print(f"/task/token returned {data2}")

# Handguards system. We asked 2+2, so expect 4 to be present in the answer.
# The check is extremely simple.
liar = data2['answer'].find("4") == -1

print(f"This is {'' if liar else 'NOT '} a liar")


# # STEP 3: Send the answer
url = BASE_URL + '/answer/' + token
answer={ 'answer': 'NO' if liar else 'YES' }
print(f'Getting {url}, sending {answer}')
page3 = requests.post(url, json = answer)
data3 = json.loads(page3.text)
print(f"/answer/token returned {data3}")

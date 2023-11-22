# This is a solution to the people task from aidevs2 course
# See https://zadania.aidevs.pl/ for details
#
# I was short on time, so this solution is cutting corners. I didn't set up any proper DB,
# just used JSON.
#
# The overall goal is to:
# 1. Get a token from aidevs
# 2. Get the task from aidevs - get the download link, also the question to be answered.
# SOLUTION:
# 3. download the remote file with data, load it into memory and keep as JSON
# 4. Send the question to OpenAI, ask to return the first/last name of the person in question.
# 5. Find appropriate record for that person in JSON
# 6. Send the whole records we have on the person as system prompt, then send the question as user input to OpenAI
# 7. Send the answer to aidevs
# 8. Profit!

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
TASK = 'people'

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
question = data2['question']
print(f"aidevs: response body: {data2}")
print(f"aidevs: the question is: {question}")


# STEP 3: Download the remote file with links. Skip download if it exists locally.
file_remote = 'https://zadania.aidevs.pl/data/people.json'
file_local = 'data/people.json'

if not os.path.exists(file_local):
    print(f'Downloading {file_remote} to {file_local}')
    os.makedirs(os.path.dirname(file_local), exist_ok=True)
    page = requests.get(file_remote)
    with open(file_local, 'wb') as f:
        f.write(page.content)
else:
    print(f"File {file_local} already exists, skipping download")

# STEP 4: extract person's name from the question

system = 'Zwróć imię i nazwisko występujące w pytaniu. Odpowiedź podaj w mianowniku. Krótka odpowiedź. Nie używaj zdrobnienia. Tylko dwa wyrazy - imię i nazwisko.'

url = 'https://api.openai.com/v1/chat/completions'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
body = { "messages": [{ "role": "system", "content": system}, { "role": "user", "content": question}], "model": "gpt-3.5-turbo"}
print(f'OpenAI, step 1: Getting {url}, using {OPENAI_KEY}')
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
print(f"OpenAI, step 1: Response body: {data}")
name = data['choices'][0]['message']['content']
print(f"OpenAI answer: the name is {name}")

first_name_search, last_name_search = name.split()

# STEP 5: Find the record for the person in question in the JSON file
with open(file_local, 'r') as f:
    data = json.load(f)

    first_names = []
    last_names = []

    print(f"Loaded {len(data)} people")
    poi = [] # person of interest

    for person in data:
        first_name = person['imie']
        last_name = person['nazwisko']

        if first_name_search in first_name and last_name_search in last_name:
            print("found match: ", first_name, last_name)
            poi = person
            print(f"Found record: {poi}")
            break

if poi == []:
    print("Could not find a match")
    sys.exit(1)

# STEP 6: Send the question to OpenAI, ask to return the first/last name of the person in question.
system = f'Oto informacje na temat osoby: {str(poi)}. Odpowiedz na pytanie na temat tej osoby. Krótka odpowiedź.'

url = 'https://api.openai.com/v1/chat/completions'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
body = { "messages": [{ "role": "system", "content": system}, { "role": "user", "content": question}], "model": "gpt-3.5-turbo"}
print(f'OpenAI, step 1: Getting {url}, using {OPENAI_KEY}')
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
print(f"OpenAI, step 1: Response body: {data}")
answer = data['choices'][0]['message']['content']
print(f"OpenAI answer: question: {question}, answer: {answer}")

# STEP 7: Send the answer to aidevs
url = BASE_URL + '/answer/' + token
print(f'aidevs: Getting {url}, sending {answer}')
response3 = requests.post(url, json = { "answer": answer })
data3 = json.loads(response3.text)
print(f"aidevs: /answer/token returned {data3}")

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
TASK = 'inprompt'


# STEP 1: Get the token from aidevs
url = BASE_URL + '/token/' + TASK
print(f'aidevs: Getting {url}, sending {APIKEY}')
page = requests.post(url, json={ "apikey": APIKEY })
data = json.loads(page.text)
token = data['token']
print(f"aidevs: My token is {token}")

# STEP 2: Get the task: lots of statements about various people and a question about one of them.
url = BASE_URL + '/task/' + token

query={  }
print(f"aidevs: Sending {query} to {url}")
page2 = requests.post(url, data=query)
data2 = json.loads(page2.text)
question = data2['question']

print(f"aidevs: there's statements about {len(data2['input'])} people")
print(f"aidevs: the question is : {question}")

# SOLUTION STEP 1: Use GPT to extract the person's name.
# Non-GPT solution. Find word that starts with capital letter.
system = 'Return name used in the question. Brief answer. Just one word - the name.'
user = data2['question']

url = 'https://api.openai.com/v1/chat/completions'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
body = { "messages": [{ "role": "system", "content": system}, { "role": "user", "content": user}], "model": "gpt-3.5-turbo"}
print(f'OpenAI, step 1: Getting {url}, using {OPENAI_KEY}')
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
print(f"OpenAI, step 1: Response body: {data}")
# print(f"Response headers: {page.headers}")
name = data['choices'][0]['message']['content']
print(f"OpenAI answer: the name is {name}")
# TODO: sometimes GPT returns name with a question mark. Need to sanitize it a bit more.

# SOLUTION STEP 2: Filter the list of statements to find the one that contains the name
context = ''
for i in data2['input']:
    #print(f"Analyzing input: {type(i)}: {i}")
    if i.find(name) != -1:
        print(f"aidevs: useful info about {name} is {i}")
        context = i
        break

if context == '':
    print(f"aidevs: ERROR: no information about {name} found in the input")
    exit(1)

# Context should contain the relevant information about the person.
print(f"OpenAI, step 2: context is {context}")

# SOLUTION STEP 3: Use GPT to answer the question about the person, provide what we know about him/her
# in the system message.

body = { "messages": [{ "role": "system", "content": context}, { "role": "user", "content": question}], "model": "gpt-3.5-turbo"}
print(f'OpenAI, step 2: Getting {url}, using {OPENAI_KEY}')
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
print(f"OpenAI, step 2: Response body: {data}")

answer = data['choices'][0]['message']['content']



# # STEP 3: Send the answer
url = BASE_URL + '/answer/' + token
answer={ 'answer': answer }
print(f'aidevs: Getting {url}, sending {answer}')
page3 = requests.post(url, json = answer)
data3 = json.loads(page3.text)
print(f"aidevs: /answer/token returned {data3}")

# This is a solution to the tools task from aidevs2 course
# See https://zadania.aidevs.pl/ for details
#
# The overall goal is to:
# 1. Get a token from aidevs
# 2. Get the task from aidevs
# 3. Write a prompt that will classify the question as either todo task or calendar.
# 4. Send the answer to aidevs
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
TASK = 'tools'

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
print(f"aidevs: response: {data2}")
print(f"aidevs: the question is: {question}")


# STEP 3: Assemble a prompt, ask GPT to answer question.
system_prompt = 'You are an assistant. User will ask you requests. Decide whether the task should ' + \
                'be added to the ToDo list or to the calendar (if time is provided) and return the ' + \
                'corresponding JSON. Always use YYYY-MM-DD format for dates. Today is 2023-11-24. ' + \
                '\n\n' + \
                'See examples below:\n' + \
                '##\n' + \
                'user: Przypomnij mi, że mam kupić mleko\n' + \
                'answer: {"tool":"ToDo","desc":"Kup mleko" }\n' + \
                '\n' + \
                'user: Jutro mam spotkanie z Marianem\n' + \
                'answer:{"tool":"Calendar","desc":"Spotkanie z Marianem","date":"2023-11-25"}'

url = 'https://api.openai.com/v1/chat/completions'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
body = { "messages": [{ "role": "system", "content": system_prompt}, {"role":"user", "content": question}], "model": "gpt-3.5-turbo"}

print(f'OpenAI: Getting {url}, using {OPENAI_KEY}')
print(f"OpenAI: system prompt: {system_prompt}")
print(f"OpenAI: user message: {question}")
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
answer = data['choices'][0]['message']['content']
print(f"OpenAI answer: the answer is {answer}")
answer = json.loads(answer)

# STEP 4: Send the answer to aidevs
url = BASE_URL + '/answer/' + token
print(f'aidevs: Getting {url}, sending {answer}')
response3 = requests.post(url, json = { "answer": answer })
data3 = json.loads(response3.text)
print(f"aidevs: /answer/token returned {data3}")

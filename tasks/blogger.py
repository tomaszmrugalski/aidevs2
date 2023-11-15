import requests
import json
import yaml
import os.path

def load_apikey():
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
TASK = 'blogger'

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
blog_titles = str(data2['blog'])


system = 'you are a culinary blogger. Please write separate paragraphs for each JSON string. Write response as JSON list, with one short paragraph for each input string.'

url = 'https://api.openai.com/v1/chat/completions'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
body = { "messages": [{ "role": "system", "content": system}, { "role": "user", "content": blog_titles}], "model": "gpt-3.5-turbo"}

print(body)

print(f'Getting {url}, using {OPENAI_KEY}')
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
print(f"Response body: {data}")
print(f"Response headers: {page.headers}")
blog = json.loads(data['choices'][0]['message']['content'])

# for this particular prompt, the model returns oddly formatted response. The returned format is:
# [{'paragraph': 'title of paragraph 1'}, {'paragraph': 'content of paragraph 1'}, {'paragraph': 'title of paragraph
# 2'}, ... ]

blog = [ blog[1]['paragraph'], blog[3]['paragraph'], blog[5]['paragraph'], blog[7]['paragraph'] ]

print(f"Written blog, sending as answer: {blog}")

# STEP 3: Send the answer
url = BASE_URL + '/answer/' + token
print(f'Getting {url}, sending {blog}')
page3 = requests.post(url, json={ "answer": blog })
data3 = json.loads(page3.text)
print(f"/answer/token returned {data3}")

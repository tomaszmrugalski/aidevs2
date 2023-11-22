# This is a solution to the search task from aidevs2 course
# See https://zadania.aidevs.pl/ for details
#
# Additional dependecies:
# pip install qdrant-client
#
# Also, you need to have qdrant running locally. See https://qdrant.readme.io/docs/quick-start
# This should do the trick if you have docker installed:
#
# docker pull qdrant/qdrant
# docker run -p 6333:6333 -v $(pwd)/path/to/data:/qdrant/storage qdrant/qdrant
#
# The overall goal is to:
# 1. Get a token from aidevs
# 2. Get the task from aidevs - get the download link, also the question to be answered.
# SOLUTION:
# 3. download the remote file with links. Skip download if it exists locally.
# 4. connect to qdrant, check if the collection exists. If not, create it.
# 5. check if there are at least 300 vectors. If not, load them from the downloaded file.
# 6. search for the vector in question
# 7. Send the answer to aidevs
# 8. Profit!

import requests
import json
import yaml
import os
import sys
from uuid import uuid4
import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct

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
TASK = 'search'

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

# STEP 3 - first need to download the file (if not present locally)
file_remote = 'https://unknow.news/archiwum.json'
file_local = 'data/archiwum.json'

if not os.path.exists(file_local):
    print(f'Downloading {file_remote} to {file_local}')
    os.makedirs(os.path.dirname(file_local), exist_ok=True)
    page = requests.get(file_remote)
    with open(file_local, 'wb') as f:
        f.write(page.content)
else:
    print(f"File {file_local} already exists, skipping download")

# STEP 4 - connect to qdrant
QDRANT_URL = "http://localhost:6333"

client = qdrant_client.QdrantClient(url=QDRANT_URL)
try:
    col = client.get_collection("aidevs_search")
    print("qdrant: Collection 'aidevs_search' exists, skipping creation")
except qdrant_client.http.exceptions.UnexpectedResponse:

    print("qdrant: Collection 'aidevs_search' does not exist, creating it")
    col = client.create_collection(
        collection_name="aidevs_search",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )

# STEP 5 - check if there is enough vectors in the collection. If there is
# less than 300, add more vectors from the downloaded file. Sometimes, the
# OpenAI API returns an error, so we need to skip the vectors that were
# already inserted in the previous run.
LIMIT_VECTORS = 300
collection_info = client.get_collection("aidevs_search")
if collection_info.vectors_count < LIMIT_VECTORS:
    print(f"qdrant: Collection does not have at least {LIMIT_VECTORS}, adding more vectors")
    with open(file_local, 'r') as f:
        data = json.load(f)
        cnt = 0
        for item in data:
            cnt = cnt + 1
            if cnt < collection_info.vectors_count:
                print(f"qdrant: Skipping item {cnt} of {len(data)} - already inserted")
                continue
            print(f"qdrant: Adding item {cnt} of {len(data)}: {item}")

            uuid = uuid4()
            item['uuid'] = str(uuid)

            url = 'https://api.openai.com/v1/embeddings'
            headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
            body = { "input": item['title'], "model": "text-embedding-ada-002"}
            print(f'OpenAI: Getting {url}, using {OPENAI_KEY}')
            page = requests.post(url, json=body, headers=headers)
            resp = json.loads(page.text)
            print(f"OpenAI: Response body: {len(page.text)} chars")
            try:
                embeddings = resp['data'][0]['embedding']
            except KeyError:
                print(f"OpenAI: Error: {resp}")
                sys.exit(-1)

            result = client.upsert(collection_name="aidevs_search",
                                   points=[
                                       PointStruct(
                                        id=cnt,
                                        vector = embeddings,
                                        payload = item
                                       )
                                    ])
            print(f"qdrant: Inserted item {cnt}: result={result}, {item['title']}")

            if cnt >= LIMIT_VECTORS:
                print(f"qdrant: Limit of {LIMIT_VECTORS} vectors reached, stopping")
                break

# STEP 6: Search for a vector
# question = "Framing - jak skutecznie komunikować się jako gość z IT"

url = 'https://api.openai.com/v1/embeddings'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
body = { "input": question, "model": "text-embedding-ada-002"}
print(f'OpenAI: Getting {url}, using {OPENAI_KEY}')
page = requests.post(url, json=body, headers=headers)
resp = json.loads(page.text)
print(f"OpenAI: Response has {len(page.text)} chars")
embeddings_search = resp['data'][0]['embedding']

hits = client.search(
    collection_name="aidevs_search",
    query_vector=embeddings_search,
    limit=1  # Return 1 closest point
)

print(f"qdrant: found nearest hit: {hits[0].payload['title']}, url {hits[0].payload['url']}")
answer = hits[0].payload['url']

# STEP 7: Send the answer
url = BASE_URL + '/answer/' + token
print(f'aidevs: Getting {url}, sending {answer}')
response3 = requests.post(url, json = { "answer": answer })
data3 = json.loads(response3.text)
print(f"aidevs: /answer/token returned {data3}")

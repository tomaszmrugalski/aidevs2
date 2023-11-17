# Installation

1. Setup the python environment
```
python -m venv venv
source venv/bin/activate
pip install requests pyyaml
```

Some scripts may require additional python packages: openai requests_toolbelt.

2. Create a file in your home directory with the APIKEY (for aidevs) and OPENAI_KEY (for OpenAI).

```
$ cat ~/.aidevs2
APIKEY: '12345678-abcd-1234-5678-0123456789ab'
OPENAI_KEY: 'sk-your-secret-openai-key-here'
```

# Usage:

Run the scripts in `tasks` directory:

`python tasks/helloapi.py`

The chat tasks have solutions in the `chat` directory.

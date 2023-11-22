# Overview

These are my solutions to the aidevs2! training. For details, see https://aidevs.pl.
To fully understand the code, you need to have access to the training.

The solutions are intentionally simplistic, almost primitive. The goal of this training
is to gain experience with OpenAI and other AI tools, not to show off python skills.
The training is done by people of varied background, ranging from no coding to senior
programmers.

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

Run the scripts in `tasks` directory. For example:

`python tasks/helloapi.py`

The chat tasks have solutions in the `chat` directory.

## Links

- The course homepage: https://aidevs.pl
- Solutions by other participants:
  - https://github.com/domik82/aidevs2 - python
  -

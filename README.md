# autogen automotive example

(python 3.11.7)

## to get the code env setup

1. run `python3 -m venv .venv`
2. kill vscode terminal
3. right click example_auto_team.py and choose run (it wont successfully run if you don't have Ollama running locally)
4. now you can `pip install -r requirements.txt`
5. you need to setup your .env file with all the appropriate api keys

```
OPENAI_API_KEY=""
OPENAI_API_BASE_URL="https://api.openai.com/v1"
#MODEL_NAME="gpt-3.5-turbo"
MODEL_NAME="gpt-4"
OPENAI_ORG_ID=""
SERPER_API_KEY=""
GEMINI-API-KEY=""
```

6. now you need to create a OAI_CONFIG_LIST

```
OAI_CONFIG_LIST=[{"model_name": "gpt-4", "api_key": "<your api key>"}]
```

7. note that `python3 inventory.py` was used to generate the local db found in inventory.db (to update delete the db and uncomment the bottom line in inventory.db)

8. finally to spin up the flask app `python3 example_auto_team.py` and go to http://127.0.0.1:5000

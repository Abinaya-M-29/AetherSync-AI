# AetherSync-AI
AetherSync is a self-governing Multi-Agent Governance System aimed at solving the "AI Power Paradox". 

### Setup

Setup credentials

```
secrets
- .env
- credentials.json
- token.pkl
```

Installations
```
uv sync
```
*requirements.txt is just for reference

```
source .venv/bin/activate
```

Set up database
```
python backend/db/seed_db.py
```


### Usage and Run

- 3 servers

FastAPI
```
cd src
python main.py
```

MCP server
```
cd src
python mcp_server/server.py
```


UI server (later change to react/js)
```
cd src
streamlit run frontend/steamlit_ui.py
```


### Dev mode usage

Auth creation

Google Gmail API - https://console.cloud.google.com/marketplace/product/google/gmail.googleapis.com?q=search&referrer=search&project=winged-woods-490206-v6

Google Calendar API - https://console.cloud.google.com/marketplace/product/google/calendar-json.googleapis.com?q=search&referrer=search&project=winged-woods-490206-v6

Google Tasks API - https://console.cloud.google.com/marketplace/product/google/tasks.googleapis.com?q=search&referrer=search&project=winged-woods-490206-v6

Google Blogger API - https://console.cloud.google.com/marketplace/product/google/blogger.googleapis.com?q=search&referrer=search&project=winged-woods-490206-v6


```
mcp dev mcp_server/server.py
```

TODO:
- create DB
- Add agent according to prompt
- Check if langgraph workflow or a single master agent + sub agents are fine

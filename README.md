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
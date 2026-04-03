# Grid-Pulse

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)
![Chainlit](https://img.shields.io/badge/Chainlit-UI-FF4B4B?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?style=flat-square&logo=google)
![LangChain](https://img.shields.io/badge/LangChain-MCP%20Adapters-1C3C3C?style=flat-square)
![MCP](https://img.shields.io/badge/Protocol-MCP-purple?style=flat-square)
![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=flat-square&logo=render)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Grid-Pulse** is an AI-powered expense tracking chatbot built on top of the [LedgerFlow MCP Server](https://github.com/a-ksharma/LedgerFlow). It uses Google Gemini 2.5 Flash as the LLM, LangChain MCP Adapters to connect to remote MCP tools, and Chainlit for the chat UI.

🚀 **Live Demo:** [https://grid-pulse-zuoy.onrender.com](https://grid-pulse-zuoy.onrender.com)

---

## What is this?

Grid-Pulse is a general-purpose AI assistant with built-in expense tracking capabilities. Users log in with Google, and all their expense data is stored privately and separately in Firestore via the LedgerFlow MCP server.

Just chat naturally:
> *"Add ₹500 for groceries today"*
> *"How much did I spend on food this month?"*
> *"Summarize my expenses for March"*
> *"What's the capital of Japan?"* ← general questions work too

---

## Features

- **Google OAuth login** — secure, one-click sign in
- **Per-user data isolation** — every user's expenses are completely separate
- **Natural language expense tracking** — no forms, just chat
- **Date-aware** — understands "last Monday", "this month", "yesterday"
- **General purpose** — answers everyday questions beyond just expenses
- **Tool call transparency** — shows which MCP tool was called and with what parameters
- **Persistent chat** — conversation history maintained within each session

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini 2.5 Flash |
| Chat UI | Chainlit |
| MCP Client | LangChain MCP Adapters |
| Authentication | Google OAuth 2.0 |
| MCP Server | LedgerFlow (Cloud Run) |
| Database | Google Cloud Firestore |
| Deployment | Render |
| Language | Python 3.13 |

---

## Architecture

```
User (Browser)
      ↓  Google OAuth
Chainlit UI (Render)
      ↓  LangChain + Gemini 2.5 Flash
MCP Client (langchain-mcp-adapters)
      ↓  Streamable HTTP
LedgerFlow MCP Server (Google Cloud Run)
      ↓
Google Cloud Firestore
users/{user_id}/expenses/
```

---

## Project Structure

```
Grid-Pulse/
├── app.py              ← Chainlit app with Google OAuth
├── mcp_config.py       ← Shared MCP server config and agent logic
├── client1.py          ← CLI client for local testing
├── chainlit.md         ← Chainlit readme shown in the UI
├── Dockerfile          ← For Render deployment
├── requirements.txt    ← Python dependencies
├── .gitignore
└── README.md
```

---

## Running Locally

**Prerequisites:** Python 3.13, pip or uv

**Step 1 — Clone and install:**
```bash
git clone https://github.com/a-ksharma/Grid-Pulse.git
cd Grid-Pulse
pip install -r requirements.txt
```

**Step 2 — Set up `.env`:**
```env
GOOGLE_API_KEY=your_gemini_api_key
OAUTH_GOOGLE_CLIENT_ID=your_google_oauth_client_id
OAUTH_GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
CHAINLIT_AUTH_SECRET=your_random_secret
```

**Step 3 — Run:**
```bash
chainlit run app.py --port 8001
```

Open `http://localhost:8001` in your browser.

---

## Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key from Google AI Studio |
| `OAUTH_GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID |
| `OAUTH_GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret |
| `CHAINLIT_AUTH_SECRET` | Random secret for Chainlit session signing |

---

## CLI Mode

For local testing without the UI, use the CLI client:

```bash
python client1.py
```

This runs the same agent logic in your terminal — useful for quick testing without spinning up the full Chainlit interface.

---

## Related

- **LedgerFlow MCP Server** — [github.com/a-ksharma/LedgerFlow](https://github.com/a-ksharma/LedgerFlow)

---

## Author

**Ayush Kumar Sharma**
- GitHub: [@a-ksharma](https://github.com/a-ksharma)
- LinkedIn: [@ayush-ksharma](https://www.linkedin.com/in/ayush-ksharma)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
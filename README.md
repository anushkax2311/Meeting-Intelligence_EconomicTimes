# 🧠 Meeting Intelligence — AI Workflow Automation System

A production-ready AI system that transforms meeting transcripts into structured tasks, verifies completeness, enables human approval, executes actions, and continuously monitors progress with automatic escalation.

---

## 🏗 Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Workflow | LangGraph |
| LLM | Claude (Anthropic) |
| Backend | FastAPI |
| Database | SQLite |
| Real-time | Server-Sent Events (SSE) |
| Integrations | Slack (Webhooks), Jira (simulated) |
| Async Tasks | asyncio |
| Frontend | HTML + JavaScript Dashboard |

---

## 📁 Project Structure

```text
meeting-intelligence/
│
├── agents/                     # AI workflow logic
│   ├── graph.py               # LangGraph workflow definition
│   ├── nodes.py               # Agents (extraction, verification, action, etc.)
│   └── state.py               # Typed workflow state
│
├── api/                       # FastAPI backend
│   ├── main.py               # Entry point + API routes
│   ├── db.py                 # Database operations
│   └── monitor.py            # Task monitoring + escalation logic
│
├── tools/                     # External integrations
│   ├── slack.py              # Slack notifications + tool schema
│   └── executor.py           # Tool execution handler
│
├── dashboard/                 # Frontend UI
│   └── index.html            # Dashboard interface
│
├── tests/                     # Test scripts
│   └── test_agents.py
│
├── tasks.db                   # Task storage (SQLite)
├── workflows.db               # LangGraph checkpoints (SQLite)
│
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```
---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/meeting-intelligence.git
cd meeting-intelligence
```

### 2. Setup Environment

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:

```env
# Google Gemini API Configuration (FREE!)
# Get your key at: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your_API_key

# Jira Configuration (optional)
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-token-here
JIRA_PROJECT_KEY=MI

# Slack Configuration (optional)
SLACK_WEBHOOK_URL=your_webhook_url

# Workflow Configuration
MAX_RETRIES=3
STALE_AFTER_HOURS=48
CHECK_INTERVAL_MINS=30

# Database
DATABASE_PATH=tasks.db
WORKFLOWS_DB_PATH=workflows.db

```

### 4. Initialize Database

```bash
python -c "from api.db import init_db; init_db()"
```

### 5. Run Backend Server

```bash
uvicorn api.main:app --reload
```

### 6. Run Dashboard

```bash
python -m http.server 5500
```

### 🌐 Open in Browser

```
http://localhost:5500/dashboard/index.html
```

---
---

## ⚙️ Core Components  

### 🧠 Extraction Agent  
- Converts raw transcript → structured tasks  
- Outputs JSON with tasks + decisions  

### ✅ Verification Agent  
Detects:  
- Missing owner  
- Missing deadlines  
- Low confidence tasks  

### 🧍 Human Review  
- Workflow pauses using LangGraph interrupt  
- Requires manual approval before proceeding  

### ⚡ Action Agent  
- Creates Jira tickets (simulated)  
- Sends Slack notifications  

### 🔁 Retry Logic  
- Handles failures with exponential backoff  

### ⏱️ Staleness Monitor  
- Runs in background  
- Detects tasks inactive for 48 hours  
- Triggers escalation:  
  - Owner → Manager → Ops  

---

## 📡 API Endpoints  

| Method | Endpoint | Description |
|--------|--------|------------|
| POST | `/run` | Start workflow |
| POST | `/approve/{thread_id}` | Resume after human input |
| GET | `/audit/{thread_id}` | Get audit trail |
| GET | `/stream/{thread_id}` | Live updates (SSE) |

---

## 🗄️ Data Models  

### Task  
- description  
- owner  
- deadline  
- priority  
- jira_url  
- status  
- escalation_level  

### Audit Log  
- stage  
- event  
- reasoning  
- timestamp  

---

## 🔄 Escalation Logic  

| Level | Action |
|------|--------|
| 0 | Notify Owner |
| 1 | Notify Manager |
| 2+ | Notify Ops |

📌 Triggered when task is stale for **48+ hours**

---

## 📊 Audit Trail Example  

```json
{
  "stage": "verification",
  "event": "GAPS_FOUND",
  "reasoning": "Task missing owner",
  "ts": "2026-03-26T10:00:04"
}
```

---

## 🏆 Key Features  

- Multi-agent AI workflow  
- Human-in-the-loop validation  
- Real-time audit tracking  
- Persistent checkpoints (resume after crash)  
- Automated escalation system  
- Live dashboard monitoring  

---

## 🚢 Deployment  

### Backend  
- Deploy on **Render / Railway**  

### Frontend  
- Static hosting (**Vercel / Netlify**)  

### Database  
- SQLite (can upgrade to Postgres)  

---

## ✅ Testing Checklist  

- [ ] Transcript → task extraction  
- [ ] Gap detection (missing owner/deadline)  
- [ ] Human approval flow  
- [ ] Task execution  
- [ ] Slack notifications  
- [ ] Escalation after 48h  
- [ ] Dashboard updates  
- [ ] Audit trail correctness  

---

## 🔮 Future Improvements  

- Real Jira API integration  
- Role-based approvals  
- Cloud deployment  
- Analytics dashboard  
- Multi-user support  

---

## 👩‍💻 Author  

**Anushka Patel**  
Economics Times GenAI Hackathon 2026  

---

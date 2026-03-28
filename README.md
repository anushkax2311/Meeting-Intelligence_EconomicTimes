# Meeting Intelligence Agent

A LangGraph-based multi-agent workflow for extracting, verifying, and executing action items from meeting transcripts.

## 🐛 Bugs Fixed

### 1. **Duplicate Function Definition in `tools/slack.py`**
   - **Issue**: `send_slack_message()` was defined twice, causing the second definition to override the first
   - **Fix**: Removed the incomplete second definition that only had a debug print statement
   - **Impact**: Slack messages will now work correctly with proper webhook integration

### 2. **Missing `confidence` Field in Fallback Task**
   - **Issue**: The fallback task in `agents/nodes.py` was missing the `confidence` field required by the `Task` TypedDict schema
   - **Fix**: Added `"confidence": "low"` to the fallback task
   - **Impact**: Prevents validation errors when extraction fails after retries

### 3. **Missing Timestamp in Monitor Audit Trail**
   - **Issue**: The `escalate()` function in `api/monitor.py` was not including the `ts` field in audit entries
   - **Fix**: Added `"ts": datetime.now(timezone.utc).isoformat()` to the audit trail entry
   - **Impact**: All audit entries now have consistent timestamp tracking

### 4. **Code Quality**
   - Removed large `venv/` directory (regenerate with `pip install -r requirements.txt`)
   - Removed generated database files (`*.db`, `*.db-shm`, `*.db-wal`)
   - Removed `__pycache__/` directories
   - Added comprehensive `.gitignore`

## 🚀 Setup

### Prerequisites
- Python 3.9+
- Anthropic API key
- Optional: Jira and Slack credentials for full integration

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r meeting-intelligence/requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp meeting-intelligence/.env.example meeting-intelligence/.env
   ```

   Edit `.env` with your credentials:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   JIRA_BASE_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   ```

   If credentials are not provided, the system runs in mock mode.

### Running the API

```bash
cd meeting-intelligence
python -m uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### 1. Run Workflow
```bash
POST /run
{
  "transcript": "Meeting transcript text..."
}
```

Returns:
```json
{
  "thread_id": "uuid",
  "stage": "extracted",
  "tasks": [...],
  "decisions": [...],
  "gaps": [...]
}
```

#### 2. Approve and Continue
```bash
POST /approve/{thread_id}
{
  "approver": "John Doe",
  "fixed_tasks": [...],
  "notes": "Optional notes"
}
```

#### 3. Get Audit Trail
```bash
GET /audit/{thread_id}
```

#### 4. Complete a Task
```bash
POST /tasks/{task_id}/complete
```

#### 5. Stream Audit Trail (Server-Sent Events)
```bash
GET /stream/{thread_id}
```

#### 6. Health Check
```bash
GET /health
```

## 📊 Workflow Stages

1. **Extraction**: Claude extracts tasks, decisions, and ambiguities from transcript
2. **Verification**: Validates that tasks have owners, deadlines (if high priority), and clear descriptions
3. **Human Review** (if gaps found): Waits for human approval and fixes
4. **Action**: Creates Jira tickets and sends Slack notifications
5. **Completion**: Tasks tracked in database with escalation monitoring

## 🔄 Retry Logic

- **Max Retries**: 3 (configurable via `MAX_RETRIES`)
- **Backoff Strategy**: Exponential backoff (2^attempt seconds, capped at 8 seconds)
- **Validation**: Automatic JSON parsing with multiple fallback strategies

## 📈 Task Monitoring

- **Stale Detection**: Tasks not updated for 48 hours (configurable)
- **Escalation Levels**: 0 (owner) → 1 (manager) → 2 (ops-team)
- **Check Interval**: Every 30 minutes (configurable)
- **Notifications**: Slack messages sent at each escalation level

## 🗄️ Database Schema

### `tasks` table
- `id`: Task UUID
- `thread_id`: Associated workflow thread
- `description`: Task description
- `owner`: Assigned person
- `deadline`: Due date
- `priority`: high|medium|low
- `status`: open|done
- `escalation_level`: 0-3
- `jira_url`: Link to Jira ticket
- `last_updated_at`: Timestamp

### `audit_log` table
- `id`: Entry UUID
- `thread_id`: Associated workflow thread
- `stage`: extraction|verification|human|action|monitor|retry
- `event`: STARTED|EXTRACTED|VERIFIED|etc.
- `reasoning`: Human-readable explanation
- `ts`: Timestamp (ISO 8601)

## 🧪 Testing

```bash
cd meeting-intelligence
python -m pytest tests/
```

## 📝 Project Structure

```
meeting-intelligence/
├── agents/
│   ├── graph.py          # LangGraph workflow definition
│   ├── nodes.py          # Extraction, verification, action nodes
│   ├── state.py          # Workflow state TypedDict
│   ├── prompts.py        # Claude system prompts
│   ├── parser.py         # JSON parsing utilities
│   └── __init__.py
├── api/
│   ├── main.py           # FastAPI application
│   ├── db.py             # Database operations
│   ├── monitor.py        # Stale task monitoring
│   └── __init__.py
├── tools/
│   ├── jira.py           # Jira integration
│   ├── slack.py          # Slack integration
│   └── __init__.py
├── tests/
│   └── test_agents.py
├── requirements.txt
└── .env.example
```

## 🔐 Security Notes

- Never commit `.env` files with real credentials
- Use environment variables or secret management systems in production
- Validate all inputs before passing to Claude
- Implement rate limiting for API endpoints
- Use HTTPS in production

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Run pytest to verify
5. Submit a pull request

## 📄 License

MIT

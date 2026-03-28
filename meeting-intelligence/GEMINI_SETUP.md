# 🚀 Using Google Gemini API (Free) with Your Project

## ✨ Why Gemini?

- **Completely FREE** - No credit card required
- **Generous Limits** - 60 requests/min, 1,500/day
- **Powerful Model** - Gemini 2.0 Flash is very capable
- **Easy Setup** - Just copy your API key

---

## 📋 Step-by-Step Setup

### 1. Get Your Free Gemini API Key

1. Go to: **https://aistudio.google.com/app/apikey**
2. Click **"Create API key"** 
3. Select **"Create API key in new project"**
4. Your API key will look like: `AIzaSy...` (starts with `AIza`)
5. **Copy it** - you'll need it next

### 2. Update Your .env File

```bash
# Navigate to your project
cd "C:\Users\Anushka Patel\Downloads\langgraph-hackathon-corrected\meeting-intelligence"

# Open .env with notepad
notepad .env
```

**Replace the contents with:**

```
GEMINI_API_KEY=AIzaSy-YOUR-ACTUAL-KEY-HERE

# Optional: Jira and Slack
JIRA_BASE_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=
SLACK_WEBHOOK_URL=
```

**Save and close** (Ctrl+S, then close)

### 3. Install Dependencies

```powershell
# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Install the updated requirements
pip install -r requirements.txt
```

**What got updated:**
- ✅ Removed: `anthropic>=0.25.0`
- ✅ Added: `google-generativeai>=0.3.0`

### 4. Run Your Project

```powershell
# Make sure you're in the meeting-intelligence folder
python -m uvicorn api.main:app --reload
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 5. Test It!

Open a **new PowerShell window** and run:

```powershell
curl -X POST http://localhost:8000/run `
  -H "Content-Type: application/json" `
  -d '{
    "transcript": "John said he will complete the API by Friday EOD. Sarah needs to update the documentation."
  }'
```

You should get back a response with extracted tasks! ✅

---

## 🆓 Free Tier Limits

| Limit | Value |
|-------|-------|
| Requests per minute | 60 |
| Requests per day | 1,500 |
| Cost | FREE |
| Credit card | NOT required |

**That's enough for:**
- Testing and development
- Small to medium production use
- Learning and prototyping

---

## 📊 Model Options (All Free)

The project uses **`gemini-2.0-flash`** which is:
- ⚡ Very fast
- 💰 Most generous free tier
- 📈 Excellent for JSON extraction tasks
- 🎯 Perfect for your meeting intelligence use case

---

## ✅ Verify Everything Works

Run this Python script to test the API connection:

```powershell
python
```

Then in the Python shell:

```python
import google.generativeai as genai
import os

# Test your API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {api_key[:10]}..." if api_key else "NO API KEY FOUND")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Say 'Hello from Gemini!' in JSON format")
print(response.text)
```

If you see the response, you're good to go! 🎉

---

## 🆘 Troubleshooting

### "API key not found" error
```
Error: GEMINI_API_KEY environment variable not set
```

**Fix:**
- Check your `.env` file has `GEMINI_API_KEY=AIza...`
- Make sure `.env` is in the `meeting-intelligence` folder
- Restart your terminal/PowerShell

### "quota exceeded" error
You've hit the free tier limit (1,500 requests/day)

**Fix:**
- Wait until the next day (quota resets at midnight UTC)
- Or upgrade to a paid plan if needed

### "Invalid API key" error
Your API key is malformed or wrong

**Fix:**
- Go back to https://aistudio.google.com/app/apikey
- Create a new API key
- Copy the full key (should start with `AIza`)
- Paste it in `.env`

---

## 💡 Tips & Tricks

### 1. Keep Your API Key Secret
Never commit `.env` to Git:
```bash
# This is already in .gitignore
echo ".env" >> .gitignore
```

### 2. Use API Key from Environment (Advanced)
If you want to set it in PowerShell instead of .env:

```powershell
$env:GEMINI_API_KEY = "AIza..."
python -m uvicorn api.main:app --reload
```

### 3. Monitor Your Quota
Track your usage at: https://console.cloud.google.com/apis/api/generativeai.googleapis.com

### 4. Switch Back to Claude Anytime
When you get Anthropic credits, just:
1. Update `requirements.txt` to use `anthropic`
2. Change imports in `nodes.py`
3. Update API calls back to Anthropic format

---

## 📚 Learn More

- **Gemini API Docs**: https://ai.google.dev/
- **Free Tier Details**: https://ai.google.dev/pricing
- **API Reference**: https://ai.google.dev/api/python/google/generativeai

---

## 🎯 You're All Set!

Your project now uses **Google Gemini API for FREE**. Start extracting tasks from meeting transcripts! 🚀

Questions? Check the main README.md in your project folder.

# 🧠 DS's Mind Tracker — Notion Summarizer

Automatically emails a visual summary of your Notion task tracker every 2 days.

## What it does

1. Queries the Task Tracker database in Notion
2. Filters to Critical/High priority tasks + anything due in the next 14 days
3. Fetches notes and comments for each task
4. Sends to OpenAI to produce a structured briefing with a unique quote of the day
5. Emails the summary via Zoho SMTP

## Stack

- Python 3.11
- Notion API
- OpenAI API (gpt-4o-mini)
- Zoho SMTP
- GitHub Actions (scheduler)

## Schedule

Runs automatically every 2 days at 7:00 AM UTC.

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/notion-summariser.git
cd notion-summariser
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

```
NOTION_API_KEY=your_notion_integration_token
OPENAI_API_KEY=your_openai_key
ZOHO_API_KEY=your_zoho_app_password
```

### 4. Run locally

```bash
python summarizer.py
```

### 5. GitHub Actions secrets

Add these 3 secrets to your repo (Settings → Secrets → Actions):

| Secret | Value |
|---|---|
| `NOTION_API_KEY` | Notion integration token |
| `OPENAI_API_KEY` | OpenAI API key |
| `ZOHO_API_KEY` | Zoho app-specific password |

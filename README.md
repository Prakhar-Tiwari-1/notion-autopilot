# Mind Tracker

Pulls critical and upcoming tasks from a Notion database, summarises them with GPT-4o-mini, and emails a formatted daily brief every two days.

---

## How it works

1. Queries the Notion task database for anything Critical, High priority, or due within the next 14 days
2. Fetches notes and comments for each task
3. Passes everything to GPT-4o-mini, which sorts tasks into buckets and writes a practical weekly plan
4. Renders the output as an HTML email (warm editorial design, Twemoji inline images) with a plain-text fallback
5. Sends it via SMTP

The model supplies only content. All HTML templating stays in Python.

---

## What the email looks like

![Email preview](shot.png)

---

## What you need from Notion

You need a Notion database with at least these properties (the names must match exactly):

| Property | Type | Notes |
|----------|------|-------|
| `Task` | Title | The task name |
| `Stage` | Select | Used to filter out finished tasks (value: `Finished`) |
| `Priority` | Select | Values used: `Critical`, `High` |
| `Due Date` | Date | Used for the 14-day lookahead filter |
| `Category` | Select | Optional grouping shown in the email |
| `Notes` | Rich text | Extra context attached to a task |

**Notion integration setup:**
1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) and create a new integration
2. Copy the integration token (this becomes `NOTION_API_KEY`)
3. Open your database in Notion, click the three-dot menu, go to **Connections**, and add your integration
4. Copy the database ID from the URL: `notion.so/YOUR_WORKSPACE/<database-id>?v=...`
5. Paste it into `TASK_DATABASE_ID` near the top of `summarizer.py`

---

## Setup

**1. Clone and install**

```bash
git clone https://github.com/YOUR_USERNAME/notion-mind-tracker.git
cd notion-mind-tracker
pip install -r requirements.txt
```

**2. Create a `.env` file**

```
NOTION_API_KEY=your_notion_integration_token
OPENAI_API_KEY=your_openai_key
ZOHO_API_KEY=your_zoho_app_password
```

**3. Run**

```bash
python summarizer.py
```

---

## Sending email

The script uses Zoho SMTP out of the box, but you can swap in any provider by editing `send_email()` at the bottom of `summarizer.py`.

**Zoho** (default)

Create an app-specific password at **Zoho Mail settings > Security > App Passwords**. Use `smtp.zoho.eu:465` for EU accounts or `smtp.zoho.com:465` for others.

**Gmail**

Enable 2-step verification on your Google account, then generate an app password at **myaccount.google.com > Security > App Passwords**. Change the SMTP line in `send_email()` to:

```python
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
```

Set `FROM_EMAIL` to your Gmail address and use the app password as `ZOHO_API_KEY` (or rename the variable).

**Other providers**

Most providers expose an SMTP host and port. Replace the host and port in the same line. Common examples:

| Provider | Host | Port |
|----------|------|------|
| Outlook / Hotmail | `smtp.office365.com` | `587` (STARTTLS) |
| Yahoo | `smtp.mail.yahoo.com` | `465` |
| Fastmail | `smtp.fastmail.com` | `465` |

For STARTTLS (port 587) instead of SSL (port 465), use `smtplib.SMTP` and call `server.starttls()` before `server.login()`.

---

## GitHub Actions

The workflow fires every two days at 7 AM UTC. Add the three keys above as repository secrets under **Settings > Secrets > Actions**, then push and it runs automatically.

You can also trigger it manually from the **Actions** tab.

| Secret | What it is |
|--------|------------|
| `NOTION_API_KEY` | Notion integration token |
| `OPENAI_API_KEY` | OpenAI API key |
| `ZOHO_API_KEY` | SMTP app password (Zoho, Gmail, or other) |

---

## Adapting it

The Notion database ID, email addresses, and task filter are all near the top of `summarizer.py`. The model prompt and bucket definitions are in `build_content()`.

---

## Stack

Python · Notion API · OpenAI API · SMTP · GitHub Actions

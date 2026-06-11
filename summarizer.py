import os
import smtplib
import requests
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY   = os.environ["NOTION_API_KEY"]
OPENAI_API_KEY   = os.environ["OPENAI_API_KEY"]
ZOHO_PASSWORD    = os.environ["ZOHO_API_KEY"]
TASK_DATABASE_ID = "911d2703b4ea4135ac8d75f17cacd3ba"

FROM_EMAIL = "contact@prakhartiwari.com"
TO_EMAIL   = "prakhar.tiwari@polytechnique.edu"

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def fetch_comments(page_id: str) -> str:
    res = requests.get(
        "https://api.notion.com/v1/comments",
        headers=NOTION_HEADERS,
        params={"block_id": page_id},
    )
    if not res.ok:
        return ""
    comments = []
    for c in res.json().get("results", []):
        text = "".join(rt["plain_text"] for rt in c.get("rich_text", []))
        if text.strip():
            comments.append(f"    💬 {text}")
    return "\n".join(comments)


def fetch_tasks() -> str:
    url      = f"https://api.notion.com/v1/databases/{TASK_DATABASE_ID}/query"
    in_14    = (date.today() + timedelta(days=14)).isoformat()
    tasks    = []

    payload = {
        "sorts": [{"property": "Due Date", "direction": "ascending"}],
        "filter": {
            "and": [
                {"property": "Stage", "select": {"does_not_equal": "✅ Finished"}},
                {
                    "or": [
                        {"property": "Priority", "select": {"equals": "🔥 Critical"}},
                        {"property": "Priority", "select": {"equals": "⚡ High"}},
                        {"property": "Due Date", "date": {"on_or_before": in_14}},
                    ]
                },
            ]
        },
    }

    while True:
        res = requests.post(url, headers=NOTION_HEADERS, json=payload)
        res.raise_for_status()
        data = res.json()

        for page in data.get("results", []):
            props    = page["properties"]
            page_id  = page["id"]

            name     = "".join(t["plain_text"] for t in props["Task"]["title"])
            priority = (props["Priority"]["select"] or {}).get("name", "—")
            stage    = (props["Stage"]["select"] or {}).get("name", "—")
            category = (props["Category"]["select"] or {}).get("name", "—")
            due      = (props["Due Date"]["date"] or {}).get("start", "no date")
            notes    = "".join(t["plain_text"] for t in props["Notes"]["rich_text"])
            comments = fetch_comments(page_id)

            line = f"[{priority}] {name}\n  Stage: {stage} | Category: {category} | Due: {due}"
            if notes:
                line += f"\n  Notes: {notes}"
            if comments:
                line += f"\n{comments}"
            tasks.append(line)

        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    return "\n\n".join(tasks)


def build_email(tasks: str) -> str:
    today     = date.today().strftime("%A, %B %d %Y")
    client    = OpenAI(api_key=OPENAI_API_KEY)

    week_start = date.today().strftime("%B %d")
    week_end   = (date.today() + timedelta(days=6)).strftime("%B %d")

    template = f"""\
You are a personal assistant. Produce a visually structured plain-text email — no markdown, no asterisks, no bold.
Use only: Unicode box/line characters, emojis, spacing, and indentation for visual structure.
Today is {today}.

Use EXACTLY this layout:


        🧠  DS'S MIND TRACKER
        {today}
-------------------------------------

  ✦  QUOTE OF THE DAY

  "[A unique, fresh quote — philosophical, from a book, person, or poem.
   Must be different every single time. Never repeat.]"
  — [Author or Source]


══════════════════════════════════════

  🔥  CRITICAL & URGENT
  ──────────────────────
  [For each task: name on its own line, then indented details below it.
   Show: due date, category, notes, comments. Leave blank line between tasks.]

  ◈  [Task Name]
     Due · [date]   Category · [category]
     [Notes if any]
     💬 [Comment if any]


══════════════════════════════════════

  📅  COMING UP — NEXT 2 WEEKS
  ─────────────────────────────
  [Same format as above. Group by urgency within the section.]

  ◇  [Task Name]
     Due · [date]   Category · [category]
     [Notes if any]
     💬 [Comment if any]


══════════════════════════════════════

  ⚡  HIGH PRIORITY  ·  NO DEADLINE
  ───────────────────────────────────
  [Same format. Only include if there are tasks here.]


══════════════════════════════════════

  🗓  WEEKLY PLAN  ·  {week_start} – {week_end}
  ──────────────────────────────────────
  [Based on the tasks above, write a short practical day-by-day plan for this week.
   3–5 lines max. Focus on what to tackle first, what to batch together, and any deadlines to hit.
   Be direct and specific — no generic advice. Use this format:]

  Mon – Wed  ·  [what to focus on]
  Thu – Fri  ·  [what to focus on]
  Weekend    ·  [anything to wrap up or prep]


══════════════════════════════════════

  🎙  WORDS TO CARRY
  ───────────────────
  [A short excerpt (3–6 sentences) from a real speech or writing by a well-known world leader,
   entrepreneur, athlete, philosopher, or artist. Pick a different person every single time —
   vary across fields and eras. Never repeat the same person twice in a row.
   Attribute it properly below.]

  "[Speech excerpt here]"

  — [Full Name], [context e.g. Stanford Commencement 2005 / Letter to shareholders 1997]


══════════════════════════════════════
  Stay sharp. 🚀
══════════════════════════════════════

Rules:
- No asterisks, no markdown syntax, no angle brackets.
- Every note and comment must appear under its task — drop nothing.
- Keep spacing clean and consistent.
- If a section has no tasks, omit it entirely.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": template},
            {"role": "user",   "content": tasks},
        ],
    )
    return response.choices[0].message.content


def send_email(body: str) -> None:
    today = date.today().strftime("%b %d")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🧠 Mind Tracker — {today}"
    msg["From"]    = FROM_EMAIL
    msg["To"]      = TO_EMAIL

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.zoho.eu", 465) as server:
        server.login(FROM_EMAIL, ZOHO_PASSWORD)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())

    print(f"Email sent to {TO_EMAIL}")


if __name__ == "__main__":
    print("Fetching tasks from Notion...")
    tasks = fetch_tasks()

    if not tasks.strip():
        print("No urgent or upcoming tasks found.")
        raise SystemExit(0)

    print("Building email...")
    body = build_email(tasks)

    print("Sending email...")
    send_email(body)

    print("Done.")

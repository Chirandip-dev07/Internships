import os
import requests
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

TO_EMAIL = "chirandiproy@gmail.com"

FROM_EMAIL = os.environ["FROM_EMAIL"]
SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
SERPAPI_KEY = os.environ["SERPAPI_KEY"]

ROLES = ["Software Intern", "Data Science Intern", "Product Intern"]
LOCATIONS = ["India", "Remote", "Delhi NCR"]
MAX_RESULTS = 8


def fetch_jobs():
    jobs = []

    for role in ROLES:
        for loc in LOCATIONS:
            params = {
                "engine": "google_jobs",
                "q": f"{role} fresher",
                "location": loc,
                "api_key": SERPAPI_KEY
            }

            r = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
            data = r.json()

            for j in data.get("jobs_results", [])[:2]:
                jobs.append({
                    "title": j.get("title"),
                    "company": j.get("company_name"),
                    "location": j.get("location"),
                    "summary": j.get("description", "")[:250],
                    "link": j.get("related_links", [{}])[0].get("link", "")
                })

            if len(jobs) >= MAX_RESULTS:
                return jobs

    return jobs


def send_email(body):
    msg = MIMEMultipart()
    msg["Subject"] = f"Daily Internships Report — {datetime.date.today()}"
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def main():
    jobs = fetch_jobs()

    if not jobs:
        body = "No internships found today."
    else:
        lines = [f"Daily Internships Report — {datetime.date.today()}\n"]
        for i, j in enumerate(jobs, 1):
            lines.append(
                f"{i}. {j['title']} — {j['company']}\n"
                f"Location: {j['location']}\n"
                f"{j['summary']}\n"
                f"Link: {j['link']}\n"
            )
        body = "\n".join(lines)

    send_email(body)


if __name__ == "__main__":
    main()


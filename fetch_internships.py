import os
import requests
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ================== EMAIL CONFIG ==================
TO_EMAIL = "chirandiproy@gmail.com"

FROM_EMAIL = os.environ["FROM_EMAIL"]
SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]

SERPAPI_KEY = os.environ["SERPAPI_KEY"]

# ================== SEARCH FILTERS ==================
ROLES = [
    "Data Science Intern",
    "Python Developer Intern",
    "Data Analyst Intern",
    "Machine Learning Intern",
    "Business Analytics Intern",
    "AI Intern"
]

KEYWORDS = [
    "python",
    "data science",
    "machine learning",
    "data analytics",
    "sql",
    "pandas",
    "numpy"
]

LOCATIONS = ["India", "Remote", "Delhi NCR"]
MAX_RESULTS = 8

# ================== FETCH JOBS ==================
def fetch_jobs():
    jobs = []

    for role in ROLES:
        for loc in LOCATIONS:
            params = {
                "engine": "google_jobs",
                "q": f"{role} fresher python",
                "location": loc,
                "api_key": SERPAPI_KEY
            }

            response = requests.get(
                "https://serpapi.com/search.json",
                params=params,
                timeout=30
            )

            data = response.json()

            for j in data.get("jobs_results", []):
                description = j.get("description", "").lower()

                # 🔍 Keyword filtering
                if not any(k in description for k in KEYWORDS):
                    continue

                jobs.append({
                    "title": j.get("title", "N/A"),
                    "company": j.get("company_name", "N/A"),
                    "location": j.get("location", loc),
                    "summary": j.get("description", "")[:250],
                    "link": j.get("related_links", [{}])[0].get("link", "N/A")
                })

                if len(jobs) >= MAX_RESULTS:
                    return jobs

    return jobs

# ================== EMAIL ==================
def send_email(jobs):
    today = datetime.date.today()
    subject = f"Daily Data Science & Python Internships — {today}"

    if not jobs:
        body = "No Data Science / Python / Analytics internships found today."
    else:
        lines = [f"Daily Internship Report — {today}\n"]
        for i, j in enumerate(jobs, 1):
            lines.append(
                f"{i}. {j['title']} — {j['company']}\n"
                f"Location: {j['location']}\n"
                f"Summary: {j['summary']}\n"
                f"Link: {j['link']}\n"
            )
        body = "\n".join(lines)

    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

# ================== MAIN ==================
def main():
    jobs = fetch_jobs()
    send_email(jobs)

if __name__ == "__main__":
    main()

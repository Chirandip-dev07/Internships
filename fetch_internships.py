

import os
import sys
import datetime
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

TO_EMAIL = "chirandiproy@gmail.com"
FROM_EMAIL = os.environ.get("FROM_EMAIL")      
SMTP_HOST = os.environ.get("SMTP_HOST")         
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")

ROLES = ["software development", "data science", "product"]
LOCATIONS = ["remote", "India", "Delhi NCR"]
MAX_RESULTS = 8

def search_indeed(role, location, max_results=3):
    q = quote_plus(role)
    l = quote_plus(location)
    url = f"https://www.indeed.com/jobs?q={q}&l={l}&sort=date"
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select(".jobsearch-SerpJobCard")[:max_results]
        results = []
        for c in cards:
            title = c.select_one(".title a")
            if not title: continue
            title_text = title.get_text(strip=True)
            link = "https://www.indeed.com" + title.get("href")
            company = c.select_one(".company").get_text(strip=True) if c.select_one(".company") else ""
            loc = c.select_one(".location").get_text(strip=True) if c.select_one(".location") else location
            summary = c.select_one(".summary").get_text(strip=True) if c.select_one(".summary") else ""
            results.append({"title": title_text, "company": company, "location": loc, "summary": summary, "link": link})
        return results
    except Exception:
        return []

def search_wellfound(role, location, max_results=3):
    q = quote_plus(role)
    url = f"https://wellfound.com/jobs?query={q}"
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("a.AnchorLink_jobCard")[:max_results]
        results = []
        for c in cards:
            title = c.select_one(".jobCard_title")
            company = c.select_one(".jobCard_company")
            link = "https://wellfound.com" + c.get("href")
            results.append({
                "title": title.get_text(strip=True) if title else "",
                "company": company.get_text(strip=True) if company else "",
                "location": location,
                "summary": "",
                "link": link
            })
        return results
    except Exception:
        return []

def search_internshala(role, location, max_results=3):
    q = quote_plus(role)
    url = f"https://internshala.com/internships/{q}-internship"
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select(".internship_listing")[:max_results]
        results = []
        for c in cards:
            title = c.select_one("a.profile")
            if not title: continue
            title_text = title.get_text(strip=True)
            link = "https://internshala.com" + title.get("href")
            company = c.select_one(".company_name").get_text(strip=True) if c.select_one(".company_name") else ""
            loc = c.select_one(".location_link").get_text(strip=True) if c.select_one(".location_link") else location
            summary = c.select_one(".other_detail_item").get_text(strip=True) if c.select_one(".other_detail_item") else ""
            results.append({"title": title_text, "company": company, "location": loc, "summary": summary, "link": link})
        return results
    except Exception:
        return []

def gather_listings():
    listings = []
    per_source = max(1, MAX_RESULTS // 3)
    for role in ROLES:
        for loc in LOCATIONS:
            listings.extend(search_internshala(role, loc, per_source))
            time.sleep(1)
            listings.extend(search_wellfound(role, loc, per_source))
            time.sleep(1)
            listings.extend(search_indeed(role, loc, per_source))
            time.sleep(1)
            if len(listings) >= MAX_RESULTS:
                break
        if len(listings) >= MAX_RESULTS:
            break
    seen = set()
    dedup = []
    for l in listings:
        if l["link"] not in seen:
            seen.add(l["link"])
            dedup.append(l)
        if len(dedup) >= MAX_RESULTS:
            break
    return dedup

def compose_markdown(listings):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    lines = [f"# Daily Internships Report — {today}\n"]
    lines.append(f"Generated: {datetime.datetime.now().isoformat()}\n")
    lines.append("## Listings\n")
    for i, l in enumerate(listings, 1):
        lines.append(f"### {i}. {l['title']} — {l['company']}\n")
        lines.append(f"- **Location:** {l['location']}")
        short = l['summary'] or "No short summary."
        if len(short) > 280: short = short[:277] + "..."
        lines.append(f"- **Summary:** {short}")
        lines.append(f"- **Link:** {l['link']}\n")
    return "\n".join(lines)

def send_email(subject, body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())

def main():
    listings = gather_listings()
    md = compose_markdown(listings)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    subject = f"Daily Internships Report — {today}"

    fname = f"daily_internships_{today}.md"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(md)

    send_email(subject, md)
    print("Email sent to", TO_EMAIL)

if __name__ == "__main__":
    main()

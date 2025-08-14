import requests, json, html
from bs4 import BeautifulSoup
from .models import Job

def scrape_remoteok():
    url = "https://remoteok.com/remote-dev-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ Failed")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    job_elements = soup.select("tr.job")

    for tr in job_elements[:5]:
        script_tag = tr.find("script", type="application/ld+json")
        if not script_tag:
            continue
        try:
            raw_json = html.unescape(script_tag.string.strip())
            raw_json = raw_json.replace(',}', '}').replace(',]', ']')
            data = json.loads(raw_json)

            title = data.get("title")
            company = data.get("hiringOrganization", {}).get("name")
            description = BeautifulSoup(data.get("description", ""), "html.parser").text.strip()
            location = data.get("jobLocationType", "Remote")
            link = "https://remoteok.com" + tr.get("data-href")

            Job.objects.create(
                title=title,
                company=company,
                location=location,
                description=description,
                link=link,
                source="remoteok",
                raw_html=str(tr)
            )
            print(f"💾 Saved: {title}")

        except Exception as e:
            print("❌ Error parsing job:", e)
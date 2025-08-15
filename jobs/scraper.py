
import requests, json, html
from bs4 import BeautifulSoup
from django.db import IntegrityError
from .models import Job

def scrape_remoteok(limit=20):
    url = "https://remoteok.com/remote-dev-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code != 200:
        print("Failed:", r.status_code); return

    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("tr.job")[:limit]

    # discover model fields so we don’t hardcode
    job_fields = {f.name for f in Job._meta.get_fields() if getattr(f, "concrete", True)}
    allowed_defaults = job_fields - {"id", "link", "source", "created_at"}  # link+source used as identity

    new, updated = 0, 0
    for tr in rows:
        script_tag = tr.find("script", type="application/ld+json")
        if not script_tag: 
            continue
        try:
            raw_json = html.unescape((script_tag.string or "").strip()).replace(",}", "}").replace(",]", "]")
            data = json.loads(raw_json)

            title = (data.get("title") or "").strip()
            company = ((data.get("hiringOrganization") or {}).get("name") or "").strip()
            description = BeautifulSoup(data.get("description", ""), "html.parser").get_text(" ", strip=True)
            location = data.get("jobLocationType", "Remote")
            link = "https://remoteok.com" + (tr.get("data-href") or "")

            if not (title and company and link):
                continue

            # Build defaults dynamically (only fields your model actually has)
            defaults = {}
            if "title" in allowed_defaults: defaults["title"] = title
            if "company" in allowed_defaults: defaults["company"] = company
            if "location" in allowed_defaults: defaults["location"] = location
            if "description" in allowed_defaults: defaults["description"] = description
            if "raw_html" in allowed_defaults: defaults["raw_html"] = str(tr)

            obj, created = Job.objects.update_or_create(
                link=link,
                source="remoteok",
                defaults=defaults
            )
            new += 1 if created else 0
            updated += 0 if created else 1
        except IntegrityError:
            continue
        except Exception as e:
            print("Error:", e)

    print(f"Upsert complete. New: {new}, Updated: {updated}")

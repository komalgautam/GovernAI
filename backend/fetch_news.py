import asyncio
from datetime import datetime, timedelta
import aiohttp
import feedparser
from bs4 import BeautifulSoup
import http.client
import json
from dateutil import parser as date_parser

# Load .env
load_dotenv()

# Get SERPER API key securely
SERPER_API_KEY = os.getenv("SERPER_API_KEY") # Replace with your actual key

RSS_FEEDS = {
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
    "Tech Policy Press": "https://techpolicy.press/feed/",
    "The Markup": "https://themarkup.org/feed",
    "Wired": "https://www.wired.com/feed/category/ai/latest/rss",
    "Rest of World": "https://restofworld.org/feed/",
    "OECD AI": "https://oecd.ai/feed.xml",
    "UNESCO": "https://en.unesco.org/artificial-intelligence/feed",
    "AI Now": "https://ainowinstitute.org/feed.xml",
    "Harvard BKC": "https://cyber.harvard.edu/rss.xml",
    "Stanford HAI": "https://hai.stanford.edu/rss.xml",
    "Brookings": "https://www.brookings.edu/blog/techtank/feed/",
    "AI Policy Exchange": "https://aipolicyexchange.org/feed/",
    "Carnegie Endowment": "https://carnegieendowment.org/rss/topic/1867"
}

TRUSTED_SITES = [
    "technologyreview.com", "techpolicy.press", "restofworld.org", "wired.com",
    "brookings.edu", "oecd.ai", "unesco.org", "ainowinstitute.org",
    "cyber.harvard.edu", "hai.stanford.edu", "aipolicyexchange.org", "carnegieendowment.org"
]

# Normalize Serper "source" to match RSS source names
SOURCE_MAP = {
    "technologyreview.com": "MIT Technology Review",
    "techpolicy.press": "Tech Policy Press",
    "restofworld.org": "Rest of World",
    "wired.com": "Wired",
    "brookings.edu": "Brookings",
    "oecd.ai": "OECD AI",
    "unesco.org": "UNESCO",
    "ainowinstitute.org": "AI Now",
    "cyber.harvard.edu": "Harvard BKC",
    "hai.stanford.edu": "Stanford HAI",
    "aipolicyexchange.org": "AI Policy Exchange",
    "carnegieendowment.org": "Carnegie Endowment"
}

def clean_html(raw_html):
    return BeautifulSoup(raw_html or '', "html.parser").get_text(separator=" ", strip=True)

async def fetch_rss(session, src, url, cutoff):
    items = []
    try:
        async with session.get(url, timeout=15, ssl=False) as resp:
            data = await resp.text()
        feed = feedparser.parse(data)
        for e in feed.entries:
            dt = datetime(*e.published_parsed[:6]) if e.get('published_parsed') else None
            if not dt or dt < cutoff:
                continue
            summary_text = clean_html(e.get("summary", "") or e.get("description", ""))
            items.append({
                "source": src,
                "title": e.get("title", "Untitled").strip(),
                "summary": summary_text[:500],
                "link": e.get("link", ""),
                "published": dt.isoformat(),
                "content": summary_text  # RSS doesn't provide full body
            })
    except Exception as e:
        print(f"RSS fetch error for {src}:", e)
    return items

def fetch_serper_results(query, cutoff):
    items = []
    try:
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
            "q": query,
            "num": 20,
            "include_webpage": True
        })
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        results = json.loads(data.decode("utf-8"))

        for r in results.get("organic", []):
            try:
                raw_date = r.get("date")
                dt = date_parser.parse(raw_date, fuzzy=True) if raw_date else datetime.now()
            except Exception as e:
                print(f"Failed to parse Serper date '{raw_date}': {e}")
                dt = datetime.now()
            if dt < cutoff:
                continue

            domain = r.get("link", "").split("/")[2] if r.get("link") else ""
            site = next((d for d in TRUSTED_SITES if d in domain), "Other")
            norm_source = SOURCE_MAP.get(site, r.get("source", "Unknown"))

            items.append({
                "source": norm_source,
                "title": r.get("title", "Untitled").strip(),
                "summary": clean_html(r.get("snippet", ""))[:500],
                "link": r.get("link"),
                "published": dt.isoformat(),
                "content": clean_html(r.get("webpage", "") or r.get("snippet", ""))
            })
    except Exception as e:
        print("Serper API error:", e)
    return items

def fetch_trusted_ai_news(limit=50, days_back=7):
    cutoff = datetime.now() - timedelta(days=days_back)

    async def fetch_all():
        async with aiohttp.ClientSession() as session:
            rss_tasks = [fetch_rss(session, src, url, cutoff) for src, url in RSS_FEEDS.items()]
            feeds = await asyncio.gather(*rss_tasks)
            rss_items = [i for sublist in feeds for i in sublist if isinstance(i, dict)]

        query = "AI ethics OR responsible AI site:" + " OR site:".join(TRUSTED_SITES)
        serper_items = fetch_serper_results(query, cutoff)

        combined = rss_items + serper_items
        combined.sort(key=lambda i: i.get("published", ""), reverse=True)
        return combined[:limit]

    return asyncio.run(fetch_all())

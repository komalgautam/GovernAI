import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from io import BytesIO
from collections import Counter
import re

def extract_country_mentions(items):
    df = pd.DataFrame(items)
    df["text"] = df["title"] + " " + df["summary"]
    countries = ["USA","China","India","UK","Germany","France","Canada","Australia"]
    for c in countries:
        df[c] = df["text"].str.contains(c, case=False).astype(int)
    cnt = df[countries].sum().reset_index()
    cnt.columns=["Country","Mentions"]
    return cnt[cnt.Mentions > 0]

def generate_wordcloud(items):
    text = " ".join(i["title"] + " " + i["summary"] for i in items)
    try:
        wc = WordCloud(width=800, height=400, background_color="white").generate(text)
        buf = BytesIO()
        wc.to_image().save(buf, format="PNG")
        buf.seek(0)
        return buf
    except Exception as e:
        print("❌ Word cloud generation failed:", e)
        return None

def sentiment_trend(items):
    df = pd.DataFrame(items)
    trend = df.groupby("source").size().reset_index(name="Count")
    return px.bar(trend, x="source", y="Count", title="Articles per Source", text_auto=True)

def source_time_trend(items):
    df = pd.DataFrame(items)
    df["date"] = pd.to_datetime(df["published"], errors="coerce").dt.date
    grouped = df.groupby(["date", "source"]).size().reset_index(name="Articles")
    return px.line(grouped, x="date", y="Articles", color="source", title="Daily Article Count by Source")

def daily_overall_trend(items):
    df = pd.DataFrame(items)
    df["date"] = pd.to_datetime(df["published"], errors="coerce").dt.date
    df = df.dropna(subset=["date"])
    daily = df.groupby("date").size().reset_index(name="Articles")
    return px.area(daily, x="date", y="Articles", title="Total Daily Articles on Responsible AI", markers=True)

def top_keywords(items, n=15):
    text = " ".join(i["title"] + " " + i["summary"] for i in items)
    tokens = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    keywords = Counter(tokens).most_common(n)
    df = pd.DataFrame(keywords, columns=["Keyword", "Frequency"])
    return px.bar(df, x="Keyword", y="Frequency", title="Top Keywords in Weekly News")

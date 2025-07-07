# 🧠 GovernAI — Tracking the Ethics of Intelligence

**GovernAI** is an experimental AI-powered assistant designed to track, analyze, and visualize trends in *AI governance, ethics, and policy* from trusted global sources.

This is **Version 1.0** — the foundation. It’s functional, insightful, and already connects to a multi-source real-time news pipeline. But it’s just the beginning. The roadmap ahead includes smarter summarization, broader data coverage, alert systems, and user-defined focus areas.

---

## 🌐 What It Does

GovernAI is your real-time assistant for responsible AI updates. It helps you:

- 🤖 **Ask Questions** about ethical AI developments using retrieval-augmented Gemini models.
- 📰 **Get Weekly Digests** with collective and source-wise bullet summaries.
- 📊 **Visualize Trends** in global mentions, sources, sentiment, and policy keywords.

All of this is built with a beautiful and responsive [Streamlit](https://streamlit.io) interface.

---

## 🗞 Trusted Sources

GovernAI pulls from respected publications and research institutes, including:

- **MIT Tech Review**
- **The Markup**
- **Tech Policy Press**
- **UNESCO**
- **OECD AI Observatory**
- **Stanford HAI**
- **Harvard Berkman Klein**
- **AI Now Institute**
- **Carnegie AI Policy Initiative**
- **AI Policy Exchange (India)**
- ...and more via Serper-powered ethical AI searches.

---

## 🧩 Features

| Feature | Description |
|--------|-------------|
| 🗣️ Ask AI | Chat interface to ask about trends, bias, laws, and frameworks |
| 📰 Weekly Digest | Summarized updates from the past 7/14/30 days |
| 📊 Visual Insights | Country-wise AI mentions, top keywords, source trends, and word clouds |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/GovernAI.git
cd GovernAI

2. Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Create a .env file with:
GOOGLE_API_KEY=your_gemini_api_key

4. Run it!
streamlit run app.py
📸 Screenshots


🔧 Tech Stack

🧠 Gemini API (Google Generative AI)
🧱 LangChain + VectorDB
📰 RSS + Serper News
📊 Plotly + Pandas
🎨 Streamlit UI
🤔 What’s Next?

GovernAI is still evolving. Planned future updates include:

✅ Addition and better data sourcing from trusted sources.
✅ Topic filtering by theme or region
✅ Email digests & alerts
✅ User-authored dashboards
✅ NLP-powered policy timeline comparison
✅ Open Graph or LinkedIn card previews

If you'd like to contribute, suggest new sources, or request custom use cases, feel free to open an issue or pull request.

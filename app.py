import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import plotly.express as px

from backend.rag_chain import (
    create_retriever_and_articles,
    answer_query,
    collective_digest,
    per_source_bullets
)
from backend.visualize import (
    extract_country_mentions,
    generate_wordcloud,
    sentiment_trend,
    source_time_trend,
    daily_overall_trend,
    top_keywords
)

# Load environment variables
load_dotenv()

# Validate API key
if not os.getenv("GOOGLE_API_KEY"):
    st.error("Set GOOGLE_API_KEY in .env")
    st.stop()

# Streamlit app setup
st.set_page_config(page_title="GovernAI", layout="wide")
st.markdown("# 🤖 GovernAI – Monitor and summarize AI governance worldwide. ")

# Sidebar options
days = st.sidebar.selectbox("Date range (days):", [7, 14, 30], index=0)
mode = st.sidebar.selectbox("Mode:", ["Ask AI", "Weekly Digest", "Visual Insights"])

# Fetch news and retriever
retriever, items = create_retriever_and_articles(days)
valid_items = [i for i in items if isinstance(i, dict) and 'title' in i and 'summary' in i]

# Mode: Ask AI
if mode == "Ask AI":
    st.subheader("💬 Ask GovernAI about AI ethics")
    q = st.chat_input("Ask about AI ethics, policies, or trends...")
    if q:
        a = answer_query(q, retriever)
        st.chat_message("user").write(q)
        st.chat_message("assistant").write(a)

# Mode: Weekly Digest
elif mode == "Weekly Digest":
    st.subheader("🗞 Weekly Digest")
    if valid_items:
        digest = collective_digest(valid_items)
        st.markdown("### 🔎 Overall Summary")
        
        # Strip double newlines, normalize spacing
        bullet_lines = [line.strip("•-– ").strip() for line in digest.splitlines() if line.strip()]
        for line in bullet_lines:
            st.markdown(f"- {line}")

        st.markdown("### 🧭 Source-specific Summaries")
        bullets = per_source_bullets(valid_items)
        for src, txt in bullets.items():
            st.markdown(f"**📰 {src}**")
            clean_lines = [
                line.lstrip("*•-– ").strip()
                for line in txt.splitlines()
                if line.strip() and not line.strip().lower().startswith("source:")
            ]
            for line in clean_lines:
                st.markdown(f"- {line}")
            st.markdown("---")

    else:
        st.warning("No valid news articles available for the selected time range.")

# Mode: Visual Insights
elif mode == "Visual Insights":
    st.subheader("📊 Visual Insights")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌍 Country Mentions",
        "📈 Article Trends",
        "📊 Source Timeline",
        "☁️ Word Cloud",
        "🔑 Top Keywords"
    ])

    with tab1:
        df = extract_country_mentions(valid_items)
        if not df.empty:
            st.plotly_chart(
                px.choropleth(df, locations="Country", locationmode="country names", color="Mentions",
                              title="AI Mentions by Country (in headlines & summaries)"))
        else:
            st.info("No country mentions detected in the selected timeframe.")

    with tab2:
        fig = sentiment_trend(valid_items)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = daily_overall_trend(valid_items)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        fig3 = source_time_trend(valid_items)
        st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        img = generate_wordcloud(valid_items)
        if img:
            st.image(img, caption="Top words in recent AI news")
        else:
            st.error("Word cloud generation failed.")

    with tab5:
        df_keywords = top_keywords(valid_items)
        if isinstance(df_keywords, pd.DataFrame) and not df_keywords.empty:
            fig_kw = px.bar(df_keywords, x="Keyword", y="Frequency", title="Top Keywords in Weekly News")
            st.plotly_chart(fig_kw, use_container_width=True)
        else:
            st.info("No keywords available.")

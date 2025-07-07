# 📁 backend/rag_chain.py – Refined Gemini Summarization Prompts
# from langchain.vectorstores import DocArrayInMemorySearch
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.fetch_news import fetch_trusted_ai_news
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load Gemini key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

EMB_MODEL = "all-MiniLM-L6-v2"

def run_llm(prompt: str) -> str:
    try:
        response = llm.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("⚠️ LLM error:", e)
        return "⚠️ Could not generate content."



def create_retriever_and_articles(days: int):
    items = fetch_trusted_ai_news(limit=50, days_back=days)
    docs = [Document(page_content=f"{i.get('title', '')}\n{i.get('summary', '')}") for i in items if isinstance(i, dict)]
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=40)
    chunks = splitter.split_documents(docs)
    
    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(chunks, embedder)

    return vectordb.as_retriever(), items

def collective_digest(items):
    valid_items = [i for i in items if isinstance(i, dict) and 'title' in i and 'summary' in i and 'link' in i]
    if not valid_items:
        return "⚠️ No valid headlines to summarize. Please try again later."

    content = "\n".join(f"- {i['title']}: {i['summary']}" for i in valid_items)
    prompt = (
        "You are summarizing weekly news articles related to AI ethics and policy. "
        "From the following headlines and summaries, extract the 5 most important insights as short bullet points. "
        "Use compact, professional language. Do not repeat headlines. Focus on substance.:\n\n"
        f"{content}\n\nRespond in bullet points only."
    )
    return run_llm(prompt)

def per_source_bullets(items):
    groups = {}
    for it in items:
        if isinstance(it, dict) and 'source' in it and 'title' in it:
            groups.setdefault(it['source'], []).append(it)

    summaries = {}
    for src, its in groups.items():
        titles = [i['title'] for i in its if 'title' in i]
        if not titles:
            continue
        content = "\n".join(f"- {title}" for title in titles)
        prompt = (
            f"You are analyzing AI ethics headlines from the source: {src}. "
            "From the list of titles below, write 3 concise bullet-point insights. "
            "Do not copy titles verbatim. Focus on the implied trend or issue:\n\n"
            f"{content}\n\nRespond with 3 concise bullet points."
        )
        summaries[src] = run_llm(prompt)
    return summaries

def answer_query(question, retriever):
    try:
        docs = retriever.get_relevant_documents(question)
        if not docs:
            return "⚠️ No relevant news articles found to answer this question."
        context = "\n\n".join(d.page_content for d in docs[:5])
        prompt = (
            "Use the context below to answer the user’s question about AI ethics or policy. "
            "Be brief and focused. If uncertain, say so clearly.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        )
        return run_llm(prompt)
    except Exception as e:
        return f"⚠️ Unable to answer the query due to an error: {e}"

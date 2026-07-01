import streamlit as st
import requests
import time
import os

st.set_page_config(page_title="Enterprise Document Intelligence Workspace", layout="wide", page_icon="📥")

# 🌐 Pulls your live Render API link or falls back locally
FASTAPI_URL = os.getenv("BACKEND_API_URL") or st.secrets.get("BACKEND_API_URL", "http://127.0.0.1:8000")

# 🔑 Grab the master security token from Streamlit environments
API_KEY = os.getenv("X_API_KEY") or st.secrets.get("X_API_KEY", "")

# 📦 Package authentication headers for FastAPI validation check
HEADERS = {
    "X-API-Key": API_KEY
}

st.title("🗂️ Enterprise Document Intelligence Workspace")
st.subheader("Upload Document for Local Index Partitioning")

uploaded_file = st.file_uploader("Choose a PDF or Text Document", type=["pdf", "txt"], label_visibility="collapsed")

if uploaded_file is not None:
    if st.button("⚡ Build Local Vector Index", use_container_width=True):
        with st.spinner("Processing document data structure and anchoring vectors..."):
            try:
                # Prepare payload file array matching FastAPI specs
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Make authorized request attaching validation headers
                response = requests.post(f"{FASTAPI_URL}/api/index-document", files=files, headers=HEADERS)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"🎉 Success! '{data['filename']}' indexed completely into {data['total_chunks']} vector embeddings.")
                elif response.status_code == 403:
                    st.error("❌ Upload Blocked: Invalid or missing API access authorization token.")
                else:
                    st.error(f"❌ Error {response.status_code}: {response.json().get('detail', 'Unknown runtime exception')}")
            except Exception as e:
                st.error(f"🔌 Connection Failed: Could not communicate with backend. Check if your Render URL is active. Details: {str(e)}")

st.write("---")
st.subheader("💬 AI Document Chat Room")

# Attempt to load indexed documents listing
try:
    list_response = requests.get(f"{FASTAPI_URL}/api/list-documents", headers=HEADERS)
    if list_response.status_code == 200:
        available_docs = list_response.json().get("documents", [])
    else:
        available_docs = []
except Exception:
    available_docs = []

if available_docs:
    selected_doc = st.selectbox("Select a target workspace context index:", available_docs)
    user_query = st.text_input("Ask a question about the document context:")
    
    if st.button("Send Query") and user_query:
        with st.spinner("Retrieving document chunks and formatting response context..."):
            payload = {"filename": selected_doc, "question": user_query}
            try:
                chat_response = requests.post(f"{FASTAPI_URL}/api/chat", json=payload, headers=HEADERS)
                if chat_response.status_code == 200:
                    result = chat_response.json()
                    st.write("**Assistant Answer:**")
                    st.info(result["answer"])
                    st.caption(f"📑 Sources Cited: Page(s) {', '.join(map(str, result['pages_cited']))}")
                else:
                    st.error(f"❌ Chat Error: {chat_response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Request failed: {str(e)}")
else:
    st.info("💡 Upload and build a vector index on a document above to initialize your interactive chat session context.")
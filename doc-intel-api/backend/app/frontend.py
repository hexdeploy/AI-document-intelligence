import streamlit as st
import requests
import time
import json

FASTAPI_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")

# Keep your security header exactly as is
HEADERS = {"X-Workspace-Token": "sec_ws_dev_2026_matrix"}

st.set_page_config(page_title="AI Document Intelligence Workspace", page_icon="⚙️", layout="wide")

with st.sidebar:
    st.header("🗂️ Document Workspace")
    st.markdown("---")
    
    active_docs = []
    try:
        #  Secured with header token injection
        res = requests.get(f"{FASTAPI_URL}/api/list-documents", headers=HEADERS)
        if res.status_code == 200:
            active_docs = res.json().get("documents", [])
    except:
        st.error("Could not reach secure backend metrics.")

    if active_docs:
        selected_doc = st.selectbox("Switch Active Document Focus:", active_docs, index=0)
        st.success(f"🎯 Loaded Index Context: **{selected_doc}**")
    else:
        selected_doc = None
        st.info("No documents are currently initialized in local index directories.")

    st.markdown("---")
    if st.button("🗑️ Reset Application Chat History", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

col1, col2 = st.columns([2, 3])

with col1:
    st.header("📥 Workspace Upload Entry")
    uploaded_file = st.file_uploader("Upload Document for Local Index Partitioning", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        if st.button("⚡ Build Local Vector Index", use_container_width=True):
            with st.spinner("Extracting content matrix, tracking pages, writing vectors..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    #  Secured with header token injection
                    response = requests.post(f"{FASTAPI_URL}/api/index-document", files=files, headers=HEADERS)
                    
                    if response.status_code == 200:
                        st.success(f"✅ Indexed! Registered to Workspace Storage.")
                        st.session_state["active_file"] = uploaded_file.name
                        time.sleep(1)
                        st.rerun()
                    elif response.status_code == 429:
                        st.error("❌ Rate Limit Exceeded: You are uploading too fast. Please wait a minute before trying again.")
                    else:
                        st.error(f"❌ Upload Blocked: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"System communication error: {str(e)}")

with col2:
    st.header("💬 Contextual Workspace Engine")
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("citations"):
                st.caption(f"📑 Sources verified from Page(s): {', '.join(map(str, msg['citations']))}")

    if user_query := st.chat_input("Query anything about the active workspace index asset..."):
        if not selected_doc:
            st.warning("Please upload a document to launch conversational tracking.")
        else:
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state["messages"].append({"role": "user", "content": user_query})

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                try:
                    payload = {"filename": selected_doc, "question": user_query}
                    #  Secured with header token injection
                    response = requests.post(f"{FASTAPI_URL}/api/chat", json=payload, headers=HEADERS)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        answer_text = res_data.get("answer", "")
                        citations = res_data.get("pages_cited", [])
                        
                        displayed_text = ""
                        for token in answer_text.split(" "):
                            displayed_text += token + " "
                            time.sleep(0.04)
                            message_placeholder.markdown(displayed_text + "▌")
                        
                        message_placeholder.markdown(answer_text)
                        if citations:
                            st.caption(f"📑 Sources verified from Page(s): {', '.join(map(str, citations))}")
                        
                        st.session_state["messages"].append({
                            "role": "assistant",
                            "content": answer_text,
                            "citations": citations
                        })
                    elif response.status_code == 429:
                        st.error("❌ Rate Limit Triggered: You're messaging too rapidly. Take a breath.")
                    else:
                        st.error(f"Chat pipeline error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"System communication error: {str(e)}")
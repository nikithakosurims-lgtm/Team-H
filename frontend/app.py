import streamlit as st
import requests
import base64
import time

st.set_page_config(page_title="PDF-Aware Smart Chatbot", layout="wide")

st.title("📄 PDF-Aware Smart Chatbot (PS4)")

# API Base URL
API_URL = "http://localhost:8001"

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_file" not in st.session_state:
    st.session_state.current_file = None
if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- UI Layout: Split Screen ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("💬 Chat & Interaction")
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
    
    if uploaded_file is not None and st.session_state.current_file != uploaded_file.name:
        with st.spinner("Processing PDF and generating smart suggestions..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post(f"{API_URL}/upload/", files=files)
            
            if response.status_code == 200:
                st.session_state.current_file = uploaded_file.name
                st.session_state.pdf_data = uploaded_file.getvalue()
                st.success(f"Successfully indexed {uploaded_file.name}!")
                # Give background task a second to generate some initial questions
                time.sleep(2) 
            else:
                try:
                    error_detail = response.json().get("detail", "Failed to process PDF.")
                except:
                    error_detail = "Failed to process PDF."
                st.error(f"Error: {error_detail}")

    st.divider()
    
    # Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Autocomplete input logic
    st.subheader("Ask a question:")
    query = st.text_input("Type your question here...", key="query_input")
    
    if query and st.session_state.current_file:
        try:
            res = requests.get(f"{API_URL}/autocomplete/", params={"query": query, "filename": st.session_state.current_file})
            if res.status_code == 200:
                suggs = res.json().get("suggestions", [])
                if suggs:
                    st.caption("✨ Suggestions based on document:")
                    for s in suggs:
                        st.markdown(f"*{s}*")
        except Exception as e:
            pass

    if st.button("Send", type="primary"):
        if query and st.session_state.current_file:
            st.session_state.chat_history.append({"role": "user", "content": query})
            
            with st.spinner("Thinking..."):
                res = requests.post(f"{API_URL}/chat/", json={"query": query, "filename": st.session_state.current_file})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.chat_history.append({"role": "assistant", "content": data["response"]})
                    
                    # Handle PDF Modification
                    if data.get("updated_pdf_url"):
                        updated_path = data["updated_pdf_url"]
                        try:
                            # Read the updated PDF file from the backend's path
                            with open(updated_path, "rb") as f:
                                st.session_state.pdf_data = f.read()
                            st.toast("PDF successfully updated!", icon="🎉")
                        except Exception as e:
                            st.error(f"Could not load updated PDF: {e}")
                else:
                    st.error("Error from chat API.")
            st.rerun()

with col2:
    st.header("📄 Live PDF Viewer")
    if st.session_state.pdf_data:
        display_pdf(st.session_state.pdf_data)
    else:
        st.info("Upload a PDF to see it here.")

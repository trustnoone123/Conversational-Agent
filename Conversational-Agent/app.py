#app.py

import streamlit as st
import os
from llm.conversational_agent import ConversationalAgent
from db.neo4j_client import (
    save_pdf_document_to_neo4j,
    get_pdf_documents
)
from utils.pdf_processor import PDFProcessor

# Page configuration
st.set_page_config(
    page_title="PDF to DB Converter with Conversational Agent", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .conversation-bubble {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    .user-bubble {
        background: #f3e5f5;
        border-left: 4px solid #9c27b0;
        text-align: right;
    }
    .pdf-info {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "conversational_agent" not in st.session_state:
    st.session_state.conversational_agent = ConversationalAgent()

if "uploaded_pdfs" not in st.session_state:
    st.session_state.uploaded_pdfs = []

if "current_chat" not in st.session_state:
    st.session_state.current_chat = []

if "pdf_processor" not in st.session_state:
    st.session_state.pdf_processor = PDFProcessor()

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 PDF to DB Converter with Conversational Agent</h1>
    <p>Upload PDFs to Neo4j database and interact through natural conversation</p>
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Conversational Assistant")
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.current_chat:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="conversation-bubble user-bubble">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="conversation-bubble">
                    <strong>Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Display suggested actions if available
                if "suggested_actions" in message and message["suggested_actions"]:
                    st.write("**Suggested actions:**")
                    for i, action in enumerate(message["suggested_actions"]):
                        # Create a unique key using message index, action index, and action content
                        unique_key = f"action_{len(st.session_state.current_chat)}_{i}_{action[:20].replace(' ', '_')}"
                        if st.button(action, key=unique_key):
                            # Add the action as a user message
                            st.session_state.current_chat.append({
                                "role": "user",
                                "content": action
                            })
                            st.rerun()
    
    # User input
    user_input = st.text_input(
        "Ask me anything about your documents or request assistance:",
        placeholder="e.g., 'What documents do I have?', 'Analyze the uploaded PDF', 'Help me with...'"
    )
    
    if user_input:
        # Add user message to chat
        st.session_state.current_chat.append({
            "role": "user",
            "content": user_input
        })
        
        # Generate response
        with st.spinner("🤔 Thinking..."):
            # Build context
            pdf_context = None
            if st.session_state.uploaded_pdfs:
                pdf_names = [pdf['filename'] for pdf in st.session_state.uploaded_pdfs]
                pdf_context = f"Available PDFs: {', '.join(pdf_names)}"
            
            graph_context = "Neo4j graph database for storing PDF documents and their content"
            
            # Get response from conversational agent
            response = st.session_state.conversational_agent.generate_response(
                user_input, pdf_context, graph_context
            )
            
            # Add assistant response to chat
            st.session_state.current_chat.append({
                "role": "assistant",
                "content": response["content"],
                "suggested_actions": response.get("suggested_actions", [])
            })
            
            # Rerun to display the new messages
            st.rerun()

with col2:
    st.header("📚 PDF Management")
    
    # PDF Upload Section
    st.subheader("📄 Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=['pdf'], 
        help="Upload a PDF document for analysis and storage"
    )
    
    if uploaded_file is not None:
        if st.button("🔍 Process & Store PDF"):
            with st.spinner("Processing PDF..."):
                # Process the PDF
                pdf_data = st.session_state.pdf_processor.extract_text_from_pdf(uploaded_file)
                
                if pdf_data:
                    # Extract key information
                    pdf_data['key_info'] = st.session_state.pdf_processor.extract_key_information(
                        pdf_data['extracted_text']
                    )
                    
                    # Save to Neo4j
                    try:
                        save_pdf_document_to_neo4j(pdf_data)
                        st.session_state.uploaded_pdfs.append(pdf_data)
                        st.success(f"✅ PDF '{pdf_data['filename']}' processed and stored successfully!")
                        
                        # Add to conversation
                        st.session_state.conversational_agent.add_message(
                            "system", 
                            f"New PDF uploaded: {pdf_data['filename']} with {pdf_data['total_pages']} pages"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Error saving to database: {str(e)}")
                else:
                    st.error("❌ Failed to process PDF")
    
    # View Uploaded PDFs
    st.subheader("📋 Uploaded Documents")
    if st.session_state.uploaded_pdfs:
        for pdf in st.session_state.uploaded_pdfs:
            with st.expander(f"📄 {pdf['filename']}"):
                st.write(f"**Title:** {pdf['metadata']['title']}")
                st.write(f"**Pages:** {pdf['total_pages']}")
                st.write(f"**Words:** {pdf['key_info']['estimated_word_count']}")
                if pdf['key_info']['main_topics']:
                    st.write(f"**Topics:** {', '.join(pdf['key_info']['main_topics'][:3])}")
    else:
        st.info("No PDFs uploaded yet.")
    
    # Conversation Controls
    st.subheader("💬 Conversation")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.current_chat = []
        st.session_state.conversational_agent.clear_history()
        st.rerun()
    
    if st.button("📊 View Chat Summary"):
        summary = st.session_state.conversational_agent.get_conversation_summary()
        st.text_area("Chat Summary", summary, height=200)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 Powered by OpenAI GPT-4 | 🗄️ Neo4j Graph Database | 📄 PDF Processing</p>
</div>
""", unsafe_allow_html=True)

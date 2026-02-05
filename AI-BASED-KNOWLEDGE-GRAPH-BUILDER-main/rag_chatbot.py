import streamlit as st
from src.knowledge_graph.pipeline.rag_pipeline import RAGPipeline

# --- Page Configuration ---
st.set_page_config(
    page_title="RAG Knowledge Graph Chatbot",
    page_icon="📚",
    layout="wide"
)

# --- Header Section ---
st.title("📚 RAG Knowledge Graph Chatbot")
st.caption(
    "Ask questions from your ingested documents. "
    "Answers are retrieved using vector search and knowledge graph context."
)

# --- 1. Startup & Initialization ---

@st.cache_resource(show_spinner=False)
def load_rag_chain():
    """Load and cache the RAG pipeline."""
    return RAGPipeline.get_rag_chain()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": (
                "👋 **Welcome!**\n\n"
                "You can ask questions based on the documents loaded into the system.\n\n"
                "The chatbot retrieves relevant information from the knowledge base "
                "and provides answers along with supporting context."
            )
        }
    ]

# Load RAG pipeline
if "chain" not in st.session_state:
    with st.spinner("🔄 Initializing the RAG system..."):
        try:
            st.session_state["chain"] = load_rag_chain()
        except Exception as e:
            st.error(f"❌ Failed to initialize the system: {str(e)}")

# --- 2. Chat Interface ---

# Display chat history
for msg in st.session_state["messages"]:
    avatar = "📘" if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your question here and press Enter..."):
    
    # Show user message
    st.session_state["messages"].append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant", avatar="📘"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 Searching the knowledge base...")

        try:
            chain = st.session_state.get("chain")
            if chain:
                response = chain.invoke(prompt)

                message_placeholder.markdown(response)

                st.session_state["messages"].append(
                    {"role": "assistant", "content": response}
                )
            else:
                message_placeholder.error(
                    "⚠️ Session expired. Please refresh the page."
                )
        except Exception as e:
            error_msg = f"⚠️ An unexpected error occurred: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state["messages"].append(
                {"role": "assistant", "content": error_msg}
            )

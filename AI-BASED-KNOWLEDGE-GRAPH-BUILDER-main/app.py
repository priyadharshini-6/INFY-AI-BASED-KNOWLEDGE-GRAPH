

import chainlit as cl

from src.knowledge_graph.components.rag_pipeline import RAGPipeline

# ---------- Startup ----------
@cl.on_chat_start
async def start():
    await cl.Message(
        content="""
# 🌟 Welcome to Cognexa.
Cognexa retrieves and synthesizes information from your knowledge base to deliver precise, evidence-grounded answers.
"""
    ).send()

    try:
        rag = RAGPipeline()
        cl.user_session.set("rag", rag)

    except Exception as e:
        await cl.Message(
            content=f"❌ Failed to initialize RAG system: {str(e)}"
        ).send()


# ---------- Chat Loop ----------
@cl.on_message
async def main(message: cl.Message):
    rag = cl.user_session.get("rag")

    if not rag:
        await cl.Message(
            content="⚠️ Session expired. Please refresh the page."
        ).send()
        return

    with cl.Step(name="🔍 Retrieving relevant documents", type="run") as step:
        try:
            answer, sources = rag.answer(message.content)
            step.output = "✅ Retrieval complete"
        except Exception as e:
            step.output = f"❌ Error: {str(e)}"
            await cl.Message(content=str(e)).send()
            return

    # ---------- Final Answer ----------
    response = f"### 📑 Answer\n{answer}\n\n---\n### 📚 Source Documents\n"
    for src in sources:
        response += f"- `{src}`\n"

    await cl.Message(content=response).send()

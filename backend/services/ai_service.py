from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config.database import get_vectorstore

autocomplete_store = {}

def generate_autocomplete_questions(text: str, filename: str):
    """Background task to generate questions using LLM for autocomplete."""
    try:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
        prompt = f"Based on the following text, generate 5 likely questions a user might ask. Output ONLY the questions, one per line.\n\nText excerpt: {text[:4000]}"
        response = llm.invoke(prompt)
        questions = [q.strip("- ") for q in response.content.split("\n") if q.strip()]
        
        if filename not in autocomplete_store:
            autocomplete_store[filename] = []
        autocomplete_store[filename].extend(questions)
        print(f"Generated {len(questions)} suggestions for {filename}")
    except Exception as e:
        print(f"Failed to generate questions: {e}")

def get_suggestions(query: str, filename: str = None):
    suggestions = []
    if filename and filename in autocomplete_store:
        all_suggs = autocomplete_store[filename]
        # Simple substring match
        suggestions = [s for s in all_suggs if query.lower() in s.lower()]
        if not suggestions:
            suggestions = all_suggs[:5] # Return top 5 if no match
    else:
        # Fallback if no specific file or no questions generated yet
        suggestions = [f"What is the summary of this document?", f"Tell me more about {query}"]
        
    return {"suggestions": suggestions[:5]}

def process_chat(query: str, filename: str):
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    vectorstore = get_vectorstore()
    
    is_mod_request = any(keyword in query.lower() for keyword in ["summarize and add", "insert as page 1", "update pdf", "add an executive summary"])
    
    if is_mod_request:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5, "filter": {"source": filename}})
        docs = retriever.invoke(query)
        context_text = "\n\n".join([doc.page_content for doc in docs])
        
        system_prompt = f"You are an assistant. Provide a concise executive summary of the document based on the user's request. Output only the summary text.\n\nContext:\n{context_text}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        response = llm.invoke(messages)
        new_text = response.content
        return {"is_mod_request": True, "new_text": new_text}
    else:
        # Standard RAG Answering
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3, "filter": {"source": filename}})
        docs = retriever.invoke(query)
        context_text = "\n\n".join([doc.page_content for doc in docs])
        
        system_prompt = f"You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, say that you don't know.\n\nContext:\n{context_text}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        response = llm.invoke(messages)
        return {"is_mod_request": False, "response": response.content}

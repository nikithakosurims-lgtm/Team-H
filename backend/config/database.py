from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

persist_directory = "./chroma_db"
vectorstore = None

def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        try:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        except Exception as e:
            print(f"Warning: Could not initialize HuggingFace Embeddings. Error: {e}")
    return vectorstore

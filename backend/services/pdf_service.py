import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.config.database import get_vectorstore

def process_and_store_pdf(file_location: str, filename: str):
    # 1. Parse PDF
    doc = fitz.open(file_location)
    full_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        full_text += page.get_text()
        
    # 2. Chunk Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(full_text)
    
    if not chunks:
        raise ValueError("No extractable text found in the PDF. This might be a scanned document without text. Please use an OCR tool first or upload a text-based PDF.")
    
    
    # 3. Store in ChromaDB
    vectorstore = get_vectorstore()
    metadatas = [{"source": filename, "chunk_id": i} for i in range(len(chunks))]
    vectorstore.add_texts(texts=chunks, metadatas=metadatas)
    
    return full_text, len(chunks)

def modify_pdf_with_summary(original_path: str, updated_path: str, new_text: str):
    doc = fitz.open(original_path)
    # Create a new blank page at the beginning
    doc.insert_page(0, width=595, height=842) # Standard A4 size
    page = doc.load_page(0)
    
    # Add a title and the generated text
    page.insert_text(fitz.Point(50, 50), "Executive Summary (Auto-Generated)", fontsize=16, fontname="helv", color=(0, 0, 1)) # Blue title
    
    # Insert the summary text with word wrap
    rect = fitz.Rect(50, 80, 545, 800)
    page.insert_textbox(rect, new_text, fontsize=11, fontname="helv", align=0)
    
    doc.save(updated_path)
    doc.close()

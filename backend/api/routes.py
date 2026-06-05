from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from backend.dto.schemas import ChatRequest
from backend.services.pdf_service import process_and_store_pdf, modify_pdf_with_summary
from backend.services.ai_service import generate_autocomplete_questions, get_suggestions, process_chat

router = APIRouter()

@router.post("/upload/")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Must be a PDF file")
        
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
        
    try:
        full_text, chunks_len = process_and_store_pdf(file_location, file.filename)
        
        # Generate Autocomplete Suggestions in background
        background_tasks.add_task(generate_autocomplete_questions, full_text, file.filename)
        
        return {
            "info": f"Successfully processed {file.filename}",
            "chunks": chunks_len
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/autocomplete/")
def get_autocomplete_suggestions_route(query: str, filename: str = None):
    return get_suggestions(query, filename)

@router.post("/chat/")
def chat(request: ChatRequest):
    try:
        result = process_chat(request.query, request.filename)
        
        if result.get("is_mod_request"):
            original_path = f"temp_{request.filename}"
            updated_path = f"updated_{request.filename}"
            
            modify_pdf_with_summary(original_path, updated_path, result["new_text"])
            
            return {
                "response": "I have summarized the section and added it as a new Executive Summary on Page 1 of the PDF. The viewer on the right should update shortly.",
                "updated_pdf_url": updated_path
            }
        else:
            return {
                "response": result["response"],
                "updated_pdf_url": None
            }
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

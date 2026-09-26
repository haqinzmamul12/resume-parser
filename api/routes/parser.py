


# Create api endpoint to load pdf of resume


from fastapi import APIRouter, File, UploadFile
from modules.resume.unstructured import UnstructuredResumeParser
from modules.resume.extractor import ResumeExtractor
import tempfile
import os
from modules.llm.model import extract_resume
import json

router = APIRouter()

@router.post("/parse")
async def parse_resume(file: UploadFile = File(...)):
    try:
        # Use NamedTemporaryFile to write uploaded PDF to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file.file.read())
            temp_path = temp_file.name

        extractor = ResumeExtractor(temp_path)
        image_paths = extractor.extract_images()
        parser = UnstructuredResumeParser(image_paths)
        # parser.extract() returns a list of dicts each containing a 'markdown' key.
        extracted = parser.extract()
        markdown = "\n".join(item.get('markdown', '') for item in extracted)
        result = extract_resume(markdown)
        
        # If the LLM response was incomplete, it is returned under "raw_response".
        # Attempt to decode it so the API always returns a proper JSON object.
        if isinstance(result, dict) and "raw_response" in result:
            try:
                result = json.loads(result["raw_response"])
            except Exception:
                # Keep the original raw string if parsing fails.
                pass
        
        return {
            "success": True,
            "data": result,
            "error": "",
            "filename": file.filename
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "error": str(e),
            "filename": file.filename
        }

    finally:
        #delete temporary path
        if os.path.exists(temp_path):
            os.remove(temp_path)

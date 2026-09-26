
import mimetypes
import os
import fitz
from typing import List
from pathlib import Path


class ResumeExtractor:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path
        self.images: List[Path] = []

    

    def extract_images(self):
        # Open the PDF document
        doc = fitz.open(self.resume_path)
        image_paths = []
        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)
            if not image_list:
                # No embedded images on this page – render the whole page as PNG
                pix = page.get_pixmap()
                image_path = f"page{page_index+1}.png"
                pix.save(image_path)
                image_paths.append(image_path)
                continue
            for image_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_path = f"page{page_index+1}_image{image_index+1}.{image_ext}"
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                image_paths.append(image_path)
        self.images = image_paths
        return self.images
    

    def _load_resume(self) -> bytes:

        # GET MIME BASED EXTENSION AND CHECK IF NOT .PDF RETURN ELSE PROCEED

        mime_file_type, _ = mimetypes.guess_type(self.resume_path)

        if mime_file_type != "application/pdf":
            raise Exception("File is not a PDF")

        try:
            return self.extract_images()
        except Exception as e:
            raise Exception(f"Error loading resume: {str(e)}")


    
            
    
        
    

        
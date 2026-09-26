from pydantic import BaseModel
from pydantic import Field


# Create a pydantic schema for resume fields use pydantic, field for description

class ResumeParserResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    data: dict[str, any] = Field(..., description="Resume data")
    error: str = Field(..., description="Error message")
    filename: str = Field(..., description="Filename")
    

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "data": {
                        "name": "John Doe",
                        "email": "[EMAIL_ADDRESS]",
                        "phone": "1234567890",
                        "address": "123 Main St, Anytown, USA",
                        "skills": ["Python", "Java", "SQL"],
                        "experience": [
                            {
                                "title": "Software Engineer",
                                "company": "Google",
                                "years": "2020-2022"
                            }
                        ],
                        "education": [
                            {
                                "degree": "Bachelor of Science",
                                "university": "University of California, Berkeley",
                                "year": "2016-2020"
                            }
                        ]
                    },
                    "error": "",
                    "filename": "resume.pdf"
                }
            ]
        }
    }

    
    
    
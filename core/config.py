
import os
from pydantic.v1 import BaseSettings
from pydantic.v1 import Field
from typing import Optional

class ConfigSettings(BaseSettings):
    project_name: str = "Resume Parser"
    project_version: str = "1.0.0"
    #load from .env
    unstructured_api_url: Optional[str] = Field("https://transform.unstructured.io", description="Unstructured API URL", env="UNSTRUCTURED_API_URL")
    unstructured_server_url: Optional[str] = Field("https://transform.unstructured.io", description="Unstructured API base URL", env="UNSTRUCTURED_SERVER_URL")
    unstructured_api_key: Optional[str] = Field("", description="Unstructured API Key", env="UNSTRUCTURED_API_KEY")
    groq_api_key: Optional[str] = Field("", description="Groq API Key", env="GROQ_API_KEY")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        env_file_encoding = "utf-8"



settings = ConfigSettings()
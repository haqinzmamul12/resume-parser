import os
# from unstructured_client import UnstructuredClient  # Deprecated, using TransformClient
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image, ImageEnhance

from core.config import settings
from .extractor import ResumeExtractor
from unstructured_transform_client import TransformClient
from io import BytesIO
import logging 


logger = logging.getLogger(__name__)


class UnstructuredResumeParser:
    """Parse resume content from images using the Unstructured.io API.

    The parser can operate on a list of image file paths directly or accept a PDF
    file via :meth:`parse_pdf`, which extracts page images using
    :class:`ResumeExtractor`.
    """

    def __init__(self, image_paths: Optional[List[Path] | List[str]] = None):
        """Create a new parser instance.

        Args:
            image_paths: Optional iterable of file paths pointing to the resume page
                images. If ``None``, the parser can be used via ``parse_pdf``.
        """
        if image_paths is None:
            self.image_paths: List[Path] = []
        else:
            # Normalise to ``Path`` objects for easier handling.
            self.image_paths = [Path(p) for p in image_paths]
        self.api_url = settings.unstructured_api_url

        if not self.api_url:
            raise ValueError("Unstructured API URL not configured")
            
        self.api_key = settings.unstructured_api_key
        if not self.api_key:
            raise ValueError("Unstructured API Key not configured")
        self.client = TransformClient(api_key=self.api_key, server_url="https://transform.unstructured.io")

    def _preprocess_image(self, image_path: Path) -> bytes:
        """Load an image, apply basic enhancements, and return raw bytes.

        The processing steps aim for a balance between quality and speed:
        * Convert to RGB (required for many OCR services).
        * Resize so the longest side is at most 1024 px while preserving aspect
          ratio.
        * Increase contrast by a factor of 1.5 – this often improves OCR
          accuracy on scanned documents.
        * Save to an in‑memory PNG buffer.
        """
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            max_dim = 1024
            if max(img.size) > max_dim:
                scale = max_dim / max(img.size)
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, Image.LANCZOS)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return buffer.getvalue()

    def _call_transform_client(self, image_bytes: bytes) -> Dict:
        """Send image bytes to Unstructured Transform service using the client.

        Returns a dictionary compatible with the previous API response structure.
        """
        # Wrap bytes in a BytesIO object with a name attribute for compatibility
        stream = BytesIO(image_bytes)
        stream.name = "image.png"
        result = self.client.parse.run(
            input=stream,
            output="markdown",
            profile="best",
        )
        
        return {"markdown": result.markdown}

    def extract(self) -> List[Dict]:
        """Process all supplied images and return the extracted data.

        Returns:
            A list where each element corresponds to the API response for one
            image. The order matches ``self.image_paths``.
        """
        results: List[Dict] = []
        for path in self.image_paths:
            if not path.is_file():
                raise FileNotFoundError(f"Image not found: {path}")
            img_bytes = self._preprocess_image(path)
            result = self._call_transform_client(img_bytes)
            results.append(result)
        return results

    

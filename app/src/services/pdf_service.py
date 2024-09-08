import fitz  # PyMuPDF library for handling PDFs
from fastapi import UploadFile
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def process_pdf(file: UploadFile) -> str:
# async def process_pdf(file: UploadFile) -> str:
    """Extracts text from the uploaded PDF file."""
    try:
        text = ""
        with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        raise ValueError(f"Failed to process PDF: {e}")

def vectorize_text(text: str) -> np.ndarray:
    """Vectorizes the extracted text using TF-IDF."""
    try:
        # Initialize TF-IDF Vectorizer
        vectorizer = TfidfVectorizer(stop_words='english')

        # Transform the text into TF-IDF features
        tfidf_matrix = vectorizer.fit_transform([text])

        # Convert the TF-IDF matrix to a numpy array
        tfidf_array = tfidf_matrix.toarray()

        return tfidf_array
    except Exception as e:
        raise ValueError(f"Failed to vectorize text: {e}")
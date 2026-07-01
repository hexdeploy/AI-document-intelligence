import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class DocumentEmbedder:
    def __init__(self):
        # 🛠️ FIXED: Swapped out the old model for Google's current active embedding endpoint
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2-preview")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def chunk_text(self, text: str) -> list[str]:
        """Splits raw string content into structured manageable chunks."""
        return self.text_splitter.split_text(text)

    def get_embeddings_engine(self):
        """Returns the core embedding engine wrapper for the vector database."""
        return self.embeddings
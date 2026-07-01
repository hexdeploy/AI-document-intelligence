import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Define structured JSON output format for entities
class InsightPayload(BaseModel):
    summary: str = Field(description="A concise 3-4 sentence summary of the entire document content.")
    sentiment: str = Field(description="Overall sentiment tone (e.g., Professional, Urgent, Informative, Critical).")
    key_entities: list[str] = Field(description="List of core named entities, companies, products, or dates found.")

class InsightsProcessor:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.1,  # Low temperature for highly accurate data extraction
            google_api_key=api_key
        )
        self.parser = JsonOutputParser(pydantic_object=InsightPayload)

    def extract_document_insights(self, full_text: str) -> dict:
        """Analyzes the full text to extract summary, sentiment, and core entities."""
        # Trim text if it exceeds structural token comfort bounds for basic parsing
        max_chars = 40000
        content = full_text[:max_chars] if len(full_text) > max_chars else full_text

        system_prompt = (
            "You are a clinical data extraction engine. Analyze the provided document text thoroughly.\n"
            "Extract a concise summary, detect the dominant tone/sentiment, and capture key entities.\n"
            "{format_instructions}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Document Content:\n{document_text}")
        ])

        # Inject formatting instructions matching our Pydantic schema rules
        partial_prompt = prompt.partial(format_instructions=self.parser.get_format_instructions())
        
        # Simple extraction chain
        chain = partial_prompt | self.llm | self.parser
        
        try:
            return chain.invoke({"document_text": content})
        except Exception as e:
            # Fallback layout if parsing fails
            return {
                "summary": "Failed to generate summary due to processing limits.",
                "sentiment": "Unknown",
                "key_entities": [f"Error: {str(e)}"]
            }
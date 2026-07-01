import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.services.vector_store import VectorStoreManager

class RAGPipeline:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            print("⚠️ WARNING: GOOGLE_API_KEY environment variable is missing!")
            
        # 🛠️ FIXED: Changed from 'gemini-2.5-flash' to the globally resolved stable 'gemini-2.5-flash' identifier
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.2,
            google_api_key=api_key
        )
        self.vector_manager = VectorStoreManager()

    def answer_question(self, question: str) -> dict:
        """Retrieves matching context chunks and passes them to Gemini for an answer."""
        retriever = self.vector_manager.get_retriever()
        
        system_prompt = (
            "You are an expert AI assistant tasked with answering questions about the provided document context.\n"
            "Use the following pieces of retrieved context to answer the question. If you don't know the answer, "
            "say that you don't know based on the document text. Keep your answer concise.\n\n"
            "Context:\n{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        response = rag_chain.invoke({"input": question})
        
        return {
            "answer": response["answer"],
            "source_documents": [doc.page_content for doc in response["context"]]
        }
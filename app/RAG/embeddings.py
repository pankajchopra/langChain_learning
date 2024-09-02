# Import necessary packages for LLM chat model APIs
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
import os
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import abc


class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Custom embedding function using the Gemini AI API for document retrieval.

    This class extends the EmbeddingFunction class and implements the __call__ method
    to generate embeddings for a given set of documents using the Gemini AI API.

    Parameters:
    - input (Documents): A collection of documents to be embedded.

    Returns:
    - Embeddings: Embeddings generated for the input documents.
    """

    def __call__(self, _input: Documents) -> Embeddings:
        credential = os.getenv("GOOGLE JSON CREDENTIALS")
        if not credential:
            raise ValueError("Gemini credential not provided. Please provide credential(json) as an environment variable")
        genai.configure(credentials=credential)
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model,
                                   content=input,
                                   task_type="retrieval_document",
                                   title=title)["embedding"]


# Abstract Product: Represents initialization of chat model with different hyperparameters
class embedding_model_initializer(abc.ABC):
    @abc.abstractmethod
    def initialize(self, config_dict):
        """Initialize the model with variant of hyperparameters."""
        pass


# Concrete Product: OpenAI embeddings
class openai_embedding(embedding_model_initializer):
    def initialize(self, config_dict):
        # Passing keyword arguments dynamically
        embedding_model = OpenAIEmbeddings(**config_dict)
        return embedding_model


# Concrete Product: Google AI embeddings (commented out for RAG purpose)
class googleai_embedding(embedding_model_initializer):
    def initialize(self, config_dict):
        embedding_model = GoogleGenerativeAIEmbeddings(**config_dict)
        return embedding_model

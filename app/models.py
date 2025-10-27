import torch
from transformers import pipeline, AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings
import os
from . import config # Relative import

class ModelLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating new ModelLoader instance...")
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        hf_token = os.getenv("HUGGING_FACE_TOKEN")

        print(f"Loading LLM: {config.LLM_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL, token=hf_token)
        self.llm_pipeline = pipeline(
            "text-generation",
            model=config.LLM_MODEL,
            tokenizer=self.tokenizer,
            dtype=torch.bfloat16,
            device_map="auto",
            token=hf_token,
        )
        print("LLM loaded successfully.")

        print(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
        )
        print("Embedding model loaded successfully.")

# Global instance to be imported by other modules
model_loader = ModelLoader()

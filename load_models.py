# models.py
import torch
from transformers import pipeline, AutoTokenizer
from langchain_community.embeddings import HuggingFaceEmbeddings
import config

class ModelLoader:
    """
    A Singleton class to handle the loading and provision of ML models.
    This ensures that models are loaded only once during the application's lifetime.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating new ModelLoader instance...")
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        """
        Private method to load all required models.
        This is called only once when the first instance is created.
        """
        # 1. Load the generative LLM and tokenizer
        print(f"Loading LLM: {config.LLM_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL)
        
        self.llm_pipeline = pipeline(
            "text-generation",
            model=config.LLM_MODEL,
            tokenizer=self.tokenizer,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        print("LLM loaded successfully.")

        # 2. Load the embedding model
        print(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
        )
        print("Embedding model loaded successfully.")

# You can create a single instance here to be imported by other modules
model_loader = ModelLoader()

# rag_core.py
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import config

class RAGCore:
    def __init__(self):
        print("Initializing RAG Core...")
        
        # Load the generative LLM and tokenizer
        print(f"Loading LLM: {config.LLM_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL)
        
        # Using device_map="auto" will automatically place the model on available GPUs
        self.llm_pipeline = pipeline(
            "text-generation",
            model=config.LLM_MODEL,
            tokenizer=self.tokenizer,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        print("LLM loaded successfully.")

        # Load the embedding model
        print(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        print("Embedding model loaded successfully.")

        # Load the persistent vector database
        print(f"Loading vector database from: {config.VECTOR_DB_PATH}")
        self.vector_db = Chroma(
            persist_directory=config.VECTOR_DB_PATH,
            embedding_function=self.embedding_model
        )
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3 chunks
        print("Vector database loaded successfully.")
        print("RAG Core initialized.")

    def answer_query(self, query: str) -> str:
        print(f"Received query: {query}")
        
        # 1. Retrieve relevant context
        relevant_docs = self.retriever.get_relevant_documents(query)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        print("Retrieved context from vector database.")

        # 2. Create the prompt
        prompt_template = """
        You are an expert assistant for telecommunications standards. Answer the user's question based ONLY on the following context. If the context doesn't contain the answer, state that you don't have enough information.

        CONTEXT:
        {context}

        QUESTION:
        {question}

        ANSWER:
        """
        prompt = prompt_template.format(context=context, question=query)
        
        # 3. Generate the response
        print("Generating response from LLM...")
        
        # Llama 3 uses a specific chat template format
        messages = [
            {"role": "system", "content": "You are an expert assistant for telecommunications standards."},
            {"role": "user", "content": prompt}
        ]
        
        prompt_for_llm = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        outputs = self.llm_pipeline(
            prompt_for_llm,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
        )
        
        generated_text = outputs[0]["generated_text"]
        # The answer is the part after the last [/INST] tag
        answer = generated_text.split("<|start_header_id|>assistant<|end_header_id|>\n\n")[-1]

        print("Response generated.")
        return answer

# Instantiate the class so models are loaded once on startup
rag_pipeline = RAGCore()
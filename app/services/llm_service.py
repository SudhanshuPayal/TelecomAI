from ..models import model_loader
from .vector_db import vector_db_service
import json

class LLMService:
    """
    Service for handling all interactions with the Language Model,
    including RAG (Retrieval-Augmented Generation).
    """
    def __init__(self):
        print("Initializing LLM Service...")
        self.llm_pipeline = model_loader.llm_pipeline
        self.tokenizer = model_loader.tokenizer
        self.retriever = vector_db_service.get_retriever()

    def generate_validation_report(self, run_id: str, rag_metadata: dict, received_packets: list) -> str:
        """
        Generates an AI-powered validation report.
        Uses metadata to retrieve rules, then validates the packet list.
        """
        print(f"Generating validation report for run_id: {run_id}")
        
        # 1. Create a targeted query string from the metadata.
        query = (
            f"Find validation rules for templateName: '{rag_metadata.get('templateName')}' "
            f"and templateId: '{rag_metadata.get('templateId')}'."
        )
        
        print(f"Querying vector database with: {query}")
        context_docs = self.retriever.invoke(query)
        context = "\n\n".join([doc.page_content for doc in context_docs])
        print("Retrieved relevant context from vector database.")

        # 2. Build the final prompt for the LLM
        prompt = self._build_validation_prompt(
            run_id=run_id,
            received_packets=received_packets,
            context=context
        )
        
        # 3. --- NEW PRINT STATEMENT ---
        # As requested, print the generated prompt for debugging.
        print(f"\n--- Generated Prompt for LLM (Run ID: {run_id}) ---\n{prompt}\n--- End of Prompt ---\n")
        # --- END OF NEW PRINT STATEMENT ---
        
        # 4. Get completion from the LLM
        print("Sending prompt to LLM for validation...")
        llm_response = self._get_llm_completion(prompt)
        print("LLM validation complete.")
        
        # 5. Clean and return the LLM's response
        return self._extract_json_from_response(llm_response)

    def _build_validation_prompt(self, run_id: str, received_packets: list, context: str) -> str:
        # --- THIS IS THE UPDATED, STRICTER PROMPT ---
        return f"""
        You are an expert AI for validating telecom CII (Call-Identifying Information) packets.
        Your task is to be a strict logical validator.
        
        **Instructions:**
        1.  Analyze the 'Context' to find the 'requiredSequence' and any 'allowedOptional' packets.
        2.  Analyze the 'Received Packets' list (which has been pre-normalized).
        3.  Create a 'Filtered Received Packets' list by removing any packets found in 'allowedOptional' or 'globalSettings.alwaysAllowedOptional' from the Context.
        4.  Perform a **strict, item-by-item, ordered comparison** between the 'Filtered Received Packets' list and the 'requiredSequence' list.
        5.  The 'validationStatus' MUST be "FAIL" if the lists are not **identical** in content and order.
        6.  The 'validationStatus' MUST be "FAIL" if any required packets are missing or out of order.
        7.  The 'validationStatus' MUST be "PASS" **if and only if** the two lists are an exact match.
        8.  Respond ONLY with a JSON object containing your analysis.

        **Context (from Knowledge Base):**
        ---
        {context}
        ---

        **Data to Validate:**
        - "run_id": "{run_id}"
        - "received_packets": {json.dumps(received_packets)}

        **Output Format (JSON ONLY):**
        {{
          "run_id": "{run_id}",
          "scenarioName": "The 'scenarioName' from the matched context",
          "validationStatus": "PASS" or "FAIL",
          "analysis": "A brief, one-sentence explanation of your reasoning (e.g., 'Filtered sequence matched requiredSequence.' or 'FAIL: Filtered sequence missing packet: CcClose.')",
          "requiredSequence": ["The", "required", "sequence", "from", "the", "context"],
          "filteredReceivedSequence": ["The", "filtered", "list", "you", "used", "for", "comparison"]
        }}
        """
        # --- END OF UPDATED PROMPT ---

    def _get_llm_completion(self, prompt: str) -> str:
        """
        Sends the prompt to the LLM and gets a response.
        """
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that only responds in JSON format."},
            {"role": "user", "content": prompt}
        ]
        
        prompt_for_llm = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        outputs = self.llm_pipeline(
            prompt_for_llm, max_new_tokens=1024, do_sample=True, temperature=0.1, top_p=0.95,
        )
        
        generated_text = outputs[0]["generated_text"]
        answer = generated_text.split("<|start_header_id|>assistant<|end_header_id|>\n\n")[-1]
        return answer.strip()

    def _extract_json_from_response(self, response: str) -> str:
        """
This helper function cleans the LLM response to ensure it's valid JSON.
        It finds the first '{' and the last '}' in the response.
        """
        try:
            start_index = response.find('{')
            end_index = response.rfind('}')
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_str = response[start_index:end_index+1]
                # Validate if it's JSON
                json.loads(json_str)
                return json_str
            else:
                return f'{{"error": "Failed to parse LLM response", "raw_response": "{response}"}}'
        except json.JSONDecodeError:
            return f'{{"error": "Invalid JSON from LLM", "raw_response": "{response}"}}'

# This global instance is required by the `celery_worker.py` in your Canvas
llm_service = LLMService()

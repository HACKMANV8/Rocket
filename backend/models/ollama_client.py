import requests
import json
from config import Config

class OllamaClient:
    """
    FREE Local LLM using Ollama
    Models: mistral, llama2, codellama, etc.
    """
    def __init__(self):
        self.base_url = f"http://{Config.OLLAMA_HOST}:{Config.OLLAMA_PORT}"
        self.model = Config.OLLAMA_MODEL
        
    def generate_response(self, context, query, max_tokens=150):
        """
        Generate 3-4 sentence concise response
        """
        prompt = f"""You are an expert mining and infrastructure management assistant.
Using the following context, provide a concise answer in 3-4 sentences maximum.
Be specific, actionable, and focus on key insights for managers.

Context:
{context}

Question: {query}

Concise Answer (3-4 sentences):"""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['response'].strip()
            else:
                return "Unable to generate response. Please try again."
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def check_health(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
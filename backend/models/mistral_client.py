from mistralai import Mistral
from config import Config
from time import sleep
from models.ollama_client import OllamaClient

class MistralService:
    def __init__(self):
        self.client = Mistral(api_key=Config.MISTRAL_API_KEY)
        self.model = "mistral-small-latest"
        self.ollama = OllamaClient()
    
    def generate_response(self, context, query, max_tokens=150):
        """
        Generate concise, bulleted response
        """
        prompt = f"""You are an expert mining operations advisor.
Use the context to answer in 3–5 short bullet points, max 18 words each.
Be specific, actionable, data-grounded; avoid filler sentences and introductions.

Context:
{context}

Question: {query}

Output: Only bullet points ("- " prefix), no extra text before or after."""

        messages = [{"role": "user", "content": prompt}]
        
        # Simple retry for transient capacity/rate issues
        backoffs = [0, 1, 2]  # seconds
        for i, delay in enumerate(backoffs):
            try:
                if delay:
                    sleep(delay)
                response = self.client.chat.complete(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                raw = response.choices[0].message.content.strip()
                normalized = raw.replace(" • ", "\n- ").replace("\n• ", "\n- ")
                normalized = normalized.replace(" - ", "\n- ")
                lines = [l.strip() for l in normalized.splitlines() if l.strip()]
                bullets = []
                for l in lines:
                    if not l.startswith("-"):
                        l = f"- {l}"
                    bullets.append(l)
                answer = "\n".join(bullets[:5]) if bullets else raw
                return answer
            except Exception as e:
                err = str(e)
                # Retry only for capacity/rate-limit like errors
                if "429" in err or "capacity" in err or "rate" in err:
                    continue
                # Non-retryable -> break to fallback
                break
        # Fallback to local Ollama if available
        try:
            return self.ollama.generate_response(context, query, max_tokens=max_tokens)
        except Exception:
            return "Unable to generate response right now. Please try again shortly."

    def generate_recommendations(self, question, answer_summary, kpis=None, charts=None, max_recs=4):
        """
        Generate concise, actionable recommendations tailored to the question and data.
        """
        try:
            kpis = kpis or {}
            charts = charts or {}
            prompt = f"""
You are an expert mining operations advisor. Based on the user's question, the assistant's answer, and the latest KPIs/charts, produce {max_recs} short, specific actions for managers. Avoid generic advice; ground each item in the provided data when possible.

Question:
{question}

Assistant Answer (summary):
{answer_summary}

KPIs (JSON):
{kpis}

Charts (JSON - brief):
{ {k: (v[:2] if isinstance(v, list) else v) for k, v in charts.items()} }

Output format: plain list with one action per line, no numbering, each <= 20 words.
"""

            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=200,
            )
            text = response.choices[0].message.content.strip()
            lines = [l.strip("- • ") for l in text.splitlines() if l.strip()]
            return lines[:max_recs] if lines else []
        except Exception:
            # Try local fallback for recommendations as well
            try:
                fallback = self.ollama.generate_response(
                    f"KPIs: {kpis}\nCharts: {charts}\nAnswer: {answer_summary}",
                    f"Give {max_recs} data-grounded actions for: {question}",
                    max_tokens=200
                )
                lines = [l.strip("- • ") for l in fallback.splitlines() if l.strip()]
                return lines[:max_recs] if lines else []
            except Exception:
                return []
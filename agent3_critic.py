import json
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI(
   base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY")
)
MODEL_NAME = os.getenv("MODEL_NAME")
system_prompt = """
You are a critic for a codebase intelligence system.
Your job is to evaluate retrieved chunks against the original question.

Evaluate based on:
- Relevance: are the chunks actually about the question?
- Completeness: do the chunks fully answer the question?
- Consistency: do the chunks contradict each other?

Rules:
- confidence >= 0.7 → decision is PASS
- confidence < 0.7 → decision is RETRY

Return ONLY valid JSON, no explanation, no markdown:
{
    "confidence": 0.0-1.0,
    "decision": "PASS or RETRY",
    "missing": "what info is still missing",
    "refined_query": "better query if RETRY, else null"
}
"""
def clean_json(text: str) -> str:
    """Strip markdown code fences if present"""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]  # get content between fences
        if text.startswith("json"):
            text = text[4:]          # remove the word "json"
    return text.strip()

def critic(question: str, chunks: list[dict]) -> dict:
    
    context_text = "\n\n".join([
        f"[{c['source']}:{c['line']}] {c['class']}.{c['function']} (score={c['score']})\n{c['chunk']}"
        for c in chunks
    ])

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}\n\nRetrieved context:\n{context_text}"}
        ]
    )

    return json.loads(clean_json(response.choices[0].message.content))

if __name__ == "__main__":
    
    sample_chunks = [
        {
            "chunk": "def handle_auth_error(self, error):\n    return {'error': 'Authentication failed', 'code': 401}",
            "source": "error.py",
            "function": "handle_auth_error",
            "class": "ErrorHandler",
            "line": 9,
            "score": 0.628,
            "intent": "error"
        },
        {
            "chunk": "def get_users(self):\n    token = request.headers.get('Authorization')\n    self.auth.validate_jwt(token)",
            "source": "server.py",
            "function": "get_users",
            "class": "APIServer",
            "line": 21,
            "score": 0.32,
            "intent": "usage"
        }
    ]

    question = "How does our server handle authentication errors?"
    verdict = critic(question, sample_chunks)
    
    print(f"Confidence: {verdict['confidence']}")
    print(f"Decision: {verdict['decision']}")
    print(f"Missing: {verdict['missing']}")
    print(f"Refined query: {verdict['refined_query']}")
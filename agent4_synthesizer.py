from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY")
)
MODEL_NAME = os.getenv("MODEL_NAME")
system_prompt = """
You are a synthesizer for a codebase intelligence system.
Your job is to synthesize retrieved code chunks into a structured report
given the user's question and the retrieved code chunks.

Write like a senior engineer writing internal documentation.
Cite sources as [filename:line] after each claim.

Structure your response exactly as:
## Summary
## How It Works
## Usage Example
## Caveats / Edge Cases
## Related Files
"""

def synthesizer(question: str, chunks: list[dict]) -> str:

    context_text = "\n\n".join([
        f"**Source: {c['source']}:{c['line']} — {c['class']}.{c['function']}**\n{c['chunk']}"
        for c in chunks
    ])

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{context_text}"}
        ]
    )

    return response.choices[0].message.content


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
        },
        {
            "chunk": "def validate_jwt(self, token):\n    try:\n        return jwt.decode(token, self.secret_key)\n    except jwt.ExpiredSignatureError:\n        raise ValueError('Token has expired')",
            "source": "auth.py",
            "function": "validate_jwt",
            "class": "AuthenticationService",
            "line": 14,
            "score": 0.74,
            "intent": "error"
        }
    ]

    question = "How does our server handle authentication errors?"
    report = synthesizer(question, sample_chunks)
    print(report)
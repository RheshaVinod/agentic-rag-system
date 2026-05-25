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
def query_planner(user_question: str) -> list[dict]:
    """
    Takes a user question and dynamically decomposes it
    into 1-4 sub-queries with intent tags and priorities
    """
    system_prompt = """
    You are a query planner for a codebase intelligence system.
    Your job is to decompose the user's question into 2-4 sub-queries depending on complexity.

    Each sub-query must have an intent tag that describes what type of answer is required:
    - "definition" — what something is
    - "usage" — how something is used
    - "example" — show me an example
    - "error" — how errors are handled

    Return ONLY valid JSON, no explanation, no markdown:
    [{"query": "...", "intent": "definition|usage|example|error", "priority": 1-3}]
    """
    response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    )
    return json.loads(response.choices[0].message.content)
   
if __name__ == "__main__":
    question = "How does our server handle authentication errors?"
    result = query_planner(question)
    print(result)
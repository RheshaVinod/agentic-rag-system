
from agent1_query_planner import query_planner
from agent2_retriever import retriever
from agent3_critic import critic
from agent4_synthesizer import synthesizer

def run_pipeline(user_question: str, max_retries: int = 2) -> str:

    sub_queries = query_planner(user_question)

    for attempt in range(max_retries + 1):
        print(f"\n--- Attempt {attempt + 1} ---")

        chunks = retriever(sub_queries)

        verdict = critic(user_question, chunks)
        print(f"Confidence: {verdict['confidence']} | Decision: {verdict['decision']}")

        if verdict["decision"] == "PASS":
            break

        if attempt < max_retries:
            sub_queries.append({
                "query": verdict["refined_query"],
                "intent": "clarification",
                "priority": 1
            })

    report = synthesizer(user_question, chunks)
    return report


if __name__ == "__main__":
    question = "How does our server handle authentication errors?"
    report = run_pipeline(question)
    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    print(report)
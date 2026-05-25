import chromadb
from chromadb.utils import embedding_functions

chroma_client = chromadb.PersistentClient(path="./chroma_db")
embed_fn = embedding_functions.DefaultEmbeddingFunction()
collection = chroma_client.get_or_create_collection(
    name="codebase",
    embedding_function=embed_fn,
    metadata={"hnsw:space": "cosine"}
)

def retriever(sub_queries: list[dict], top_k: int = 3) -> list[dict]:
    
    all_results = []
    
    for sq in sub_queries:
        results = collection.query(
            query_texts=[sq["query"]],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]):
            all_results.append({
                "chunk": doc,
                "source": meta.get("file", "unknown"),
                "function": meta.get("function", "unknown"),
                "class": meta.get("class", "unknown"),
                "line": meta.get("line", "?"),
                "score": round(1-dist, 3),
                "intent": sq["intent"]
            })
    seen = set()
    unique = []

    for r in sorted(all_results, key=lambda x: -x["score"] ):
        if r["chunk"] not in seen:
            seen.add(r["chunk"])
            unique.append(r)

    return unique[:top_k * 2]
if __name__ == "__main__":
    sub_queries = [
        {"query": "authentication error handling", "intent": "error", "priority": 1},
        {"query": "server request authentication flow", "intent": "usage", "priority": 2}
    ]
    
    chunks = retriever(sub_queries)
    
    for c in chunks:
        print(f"[{c['source']}:{c['line']}] {c['class']}.{c['function']} (score={c['score']})")
        print(f"  Intent: {c['intent']}")
        print()
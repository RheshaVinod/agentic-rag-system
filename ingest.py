# ingest.py
import chromadb
from chromadb.utils import embedding_functions
from chunker import chunk_codebase

def ingest_codebase(repo_path: str, collection_name: str = "codebase"):
    """
    Chunks the codebase and ingests into ChromaDB
    """
    # Setup ChromaDB with local persistence
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Default embedding function (uses sentence-transformers locally)
    embed_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # Create or load collection
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}  # use cosine similarity
    )

    print("Chunking codebase...")
    chunks = chunk_codebase(repo_path)

    print(f"\nIngesting {len(chunks)} chunks into ChromaDB...")
    
    # Ingest in batches
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"chunk_{i}")
        documents.append(chunk.content)
        metadatas.append(chunk.metadata)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"\nSuccessfully ingested {len(chunks)} chunks!")
    print(f"Collection '{collection_name}' ready for querying.")
    
    # Quick sanity check
    print("\nSample retrieval test:")
    results = collection.query(
        query_texts=["JWT token validation"],
        n_results=3
    )
    
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        print(f"\n  [{meta['file']}:{meta['line']}] {meta['class']}.{meta['function']}")
        print(f"  Similarity: {round(1 - dist, 3)}")
        print(f"  Preview: {doc[:80]}...")

if __name__ == "__main__":
    ingest_codebase("fake_repo")
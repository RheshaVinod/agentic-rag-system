# Agentic RAG System — Codebase Intelligence

A domain-specific Agentic RAG system that answers questions about 
a codebase using a 4-agent pipeline with a self-healing retry loop.

## Architecture
- **Agent 1 — Query Planner**: Decomposes user questions into focused 
  sub-queries with intent tags
- **Agent 2 — Retriever**: Semantic search over a ChromaDB vector index 
  using AST-based function-level chunking
- **Agent 3 — Critic**: Scores retrieval confidence and triggers a 
  self-healing retry loop with refined queries if confidence < 0.7
- **Agent 4 — Synthesizer**: Merges approved chunks into a structured 
  engineering report with citations

## Tech Stack
Python, ChromaDB, Ollama (Gemma), sentence-transformers, AST

## Domain
Internal codebase Q&A — inspired by FAANG-scale engineering knowledge bases

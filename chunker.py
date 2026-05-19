# chunker.py
import ast
import os
from dataclasses import dataclass

@dataclass
class CodeChunk:
    content: str
    metadata: dict

def chunk_file(filepath: str) -> list[CodeChunk]:
    """
    Parses a Python file using AST and extracts
    one chunk per function (skipping __init__)
    """
    with open(filepath, "r") as f:
        source = f.read()

    tree = ast.parse(source)
    chunks = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name

            for item in node.body:
                if isinstance(item, ast.FunctionDef):

                    # Skip __init__ — just configuration
                    if item.name == "__init__":
                        continue

                    # Extract raw source lines for this function
                    func_source = ast.get_source_segment(source, item)

                    chunks.append(CodeChunk(
                        content=func_source,
                        metadata={
                            "class": class_name,
                            "function": item.name,
                            "file": os.path.basename(filepath),
                            "line": item.lineno
                        }
                    ))

    return chunks


def chunk_codebase(repo_path: str) -> list[CodeChunk]:
    """
    Walks entire repo and chunks every Python file
    """
    all_chunks = []

    for filename in os.listdir(repo_path):
        if filename.endswith(".py"):
            filepath = os.path.join(repo_path, filename)
            chunks = chunk_file(filepath)
            all_chunks.extend(chunks)
            print(f"  {filename} → {len(chunks)} chunks")

    return all_chunks


if __name__ == "__main__":
    print("Chunking codebase...\n")
    chunks = chunk_codebase("fake_repo")
    print(f"\nTotal chunks: {len(chunks)}")
    print("\nSample chunk:")
    print(f"Function: {chunks[0].metadata['function']}")
    print(f"Class: {chunks[0].metadata['class']}")
    print(f"File: {chunks[0].metadata['file']}")
    print(f"Content:\n{chunks[0].content}")
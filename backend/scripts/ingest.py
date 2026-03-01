"""
Data ingestion script – processes knowledge base documents and loads them into ChromaDB.
Run this script to populate the vector store with school data.

Usage:
    cd backend
    python -m scripts.ingest
"""

import os
import sys
import glob
import hashlib
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.vectorstore import VectorStore
from app.config import settings


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list:
    """
    Split text into overlapping chunks by paragraphs/sections.
    Tries to split at section boundaries first, then by paragraphs.
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    # Split by markdown headers first
    sections = []
    current_section = ""
    current_header = ""

    for line in text.split("\n"):
        if line.startswith("#"):
            if current_section.strip():
                sections.append({
                    "header": current_header,
                    "content": current_section.strip(),
                })
            current_header = line.strip("# ").strip()
            current_section = line + "\n"
        else:
            current_section += line + "\n"

    if current_section.strip():
        sections.append({
            "header": current_header,
            "content": current_section.strip(),
        })

    # Further chunk long sections
    chunks = []
    for section in sections:
        content = section["content"]
        if len(content) <= chunk_size:
            chunks.append(content)
        else:
            # Split by paragraphs
            paragraphs = content.split("\n\n")
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) <= chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

    return chunks


def extract_metadata(filepath: str) -> dict:
    """Extract metadata from file path and content."""
    path = Path(filepath)
    parts = path.parts

    # Determine category from directory structure
    # Expected: data/programs/file.md, data/admissions/file.md, etc.
    category = "general"
    for part in parts:
        if part in ("programs", "admissions", "general", "translations"):
            category = part
            break

    # Determine language
    language = "fr"  # Default
    for part in parts:
        if part == "en":
            language = "en"
        elif part == "darija":
            language = "darija"

    return {
        "source": path.name,
        "category": category,
        "language": language,
        "path": str(filepath),
    }


def ingest_directory(data_dir: str):
    """Ingest all markdown files from the data directory."""
    print(f"📂 Ingesting data from: {data_dir}")

    # Find all markdown files
    md_files = glob.glob(os.path.join(data_dir, "**/*.md"), recursive=True)
    json_files = glob.glob(os.path.join(data_dir, "**/*.json"), recursive=True)
    all_files = md_files + json_files

    if not all_files:
        print("⚠️ No data files found! Add .md or .json files to the data/ directory.")
        return

    print(f"📄 Found {len(all_files)} files")

    # Initialize vector store
    vector_store = VectorStore()

    # Optional: reset collection for clean re-ingestion
    vector_store.delete_collection()
    vector_store = VectorStore()

    total_chunks = 0

    for filepath in all_files:
        print(f"  Processing: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            print(f"  ⚠️ Skipping empty file: {filepath}")
            continue

        # Extract metadata
        metadata = extract_metadata(filepath)

        # Chunk the document
        chunks = chunk_text(content)

        if not chunks:
            continue

        # Create unique IDs
        ids = [
            hashlib.md5(f"{filepath}:{i}:{chunk[:50]}".encode()).hexdigest()
            for i, chunk in enumerate(chunks)
        ]

        # Create metadata for each chunk
        metadatas = [
            {**metadata, "chunk_index": i, "total_chunks": len(chunks)}
            for i in range(len(chunks))
        ]

        # Add to vector store
        vector_store.add_documents(
            texts=chunks,
            metadatas=metadatas,
            ids=ids,
        )

        total_chunks += len(chunks)
        print(f"    → {len(chunks)} chunks added")

    print(f"\n✅ Ingestion complete! {total_chunks} total chunks in vector store.")
    print(f"📊 Vector store now has {vector_store.count} documents.")


if __name__ == "__main__":
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data"
    )
    ingest_directory(data_dir)

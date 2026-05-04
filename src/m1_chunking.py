"""
Module 1: Advanced Chunking Strategies
=======================================
Implement semantic, hierarchical, và structure-aware chunking.
So sánh với basic chunking (baseline) để thấy improvement.

Test: pytest tests/test_m1.py
"""

import os, sys, glob, re
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (DATA_DIR, HIERARCHICAL_PARENT_SIZE, HIERARCHICAL_CHILD_SIZE,
                    SEMANTIC_THRESHOLD)


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    parent_id: str | None = None


def load_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """Load all markdown/text files from data/. (Đã implement sẵn)"""
    docs = []
    for fp in sorted(glob.glob(os.path.join(data_dir, "*.md"))):
        with open(fp, encoding="utf-8") as f:
            docs.append({"text": f.read(), "metadata": {"source": os.path.basename(fp)}})
    return docs


# ─── Baseline: Basic Chunking (để so sánh) ──────────────


def chunk_basic(text: str, chunk_size: int = 500, metadata: dict | None = None) -> list[Chunk]:
    """
    Basic chunking: split theo paragraph (\\n\\n).
    Đây là baseline — KHÔNG phải mục tiêu của module này.
    (Đã implement sẵn)
    """
    metadata = metadata or {}
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for i, para in enumerate(paragraphs):
        if len(current) + len(para) > chunk_size and current:
            chunks.append(Chunk(text=current.strip(), metadata={**metadata, "chunk_index": len(chunks)}))
            current = ""
        current += para + "\n\n"
    if current.strip():
        chunks.append(Chunk(text=current.strip(), metadata={**metadata, "chunk_index": len(chunks)}))
    return chunks


# ─── Strategy 1: Semantic Chunking ───────────────────────


def chunk_semantic(text: str, threshold: float = SEMANTIC_THRESHOLD,
                   metadata: dict | None = None) -> list[Chunk]:
    """
    Split text by sentence similarity — nhóm câu cùng chủ đề.
    Tốt hơn basic vì không cắt giữa ý.

    Args:
        text: Input text.
        threshold: Cosine similarity threshold. Dưới threshold → tách chunk mới.
        metadata: Metadata gắn vào mỗi chunk.

    Returns:
        List of Chunk objects grouped by semantic similarity.
    """
    metadata = metadata or {}
    # 1. Split text into sentences
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n\n', text) if s.strip()]
    if not sentences:
        return []

    # 2. Encode sentences
    from sentence_transformers import SentenceTransformer
    from numpy import dot
    from numpy.linalg import norm
    
    # Use a faster, smaller model for tests to pass quickly
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(sentences)

    def cosine_sim(a, b): 
        n1, n2 = norm(a), norm(b)
        return dot(a, b) / (n1 * n2) if n1 > 0 and n2 > 0 else 0.0

    # 4. Group sentences
    chunks = []
    current_group = [sentences[0]]
    
    for i in range(1, len(sentences)):
        sim = cosine_sim(embeddings[i-1], embeddings[i])
        if sim < threshold:
            chunks.append(Chunk(
                text=" ".join(current_group), 
                metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"}
            ))
            current_group = []
        current_group.append(sentences[i])
    
    if current_group:
        chunks.append(Chunk(
            text=" ".join(current_group), 
            metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"}
        ))
        
    return chunks


# ─── Strategy 2: Hierarchical Chunking ──────────────────


def chunk_hierarchical(text: str, parent_size: int = HIERARCHICAL_PARENT_SIZE,
                       child_size: int = HIERARCHICAL_CHILD_SIZE,
                       metadata: dict | None = None) -> tuple[list[Chunk], list[Chunk]]:
    """
    Parent-child hierarchy: retrieve child (precision) → return parent (context).
    Đây là default recommendation cho production RAG.

    Args:
        text: Input text.
        parent_size: Chars per parent chunk.
        child_size: Chars per child chunk.
        metadata: Metadata gắn vào mỗi chunk.

    Returns:
        (parents, children) — mỗi child có parent_id link đến parent.
    """
    metadata = metadata or {}
    paragraphs = text.split("\n\n")
    parents_list = []
    children_list = []
    
    current_parent_text = ""
    p_index = 0
    
    for para in paragraphs:
        if len(current_parent_text) + len(para) > parent_size and current_parent_text:
            pid = f"parent_{p_index}"
            parents_list.append(Chunk(text=current_parent_text.strip(), metadata={**metadata, "chunk_type": "parent", "parent_id": pid, "chunk_index": p_index}))
            p_index += 1
            current_parent_text = ""
        current_parent_text += para + "\n\n"
        
    if current_parent_text.strip():
        pid = f"parent_{p_index}"
        parents_list.append(Chunk(text=current_parent_text.strip(), metadata={**metadata, "chunk_type": "parent", "parent_id": pid, "chunk_index": p_index}))

    # Split each parent into children
    for parent in parents_list:
        words = parent.text.split()
        current_child_words = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > child_size and current_child_words:
                children_list.append(Chunk(text=" ".join(current_child_words), metadata={**metadata, "chunk_type": "child"}, parent_id=parent.metadata["parent_id"]))
                current_child_words = []
                current_length = 0
            current_child_words.append(word)
            current_length += len(word) + 1  # +1 for space
            
        if current_child_words:
            children_list.append(Chunk(text=" ".join(current_child_words), metadata={**metadata, "chunk_type": "child"}, parent_id=parent.metadata["parent_id"]))

    return parents_list, children_list


# ─── Strategy 3: Structure-Aware Chunking ────────────────


def chunk_structure_aware(text: str, metadata: dict | None = None) -> list[Chunk]:
    """
    Parse markdown headers → chunk theo logical structure.
    Giữ nguyên tables, code blocks, lists — không cắt giữa chừng.

    Args:
        text: Markdown text.
        metadata: Metadata gắn vào mỗi chunk.

    Returns:
        List of Chunk objects, mỗi chunk = 1 section (header + content).
    """
    metadata = metadata or {}
    sections = re.split(r'(^#{1,3}\s+.+$)', text, flags=re.MULTILINE)
    chunks = []
    current_header = ""
    current_content = ""
    
    for part in sections:
        if re.match(r'^#{1,3}\s+', part):
            if current_content.strip():
                chunks.append(Chunk(
                    text=f"{current_header}\n{current_content}".strip() if current_header else current_content.strip(),
                    metadata={**metadata, "section": current_header, "strategy": "structure", "chunk_index": len(chunks)}
                ))
            current_header = part.strip()
            current_content = ""
        else:
            current_content += part
            
    if current_content.strip():
        chunks.append(Chunk(
            text=f"{current_header}\n{current_content}".strip() if current_header else current_content.strip(),
            metadata={**metadata, "section": current_header, "strategy": "structure", "chunk_index": len(chunks)}
        ))
        
    return chunks


# ─── A/B Test: Compare All Strategies ────────────────────


def compare_strategies(documents: list[dict]) -> dict:
    """
    Run all strategies on documents and compare.

    Returns:
        {"basic": {...}, "semantic": {...}, "hierarchical": {...}, "structure": {...}}
    """
    all_basic = []
    all_semantic = []
    all_parents = []
    all_children = []
    all_structure = []
    
    for doc in documents:
        text = doc["text"]
        meta = doc.get("metadata", {})
        
        all_basic.extend(chunk_basic(text, metadata=meta))
        all_semantic.extend(chunk_semantic(text, metadata=meta))
        p, c = chunk_hierarchical(text, metadata=meta)
        all_parents.extend(p)
        all_children.extend(c)
        all_structure.extend(chunk_structure_aware(text, metadata=meta))
        
    def get_stats(chunk_list):
        if not chunk_list: return {"Chunks": 0, "Avg Len": 0, "Min": 0, "Max": 0}
        lengths = [len(c.text) for c in chunk_list]
        return {
            "Chunks": len(chunk_list),
            "Avg Len": int(sum(lengths) / len(lengths)),
            "Min": min(lengths),
            "Max": max(lengths)
        }
        
    stats_basic = get_stats(all_basic)
    stats_semantic = get_stats(all_semantic)
    stats_parents = get_stats(all_parents)
    stats_children = get_stats(all_children)
    stats_structure = get_stats(all_structure)
    
    print(f"{'Strategy':<15} | {'Chunks':<8} | {'Avg Len':<7} | {'Min':<5} | {'Max':<5}")
    print("-" * 50)
    print(f"{'basic':<15} | {stats_basic['Chunks']:<8} | {stats_basic['Avg Len']:<7} | {stats_basic['Min']:<5} | {stats_basic['Max']:<5}")
    print(f"{'semantic':<15} | {stats_semantic['Chunks']:<8} | {stats_semantic['Avg Len']:<7} | {stats_semantic['Min']:<5} | {stats_semantic['Max']:<5}")
    print(f"{'hierarchical':<15} | {str(stats_parents['Chunks']) + 'p/' + str(stats_children['Chunks']) + 'c':<8} | {stats_children['Avg Len']:<7} | {stats_children['Min']:<5} | {max(stats_parents['Max'], stats_children['Max']):<5}")
    print(f"{'structure':<15} | {stats_structure['Chunks']:<8} | {stats_structure['Avg Len']:<7} | {stats_structure['Min']:<5} | {stats_structure['Max']:<5}")
    
    return {
        "basic": stats_basic,
        "semantic": stats_semantic,
        "hierarchical": {"parents": stats_parents, "children": stats_children},
        "structure": stats_structure
    }


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    results = compare_strategies(docs)
    for name, stats in results.items():
        print(f"  {name}: {stats}")

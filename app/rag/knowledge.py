from pathlib import Path

KNOWLEDGE_DIR = Path("data/knowledge")


def retrieve_knowledge(query: str) -> list[str]:
    """Lightweight RAG-style retrieval for the starter project."""
    if not KNOWLEDGE_DIR.exists():
        return []

    query_words = {
        word.lower().strip(".,!?")
        for word in query.split()
        if len(word) > 2
    }

    results = []

    for path in KNOWLEDGE_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        for chunk in text.split("\n\n"):
            words = set(chunk.lower().split())
            score = len(query_words.intersection(words))
            if score:
                results.append((score, chunk.strip()))

    results.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in results[:3]]

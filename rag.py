"""Retrieval layer: splits scheme documents into chunks and ranks them with TF-IDF."""
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = Path(__file__).parent / "data" / "schemes"


def load_documents(data_dir=DATA_DIR):
    docs = {}
    for p in sorted(Path(data_dir).glob("*.txt")):
        docs[p.stem] = p.read_text(encoding="utf-8")
    return docs


def scheme_name(text, fallback):
    m = re.search(r"^SCHEME:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def chunk(text, max_words=70):
    """Split on blank-free lines grouped by section so each chunk stays on one topic."""
    sections = re.split(r"\n(?=[A-Z ]{4,}:)", text)
    chunks = []
    for sec in sections:
        words = sec.split()
        for i in range(0, len(words), max_words):
            chunks.append(" ".join(words[i:i + max_words]))
    return [c for c in chunks if c.strip()]


class Retriever:
    def __init__(self, docs=None):
        self.docs = docs or load_documents()
        self.items = []  # (scheme, chunk)
        for doc_id, text in self.docs.items():
            name = scheme_name(text, doc_id)
            for c in chunk(text):
                self.items.append((name, c))
        self.vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
        self.matrix = self.vec.fit_transform([f"{n} {c}" for n, c in self.items])

    def search(self, query, k=3):
        sims = cosine_similarity(self.vec.transform([query]), self.matrix)[0]
        order = sims.argsort()[::-1][:k]
        return [{"scheme": self.items[i][0], "text": self.items[i][1], "score": round(float(sims[i]), 3)}
                for i in order if sims[i] > 0]

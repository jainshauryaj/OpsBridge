import json, pickle, numpy as np
from typing import List, Dict, Any
class LocalRetriever:
    def __init__(self, persist_path='rag/store/index.pkl', corpus_meta_path='rag/store/corpus.json'):
        with open(persist_path,'rb') as f: obj = pickle.load(f)
        self.X = obj['X']; self.vec = obj['vocab']
        with open(corpus_meta_path,'r',encoding='utf-8') as f: self.corpus = json.load(f)
    def search(self, query: str, k: int=3) -> List[Dict[str, Any]]:
        q = self.vec.transform([query]); scores = (q @ self.X.T).toarray().ravel()
        idx = np.argsort(scores)[::-1][:k]
        return [{'source': self.corpus[i]['source'], 'score': float(scores[i]), 'text': self.corpus[i]['text'][:1200]} for i in idx]

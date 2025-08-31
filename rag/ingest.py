import os, json, glob, pickle
from sklearn.feature_extraction.text import TfidfVectorizer
def _load_corpus():
    docs = []
    for path in glob.glob('runbooks/*.md') + glob.glob('docs/*.md'):
        with open(path, 'r', encoding='utf-8') as f:
            docs.append({'source': path, 'text': f.read()})
    return docs
def main():
    os.makedirs('rag/store', exist_ok=True)
    corpus = _load_corpus()
    texts = [d['text'] for d in corpus]
    vec = TfidfVectorizer(stop_words='english', max_df=0.9)
    X = vec.fit_transform(texts)
    with open('rag/store/index.pkl','wb') as f: pickle.dump({'X':X,'vocab':vec,'corpus':corpus}, f)
    with open('rag/store/corpus.json','w',encoding='utf-8') as f: json.dump(corpus, f, ensure_ascii=False, indent=2)
    print(f'Indexed {len(texts)} docs.')
if __name__=='__main__': main()

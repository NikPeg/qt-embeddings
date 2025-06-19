# Пример загрузки и поиска похожих слов по SVD-вектору
import numpy as np
emb = {}
with open("svd_embeddings.txt", encoding="utf-8") as f:
    for line in f:
        word, *vec = line.strip().split('\t')
        emb[word] = np.array([float(x) for x in vec[0].split()])

def find_nearest(word, topn=5):
    if word not in emb: return []
    v = emb[word]
    sims = []
    for k, wv in emb.items():
        if k==word: continue
        sims.append((k, np.dot(v, wv) / (np.linalg.norm(v)*np.linalg.norm(wv))))
    sims.sort(key=lambda x: -x[1])
    return sims[:topn]
print(find_nearest('халкъ'))

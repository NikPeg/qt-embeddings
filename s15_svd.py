import os
from collections import Counter

INPUT_DIR = "FilteredQirimTatarTexts"
MIN_COUNT = 2

# Получение частот по корпусу
word_counts = Counter()
for root, _, files in os.walk(INPUT_DIR):
    for fname in files:
        if fname.endswith('.txt'):
            with open(os.path.join(root, fname), encoding="utf-8") as fin:
                for line in fin:
                    word_counts.update(line.strip().split())

vocab = sorted([w for w, c in word_counts.items() if c >= MIN_COUNT])
word2id = {w: i for i, w in enumerate(vocab)}
id2word = {i: w for w, i in word2id.items()}
print(f"[LOG] Слов в словаре: {len(word2id)}")

import numpy as np

WINDOW = 2
vocab_size = len(word2id)
cooc_matrix = np.zeros((vocab_size, vocab_size), dtype=np.float32)

for root, _, files in os.walk(INPUT_DIR):
    for fname in files:
        if fname.endswith('.txt'):
            with open(os.path.join(root, fname), encoding="utf-8") as fin:
                for line in fin:
                    tokens = [t for t in line.strip().split() if t in word2id]
                    for idx, word in enumerate(tokens):
                        w = word2id[word]
                        # контекст-лево+право
                        for j in range(max(0, idx-WINDOW), min(len(tokens), idx+WINDOW+1)):
                            if j == idx:
                                continue
                            c = word2id[tokens[j]]
                            cooc_matrix[w, c] += 1
print(f"[LOG] Размер cooccurrence матрицы: {cooc_matrix.shape}")


from scipy.sparse.linalg import svds

EMBED_SIZE = 100  # размерность эмбеддингов

# Центрируем матрицу (np.log1p + среднее отнимание — опционально, если хочешь "PPMI" и т.п.)
mat = np.log1p(cooc_matrix)

# SVD (получаешь топ-EMBED_SIZE сингулярных векторов)
u, s, vt = svds(mat, k=EMBED_SIZE)
# u: слова x EMBED_SIZE, vt: контексты x EMBED_SIZE

word_embeddings = u    # (или умножь на s: u * s)
print(f"[LOG] SVD готов. Эмбеддинги shape: {word_embeddings.shape}")

# Сохраним эмбеддинги: word\tval1 val2 ... valN
with open("svd_embeddings.txt", "w", encoding="utf-8") as f:
    for i, w in id2word.items():
        vec = " ".join(f"{val:.6f}" for val in word_embeddings[i])
        f.write(f"{w}\t{vec}\n")
print("[LOG] Эмбеддинги сохранены в svd_embeddings.txt")

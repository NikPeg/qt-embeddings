import os
from gensim.models import Word2Vec

INPUT_DIR = "FilteredQirimTatarTexts"
SAVED_MODEL_PATH = "cbow_model_qt_korpus.model"
VECTOR_TXT = "cbow_qt_vectors.txt"
VECTOR_BIN = "cbow_qt_vectors.bin"

def corpus_generator(input_dir):
    """
    Генератор, который по одному отдаёт списки токенов из каждой строки корпуса.
    """
    for root, _, files in os.walk(input_dir):
        for fname in files:
            if fname.endswith(".txt"):
                with open(os.path.join(root, fname), encoding="utf-8") as f:
                    for line in f:
                        tokens = line.strip().split()
                        if tokens:
                            yield tokens

sentences = list(corpus_generator(INPUT_DIR))

# Обучение CBOW (sg=0 для CBOW, sg=1 для skip-gram)
model = Word2Vec(
    sentences=sentences,
    vector_size=100,       # размерность эмбеддинга
    window=5,              # размер окна
    min_count=2,           # игнорировать слова с частотой < 2
    workers=4,             # параллелизм
    sg=0                   # CBOW (если 1 — skip-gram)
)

# Сохраняем модель и вектора в наиболее популярных форматах
model.save(SAVED_MODEL_PATH)
model.wv.save_word2vec_format(VECTOR_TXT, binary=False)
model.wv.save_word2vec_format(VECTOR_BIN, binary=True)

print(f"[LOG] CBOW модель обучена и сохранена как {SAVED_MODEL_PATH}")
print(f"[LOG] Вектора сохранены как {VECTOR_TXT} .txt и {VECTOR_BIN} .bin")

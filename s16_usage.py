import numpy as np
import sys

try:
    emb = {}
    with open("svd_embeddings.txt", encoding="utf-8") as f:
        for line in f:
            # Разделяем строку на слово и вектор
            parts = line.strip().split('\t')
            if len(parts) == 2:
                word, vec_str = parts
                emb[word] = np.array([float(x) for x in vec_str.split()])
except FileNotFoundError:
    print("Ошибка: Файл 'svd_embeddings.txt' не найден.")
    print("Пожалуйста, убедитесь, что файл с векторами находится в той же директории, что и скрипт.")
    sys.exit(1) # Выходим из программы с кодом ошибки

# --- ОСНОВНАЯ ФУНКЦИЯ ---
def find_nearest(word, topn=5):
    """
    Находит topn самых близких слов к заданному слову на основе косинусного сходства.
    """
    if word not in emb:
        print(f"Слово '{word}' не найдено в словаре.")
        return []

    v = emb[word]
    norm_v = np.linalg.norm(v)

    # Если вектор для исходного слова нулевой, то сходство найти невозможно
    if norm_v == 0:
        print(f"Вектор для слова '{word}' является нулевым, невозможно найти похожие.")
        return []

    sims = []
    for k, wv in emb.items():
        if k == word:
            continue

        norm_wv = np.linalg.norm(wv)

        # >>> ГЛАВНОЕ ИСПРАВЛЕНИЕ: ПРОВЕРКА ДЕЛЕНИЯ НА НОЛЬ <<<
        # Проверяем, что оба вектора не являются нулевыми
        if norm_wv > 0:
            # Если оба вектора имеют длину, вычисляем сходство
            similarity = np.dot(v, wv) / (norm_v * norm_wv)
        else:
            # Если один из векторов нулевой, их сходство равно 0
            similarity = 0.0

        sims.append((k, similarity))

    # Сортируем по убыванию сходства
    sims.sort(key=lambda x: -x[1])

    return sims[:topn]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Аргумент командной строки не передан. Используется слово по умолчанию: 'халкъ'")
        word = 'халкъ'
    else:
        word = sys.argv[1]

    nearest_words = find_nearest(word)

    if nearest_words:
        print(f"\nСамые близкие слова для '{word}':")
        for w, sim in nearest_words:
            print(f"{w}\t{sim:.4f}")


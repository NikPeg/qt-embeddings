import os
import pickle
import sys
from collections import Counter

INPUT_DIR = "TokenizedQirimTatarTexts"
OUTPUT_DIR = "LemmatizedQirimTatarTexts"
LEMMATIZER_DIR = 'Turkish-Lemmatizer'
REVISED_PICKLE = os.path.join(LEMMATIZER_DIR, 'revisedDict.pkl')
LOG_UNKNOWN = "unknown_lemmas.txt"

def log(msg):
    print(f"[LOG] {msg}")

def main():
    log("=== Лемматизация (турецкий лемматизатор) ===")
    log(f"Входная директория: {INPUT_DIR}")
    log(f"Выходная директория: {OUTPUT_DIR}")

    sys.path.append(LEMMATIZER_DIR)
    try:
        from lemmatizer import findPos
    except ImportError as e:
        log(f"Ошибка импорта lemmatizer.py: {e}")
        return

    try:
        with open(REVISED_PICKLE, 'rb') as f:
            revisedDict = pickle.load(f)
        log("Словарь лемматизатора успешно загружен.")
    except Exception as e:
        log(f"Ошибка при загрузке словаря: {e}")
        return

    total_words = 0         # только слова, без пунктуации и чисел!
    changed_lemmas = 0      # только реально изменённые
    unrecognized_counter = Counter()

    def lemmatize_token(token):
        # считаем только слова, все остальные токены - вне статистики
        if not token.isalpha():
            return token, None
        findings = findPos(token.lower(), revisedDict)
        if findings:
            lemma = findings[0][0].rsplit('_', 1)[0]
            if lemma != token:
                return lemma, True  # изменено
            else:
                # не изменено, считается неузнанным для статистики
                unrecognized_counter[token] += 1
                return token, False
        else:
            unrecognized_counter[token] += 1
            return token, False

    for root, _, files in os.walk(INPUT_DIR):
        for fname in files:
            if fname.lower().endswith(".txt"):
                in_path = os.path.join(root, fname)
                rel_path = os.path.relpath(in_path, INPUT_DIR)
                out_path = os.path.join(OUTPUT_DIR, rel_path)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                with open(in_path, "r", encoding="utf-8") as f_in, open(out_path, "w", encoding="utf-8") as f_out:
                    for line in f_in:
                        tokens = line.strip().split()
                        lemmas = []
                        for token in tokens:
                            lemma, status = lemmatize_token(token)
                            lemmas.append(lemma)
                            if status is not None:
                                total_words += 1
                                if status:
                                    changed_lemmas += 1
                        f_out.write(" ".join(lemmas) + "\n")

    percent = (changed_lemmas / total_words * 100) if total_words else 0.0

    log("=== Лемматизация завершена ===")
    log(f"Всего обработано слов: {total_words}")
    log(f"Изменённых лемм: {changed_lemmas} ({percent:.2f}%)")
    log(f"Неузнанных слов: {len(unrecognized_counter)} (см. {LOG_UNKNOWN})")
    log(f"Результаты сохранены в {OUTPUT_DIR}")

    # Записываем неузнанные слова и их частоты
    with open(LOG_UNKNOWN, "w", encoding="utf-8") as f:
        for word, count in unrecognized_counter.most_common():
            f.write(f"{word}\t{count}\n")

    log(f"Файл неизвестных лемм с частотами записан в {LOG_UNKNOWN}")

if __name__ == "__main__":
    main()

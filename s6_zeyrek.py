import os
from collections import Counter
import zeyrek
import nltk
nltk.download('punkt_tab')

INPUT_DIR = "TokenizedQirimTatarTexts"
OUTPUT_DIR = "LemmatizedQirimTatarTexts_Zeyrek"
LOG_UNKNOWN = "unknown_lemmas_zeyrek.txt"

def log(msg):
    print(f"[LOG] {msg}")

def main():
    log("=== Лемматизация с помощью Zeyrek ===")
    log(f"Входная директория: {INPUT_DIR}")
    log(f"Выходная директория: {OUTPUT_DIR}")

    analyzer = zeyrek.MorphAnalyzer()
    total_words = 0
    changed_lemmas = 0
    unrecognized_counter = Counter()

    def lemmatize_token(token):
        if not token.isalpha():
            return token, None
        lemmalist = analyzer.lemmatize(token)
        if lemmalist and lemmalist[0][1]:
            lemma = lemmalist[0][1][0]   # первый возможный вариант
            if lemma != token:
                return lemma, True
            else:
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

    with open(LOG_UNKNOWN, "w", encoding="utf-8") as f:
        for word, count in unrecognized_counter.most_common():
            f.write(f"{word}\t{count}\n")

    log(f"Файл неизвестных лемм с частотами записан в {LOG_UNKNOWN}")

if __name__ == "__main__":
    main()

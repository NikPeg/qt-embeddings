import os

# Импорт твоего лемматизатора
from s10_lemmatizer import findPos, revisedDict

def get_lemma(word):
    """
    Возвращает лемму слова через findPos.
    Если не найдено — возвращает исходное слово.
    """
    findings = findPos(word.lower(), revisedDict)
    if findings and findings[0][0]:
        lemma_id = findings[0][0]
        lemma = lemma_id.split("_")[0]
        return lemma
    return word

INPUT_DIR = "TokenizedQirimTatarTexts"
OUTPUT_DIR = "LemmatizedQirimTatarTexts_NEW"

def process_file(in_path, out_path):
    with open(in_path, "r", encoding="utf-8") as fin:
        lines = fin.readlines()
    lemmatized_lines = []
    for line in lines:
        tokens = line.strip().split()
        lemmas = [get_lemma(token) for token in tokens]
        lemmatized_lines.append(" ".join(lemmas))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fout:
        fout.write("\n".join(lemmatized_lines))

def main():
    file_count = 0
    for root, _, files in os.walk(INPUT_DIR):
        for fname in files:
            if fname.lower().endswith(".txt"):
                in_path = os.path.join(root, fname)
                rel_path = os.path.relpath(in_path, INPUT_DIR)
                out_path = os.path.join(OUTPUT_DIR, rel_path)
                process_file(in_path, out_path)
                file_count += 1
                if file_count % 10 == 0:
                    print(f"[LOG] Обработано файлов: {file_count}")
    print(f"[LOG] Готово! Всего обработано файлов: {file_count}")
    print(f"[LOG] Лемматизированные тексты сохранены в {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

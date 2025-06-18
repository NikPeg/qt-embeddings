import os
import re

INPUT_DIR = "CleanQirimTatarTexts"
OUTPUT_DIR = "TokenizedQirimTatarTexts"

def log(msg):
    print(msg)

def to_output_path(filepath):
    rel_path = os.path.relpath(filepath, INPUT_DIR)
    out_path = os.path.join(OUTPUT_DIR, rel_path)
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)
    return out_path

def split_sentences(text):
    # Разбить текст на предложения (учитывая знаки препинания)
    sentence_end_re = r'(?<=[.!?…])\s+'
    sentences = re.split(sentence_end_re, text)
    # Удаляем пустые
    return [s.strip() for s in sentences if s.strip()]

def tokenize_sentence(sentence):
    # Самый простой токенизатор: слова и числа, французские/русские кавычки и дефисы отделяются
    tokens = re.findall(r"\b\w+\b|[.,!?;:«»\"'“”‘’\-–—()]", sentence, re.UNICODE)
    return tokens

def process_file(infile, outfile):
    with open(infile, "r", encoding="utf-8") as fin:
        text = fin.read()
    sentences = split_sentences(text)
    log(f"   Предложений найдено: {len(sentences)}")
    tokenized_sentences = []
    for sent in sentences:
        tokens = tokenize_sentence(sent)
        tokenized_sentences.append(" ".join(tokens))
    with open(outfile, "w", encoding="utf-8") as fout:
        for line in tokenized_sentences:
            fout.write(line + "\n")
    log(f"   Сохранено токенизированных предложений: {len(tokenized_sentences)} в файл: {outfile}")

def main():
    log("=== Старт токенизации текстов ===")
    files_processed = 0
    total_sentences = 0
    for root, _, files in os.walk(INPUT_DIR):
        for fname in files:
            if not fname.lower().endswith(".txt"):
                continue
            in_path = os.path.join(root, fname)
            out_path = to_output_path(in_path)
            log(f"[Файл] Обрабатывается: {in_path}")
            process_file(in_path, out_path)
            files_processed += 1
            with open(out_path, "r", encoding="utf-8") as f:
                count = sum(1 for _ in f)
            total_sentences += count
    log(f"=== Токенизация завершена ===")
    log(f"Обработано файлов: {files_processed}")
    log(f"Всего токенизированных предложений: {total_sentences}")
    log(f"Результаты сохранены в: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

import os
import hashlib
from pathlib import Path

# Папка с исходными текстами и папка для сохранения обработанных
INPUT_DIR = "QirimTatarTexts"
OUTPUT_DIR = "CleanQirimTatarTexts"

def log(message):
    print(message)

def ensure_output_path(input_file):
    relpath = os.path.relpath(input_file, INPUT_DIR)
    out_path = os.path.join(OUTPUT_DIR, relpath)
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)
    return out_path

def is_informative(text, min_len=100):  # длина/слова корректируй по задаче
    # Оставляем только "длинные" тексты без многочисленных повторов одного символа, без веб-меток и т.п.
    text = text.strip()
    if len(text) < min_len:
        return False
    if text.lower().startswith(("copyright", "isbn", "www", "https", "<html", "[", "#", "//")):
        return False
    return True

def to_unicode(text):
    # Пытаемся привести текст к utf-8
    try:
        return text.encode('utf-8').decode('utf-8')
    except Exception as e:
        log(f"[!] Ошибка перекодировки: {e}")
        return text

def get_text_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def clean_text(text):
    # Удаляем неинформативные технические строки (регулярки можно расширять):
    import re
    # удалим html-теги
    text = re.sub(r'<.*?>', '', text)
    # удалим web-адреса
    text = re.sub(r'http\S+|www\.\S+', '', text)
    # удалим бессмысленные длинные повторения не-буквенных символов
    text = re.sub(r'(\n\s*\n)+', '\n\n', text)
    return text.strip()

def walk_txt_files(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith('.txt'):
                yield os.path.join(root, file)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log("=== Старт предварительной обработки текстов ===")

    seen_hashes = set()
    total_files = 0
    saved_files = 0
    skipped_dups = 0
    skipped_uninf = 0

    for file_path in walk_txt_files(INPUT_DIR):
        total_files += 1
        log(f"Обрабатывается: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="cp1251") as f:
                    text = f.read()
            except Exception as e:
                log(f"[!] Пропущен (ошибка при чтении файла): {file_path} ({e})")
                continue

        # Работа с текстом
        text = to_unicode(text)
        text = clean_text(text)

        content_hash = get_text_hash(text)

        if content_hash in seen_hashes:
            log(f" [!] Дубликат. Пропущен.")
            skipped_dups += 1
            continue
        seen_hashes.add(content_hash)

        if not is_informative(text):
            log(f" [!] Неинформативный/короткий. Пропущен.")
            skipped_uninf += 1
            continue

        out_file = ensure_output_path(file_path)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text)
        saved_files += 1
        log(f" [+] Сохранено в: {out_file}")

    log("=== Обработка завершена ===")
    log(f"Всего файлов обработано: {total_files}")
    log(f"Сохранено уникальных и информативных файлов: {saved_files}")
    log(f"Пропущено дубликатов: {skipped_dups}")
    log(f"Пропущено неинформативных: {skipped_uninf}")
    log(f"Очищенные тексты находятся в папке: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

import os
import re

INPUT_DIR = "LemmatizedQirimTatarTexts_NEW"
OUTPUT_DIR = "FilteredQirimTatarTexts"

# Минимальный список крымскотатарских стоп-слов (можно расширять)
STOP_WORDS = {
    "ве", "да", "де", "бу", "лякин", "сонъ", "ичин", "ички", "ичюн", "ларни",
    "ки", "у", "эди", "билдирди", "ир"  # и др.
}

# Крымскотатарский алфавит (кириллица)
KT_CYR = "абвгґдеёжзийiклмнопрстуфхцчшщъьюяәєіїөүһҫғңөқұўҗӣҧҗэ"  # можно дополнить
# Крымскотатарский алфавит (латиница, минимум)
KT_LAT = "abcçdefgğhıijklmnoöprsştuüvyz"

# Функция для определения крымскотатарскости (упрощенная)
def is_qt_word(word):
    word = word.lower()
    return all(c in KT_CYR or c in KT_LAT for c in word)

# Стандартные знаки препинания
PUNCTUATION = set(".,!?;:()«»\"'-–—”“‘’[]{}…/\\`~^*=+@#%$_|<>№")

def clean_line(line):
    # Нормализуем (приводим к нижнему регистру)
    tokens = line.strip().lower().split()
    filtered = []
    for tok in tokens:
        # Удаляем знаки препинания
        tok = tok.strip("".join(PUNCTUATION))
        # Пропуск стоп-слов
        if tok in STOP_WORDS:
            continue
        # Пропуск не крымскотатарских слов и мусора, чисел
        if not is_qt_word(tok):
            continue
        if not tok.isalpha():
            continue
        filtered.append(tok)
    return " ".join(filtered)

def process_file(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
    cleaned = [clean_line(line) for line in lines if line.strip()]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as fout:
        fout.write("\n".join(line for line in cleaned if line.strip()))

def main():
    file_count = 0
    for root, _, files in os.walk(INPUT_DIR):
        for fname in files:
            if fname.lower().endswith('.txt'):
                in_path = os.path.join(root, fname)
                rel_path = os.path.relpath(in_path, INPUT_DIR)
                out_path = os.path.join(OUTPUT_DIR, rel_path)
                process_file(in_path, out_path)
                file_count += 1
                if file_count % 10 == 0:
                    print(f"[LOG] Очищено файлов: {file_count}")
    print(f"[LOG] Готово! Всего файлов очищено: {file_count}")
    print(f"[LOG] Отфильтрованные тексты сохранены в {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

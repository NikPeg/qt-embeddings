import os
import pickle

# Файлы и папки
WORDS_FILE = "words.txt"
TEXTS_DIR = "TokenizedQirimTatarTexts"
LEMMATIZER_DIR = 'turkish_lemmatizer'
REVISED_PICKLE = os.path.join(LEMMATIZER_DIR, 'revisedDict.pkl')
PKL_OUT = "ktatar_dict.pkl"

def get_forms_for_words(words_set, texts_dir):
    """Для каждого слова из words_set ищет формы-употребления в корпусе."""
    forms = {w: set() for w in words_set}
    for root, _, files in os.walk(texts_dir):
        for fname in files:
            if fname.lower().endswith(".txt"):
                with open(os.path.join(root, fname), encoding="utf-8") as fin:
                    for line in fin:
                        for tok in line.strip().split():
                            if tok in forms:
                                forms[tok].add(tok)
    return forms

def find_best_lemma(form, findPos, revisedDict):
    findings = findPos(form.lower(), revisedDict)
    if findings:
        return findings[0][0].split('_')[0]
    else:
        return form  # fallback: если вообще ничего не нашли

def main():
    # --- Считать слова ---
    with open(WORDS_FILE, encoding="utf-8") as f:
        target_words = {line.strip() for line in f if line.strip()}

    # --- Собрать все варианты употребления этих слов (вдруг формы разные) ---
    forms_dict = get_forms_for_words(target_words, TEXTS_DIR)

    # --- Подключить турецкий лемматизатор ---
    import sys
    sys.path.append(LEMMATIZER_DIR)
    from lemmatizer import findPos
    with open(REVISED_PICKLE, "rb") as f:
        revisedDict = pickle.load(f)

    # --- Сборка итогового словаря ---
    lemma_dict = dict()
    for w, forms in forms_dict.items():
        # Берём базовую форму как лемму через турецкий лемматизатор (можно вручную заменить, если есть gold-standard)
        for form in forms:
            lemma = find_best_lemma(form, findPos, revisedDict)
            lemma_dict[form] = lemma

    # --- Сохраняем pkl ---
    with open(PKL_OUT, "wb") as f:
        pickle.dump(lemma_dict, f)

    print(f"Создан словарь {len(lemma_dict)} форма-лемма => {PKL_OUT}")

if __name__ == "__main__":
    main()

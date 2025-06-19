import os
import pickle

LEMMATIZED_DIR = "LemmatizedQirimTatarTexts"
WORDS_FILE = "words.txt"  # вручную отвалидированные крымскотатарские слова
LEMMATIZER_DIR = 'Turkish-Lemmatizer'
REVISED_PICKLE = os.path.join(LEMMATIZER_DIR, 'revisedDict.pkl')
PKL_OUT = "ktatar_final_dict.pkl"

def log(msg):
    print(f"[LOG] {msg}")

def load_manual_words(words_file):
    # Множество слов, которые были вручную признаны крымскотатарскими
    with open(words_file, encoding='utf-8') as f:
        words = {line.strip() for line in f if line.strip()}
    return words

def get_all_forms_from_texts(text_dir):
    forms = set()
    for root, _, files in os.walk(text_dir):
        for fname in files:
            if fname.lower().endswith(".txt"):
                with open(os.path.join(root, fname), encoding='utf-8') as fin:
                    for line in fin:
                        for tok in line.strip().split():
                            if tok.isalpha():
                                forms.add(tok)
    return forms

def lemmatize_with_turkish_lemmatizer(form, findPos, revisedDict):
    findings = findPos(form.lower(), revisedDict)
    if findings:
        lemma = findings[0][0].split('_')[0]
        return lemma
    return None

def main():
    # --- Шаг 1: собрать вручную валидированные крымскотатарские слова ---
    manual_words = load_manual_words(WORDS_FILE)
    log(f"Загружено вручную определённых крымскотатарских слов: {len(manual_words)}")

    # --- Шаг 2: собрать все слова из лемматизированного корпуса ---
    all_forms = get_all_forms_from_texts(LEMMATIZED_DIR)
    log(f"В корпусе найдено уникальных слов: {len(all_forms)}")

    # --- Шаг 3: подключить Turkish-Lemmatizer ---
    import sys
    sys.path.append(LEMMATIZER_DIR)
    from lemmatizer import findPos
    with open(REVISED_PICKLE, "rb") as f:
        revisedDict = pickle.load(f)
    log("Загружен Turkish-Lemmatizer.")

    # --- Шаг 4: строим итоговый словарь ---
    lemma_dict = dict()
    not_recognized = 0
    for form in all_forms:
        lemma = lemmatize_with_turkish_lemmatizer(form, findPos, revisedDict)
        if lemma and lemma != form:
            lemma_dict[form] = lemma
        elif form in manual_words:
            lemma_dict[form] = form
        else:
            not_recognized += 1

    log(f"Итого лемм в словаре: {len(lemma_dict)}")
    log(f"Не удалось лемматизировать и вручную провалидировать: {not_recognized} слов (они отброшены)")
    with open(PKL_OUT, "wb") as f:
        pickle.dump(lemma_dict, f)
    log(f"Сохранено в {PKL_OUT}")

if __name__ == "__main__":
    main()

import os
import sys
import pickle
import torch
from collections import Counter

from transformers import AutoModelForCausalLM, AutoTokenizer

LEMMATIZER_DIR = 'turkish_lemmatizer'  # Папка, где лежит lemmatizer.py и revisedDict.pkl
REVISED_PICKLE = os.path.join(LEMMATIZER_DIR, 'revisedDict.pkl')
DEEPSEEK_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

def log(msg):
    print(f"[LOG] {msg}")

def load_lemmatizer():
    # Корректно добавляем путь к turkish_lemmatizer
    abs_path = os.path.abspath(LEMMATIZER_DIR)
    if abs_path not in sys.path:
        sys.path.append(abs_path)
    try:
        from lemmatizer import findPos
    except ImportError as e:
        log(f"Ошибка импорта lemmatizer.py: {e}")
        sys.exit(1)
    with open(REVISED_PICKLE, 'rb') as f:
        revisedDict = pickle.load(f)
    return findPos, revisedDict

def load_deepseek():
    tokenizer = AutoTokenizer.from_pretrained(DEEPSEEK_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        DEEPSEEK_MODEL,
        device_map="auto",
        torch_dtype=torch.float16,
        use_flash_attention_2=False,
        trust_remote_code=True
    )
    return tokenizer, model

def is_tatar_or_russian(word, tokenizer, model):
    # Промпт для уточнения языка слова (односложный ответ)
    system_prompt = (
        "Перед тобой слово из текста. Ответь только одним словом (без кавычек): 'татарский', если это крымскотатарское слово, или 'русский', если это русское слово.\n"
        f"Слово: {word}\n"
        "Ответ:"
    )
    inputs = tokenizer(system_prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=1,
        do_sample=False,
        temperature=0.01,
        top_p=0.95,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = (response.split("Ответ:")[-1].strip() or response.strip()).lower()
    if 'татар' in answer:
        return 'tatar'
    if 'рус' in answer:
        return 'russian'
    return answer # fallback

def process_words(words, findPos, revisedDict, tokenizer, model):
    results = []
    tatar_count = 0
    russian_count = 0
    unknown_count = 0
    for word in words:
        word = word.strip()
        if not word or not word.isalpha():
            continue
        findings = findPos(word.lower(), revisedDict)
        # Узнаём слово через лемматизатор:
        if findings:
            lemma = findings[0][0].rsplit('_', 1)[0]
            results.append((word, lemma, "lem"))
        else:
            lang = is_tatar_or_russian(word, tokenizer, model)
            results.append((word, word, lang))
            if lang == "tatar":
                tatar_count += 1
            elif lang == "russian":
                russian_count += 1
            else:
                unknown_count += 1
    return results, tatar_count, russian_count, unknown_count

def main():
    # ------ Пути к входу/выходу ------
    input_file = "words.txt"                  # один токен в строке
    output_file = "word_filter_output.tsv"

    # ------ Подгружаем модели ------
    log("Загружаем Turkish-Lemmatizer...")
    findPos, revisedDict = load_lemmatizer()
    log("Загружаем DeepSeek-R1-Distill-Qwen-32B...")
    tokenizer, model = load_deepseek()

    # ------ Чтение слов ------
    with open(input_file, "r", encoding="utf-8") as f:
        in_words = [w.strip() for w in f if w.strip()]

    # ------ Обработка ------
    log("Начата обработка слов...")
    results, tatar_count, russian_count, unknown_count = process_words(
        in_words, findPos, revisedDict, tokenizer, model)

    # ------ Запись результата ------
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("word\tlemma\tmethod\n")
        for word, lemma, method in results:
            out.write(f"{word}\t{lemma}\t{method}\n")

    log(f"Татарских: {tatar_count}, Русских: {russian_count}, не смог классифицировать: {unknown_count}")
    log(f"Всего пройдено: {len(results)}")
    log(f"Результаты записаны в {output_file}")

if __name__ == "__main__":
    main()

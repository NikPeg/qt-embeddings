import os
import pickle
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from collections import Counter

# Turkish Lemmatizer settings
LEMMATIZER_DIR = 'Turkish-Lemmatizer'
REVISED_PICKLE = os.path.join(LEMMATIZER_DIR, 'revisedDict.pkl')

# DeepSeek model
DEEPSEEK_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

def load_lemmatizer():
    sys.path.append(LEMMATIZER_DIR)
    from lemmatizer import findPos
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
        temperature=0.01,  # Сделать ответ более детерминированным
        top_p=0.95,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = response.split("Ответ:")[-1].strip().lower()
    if 'татар' in answer:
        return 'tatar'
    if 'рус' in answer:
        return 'russian'
    return answer  # fallback

def process_words(words, findPos, revisedDict, tokenizer, model):
    results = []
    tatar_count = 0
    russian_count = 0
    for word in words:
        # Пропускаем пунктуацию или числа
        if not word.isalpha():
            continue
        findings = findPos(word.lower(), revisedDict)
        if findings:
            lemma = findings[0][0].rsplit('_', 1)[0]
            # Считаем латентные "узнанные" слова
            results.append((word, lemma, "lem"))
        else:
            lang = is_tatar_or_russian(word, tokenizer, model)
            results.append((word, word, lang))
            if lang == "tatar":
                tatar_count += 1
            elif lang == "russian":
                russian_count += 1
    return results, tatar_count, russian_count

def main():
    # ====== Подгружаем модели ======
    print("[LOG] Загружаем Turkish-Lemmatizer...")
    findPos, revisedDict = load_lemmatizer()
    print("[LOG] Загружаем DeepSeek-R1-Distill-Qwen-32B...")
    tokenizer, model = load_deepseek()

    # ====== Пример: читаем слова из файла ======
    input_file = "words.txt"
    output_file = "word_filter_output.tsv"

    with open(input_file, "r", encoding="utf-8") as f:
        in_words = [w.strip() for w in f if w.strip()]

    # ====== Обработка ======
    print("[LOG] Начата обработка слов...")
    results, tatar_count, russian_count = process_words(in_words, findPos, revisedDict, tokenizer, model)

    # ====== Запись результатов ======
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("word\tlemma\tmethod\n")
        for word, lemma, method in results:
            out.write(f"{word}\t{lemma}\t{method}\n")

    print(f"[LOG] Итог — татарских: {tatar_count}, русских: {russian_count}, всего: {len(results)}")
    print(f"[LOG] Результаты сохранены в {output_file}")

if __name__ == "__main__":
    main()

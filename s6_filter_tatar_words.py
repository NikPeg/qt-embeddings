import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

IN_FILE = "unknown_lemmas.txt"
OUT_FILE = "words.txt"
DEEPSEEK_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

def log(msg):
    print(f"[LOG] {msg}")

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

def is_tatar_word(word, tokenizer, model):
    prompt = (
        "Перед тобой слово из текста. Ответь одним словом (без кавычек): 'татарский', если это крымскотатарское слово, или 'русский', если это русское слово.\n"
        f"Слово: {word}\n"
        "Ответ:"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=1,
        do_sample=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = (response.split("Ответ:")[-1].strip() or response.strip()).lower()
    if 'татар' in answer:
        return True
    return False

def main():
    log("Загружаем DeepSeek...")
    tokenizer, model = load_deepseek()
    log(f"Читаем из {IN_FILE}")

    words_to_check = []
    with open(IN_FILE, encoding="utf-8") as fin:
        for line in fin:
            if not line.strip():
                continue
            word = line.split('\t')[0].strip()   # если словарь типа <word>\t<count>
            if word.isalpha():
                words_to_check.append(word)

    log(f"Всего уникальных слов для проверки: {len(words_to_check)}")
    tatar_words = []
    for i, word in enumerate(words_to_check, 1):
        if is_tatar_word(word, tokenizer, model):
            tatar_words.append(word)
        if i % 20 == 0:
            log(f"Обработано: {i} / {len(words_to_check)} ... Татарских найдено: {len(tatar_words)}")

    with open(OUT_FILE, "w", encoding="utf-8") as fout:
        for w in tatar_words:
            fout.write(w + "\n")

    log(f"Записано {len(tatar_words)} крымскотатарских слов в {OUT_FILE}")

if __name__ == "__main__":
    main()

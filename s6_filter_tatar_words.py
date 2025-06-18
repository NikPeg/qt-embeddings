import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

IN_FILE = "unknown_lemmas.txt"
OUT_FILE = "words.txt"
DEEPSEEK_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

FREQ_THRESHOLD = 2

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

def process_llm_response(response):
    # Берём текст после </think> если такой тег есть
    idx = response.find("</think>")
    if idx != -1:
        result = response[idx + len("</think>"):].strip()
    else:
        result = response.strip()
    return result

def is_tatar_word(word, tokenizer, model):
    prompt = (
        "Перед тобой слово из текста. Ответь одним словом: татарский, если это крымскотатарское слово, или русский, если это русское слово. "
        f"Слово: {word} "
        "Ответ:"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    postprocessed = process_llm_response(full_response[len(prompt):])
    log(f"[DEEPSEEK Q] {word}")
    log(f"  [RAW RESPONSE]: {full_response!r}")
    log(f"  [POSTPROCESSED]: {postprocessed!r}")

    answer = postprocessed.lower()
    res = 'татар' in answer or 'tatar' in answer
    log(f"  [RESULT]: {res}")
    return res

def main():
    log("Загружаем DeepSeek...")
    tokenizer, model = load_deepseek()
    log(f"Читаем из {IN_FILE}")

    words_to_check = []
    with open(IN_FILE, encoding="utf-8") as fin:
        for line in fin:
            if not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            word = parts[0].strip()
            try:
                freq = int(parts[1])
            except Exception:
                continue
            if word.isalpha() and freq > FREQ_THRESHOLD:
                words_to_check.append(word)

    total = len(words_to_check)
    log(f"Всего уникальных слов для проверки (частота>{FREQ_THRESHOLD}): {total}")
    tatar_words = []

    for i, word in enumerate(words_to_check, 1):
        if is_tatar_word(word, tokenizer, model):
            tatar_words.append(word)
        if i % 10 == 0 or i == total:
            log(f"Обработано: {i} / {total} (Осталось: {total-i})")

    with open(OUT_FILE, "w", encoding="utf-8") as fout:
        for w in tatar_words:
            fout.write(w + "\n")

    log(f"Записано {len(tatar_words)} крымскотатарских слов в {OUT_FILE}")

if __name__ == "__main__":
    main()

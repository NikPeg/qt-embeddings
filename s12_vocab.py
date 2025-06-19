import os
from collections import Counter

INPUT_DIR = "FilteredQirimTatarTexts"
VOCAB_OUT = "vocab.txt"
VOCAB_FREQ_OUT = "vocab_freq.txt"

vocab_counter = Counter()

for root, _, files in os.walk(INPUT_DIR):
    for fname in files:
        if fname.lower().endswith('.txt'):
            with open(os.path.join(root, fname), encoding='utf-8') as fin:
                for line in fin:
                    tokens = line.strip().split()
                    vocab_counter.update(tokens)

# Сохраним словарь (только уникальные слова, по убыванию частоты)
with open(VOCAB_OUT, 'w', encoding='utf-8') as f:
    for word, _ in vocab_counter.most_common():
        f.write(word + '\n')

# Сохраним словарь с частотами
with open(VOCAB_FREQ_OUT, 'w', encoding='utf-8') as f:
    for word, count in vocab_counter.most_common():
        f.write(f'{word}\t{count}\n')

print(f"[LOG] Уникальных слов: {len(vocab_counter)}")
print(f"[LOG] vocab.txt и vocab_freq.txt сохранены.")

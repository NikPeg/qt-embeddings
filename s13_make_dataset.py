import os

INPUT_DIR = "FilteredQirimTatarTexts"
OUTPUT_DATASET = "cbow_dataset.txt"
WINDOW_SIZE = 2  # количество слов слева и справа от центрального слова

def generate_cbow_pairs(tokens, window_size):
    pairs = []
    for idx in range(len(tokens)):
        context = []
        # Слова слева
        for i in range(1, window_size+1):
            if idx-i >= 0:
                context.append(tokens[idx-i])
        # Слова справа
        for i in range(1, window_size+1):
            if idx+i < len(tokens):
                context.append(tokens[idx+i])
        if context:
            # Для word2vec обычно сортировка контекста неважна (его можно рандомизировать или хранить при желании)
            pairs.append((context, tokens[idx]))
    return pairs

dataset_pairs = []

for root, _, files in os.walk(INPUT_DIR):
    for fname in files:
        if fname.lower().endswith('.txt'):
            with open(os.path.join(root, fname), encoding='utf-8') as f:
                for line in f:
                    tokens = line.strip().split()
                    if len(tokens) < 2:
                        continue
                    dataset_pairs.extend(generate_cbow_pairs(tokens, WINDOW_SIZE))

# Записываем пары в файл (tab-separated, контекст = слова через пробел, target-слово)
with open(OUTPUT_DATASET, 'w', encoding='utf-8') as fout:
    for context, target in dataset_pairs:
        fout.write(" ".join(context) + "\t" + target + "\n")

print(f"[LOG] Всего подготовлено пар контекст-таргет: {len(dataset_pairs)}")
print(f"[LOG] Датасет сохранён в {OUTPUT_DATASET}")

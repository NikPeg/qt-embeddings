from s10_lemmatizer import findPos, revisedDict

def get_lemma(word):
    """
    Получить лемму для слова через findPos из твоего лемматизатора.
    Возвращает строку-лемму или None, если не найдено.
    """
    findings = findPos(word.lower(), revisedDict)
    if findings and findings[0][0]:
        lemma_id = findings[0][0]
        # Отрезаем _1/_2 от леммы (берём до первого "_")
        lemma = lemma_id.split("_")[0]
        return lemma
    return None

# Тестовые слова и формы (кейсы покрывают разные морфологические преобразования)
test_words = [
    # Существительные (кириллица)
    "халкъларымызда", "халкъны", "халкънынъ", "халкълар", "халкъма",
    # Существительные (латиница)
    "halkımızda", "halklarına", "halkı",
    # Глаголы (кириллица)
    "бараджакъмыз", "бардым", "бармайджакъ", "бармакъ", "барырым",
    # Глаголы (латиница)
    "geldim", "geleceksiniz", "gelmeyen",
    # Прилагательные/наречия (разные формы)
    "яхшысы", "яхшылап", "güzelinden",
    # Местоимения, служебные (если есть в словаре)
    "меним", "сенинъ", "бизни", "сизге",
    # Прочее, смешанные формы
    "коюмда", "махульдюрде", "ишледим", "учун", "эди",
    "санъатчиларымыз", "айларымызда", "чинликлеринде", "айланып", "ярдымчы"
]

print("Тест слов и их лемм:")
print("Слово\t\t→ Лемма")
print("-" * 30)
for word in test_words:
    lemma = get_lemma(word)
    print(f"{word:15s} → {lemma}")

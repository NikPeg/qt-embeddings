import pickle

# Загрузим заранее собранный словарь
with open("ktatar_final_dict.pkl", "rb") as f:
    lemma_dict = pickle.load(f)

def qt_lem(word):
    """
    Крымскотатарский лемматизатор (кириллица + латиница).
    Возвращает лемму в корпусном словаре, иначе None.
    """
    return lemma_dict.get(word.lower(), None)

test_words = [
    # Кириллица (разные формы, служебные, имена, аффиксы)
    "Бир", "бир", "Ай", "ай", "коюм", "Коюм", "коюмда",
    "махульдюрни", "зиярет", "Эттим", "борджум", "эди",
    "Акъмесджит", "сокъакъларында", "ЯКЪЫНДА", "мектепке",
    "мектюбинде", "ЮРИП", "отуз", "чакъырым", "маджлис", # и др.
    # Латиница (то же слово, аналогичные формы)
    "Bir", "bir", "Ay", "ay", "koyum", "Koyum", "koyumda",
    "mahuldürni", "ziyaret", "Ettim", "borcum", "edi",
    "Aqmescit", "soqaqlarında", "YAKINDA", "mektepke",
    "mektubinde", "YURIP", "otuz", "çakırım", "meclis",
    # Русские и нерелевантные — для теста
    "Москва", "яблоко", "работает", "AI", "hello"
]

print("Слово → Лемма (None, если не крымскотатарское слово):\n")
for word in test_words:
    lemma = qt_lem(word)
    print(f"{word:15} → {lemma}")

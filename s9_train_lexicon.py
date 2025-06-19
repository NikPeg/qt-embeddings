# -*- coding: utf-8 -*-
import pickle
import sys

# Файл с корпусным словарём форма:лемма (создан тобой из корпуса)
KTATAR_PKL = "ktatar_final_dict.pkl"
REVISED_PICKLE = "revisedDict.pkl"

def loadWord(ktatar_pkl):
    """
    Загружает словарь крымскотатарских форм и строит wordDict (как у Turkish-Lemmatizer)
    -> wordDict = {"форма_1": ["kok", "форма_1"], ...}
    """
    with open(ktatar_pkl, "rb") as f:
        base_dict = pickle.load(f)
    wordDict = {}
    for form, lemma in base_dict.items():
        wordDict[findID(wordDict, form)] = ["kok", findID(wordDict, lemma)]
    return wordDict

def findID(wordDict, word):
    """
    Генерирует уникальный ключ слова для многозначности.
    """
    ct = 1
    while word+"_"+str(ct) in wordDict:
        ct += 1
    return word+"_"+str(ct)

def generate(wordDict, olay):
    """
    Генерация дополнительных форм для слов по простым типичным крымскотатарским морфемам.
    Можно развить — добавить больше окончаний и схем аффиксов.
    """
    newDict = {}
    # Пример: отрицание в глаголах: -ма/-ме (аналог тур. -ma/-me)
    # Можно создать негативные формы от инфинитива, если есть слова с окончаниями -maq/-mek или -mak/-mek (разные тюркские варианты!)
    if olay == "olumsuzluk eki":  # генерируем отрицательные формы глаголов
        for kelime, valueList in wordDict.items():
            ind = kelime[kelime.index("_")+1:]
            base = kelime[:kelime.index("_")]
            # Для глаголов, оканчивающихся на -maq/-mek/-mak/-mek
            if base.endswith("maq"):
                neg = base[:-3] + "mamaq"
                newDict[findID(wordDict, neg)] = ["olumsuzluk", kelime+"_"+ind]
            if base.endswith("mek"):
                neg = base[:-3] + "memek"
                newDict[findID(wordDict, neg)] = ["olumsuzluk", kelime+"_"+ind]
            if base.endswith("mak"):
                neg = base[:-3] + "mamak"
                newDict[findID(wordDict, neg)] = ["olumsuzluk", kelime+"_"+ind]
    # Пример: можно добавить генерацию других форм — стемминг, суффиксы притяжательности/множественного числа и др.
    return newDict

def appendDict(revisedDict, newDict):
    for kelime, valueList in newDict.items():
        if kelime in revisedDict:
            revisedDict[findID(revisedDict, kelime[:kelime.index("_")])] = valueList
        else:
            revisedDict[kelime] = valueList
    return revisedDict

def main():
    wordDict = loadWord(KTATAR_PKL)
    print(f"Базовый корпусный словарь загружен, слов: {len(wordDict)}")

    # Генерируем дополнительные формы на основе простых крымскотатарских аффиксов (можно расширять самому!)
    wordDict = appendDict(wordDict, generate(wordDict, "olumsuzluk eki"))
    print("Отрицательные формы добавлены.")

    # Можно добавить расширения (например, простые притяжательные/множественные окончания)

    revisedDict = dict(wordDict)
    print(f"Словарь итогово содержит лемм: {len(revisedDict)}")
    with open(REVISED_PICKLE, "wb") as f:
        pickle.dump(revisedDict, f)
    print(f"Готово! Словарь сохранён в {REVISED_PICKLE}")

if __name__ == "__main__":
    main()

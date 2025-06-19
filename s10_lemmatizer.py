import pickle

# Загрузи свой корпусный словарь-ревизор (после trainLexicon.py)
with open("revisedDict.pkl", "rb") as f:
    revisedDict = pickle.load(f)

# Крымскотатарские суффиксы (расширяем по желанию)
suffixList = [
    "",
    # существительное: множественное, притяжательные, родительные, винительные и т.д.
    "лар", "лер",           # множественное число
    "мыз", "миз", "мызлар", "мизлер", "быз", "биз",  # притяжательные 1 л. мн.
    "ың", "иң", "ыңыз", "иңиз",         # притяжательные 2 л.
    "ы", "и", "ысы", "иси",             # притяжат. 3 л.
    "да", "де", "та", "те",             # местный падеж
    "дан", "ден", "тан", "тен",         # исходный падеж
    "га", "ге", "ка", "ке",             # дательный падеж
    "ны", "ни", "ныны", "нини",         # винительный падеж
    "даки", "деки",                     # относительный
    "ым", "им", "ум", "үм",             # притяжательные
    # глагольные: времена, повелит.
    "ды", "ди", "ду", "дү", "тым", "тим", "тук", "тик",  # прош.вр
    "ма", "ме",           # отрицание
    "сын", "син",         # повелительное
    "мак", "мек",         # инфинитив
    "гъа", "ге", "къа", "ке",           # направительный (разные варианты)
    "чы", "чи",            # -чик суффиксы (уменьшаительно-ласкательные)
    "лык", "лик", "лыкъ", "ликъ", "лук", "люк",  # абстракция
    "сыз", "сиз",          # без-
    "чы", "чи", "дик", "дык",           # деепричастия, причастия
    "чы", "чи", "чыгъ", "чиңиз",        # агентные и производные
    # ... (добавляй!)
]

def checkSuffixValidation(suff):
    validList = []
    if suff in suffixList:
        validList.append(suff)
    for ind in range(1, len(suff)):
        if suff[:ind] in suffixList:
            cont, contList = checkSuffixValidation(suff[ind:])
            if cont:
                contList = [suff[:ind] + "+" + l for l in contList]
                validList = validList + contList
    return len(validList) > 0, validList

def check(root, suffix, guess, action):
    # В простейшем варианте для крымскотатарского — всегда True, если суффиксы валидны.
    return checkSuffixValidation(suffix)[0]

def findPos(kelime, revisedDict):
    l = []
    if "'" in kelime:
        l.append([kelime[:kelime.index("'")]+"_1", "tirnaksiz", kelime])
    mid = []
    for i in range(len(kelime)):
        guess = kelime[:len(kelime)-i]
        suffix = kelime[len(kelime)-i:]
        ct = 1
        while guess+"_"+str(ct) in revisedDict:
            if check(guess, suffix, revisedDict[guess+"_"+str(ct)][1], revisedDict[guess+"_"+str(ct)][0]):
                guessList = (revisedDict[guess+"_"+str(ct)])
                while guessList[0] not in ["kok", "fiil", "olumsuzluk"]:
                    guessList = revisedDict[guessList[1]]
                mid.append([guessList[1], revisedDict[guess+"_"+str(ct)][0], guess+"_"+str(ct)])
            ct = ct + 1
    temp = []
    for kel in mid:
        kelime_kok = kel[0][:kel[0].index("_")]
        kelime_len = len(kelime_kok)
        if kelime_kok.endswith("mak") or kelime_kok.endswith("мек"):
            kelime_len -= 3
        not_inserted = True
        for index in range(len(temp)):
            temp_kelime = temp[index]
            temp_kelime_kok = temp_kelime[0][:temp_kelime[0].index("_")]
            temp_len = len(temp_kelime_kok)
            if temp_kelime_kok.endswith("mak") or temp_kelime_kok.endswith("мек"):
                temp_len -= 3
            if(kelime_len > temp_len):
                temp.insert(index, kel)
                not_inserted = False
        if not_inserted:
            temp.append(kel)
    output = l + temp
    if len(output) == 0:
        output.append([kelime+"_1", "çaresiz", kelime+"_1",])
    return output

# --- Тест
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Please provide a word as a system argument")
        sys.exit(0)
    word = sys.argv[1]
    print("Possible lemmas for", word, "in ranked order:")
    findings = findPos(word.lower(), revisedDict)
    for finding in findings:
        print(finding[0])

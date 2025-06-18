import os

TARGET_DIR = "CleanQirimTatarTexts"

def should_delete(filename):
    lowered = filename.lower()
    return "rus" in lowered or "рус" in lowered

def main():
    files_deleted = 0
    for root, _, files in os.walk(TARGET_DIR):
        for fname in files:
            if should_delete(fname):
                fpath = os.path.join(root, fname)
                try:
                    os.remove(fpath)
                    print(f"[Удалено] {fpath}")
                    files_deleted += 1
                except Exception as e:
                    print(f"[Ошибка] {fpath}: {e}")
    print(f"Всего файлов удалено: {files_deleted}")

if __name__ == "__main__":
    main()

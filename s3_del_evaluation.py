import os

TARGET_DIR = "CleanQirimTatarTexts"
ASPOSE_LINE = "Evaluation Only. Created with Aspose.Words. Copyright 2003-2025 Aspose Pty Ltd."

def clean_file(filepath):
    changed = False
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = [line for line in lines if ASPOSE_LINE not in line]
    if len(new_lines) != len(lines):
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        changed = True
    return changed

def main():
    files_checked = 0
    files_cleaned = 0
    for root, _, files in os.walk(TARGET_DIR):
        for fname in files:
            if fname.lower().endswith(".txt"):
                fpath = os.path.join(root, fname)
                files_checked += 1
                if clean_file(fpath):
                    print(f"[Очищено] {fpath}")
                    files_cleaned += 1
    print(f"Всего файлов проверено: {files_checked}")
    print(f"Файлов очищено от Aspose-строк: {files_cleaned}")

if __name__ == "__main__":
    main()

from pathlib import Path

file_path = Path("03_materials/rag_intro.txt")
text = file_path.read_text(encoding="utf-8")

print("读取到的资料：")
print(text)
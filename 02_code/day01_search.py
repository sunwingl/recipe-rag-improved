from pathlib import Path

file_path = Path("03_materials/rag_intro.txt")
text = file_path.read_text(encoding="utf-8")

keyword = input("请输入要查找的关键词：").strip()

if not keyword:
    print("关键词不能为空。")
else:
    found = False

    for line in text.splitlines():
        if keyword in line:
            print("找到：", line)
            found = True

    if not found:
        print("资料中没有找到这个关键词。")
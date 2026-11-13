from pathlib import Path

file_path = Path("03_materials/rag_intro.txt")
text = file_path.read_text(encoding="utf-8")

question = input("请输入你的问题：").strip()
keyword = input("请输入检索关键词：").strip()

matches = []

for line in text.splitlines():
    if keyword and keyword in line:
        matches.append(line)

if not matches:
    print("没有找到相关资料，请换一个关键词。")
else:
    context = "\n".join(matches)

    prompt = f"""请根据以下资料回答问题。
如果资料不足以回答，请明确说明，不要编造。

资料：
{context}

问题：
{question}
"""

    print("\n请把下面的提示词复制给 AI：")
    print(prompt)
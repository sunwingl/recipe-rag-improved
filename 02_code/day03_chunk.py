from pathlib import Path
import json

from dotenv import dotenv_values
from openai import OpenAI

# 找到知识文档
file_path = (
    Path(__file__).resolve().parent.parent
    / "03_materials"
    / "rag_intro.txt"
)

# 读取文档内容
text = file_path.read_text(encoding="utf-8")

# 查看读取结果
print("文档路径：", file_path)
print("文档字符数：", len(text))
print("\n文档内容：")
print(text)



# # 设置每个文本块的最大字符数
# chunk_size = 50

# # 用来保存所有文本块
# chunks = []

# # 每隔50个字符切一次
# for start in range(0, len(text), chunk_size):
#     end = start + chunk_size
#     chunk = text[start:end]
#     chunks.append(chunk)

# 每个文本块最多50个字符
chunk_size = 50

# 相邻文本块重复10个字符
chunk_overlap = 10

# 保存切块结果
chunks = []

# 第一个文本块从第0个字符开始
start = 0

while start < len(text):
    # 计算当前文本块的结束位置
    end = min(start + chunk_size, len(text))

    # # 截取当前文本块
    # chunk = text[start:end]
    # chunks.append(chunk)
    chunk = text[start:end]

    chunk_data = {
        "chunk_id": len(chunks) + 1,
        "source": file_path.name,
        "start": start,
        "end": end,
        "content": chunk,
    }

    chunks.append(chunk_data)

    # 如果已经读取到文档末尾，就结束循环
    if end == len(text):
        break

    # 下一个文本块向前退10个字符
    start = end - chunk_overlap

# # 显示切块结果
# print("\n切块数量：", len(chunks))

# for index, chunk in enumerate(chunks, start=1):
#     print(f"\n--- 文本块 {index} ---")
#     print(chunk)
print("\n切块数量：", len(chunks))

for chunk_data in chunks:
    print(f"\n--- 文本块 {chunk_data['chunk_id']} ---")
    print("来源：", chunk_data["source"])
    print(
        "字符范围：",
        f"{chunk_data['start']}～{chunk_data['end'] - 1}",
    )
    print("内容：", chunk_data["content"])


    # 设置切块结果的保存位置
output_path = (
    Path(__file__).resolve().parent.parent
    / "04_showcase"
    / "day03_chunks.json"
)

# 将Python数据转换为JSON文本
json_text = json.dumps(
    chunks,
    ensure_ascii=False,
    indent=2,
)

# 写入JSON文件
output_path.write_text(
    json_text,
    encoding="utf-8",
)

print("\n切块结果已保存到：", output_path)


# 接收用户的问题和检索关键词
question = input("\n请输入你的问题：").strip()
keyword = input("请输入一个检索关键词：").strip()

# 保存检索到的文本块
retrieved_chunks = []

# 遍历全部文本块
for chunk_data in chunks:
    if keyword in chunk_data["content"]:
        retrieved_chunks.append(chunk_data)

# 显示检索结果
print("\n用户问题：", question)
print("检索关键词：", keyword)
print("找到的文本块数量：", len(retrieved_chunks))

for chunk_data in retrieved_chunks:
    print(f"\n--- 命中文本块 {chunk_data['chunk_id']} ---")
    print("来源：", chunk_data["source"])
    print("内容：", chunk_data["content"])



    # 如果没有检索到任何文本块，就停止运行
if not retrieved_chunks:
    raise SystemExit("没有找到相关知识，无法生成回答。")

# 把检索到的文本块合并成上下文
context = "\n\n".join(
    chunk_data["content"]
    for chunk_data in retrieved_chunks
)

# 构造带有外部知识的提示词
prompt = f"""
请只根据下面提供的知识回答用户问题。
如果知识中没有答案，请明确回答“资料中没有相关信息”。

【知识】
{context}

【用户问题】
{question}
"""

# 读取模型配置
env_path = (
    Path(__file__).resolve().parent.parent
    / ".env"
)

config = dotenv_values(
    env_path,
    encoding="utf-8-sig",
)

# 创建模型客户端
client = OpenAI(
    api_key=config["LLM_API_KEY"],
    base_url=config["LLM_BASE_URL"],
    timeout=120,
    max_retries=0,
)

print("\n正在等待模型回答……", flush=True)

# 对照组：只把用户问题交给模型，不提供外部知识
plain_response = client.chat.completions.create(
    model=config["LLM_MODEL"],
    messages=[
        {
            "role": "user",
            "content": question,
        }
    ],
    max_tokens=256,
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    },
)

print("\n普通模型回答：")
print(plain_response.choices[0].message.content)

# 调用模型
response = client.chat.completions.create(
    model=config["LLM_MODEL"],
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    max_tokens=256,
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    },
)

# 显示最终答案
print("\nRAG回答：")
print(response.choices[0].message.content)
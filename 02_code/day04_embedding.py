from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
from dotenv import dotenv_values
from openai import OpenAI

# 加载文本向量模型
print("正在加载模型……", flush=True)

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    device="cpu",
)

# 准备一句话
text = "学生可以申请住宿补贴。"

# 把文本转换成向量
vector = model.encode(text)

# 查看结果
print("原文：", text)
print("向量维度：", vector.shape)
print("前10个数字：", vector[:10])


# 准备两句待比较的文本
sentences = [
    "在校生租房有什么补助？",
    "今天晚饭吃面条。",
]

# 把两句话分别转换成向量
sentence_vectors = model.encode(sentences)

print("\n两句话的向量形状：", sentence_vectors.shape)

# 比较原句与这两句话的相似度
scores = model.similarity(vector, sentence_vectors)[0]

# 逐条显示结果
for sentence, score in zip(sentences, scores):
    print(f"相似度：{score.item():.4f} | 文本：{sentence}")


    # 读取昨天保存的文本块
chunks_path = (
    Path(__file__).resolve().parent.parent
    / "04_showcase"
    / "day03_chunks.json"
)

chunks = json.loads(chunks_path.read_text(encoding="utf-8"))

# 提取每个文本块的正文，并转换成向量
contents = [chunk["content"] for chunk in chunks]
chunk_vectors = model.encode(contents)

# 把用户的问题也转换成向量
question = input("\n请输入你的问题：").strip()
question_vector = model.encode(question)

# 分别计算问题与每个文本块的相似度
chunk_scores = model.similarity(question_vector, chunk_vectors)[0]

print("\n各文本块的相似度：")
for chunk, score in zip(chunks, chunk_scores):
    print(f"文本块 {chunk['chunk_id']}：{score.item():.4f}")

# # 找出分数最高的文本块
# best_index = chunk_scores.argmax().item()
# best_chunk = chunks[best_index]

# print("\n最相关的文本块：")
# print("来源：", best_chunk["source"])
# print("内容：", best_chunk["content"])

# 最多取相似度最高的两个文本块
top_k = min(2, len(chunks))

# 得到前两名在列表中的位置，按分数从高到低排列
top_indices = chunk_scores.topk(k=top_k).indices.tolist()

# 按这些位置取回原始文本块
retrieved_chunks = [chunks[i] for i in top_indices]

print("\n检索到的文本块：")
for i in top_indices:
    chunk = chunks[i]
    print(f"\n文本块 {chunk['chunk_id']}")
    print("相似度：", round(chunk_scores[i].item(), 4))
    print("来源：", chunk["source"])
    print("内容：", chunk["content"])

# 合并文本，准备作为大模型的参考资料
context = "\n\n".join(
    chunk["content"] for chunk in retrieved_chunks
)

print("\n准备提供给大模型的资料：")
print(context)


# 读取项目中的模型配置
env_path = Path(__file__).resolve().parent.parent / ".env"
config = dotenv_values(env_path, encoding="utf-8-sig")

# 创建调用 GLM 的客户端
llm_client = OpenAI(
    api_key=config["LLM_API_KEY"],
    base_url=config["LLM_BASE_URL"],
    timeout=120,
    max_retries=0,
)

# 把检索资料和用户问题组合成提示词
prompt = f"""
请只根据下面提供的资料回答问题。
如果资料不足以回答，请回答“资料中没有相关信息”，不要猜测。

【参考资料】
{context}

【用户问题】
{question}
"""

print("\n正在等待 GLM 回答……", flush=True)

# 将提示词发送给 GLM
response = llm_client.chat.completions.create(
    model=config["LLM_MODEL"],
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=256,
    extra_body={
        "thinking": {"type": "disabled"}
    },
)

print("\nRAG 回答：")
print(response.choices[0].message.content)
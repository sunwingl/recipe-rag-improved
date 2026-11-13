# 2026-11-05 · Day 4 学习复盘

## 今日工作回顾

本次根据当前可见的学习对话、用户提供的运行结果和项目代码整理。Day 4 从 11 月 4 日开始，跨日完成；本篇按复盘时的法国当地日期命名。

今天的目标是把 Day 3 的关键词检索升级为语义检索。昨天需要手动输入关键词，用字符串匹配寻找资料；今天把问题和文本块转换成向量，通过相似度自动选择资料，再交给 GLM 回答。

学习顺序是：先观察一句话的向量，再比较句子相似度，然后读取昨天的文本块进行 Top-1、Top-2 检索，最后接回 GLM。实际发现最高分文本块里的答案被切断，因此改取前两块；之后虽然出现过一次错误拒答和一次 HTTP 500，最终在仍使用原有拼接方式的情况下，成功回答了“蓝色书签”。资料外问题的检查由用户回复 `0` 确认通过，未提供完整终端输出。

当前完成的是一个最小语义检索 RAG 原型。文档向量仍在每次运行时重新计算，没有新增向量持久化或向量数据库；今天能确认流程跑通，尚不能据此证明它在大量问题上稳定可靠。

## 关键步骤与命令

### 1. 确认继续使用原来的 Conda 环境

今天开始时误用了新开的 VS Code PowerShell 终端，又尝试切换到项目旧 `.venv`，造成环境混淆。查明历史记录后，确定继续使用已经建立的 Miniconda `rag-learning` 环境。

以下是学习中沿用的启动命令，在 **Anaconda Prompt（Miniconda）** 中逐条执行：

```bat
conda activate rag-learning
cd /d "D:\03Personal\20_CodeStudy\40_Projects\rag-learning"
```

`conda activate` 选择项目环境；`cd /d` 同时切换盘符和目录。后续的 `python` 和安装操作都应使用这个环境。用户提供的报错路径也确认程序使用了 `Miniconda3\envs\rag-learning` 中的库。

### 2. 安装并认识 Sentence Transformers

```bat
python -m pip install sentence-transformers
```

`python -m pip` 使用当前环境的 Python 运行包管理器，`install` 安装指定包。用户以 `0` 确认该步成功，未提供具体安装版本或完整输出。

三个名称的区别：

| 名称 | 是什么 |
|---|---|
| `sentence-transformers` | 安装的 Python 工具库 |
| `SentenceTransformer` | 从工具库导入、用于创建模型对象的类 |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 本次加载的具体预训练模型标识 |

工具库最初来自达姆施塔特工业大学 UKP 实验室，项目当前由 Hugging Face 人员及开源社区维护；本次具体模型由 Sentence Transformers 团队训练发布，托管在 Hugging Face。安装工具库与下载具体模型是两件事；首次加载时下载模型，随后在本地 CPU 上计算向量。

### 3. 创建脚本，把一句话转换成向量

```bat
notepad .\02_code\day04_embedding.py
```

这条命令打开或创建今天的 Python 脚本。关键代码如下：

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    device="cpu",
)

text = "学生可以申请住宿补贴。"
vector = model.encode(text)

print("向量维度：", vector.shape)
print("前10个数字：", vector[:10])
```

`model.encode()` 将文本转换成向量，即一组表示文本特征的数字。该模型输出 384 维向量；384 表示数字的数量，不是字数，也不是 384 个可以逐个命名的语义标签。

日常运行命令：

```bat
python .\02_code\day04_embedding.py
```

它使用当前 Conda 环境的 Python 执行脚本。首次运行需要下载模型，后续通常使用本地缓存。

### 4. 计算句子相似度

```python
sentences = [
    "在校生租房有什么补助？",
    "今天晚饭吃面条。",
]

sentence_vectors = model.encode(sentences)
scores = model.similarity(vector, sentence_vectors)[0]

for sentence, score in zip(sentences, scores):
    print(f"相似度：{score.item():.4f} | 文本：{sentence}")
```

两句话分别对应一条向量，实际形状为 `(2, 384)`。相似度结果为：

| 与“学生可以申请住宿补贴。”比较的句子 | 余弦相似度 |
|---|---:|
| 在校生租房有什么补助？ | 0.7716 |
| 今天晚饭吃面条。 | -0.0092 |

这一组结果符合预期：不同措辞的住房补助句子更相似，晚饭句子接近零。余弦相似度范围为 -1～1，负数正常；0.7716 不表示正确率为 77.16%。

`model.similarity()` 在这里返回一行分数，`[0]` 取出这一行。`zip()` 把句子与分数配对，`.item()` 将单个张量数值转成普通 Python 数字，`.4f` 保留四位小数。

### 5. 读取昨天的文本块，进行语义检索

复用了已有的 `04_showcase/day03_chunks.json`，本次没有重新切块。文件共有三个文本块，每块包含正文、来源、编号和字符范围。

```python
chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
contents = [chunk["content"] for chunk in chunks]
chunk_vectors = model.encode(contents)

question = input("\n请输入你的问题：").strip()
question_vector = model.encode(question)
chunk_scores = model.similarity(question_vector, chunk_vectors)[0]
```

`json.loads()` 把 JSON 文本恢复为 Python 数据；列表推导式提取各块正文。问题与正文使用同一个模型生成向量，才能在同一个向量空间比较。

输入问题“这个项目用什么名字做内部测试？”后，实际分数为：

| 文本块 | 相似度 | 与答案的关系 |
|---|---:|---|
| 1 | 0.2613 | 主要介绍 RAG |
| 2 | 0.5390 | 包含“本项目的内部测试代号”，但名字在“蓝色书”处被切断 |
| 3 | 0.4224 | 包含完整“蓝色书签” |

最初使用 `chunk_scores.argmax().item()` 取第一名的位置，再从 `chunks` 取回对应文本块。结果证明检索能够运行，也暴露了一个局限：最高分文本块不一定包含完整答案。

### 6. 从 Top-1 改成 Top-2，合并参考资料

```python
top_k = min(2, len(chunks))
top_indices = chunk_scores.topk(k=top_k).indices.tolist()
retrieved_chunks = [chunks[i] for i in top_indices]

context = "\n\n".join(
    chunk["content"] for chunk in retrieved_chunks
)
```

`top_k` 是取回数量；`min()` 避免要取的数量超过现有块数。`.topk()` 找前 K 名，`.indices.tolist()` 提取它们在列表中的位置；列表位置从 0 开始，与 `chunk_id` 不是同一个概念。

这次按分数依次取回文本块 2、3，`context` 中包含完整的“蓝色书签”。`join()` 只用空行连接片段，不会自动去重、补齐断句或恢复原文。实际最终成功版本仍采用这个拼接方式。

### 7. 读取配置，调用 GLM 生成回答

```python
config = dotenv_values(env_path, encoding="utf-8-sig")

llm_client = OpenAI(
    api_key=config["LLM_API_KEY"],
    base_url=config["LLM_BASE_URL"],
    timeout=120,
    max_retries=0,
)
```

`.env` 保存调用配置，密钥不写进复盘。`timeout=120` 设置请求超时，`max_retries=0` 表示不自动重试。本次沿用项目配置中的 `glm-4.7-flash`。

```python
prompt = f"""
请只根据下面提供的资料回答问题。
如果资料不足以回答，请回答“资料中没有相关信息”，不要猜测。

【参考资料】
{context}

【用户问题】
{question}
"""

response = llm_client.chat.completions.create(
    model=config["LLM_MODEL"],
    messages=[{"role": "user", "content": prompt}],
    max_tokens=256,
    extra_body={"thinking": {"type": "disabled"}},
)

print(response.choices[0].message.content)
```

向量模型负责帮助检索；GLM 收到的是参考资料的原始文字和问题，负责组织回答。本次没有把向量发送给 GLM。

最终用户提供的实际回答是 **“蓝色书签”**。随后使用资料中没有答案的问题“这个项目的开发者出生于哪一年？”进行检查，用户以 `0` 确认结果符合预期；只能记录本次样例通过，不能推断模型始终能够正确拒答。

## 问题与易混点

1. **环境混淆：Conda、旧 `.venv` 与 `.env`。** 新开的 PowerShell 中，`python` 指向 Windows 应用入口，检查命令未输出；尝试运行 `.venv\Scripts\Activate.ps1` 又被 PowerShell 执行策略拦截。查历史记录确认，旧 `.venv` 是 11 月 2 日初始配置时按助手指令创建的，当天稍后已明确改用 Miniconda。最终继续使用 Conda；没有修改执行策略，旧 `.venv` 是否已删除没有明确记录。`.env` 则是当前脚本使用的纯文本配置文件，须保留；历史中创建它的指令是 `notepad .env`，没有查到由 `.txt` 重命名的操作。

2. **最高相似度不等于完整答案，取回资料不等于资料有答案。** Top-1 取到了答案被截断的块，Top-2 补充了含完整代号的块。当前代码没有相似度阈值，只要块数足够，就会为任何问题取回两块；资料是否支持回答还需要进一步判断。曾建议按字符范围恢复连续原文，以及打印实际 `prompt`，但当前检查的代码未应用这些调整，不能把它们写成已完成的修复。

3. **错误拒答与 HTTP 500 是两类问题。** 首次 GLM 返回“资料中没有相关信息”，属于正常响应但答案不符合资料；另一次抛出 `InternalServerError: 500`，属于接口调用失败。原代码重试后正确回答“蓝色书签”，因此无法把先前拒答确定归因于断句；500 的具体原因也未确定，不能直接断言平台整体故障。只读检查确认代码语法通过、文本块与原文位置一致、提示词正确引用资料和问题。建议运行昨天脚本作对照，但没有收到该项执行结果。

## 明天复习

1. 不看代码，用自己的话解释工具库、向量模型、Embedding、GLM 分别负责什么；说明 GLM 最终收到的是文字还是向量。
2. 找出代码中的 `(2, 384)`、`.topk()` 和 `context`，解释其含义；结合今天的三个分数说明为什么取两个块。
3. 回忆一次错误拒答和一次 HTTP 500，说明它们分别发生在什么阶段，以及下一次如何用打印提示词或最小调用做对照。

下一步计划（尚未开始）：保存并复用文档向量，减少每次启动时的重复计算；后续再逐步改进切块、资料拼接和接口异常处理。

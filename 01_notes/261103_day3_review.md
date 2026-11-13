# 2026-11-03 工作复盘

## 今日工作回顾

今天的目标是完成最小 RAG 问答流程中的“文档读取、文本切分、检索和生成回答”。学习顺序从读取本地知识开始，再逐步加入固定长度切块、重叠区域、元数据和 JSON 保存，最后使用关键词找到相关文本块，并把检索结果放入提示词交给 GLM 回答。

最终已跑通一个可验证的最小 RAG 原型：普通模型不知道项目内部测试代号，而 RAG 从本地 `rag\_intro.txt` 命中相关文本块后，能够回答“蓝色书签”。这说明模型没有被重新训练，而是在回答前临时获得了从本地资料中检索出的知识。Day 4 的 Embedding 与语义检索只做了概念引入，随后决定暂停，因此不计为今天已完成的学习内容。

## 关键步骤与命令

1. **读取本地知识文档**

   使用 `Path` 从脚本位置定位项目根目录，再读取 `03\_materials/rag\_intro.txt`。这样脚本不依赖终端当前所在目录，也能找到知识文件。

```python
   file\_path = (
       Path(\_\_file\_\_).resolve().parent.parent
       / "03\_materials"
       / "rag\_intro.txt"
   )
   text = file\_path.read\_text(encoding="utf-8")
   ```

   运行脚本后成功显示了文档路径、字符数和完整内容，说明文档加载成功。

2. **按固定字符数切块，并加入重叠内容**

   设置每块最多 50 个字符，相邻块重叠 10 个字符。重叠区域用于降低句子恰好在边界处被切断造成的信息损失。

```python
   chunk\_size = 50
   chunk\_overlap = 10

   start = 0
   while start < len(text):
       end = min(start + chunk\_size, len(text))
       chunk = text\[start:end]

       if end == len(text):
           break

       start = end - chunk\_overlap
   ```

   当前结果生成了 3 个文本块，字符范围分别为 `0–49`、`40–89` 和 `80–113`。相邻块之间保留了 10 个字符的重叠。

3. **为文本块增加元数据**

   每个文本块不仅保存正文，还保存编号、来源文件和字符范围。元数据便于后续显示知识来源、定位原文和排查检索问题。

```python
   chunk\_data = {
       "chunk\_id": len(chunks) + 1,
       "source": file\_path.name,
       "start": start,
       "end": end,
       "content": chunk,
   }
   ```

   终端成功显示了每个文本块的编号、来源、字符范围和正文。

4. **将切块结果保存为 JSON**

   使用 `json.dumps()` 将 Python 列表和字典转换为可保存的 JSON 文本。`ensure\_ascii=False` 用于保留正常中文，`indent=2` 用于提高可读性。

```python
   json\_text = json.dumps(
       chunks,
       ensure\_ascii=False,
       indent=2,
   )
   output\_path.write\_text(json\_text, encoding="utf-8")
   ```

   已生成并验证 `04\_showcase/day03\_chunks.json`，文件中包含 3 个结构完整的文本块。

5. **实现关键词检索**

   用户输入问题和关键词后，程序遍历全部文本块，通过 `in` 判断关键词是否存在于正文中，将命中的块加入 `retrieved\_chunks`。

```python
   for chunk\_data in chunks:
       if keyword in chunk\_data\["content"]:
           retrieved\_chunks.append(chunk\_data)
   ```

   使用关键词“蓝色书签”时，程序成功命中文本块 3，并显示其来源和正文。

6. **把检索结果加入提示词**

   将所有命中文本块的 `content` 合并为 `context`，再把外部知识和用户问题共同组成 `prompt`。**这一步对应 RAG 中的 Augmented**，即用检索结果增强原始问题。

```python
   context = "\\n\\n".join(
       chunk\_data\["content"]
       for chunk\_data in retrieved\_chunks
   )

   prompt = f"""
   请只根据下面提供的知识回答用户问题。

   【知识】
   {context}

   【用户问题】
   {question}
   """
   ```

   模型配置继续从项目根目录的 `.env` 读取，没有把 API Key 写进 Python 代码。

7. **完成普通问答与 RAG 问答的对照实验**

   普通问答只把 `question` 发送给 GLM；RAG 问答发送的是包含本地知识的 `prompt`。测试问题为“这个项目的内部测试代号是什么？”。

```python
   # 普通问答
   {"role": "user", "content": question}

   # RAG 问答
   {"role": "user", "content": prompt}
   ```

   普通模型表示无法知道该项目的内部代号，RAG 则根据命中的本地文本块回答“蓝色书签”。在智谱官网的新对话中直接询问同一问题，也得到“不知道内部信息”的结果，进一步验证了差异来自 RAG 提供的本地知识。

8. **当天主要运行命令**

   在项目根目录和 `rag-learning` Conda 环境中运行：

```powershell
   python .\\02\_code\\day03\_chunk.py
   ```

   该命令会重新读取文档、生成切块、覆盖 JSON 结果、进行关键词检索，并调用 GLM 输出普通回答和 RAG 回答。

## 问题与易混点

1. **最后一个文本块不足 50 个字符是否有问题**：Python 切片超过字符串末尾不会报错，最后一块可以短于 `chunk\_size`。`chunk\_size` 表示最大长度，不要求每块长度完全相同。
2. **为什么仍然要使用 `min()`**：`min()` 不是为了防止切片报错，而是让 `end` 表示真实的文档末尾，使 `while` 循环能够准确停止，避免在有重叠时生成一个多余的小块。
3. **三个 `content` 容易混淆**：`chunk\_data\["content"]` 是知识块正文，消息字典中的 `"content": prompt` 是发送给模型的提示词，`response.choices\[0].message.content` 是模型返回的回答正文。

## 明天复习

1. 不看代码，用自己的话解释 `chunk\_size`、`chunk\_overlap` 和 `min()` 分别负责什么。
2. 打开 `day03\_chunks.json`，检查三个文本块的字符范围，并说明为什么相邻文本块存在重复文字。
3. **下一步计划**：学习 Embedding 和语义相似度，让系统不再要求用户手动输入与文档完全相同的关键词。


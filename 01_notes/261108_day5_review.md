# 2026-11-08 · Day 5 复盘

## 今日工作回顾

Day 5 的目标是跑通 Datawhale《All-in-RAG》第 8 章的食谱问答。先用 GLM 跑通问答，在遇到访问量过大的报错后切换到 Gemini，并从终端确认请求返回 `200 OK`。从可乐鸡翅这道题出发，追了一遍食谱从切块、检索、找回完整文档，到进入 `Human:` 提示词的过程。

按计划跑完了 5 道测试题。「西红柿炒鸡蛋」和「推荐几道素菜」分别暴露了上下文长度限制和分类标签的问题。「汽水炖鸡翅」和「Python 列表和元组」在 Day 5 已确认运行，具体输出没有记录在本次复盘所用的日志里。

## 关键步骤与命令

1. **切换模型并启动程序。** 在项目根目录 `.env` 里更新 `LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL`，在 `generation_integration.py` 的 `setup_llm()` 里去掉 GLM 专用的思考参数。Gemini 的 OpenAI 兼容接口地址为 `https://generativelanguage.googleapis.com/v1beta/openai/`。

   当前 PowerShell 找不到 `conda` 命令，最后直接使用 `rag-learning` 环境里的 Python 启动 C8。

   ```powershell
   cd "D:\03Personal\20_CodeStudy\40_Projects\rag-learning\02_code\all-in-rag\code\C8"
   & "D:\03Personal\10_DevTools\20_Python\Miniconda3\envs\rag-learning\python.exe" main.py
   ```

2. **跟踪问题和资料怎么进入提示词。** `detail` 和 `general` 先经过查询重写，搜索用重写步骤返回的问句，最终提示词的 `{question}` 用用户原话。检索命中的是小块，程序用 `parent_id` 找回完整食谱，去重后拼成 `{context}`。详细回答选择非流式输出 `n`，即可看到打印出的提示词。

   ```python
   print(prompt.format(question=query, context=context))
   ```

3. **检查五道题各自测了什么。**

   | 测试题 | 要检查的行为 | 记录 |
   |---|---|---|
   | 可乐鸡翅需要哪些食材？具体怎么做？ | 从检索到最终提示词 | 可乐鸡翅和鸡蛋羹都进了提示词。 |
   | 西红柿炒鸡蛋怎么做？ | 正确食谱能否进入上下文 | 检索找回了正确食谱，但拼接时超出字符限制。 |
   | 推荐几道素菜。 | 列表路由、分类过滤和去重 | 3 个文本块合成 2 道菜，上汤娃娃菜的配料含午餐肉。 |
   | 汽水炖鸡翅怎么做？ | 换一种说法能否找到同一道菜 | Day 5 已运行，详细对照见 Day 6 复盘。 |
   | Python 的列表和元组有什么区别？ | 问题超出菜谱库范围时的表现 | 已确认运行，具体回答未记录。 |

## 问题与易混点

- **搜到了，模型却没有看到。** `_build_context()` 按顺序放入完整食谱，前两份累计 1383 字符，加入第三份后需要 2246 字符。超过 2000 字符时，`break` 会停止拼接，西红柿炒鸡蛋的整份食谱就被留在了提示词外。
- **`list` 模式的大模型调用。** Gemini 负责判断是不是列表问题。后面的检索、按 `category` 筛选、回查和拼菜名都由程序处理。「素菜」在这里是目录分类标签，按这个标签筛选仍可能返回含肉的配方。

## 明天复习

1. 用自己的话讲清楚「找到文档」和 `Human:` 里的「相关食谱信息」有什么区别。
2. 想一想遇到答偏时，分别在检索、上下文和回答这三处看什么。

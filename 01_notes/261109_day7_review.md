# 2026-11-09 · Day 7 复盘

## 今日工作回顾

Day 7 用「可乐鸡翅需要哪些食材？具体怎么做？」把「尝尝咸淡」的核心问答流程串了一遍。先跑原来的交互程序、看终端日志，再回到 `main.py` 对照每一步的输入和输出。重点弄清了为什么检索结果里即使命中的是「操作」子块，最终提示词里也能出现食材：程序会根据子块的 `parent_id` 回查整份食谱。

接着新建并跑通了 `day07_ask_once.py`。这个脚本复用已有的 RAG 系统，只读入一个问题、打印一次答案并退出。最后还查看了本地保存的 FAISS 索引及其配套文件，确认向量和原文分别存在哪里。到这里，「尝尝咸淡」C8 的核心问答复现阶段完成。

## 关键步骤与命令

1. **运行原入口，追踪一轮问答。** 从 `rag-learning` 根目录在 PowerShell 运行：

   ```powershell
   cd .\02_code\all-in-rag\code\C8
   & 'D:\03Personal\10_DevTools\20_Python\Miniconda3\envs\rag-learning\python.exe' .\main.py
   ```

   输入「可乐鸡翅需要哪些食材？具体怎么做？」，流式输出选 `n`。依次查看启动时的索引日志、问题类型和改写日志、命中的子块、回查的食谱，以及提示词中的「相关食谱信息」。

2. **对照 `main.py` 里的三个调用，梳理启动和提问两个阶段。**

   | 调用 | 做了什么 |
   |---|---|
   | `initialize_system()` | 初始化数据准备、索引和生成模块 |
   | `build_knowledge_base()` | 加载已有 FAISS 索引，或构建并保存新索引。读取并切分食谱，准备 BM25 和父文档回查所需的资料，再创建检索模块 |
   | `ask_question()` | 判断问题类型，按需改写问句，检索子块，再回查完整食谱。详细问答会把原问题和食谱资料填进提示词，交给大模型回答 |

   查看子块回查时，去 `rag_modules/data_preparation.py` 找 `get_parent_documents()`。同一份食谱命中多块时，只返回一份原文，并把命中块数用于父文档排序。要看实际提示词，去 `rag_modules/generation_integration.py` 找 `generate_step_by_step_answer()` 和 `_build_context()`。

3. **运行单次问答脚本。** 脚本在 `C8/day07_ask_once.py`，核心调用如下：

   ```python
   from main import RecipeRAGSystem

   rag = RecipeRAGSystem()
   rag.initialize_system()
   rag.build_knowledge_base()
   answer = rag.ask_question(question, stream=False)
   print(answer)
   ```

   完整脚本先用 `input()` 读取 `question`，并在 `if __name__ == "__main__":` 下执行。在 `C8` 目录运行：

   ```powershell
   & 'D:\03Personal\10_DevTools\20_Python\Miniconda3\envs\rag-learning\python.exe' .\day07_ask_once.py
   ```

   已用可乐鸡翅的问题跑通。成功时打印一次答案，然后回到 PowerShell 提示符。

4. **查看实际保存的向量索引。** `C8/vector_index/index.faiss` 里有 1,764 个 512 维向量，索引类型是 `IndexFlatL2`。`index.pkl` 保存向量编号到文档的映射，以及文本块正文和元数据。实查第 0 条向量以 `[0.01927, -0.02070, 0.00608, 0.01854, …]` 开头，对应「咖喱炒蟹的做法」主标题块。提问时，向量检索把问句转成同样维度的向量，按距离找到候选编号，再取回对应子块。

## 问题与易混点

- **两个模块怎么分工。** `self.retrieval_module` 负责找子块。`self.generation_module` 负责问题路由、按需改写和组织答案。`self.data_module` 负责从命中的子块回查完整食谱。
- **加载索引后为什么还在切块。** 旧索引可以复用已经算好的食谱向量。BM25 仍需要本次加载的文本块，父文档回查仍需要原始食谱，新的问句也要单独计算向量。

## 明天复习

1. 用 30 秒复述可乐鸡翅问答：从子块怎么找到整份食谱，食材又是怎么进入提示词的？
2. 不看笔记，说出单次问答脚本中三个函数的调用顺序，并分别解释它们准备了什么。
3. 打开 `main.py`，指出准备知识库和处理问题的两个入口。面试展开时，用一次真实日志说明检索命中了什么，以及模型实际收到了什么。

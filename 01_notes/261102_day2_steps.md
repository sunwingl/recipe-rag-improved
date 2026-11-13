# Day 2 操作步骤：让 Python 调用大模型

## 目标

让电脑上的 Python 程序向智谱服务器上的模型提问，接收回答，再显示在终端。之后改变提示词，观察回答怎样变化。

```text
填写配置 → Python 发送问题 → 智谱模型生成回答 → Python 显示结果
```

本文按最终跑通的智谱方案整理。Day 1 的环境和项目依赖已经准备好，直接沿用。Kimi 测试与历史报错见 [Day 2 实验记录](D:/03Personal/20_CodeStudy/40_Projects/rag-learning/01_notes/day02.md)。

## 第 1 步：进入环境和项目目录

打开 Windows 开始菜单中的 **Anaconda Prompt**，逐条执行：

```text
conda activate rag-learning
```

* `conda`：环境管理工具。
* `activate`：启用指定环境。
* `rag-learning`：Day 1 创建的环境名称。
* 启用后，提示符前面应显示 `(rag-learning)`。

```text
cd /d "D:\\03Personal\\20\_CodeStudy\\40\_Projects\\rag-learning"
```

* `cd`：切换当前目录。
* `/d`：同时切换盘符，适用于 Anaconda Prompt 使用的 CMD。
* 引号中的路径：项目总文件夹。

后续命令都从这个项目总目录执行。

## 第 2 步：创建智谱密钥，保存本地配置

1. 登录 [智谱 BigModel 国内站的 API Key 管理页](https://bigmodel.cn/usercenter/proj-mgmt/apikeys)。
2. 按平台要求完成账号开通，创建标准 API Key，名称可以填 `rag-learning`。
3. 密钥用于验证身份；具体使用哪个模型，稍后由代码中的 `model` 参数指定。

在 Anaconda Prompt 执行：

```text
notepad .env
```

`notepad` 用记事本打开当前目录的 `.env` 文件；不存在时创建它。

填写以下配置，将第一行中文替换为自己的智谱 API Key。已有同名项时修改原值，避免重复填写：

```dotenv
LLM\_API\_KEY=在这里粘贴你的智谱密钥
LLM\_BASE\_URL=https://open.bigmodel.cn/api/paas/v4/
LLM\_MODEL=glm-4.7-flash
```

|配置项|回答的问题|
|-|-|
|`LLM\_API\_KEY`|我是谁，用哪个账号访问？|
|`LLM\_BASE\_URL`|请求发给哪家服务？|
|`LLM\_MODEL`|这次使用哪个模型？|

按 **Ctrl + S** 保存。确认实际文件名是 `.env`，保存在项目总目录，且文件中有内容。真实密钥只填在本地，不写进代码、学习笔记或聊天。

本次使用的 `glm-4.7-flash` 在 [智谱模型概览](https://docs.bigmodel.cn/cn/guide/start/model-overview) 中标注为免费文本模型，账号实际可用性通过下一步请求验证。

## 第 3 步：创建模型调用脚本

执行：

```text
notepad .\\02\_code\\day02\_glm\_test.py
```

* `notepad`：用记事本编辑文件。
* `.\\`：从终端当前目录开始。
* `02\_code\\day02\_glm\_test.py`：代码文件夹中的 Python 文件。

下面是当前脚本的完整版本。已有文件可对照阅读；保留自己需要的实验记录。

```python
from pathlib import Path
from dotenv import dotenv\_values
from openai import OpenAI, APITimeoutError, APIConnectionError, APIStatusError

# 读取项目总目录中的配置
env\_path = Path(\_\_file\_\_).resolve().parent.parent / ".env"
config = dotenv\_values(env\_path, encoding="utf-8-sig")

# 创建连接智谱的客户端
client = OpenAI(
    api\_key=config\["LLM\_API\_KEY"],
    base\_url=config\["LLM\_BASE\_URL"],
    timeout=120,
    max\_retries=0,
)

# 发送消息，等待模型返回结果
print("正在等待模型回答……", flush=True)
try:
    response = client.chat.completions.create(
        model=config\["LLM\_MODEL"],
        messages=\[
            {"role": "user", "content": "Python 列表有什么用？"}
        ],
        max\_tokens=512,
        extra\_body={"thinking": {"type": "disabled"}},
    )
except APITimeoutError:
    raise SystemExit("读取模型响应超时。本次没有获得完整回答，请稍后再试。")
except APIConnectionError:
    raise SystemExit("连接模型服务失败，请检查网络后再试。")
except APIStatusError as error:
    if error.status\_code == 429:
        raise SystemExit(f"服务返回 429，请稍后再试。错误详情：{error.message}")
    raise SystemExit(f"请求失败，HTTP {error.status\_code}。错误详情：{error.message}")

# 显示回答与用量
print("模型回答：", response.choices\[0].message.content)
print("Token 用量：", response.usage)
print("结束原因：", response.choices\[0].finish\_reason)
```

按 **Ctrl + S** 保存。

### 先按四段理解代码

|代码段|在做什么|
|-|-|
|`from ... import ...`|引入路径处理、配置读取和 API 客户端工具。|
|`env\_path`、`dotenv\_values(...)`|找到并读取项目根目录的 `.env`，将配置存入字典。|
|`client = OpenAI(...)`|根据 API Key 和地址准备客户端；此时还没有向模型提问。|
|`client.chat.completions.create(...)`|发出模型请求，返回结果存入 `response`，最后打印回答。|

`\_\_file\_\_` 是当前脚本的位置，`resolve()` 得到绝对路径，两个 `.parent` 依次取父目录 `02\_code` 和项目总目录，再用 `/ ".env"` 拼出配置文件路径。

虽然客户端类叫 `OpenAI`，本次实际服务提供方由智谱的 `base\_url` 决定，使用的是智谱密钥和模型。[智谱官方兼容接口说明](https://docs.bigmodel.cn/cn/guide/develop/openai/introduction)

### 认识调用参数

|参数或表达式|含义|
|-|-|
|`model=config\["LLM\_MODEL"]`|从配置读取本次使用的模型名称。|
|`messages`|发给模型的消息列表，包含角色与内容。|
|`role="user"`|当前消息是用户提出的问题。|
|`content`|消息正文。|
|`max\_tokens=512`|限制生成的 token 数；输入 token 另计。|
|`thinking: disabled`|关闭本次请求的思考模式。|
|`timeout=120`|客户端的超时设置；较长等待仍可能超时。|
|`max\_retries=0`|失败后不自动重试。|
|`response.choices\[0].message.content`|取出第一个候选回答的正文。|
|`response.usage`|本次调用的 token 用量。|
|`response.choices\[0].finish\_reason`|模型停止生成的原因。|

`try` 中执行请求；`except` 在遇到指定错误时显示简短提示；`SystemExit` 结束本次程序运行。

## 第 4 步：运行，查看请求结果

```text
python .\\02\_code\\day02\_glm\_test.py
```

* `python`：使用当前 Conda 环境中的 Python。
* 后面的路径：指定要执行的程序。

查看三个输出：

1. **模型回答**：实际返回的文字，内容可能每次不同。
2. **Token 用量**：输入、输出、合计等统计。
3. **结束原因**：`stop` 表示正常结束；`length` 表示达到了生成上限，正文可能被截断。

如果输出为空，检查 token 用量和结束原因。本次练习关闭思考，避免有限的生成额度被思考占用。

## 第 5 步：对同一个问题增加回答规则

第 3 步代码只有一条 `user` 消息，先记录它的回答。

然后将 `messages` 参数替换为以下内容，其他调用参数保持一致：

```python
        messages=\[
            {
                "role": "system",
                "content": "你是一名 Python 入门老师。请用中文回答，只写三条编号短句，每条不超过25字，并包含一个生活中的类比。",
            },
            {
                "role": "user",
                "content": "Python 列表有什么用？",
            },
        ],
```

* `system` 消息：设定角色、格式、长度等回答规则。
* `user` 消息：保持同一个问题，便于观察添加规则后的差异。

保存后，再执行同一条运行命令：

```text
python .\\02\_code\\day02\_glm\_test.py
```

这条命令仍然是运行同一个文件，此时执行的是刚保存的新内容。

比较：是否变成三条编号短句、是否出现生活类比、回答长度和 token 用量怎样变化。提示词是对模型的要求，需要检查它实际是否遵守。

## 第 6 步：记录结论，完成 Day 2 验收

本次已经得到的记录：

|消息设置|表现|输入 token|输出 token|结束原因|
|-|-|-:|-:|-|
|只有 user 问题，用户运行|多个小节，写到上限被截断|12|512|`length`|
|system 规则 + 同一个 user 问题，助手实测|三条简短编号回答|44|31|`stop`|

本次观察：system 规则让回答更短、更符合指定格式。两次都是成功获得模型响应，其中无规则的一次正文被截断。

用自己的话解释以下三件事，作为理解自查：

1. **Python 和模型各自做什么？** Python 发请求、收结果、显示文字；服务器上的模型生成回答。
2. **请求里放什么？** 选择模型、消息、输出上限与思考开关，并使用 API Key 验证身份。
3. **添加 system 消息有什么作用？** 向模型提出回答规则，可能改变格式、长度和表达方式。

操作与实验结果已记录；理解验收以能解释以上三件事为准。

## 常见问题速查

|现象|判断与处理|
|-|-|
|配置项 `KeyError`|打开项目根目录的 `.env`，核对名称、内容是否保存。|
|`429`，业务码 `1305`|模型当前访问量过大，稍后再试；不连续重复发送。|
|`APITimeoutError`|本次等待响应超时；增加等待时间不保证解决网络或平台问题。|
|`finish\_reason=length`|达到了生成上限，检查正文是否被截断。|

官方参考：[思考模式](https://docs.bigmodel.cn/cn/guide/capabilities/thinking-mode)、[错误码](https://docs.bigmodel.cn/cn/api/api-code)。

Day 2 的操作到此结束。文档加载、分块、向量检索留给后续对应天数。


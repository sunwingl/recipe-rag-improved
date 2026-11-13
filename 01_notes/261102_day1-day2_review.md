# Day 1 + Day 2 合并复盘

## 今日工作回顾

本次根据当前可见记录整理，合并回顾 Day 1 和 Day 2。

Day 1 解决的是“让项目能在自己的电脑上运行”。你建立项目目录、下载 all-in-rag 仓库，安装 Miniconda，建立并进入 rag-learning 独立环境，安装依赖，再查看 C8 的配置和主程序。先准备工具与环境，再认识代码和资料的位置，后面的运行与排错才有依据。

Day 2 解决的是“让自己的 Python 程序向大模型提问并取得回答”。你先尝试 Kimi，遇到配置和模型访问问题，随后改用智谱 GLM 成功获得回答，并比较不同提示词下的回答格式、长度和 token 用量。到这两个阶段结束时，环境与独立模型调用已经跑通；概念是否理解，仍需以能用自己的话解释为准。

## 关键步骤与命令

### Day 1：准备环境，认识项目

1. **安排项目目录并下载原项目。**

   项目总目录是 `D:\\03Personal\\20\_CodeStudy\\40\_Projects\\rag-learning`。`01\_notes` 存笔记，`02\_code` 存代码，`03\_materials` 存参考资料，`04\_showcase` 存展示成果。原项目位于 `02\_code\\all-in-rag`，本阶段关注其中的 C8 菜谱问答项目。

   下载或克隆的具体命令未记录，不补写为当天执行事实。结果是本地已有原项目代码、教程和菜谱资料。

2. **安装 Miniconda，创建独立环境并安装依赖。**

   Miniconda 用来管理 Python 环境。独立环境把本项目使用的 Python 和第三方库放在一起，便于确认运行时使用哪些工具。

   安装位置是 `D:\\03Personal\\10\_DevTools\\20\_Python\\Miniconda3`，项目环境名称是 `rag-learning`。安装器选项、创建环境及安装依赖的完整命令未记录；此处不补造版本和安装输出。

   以下是**复习参考命令（非当天逐条执行记录）**，在 Windows 开始菜单打开 Anaconda Prompt 后使用：

```cmd
   conda activate rag-learning
   ```

   `conda` 是环境管理工具，`activate` 表示启用，`rag-learning` 是要启用的环境。成功后，终端提示符前面显示 `(rag-learning)`。

```cmd
   cd /d "D:\\03Personal\\20\_CodeStudy\\40\_Projects\\rag-learning"
   ```

   `cd` 切换当前目录；`/d` 同时切换盘符，适用于 Anaconda Prompt 使用的 CMD；引号中是项目总目录。启用环境与进入文件夹是两件事：前者选择运行工具，后者决定相对路径从哪里开始。

3. **检查 Python，并做了文件读取等入门练习。**

   `day01.py` 中使用以下代码显示当前运行程序的 Python 位置：

```python
   import sys
   print(sys.executable)
   ```

   `import sys` 引入系统信息工具；`sys.executable` 是当前 Python 程序的路径；`print` 把它显示出来。检查结果时，应关注路径是否指向 Miniconda 的 `envs\\rag-learning` 环境，而不只看程序有没有输出。

   现有练习还包括读取 `03\_materials\\rag\_intro.txt`、按关键词查找文本行，以及将找到的资料和问题拼成提示词。它们分别保存在 `02\_code` 下的 `day01\_read.py`、`day01\_search.py`、`day01\_prompt.py`。这些文件保留了入门练习过程，不能据此认定完整 C8 系统已运行成功。

4. **查看配置与主程序结构。**

   你查看了 C8 配置及入口，认识了代码、数据、配置之间的关系。

|内容|位置（相对于 all-in-rag 仓库）|负责什么|
|-|-|-|
|原始菜谱|`data/C8/cook`|提供后续检索和回答使用的资料|
|配置|<br />`code/C8/config.py`|指定资料路径、模型、检索数量等参数|
|主程序|`code/C8/main.py`|组织初始化、建库和问答流程|
|依赖清单|`code/C8/requirements.txt`|列出项目需要的第三方库|

   主程序中的 `initialize\_system`、`build\_knowledge\_base`、`ask\_question` 分别对应初始化、建立知识库和提问。Day 1 的重点是能找到这些位置，并确认使用哪个 Python 环境。

### Day 2：连接模型，观察请求与回答

1. **尝试 Kimi，随后选择智谱完成练习。**

   最初运行 `02\_code\\day02\_kimi\_test.py` 时，出现 `KeyError: 'MOONSHOT\_API\_KEY'`；补充配置后，又收到模型不存在或无权限的 404 响应。这次 Kimi 调用没有成功，随后使用智谱 `glm-4.7-flash` 完成独立模型调用。

   API 可以理解为程序请求模型服务的入口。API Key 用于验证账号身份；使用哪个模型，由请求的 `model` 参数指定。

2. **把连接信息保存在项目根目录的 .env 中。**

   本次智谱脚本读取以下三项配置，真实密钥不写入本复盘：

```dotenv
   LLM\_API\_KEY=自己的智谱密钥
   LLM\_BASE\_URL=https://open.bigmodel.cn/api/paas/v4/
   LLM\_MODEL=glm-4.7-flash
   ```

   三项分别表示“使用哪个账号”“请求发到哪里”“使用哪个模型”。判断配置是否有效，需要实际请求结果，文件存在本身不代表配置正确。

3. **编写读取配置和连接服务的代码。**

   当前练习文件是 [day02\_glm\_test.py](../02_code/day02_glm_test.py)。读取配置的关键片段如下：

```python
   env\_path = Path(\_\_file\_\_).resolve().parent.parent / ".env"
   config = dotenv\_values(env\_path, encoding="utf-8-sig")
   ```

   `\_\_file\_\_` 表示当前脚本，`resolve()` 得到绝对路径，两个 `.parent` 从脚本向上找到项目总目录，最后拼出 `.env` 的位置。`dotenv\_values` 读取配置并保存为字典。

```python
   client = OpenAI(
       api\_key=config\["LLM\_API\_KEY"],
       base\_url=config\["LLM\_BASE\_URL"],
       timeout=120,
       max\_retries=0,
   )
   ```

   这段代码准备客户端：填写密钥、服务地址，设置超时，并关闭自动重试。客户端类虽然叫 `OpenAI`，本次实际请求地址是智谱；准备客户端时尚未向模型提问。

4. **发送问题，接收并显示回答。**

   关键请求片段如下：

```python
   response = client.chat.completions.create(
       model=config\["LLM\_MODEL"],
       messages=\[
           {"role": "user", "content": "Python 列表有什么用？"}
       ],
       max\_tokens=512,
       extra\_body={"thinking": {"type": "disabled"}},
   )
   ```

   `model` 选择模型；`messages` 是消息列表；`user` 表示用户提问；`content` 是正文；`max\_tokens` 限制生成量；最后一项关闭本次请求的思考模式。返回结果保存在 `response` 中。

   你在项目总目录、`rag-learning` 环境中实际运行过：

```cmd
   python .\\02\_code\\day02\_glm\_test.py
   ```

   `python` 使用当前环境中的 Python；`.\\` 从当前目录开始；后面的路径指定要运行的脚本。程序成功显示过“连接成功”，也成功回答过“Python 列表有什么用？”。

```python
   print(response.choices\[0].message.content)
   print(response.usage)
   print(response.choices\[0].finish\_reason)
   ```

   这三行分别显示回答正文、token 用量和结束原因。Python 负责发送请求、接收结果和显示文字，服务器上的模型负责生成回答。

5. **修改提示词，比较回答格式与长度。**

   对同一个问题，可以在消息列表前加上 `system` 规则：

```python
   {
       "role": "system",
       "content": "你是一名 Python 入门老师。请用中文回答，只写三条编号短句，每条不超过25字，并包含一个生活中的类比。",
   }
   ```

   `system` 用于提出回答规则，`user` 放具体问题。修改后保存，再执行同一条运行命令，运行的就是新内容。

   可见记录中的结果是：你运行的无规则版本输入 12 个 token、生成 512 个 token，结束原因为 `length`，回答末尾被截断；助手实测的带规则版本输入 44 个 token、生成 31 个 token，返回三条简短编号回答，结束原因为 `stop`。这些是本次观察结果，不保证每次生成都完全相同。

   Day 2 的“Python 列表”只是测试问题。学习重点是理解一次模型调用如何配置、发送、返回，以及提示词怎样影响回答。更完整的重做步骤见 [Day 2 操作步骤](day02_steps.md)。

## 问题与易混点

1. **配置错误与模型访问错误是不同问题。** `KeyError` 出现在读取本地配置时；Kimi 的 404 是服务端返回模型不存在或无权限。补好密钥配置后，并不代表账号一定能使用某个模型。本次最终使用智谱取得了回答，Kimi 未成功。
2. **模型繁忙与等待超时。** 智谱曾返回 `429`、业务码 `1305`，消息明确表示模型访问量过大；另一次出现 `APITimeoutError`，表示等待响应超时，具体原因没有完全确认。脚本随后增加了超时设置和简短错误提示，后续调用成功，但延长等待时间不能保证消除平台繁忙。
3. **有响应不等于回答完整。** 早期曾出现生成用量接近上限、思考 token 较多而正文为空的情况；后来关闭思考模式后获得正文。最后一次截图明确显示 `length`，说明生成达到上限；`stop` 表示正常结束。Token 是模型处理文本的计量单位，不等于汉字数，`max\_tokens=512` 限制生成部分，输入 token 另计。

## 明天复习

用 5–10 分钟完成以下回忆，不需要重新安装或重复调用 API：

1. 解释“启用 Conda 环境”和“切换项目目录”分别决定什么，并回忆项目的代码、资料、配置位置。
2. 用自己的话说出 `.env` 的三项配置，以及 `system`、`user` 各自负责什么。
3. 画出“Python 发送请求 → 模型生成回答 → Python 显示结果”，再说明 token 用量与 `finish\_reason` 能帮助检查什么。

本复盘只覆盖 Day 1、Day 2；后续阶段的成果与当前进度以对应学习记录为准。


from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI, APITimeoutError, APIConnectionError, APIStatusError

# 读取项目总目录中的配置
env_path = Path(__file__).resolve().parent.parent / ".env"
config = dotenv_values(env_path, encoding="utf-8-sig")

# 创建连接智谱的客户端
client = OpenAI(
    api_key=config["LLM_API_KEY"],
    base_url=config["LLM_BASE_URL"],
    timeout=120,
    max_retries=0,
)

# 发送消息，等待模型返回结果
print("正在等待模型回答……", flush=True)
try:
    response = client.chat.completions.create(
        model=config["LLM_MODEL"],
        messages=[ 
            {"role": "user", "content": "Python 列表有什么用？"}
        ],
        max_tokens=512,
        extra_body={"thinking": {"type": "disabled"}},
    )
except APITimeoutError:
    raise SystemExit("读取模型响应超时。本次没有获得完整回答，请稍后再试。")
except APIConnectionError:
    raise SystemExit("连接模型服务失败，请检查网络后再试。")
except APIStatusError as error:
    if error.status_code == 429:
        raise SystemExit(f"服务返回 429，请稍后再试。错误详情：{error.message}")
    raise SystemExit(f"请求失败，HTTP {error.status_code}。错误详情：{error.message}")

# 显示回答与用量
print("模型回答：", response.choices[0].message.content)
print("Token 用量：", response.usage)
print("结束原因：", response.choices[0].finish_reason)

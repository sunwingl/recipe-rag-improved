from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI

# 读取项目总目录中的配置文件
env_path = Path(__file__).resolve().parent.parent / ".env"
config = dotenv_values(env_path)

# 创建连接 Kimi 的客户端
client = OpenAI(
    api_key=config["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.cn/v1",
    timeout=30,
    max_retries=0,
)

# 发送一次简短请求
response = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[
        {"role": "user", "content": "请只回复：连接成功"}
    ],
    max_tokens=128,
    extra_body={"thinking": {"type": "disabled"}},
)

# 显示模型回答
print(response.choices[0].message.content)
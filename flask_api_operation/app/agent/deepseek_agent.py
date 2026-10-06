import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
    return _client


def _chat(prompt: str, system: str = "") -> str:
    client = _get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.8,
    )
    return resp.choices[0].message.content or ""


# 热词搜索：根据用户主题生成板块和标题
def hot_topic(question: str) -> str:
    return _chat(
        prompt=question,
        system="你是一个小红书运营专家，根据用户主题生成5个内容板块，每个板块给出10个吸引人的小红书标题。输出格式为JSON。",
    )


# 根据标题进行内容创作
def content_creation(title_text: str) -> str:
    return _chat(
        prompt=f"请为以下小红书标题写一篇完整的笔记文案：{title_text}",
        system="你是一个小红书爆款文案写手，风格轻松自然，多用emoji和口语化表达，800字左右。",
    )


# 根据小红书笔记URL提取笔记数据
def fetch_xhs_note(xhs_url: str) -> str:
    return _chat(
        prompt=f"请分析这个小红书笔记：{xhs_url}",
        system="你是一个小红书数据分析助手。",
    )

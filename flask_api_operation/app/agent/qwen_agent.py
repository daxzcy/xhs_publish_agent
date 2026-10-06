import os
import logging
import dashscope
from dashscope import MultiModalConversation
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 阿里百炼调用模型路径
dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

# 构建生成图片提示词
# title:文章标题
# style_description:风格描述文本
# include_text:是否包含文字
def generate_cover_prompt(
    title: str,
    style_description: str,
    include_text: bool = False,
) -> str:
    # 提示词部分
    prompt_parts = []

    # 1.风格描述
    prompt_parts.append(style_description)

    # 2.画面主体
    prompt_parts.append(f"画面主体内容与 {title} 相关")

    # 3.文字处理
    if include_text:
        prompt_parts.append(
            f"必须包含清晰准确的标题文字：{title}。"
            "文字要求：使用醒目的粗体无衬线字体，文字居中排列，"
            "文字颜色与背景形成强烈对比，文字边缘清晰锐利，"
            "无变形无模糊，确保每个汉字都完整正确显示，"
            "文字区域干净整洁，无干扰元素"
            "重要：标题文字必须完整、准确、清晰，"
            "不能出现错别字、缺字、乱码、字体变形或模糊"
        )
    else:
        prompt_parts.append(
            "画面中绝对不能出现任何文字，包括标题、数字、符号、字母。"
            "只使用图形、图标、插画和形状来表达主题。"
            "画面干净整洁，没有任何文字元素"
        )

    # 4.质量要求
    prompt_parts.append("高清画质，细节丰富，适合做文章封面图")

    # 5.组装提示词
    full_prompt = "。".join(prompt_parts)

    # 返回
    return full_prompt

# 生成图片，使用阿里云百炼生成图片，成功时返回图片URL
# prompt:提示词
# n:生成图片数量
# size:图片尺寸
# prompt_extend:是否扩展提示词
# wartermark:是否添加水印
# model:模型名称
def generate_image(
    prompt: str,
    n: int = 1,
    size: str = "960*1696",
    prompt_extend : bool = False,
    wartermark : bool = False,
    model: str = "qwen-image-2.0-pro",
) -> str | None:
    # 密钥
    api_key = os.getenv("QWEN_KEY")

    # 负向提示词
    negative_prompt = (
        "模糊，变形，扭曲，低质量，像素化，噪点，"
        "血腥暴力，色情，政治敏感，品牌标识，"
        "多余人脸，多余肢体，解剖错误"
    ) 
    
    # 调用模型
    messages = [
        {
            "role": "user",
            "content": [
                {"text": prompt}
            ]
        }
    ]

    response = MultiModalConversation.call(
        api_key=api_key,
        model=model,
        messages=messages,
        watermark=wartermark,
        prompt_extend=prompt_extend,
        negative_prompt=negative_prompt,
        size=size,
        n=n
    )
    
    # 解析模型返回数据
    if response.status_code != 200:
        logger.error(
            f"生成图片失败：status_code: {response.status_code}"
            f"code: {response.code},message: {response.message}"
        )
        return None

    # 返回图片URL
    return response['output']['choices'][0]['message']['content'][0]['image']
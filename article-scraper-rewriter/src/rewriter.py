"""内容润色模块 - 调用 LLM API"""

import json
from typing import Dict
from src.utils import create_llm_client


REWRITE_PROMPT_TEMPLATE = """请对以下文章内容进行专业润色，要求：
1. 保持原意和关键信息完整
2. 修正语法、拼写、标点错误
3. 优化句式结构，提升流畅度和专业性
4. 段落划分合理，层次清晰
5. 不要添加原文没有的新内容
6. 输出纯文本，保持段落用两个换行分隔
{language_hint}

原文标题：{title}
原文内容：
{content}

请返回润色后的标题和正文，格式如下：
【标题】
润色后的标题
【正文】
润色后的正文"""


def rewrite_content(title: str, content: str, config: Dict, language: str = "auto") -> Dict[str, str]:
    """
    调用 LLM 润色标题和正文
    
    Returns:
        {"title": str, "content": str}
    """
    client = create_llm_client(config)
    
    language_hint = ""
    if language != "auto":
        language_hint = f"\n文章语言：{language}"
    
    prompt = REWRITE_PROMPT_TEMPLATE.format(
        title=title,
        content=content,
        language_hint=language_hint
    )
    
    try:
        response = client.chat(prompt)
        return parse_rewrite_response(response)
    except Exception as e:
        print(f"LLM 润色失败，返回原始内容: {e}")
        # 降级：返回原始内容
        return {"title": title, "content": content}


def parse_rewrite_response(response: str) -> Dict[str, str]:
    """解析 LLM 返回的润色结果"""
    # 尝试提取标题部分
    title = ""
    content = response
    
    if "【标题】" in response:
        parts = response.split("【标题】", 1)
        if len(parts) > 1:
            after_title = parts[1]
            if "【正文】" in after_title:
                title_part, content_part = after_title.split("【正文】", 1)
                title = title_part.strip()
                content = content_part.strip()
            else:
                lines = after_title.strip().split("\n", 1)
                title = lines[0].strip()
                content = lines[1].strip() if len(lines) > 1 else ""
    elif "标题：" in response:
        # 兼容中文冒号
        parts = response.split("标题：", 1)
        if len(parts) > 1:
            rest = parts[1]
            if "正文：" in rest:
                title_part, content_part = rest.split("正文：", 1)
                title = title_part.strip()
                content = content_part.strip()
    
    # 清理标题中可能的多余符号
    title = title.replace("【", "").replace("】", "").strip()
    
    return {
        "title": title if title else "未提取到标题",
        "content": content if content else response
    }
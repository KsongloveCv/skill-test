"""关键词和标签提取模块"""

from typing import Dict, List
from src.utils import create_llm_client


EXTRACT_PROMPT_TEMPLATE = """请根据以下文章内容，提取：
1. {max_keywords} 个关键词（2-4 个词的短语，反映核心主题）
2. {max_tags} 个标签（1-2 个词的分类词或热门话题）

要求：
- 关键词和标签都使用英文逗号分隔
- 关键词和标签不要重复
- 只输出最终的逗号分隔列表，不要其他解释

文章内容：
{content}

输出格式示例：
关键词1,关键词2,关键词3
标签1,标签2"""


def extract_keywords_tags(
    content: str,
    config: Dict,
    max_keywords: int = 5,
    max_tags: int = 3
) -> Dict[str, List[str]]:
    """
    提取关键词和标签
    
    Returns:
        {"keywords": [...], "tags": [...]}
    """
    client = create_llm_client(config)
    
    prompt = EXTRACT_PROMPT_TEMPLATE.format(
        max_keywords=max_keywords,
        max_tags=max_tags,
        content=content  # 限制长度，避免超出 token 限制
    )
    
    try:
        response = client.chat(prompt)
        return parse_extract_response(response, max_keywords, max_tags)
    except Exception as e:
        print(f"关键词提取失败: {e}")
        return {"keywords": ["文章", "内容"], "tags": ["未分类"]}


def parse_extract_response(response: str, max_keywords: int, max_tags: int) -> Dict[str, List[str]]:
    """解析 LLM 返回的关键词和标签"""
    lines = response.strip().split("\n")
    
    keywords = []
    tags = []
    
    if len(lines) >= 2:
        # 第一行应该是关键词
        kw_line = lines[0].strip()
        keywords = [kw.strip() for kw in kw_line.split(",") if kw.strip()]
        
        # 第二行应该是标签
        tag_line = lines[1].strip()
        tags = [tag.strip() for tag in tag_line.split(",") if tag.strip()]
    
    # 如果解析失败，尝试按逗号分割整段文本
    if not keywords and not tags:
        parts = response.split("\n")
        for part in parts:
            if "关键词" in part or "keyword" in part.lower():
                kw_part = part.split("：")[-1] if "：" in part else part.split(":")[-1]
                keywords = [k.strip() for k in kw_part.split(",") if k.strip()]
            elif "标签" in part or "tag" in part.lower():
                tag_part = part.split("：")[-1] if "：" in part else part.split(":")[-1]
                tags = [t.strip() for t in tag_part.split(",") if t.strip()]
    
    # 限制数量并补齐
    keywords = keywords[:max_keywords] if keywords else ["文章", "内容", "资讯"]
    tags = tags[:max_tags] if tags else ["未分类"]
    
    return {"keywords": keywords, "tags": tags}
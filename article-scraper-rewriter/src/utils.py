"""工具函数模块"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI


def load_config(config_path: str = "config.yaml") -> Dict:
    """加载 YAML 配置文件"""
    path = Path(config_path)
    if not path.exists():
        # 尝试从环境变量构建默认配置
        return {
            "llm": {
                "provider": os.getenv("LLM_PROVIDER", "openai"),
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "model": os.getenv("LLM_MODEL", "gpt-4"),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            },
            "scraping": {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "timeout": 30,
                "retry": 3,
                "delay": 1
            },
            "defaults": {
                "max_keywords": 5,
                "max_tags": 3,
                "language": "auto"
            }
        }
    
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class LLMClient:
    """LLM API 客户端封装"""
    
    def __init__(self, config: Dict):
        self.config = config.get("llm", {})
        self.provider = self.config.get("provider", "openai")
        
        if self.provider == "deepseek":
            self.client = OpenAI(
                api_key=self.config.get("api_key"),
                base_url=self.config.get("base_url", "https://api.openai.com/v1")
            )
            self.model = self.config.get("model", "gpt-4")
        elif self.provider == "azure":
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=self.config.get("api_key"),
                azure_endpoint=self.config.get("endpoint"),
                api_version=self.config.get("api_version", "2024-02-15-preview")
            )
            self.model = self.config.get("deployment", "gpt-4")
        elif self.provider == "ollama":
            self.client = OpenAI(
                base_url=self.config.get("base_url", "http://localhost:11434/v1"),
                api_key="ollama"
            )
            self.model = self.config.get("model", "llama3")
        else:
            raise ValueError(f"不支持的 LLM 提供商: {self.provider}")
    
    def chat(self, prompt: str) -> str:
        """发送对话请求"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            extra_body={"thinking": {"type": "enabled"}}
        )
        return response.choices[0].message.content


def create_llm_client(config: Dict) -> LLMClient:
    """创建 LLM 客户端实例"""
    return LLMClient(config)


def format_output(title: str, content: str, keywords: List[str], tags: List[str], url: str) -> str:
    """格式化最终输出"""
    output = f"【标题】\n{title}\n\n"
    output += f"【正文】\n{content}\n\n"
    output += f"【关键词】\n{','.join(keywords)}\n\n"
    output += f"【标签】\n{','.join(tags)}"
    output += f"【原文链接】\n{url}\n\n"
    return output
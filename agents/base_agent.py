"""
基础Agent类
参考 AutoGen 框架的多智能体设计模式
"""
import os
import httpx
from openai import OpenAI
from config import AI_CONFIG

# 清除可能导致问题的代理环境变量
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(key, None)


class BaseAgent:
    """基础Agent类，所有专业Agent的父类"""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.client = None
        self.conversation_history = []
    
    def _get_client(self):
        """获取OpenAI客户端"""
        if self.client is None:
            # 创建不使用代理的 httpx 客户端，增加超时时间
            http_client = httpx.Client(
                timeout=httpx.Timeout(300.0, connect=30.0),  # 5分钟超时
                follow_redirects=True
            )
            self.client = OpenAI(
                api_key=AI_CONFIG["api_key"],
                base_url=AI_CONFIG["api_base"],
                http_client=http_client,
                timeout=300.0  # 5分钟
            )
        return self.client
    
    def chat(self, message: str, temperature: float = None) -> str:
        """与Agent对话"""
        client = self._get_client()
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history,
            {"role": "user", "content": message}
        ]
        
        response = client.chat.completions.create(
            model=AI_CONFIG["model"],
            messages=messages,
            temperature=temperature or AI_CONFIG["temperature"],
            max_tokens=AI_CONFIG["max_tokens"]
        )
        
        assistant_message = response.choices[0].message.content
        
        # 保存对话历史
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def reset(self):
        """重置对话历史"""
        self.conversation_history = []
        self.client = None

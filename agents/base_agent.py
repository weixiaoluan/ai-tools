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


# 全局共享的HTTP客户端（连接池复用）
_shared_http_client = None
_shared_openai_client = None

def get_shared_client():
    """获取共享的OpenAI客户端（连接池复用）"""
    global _shared_http_client, _shared_openai_client
    
    # 检查API配置是否变化，如果变化则重建客户端
    current_key = AI_CONFIG.get("api_key", "")
    current_base = AI_CONFIG.get("api_base", "")
    
    if _shared_openai_client is None or \
       getattr(_shared_openai_client, '_cached_key', None) != current_key or \
       getattr(_shared_openai_client, '_cached_base', None) != current_base:
        
        if _shared_http_client:
            try:
                _shared_http_client.close()
            except:
                pass
        
        _shared_http_client = httpx.Client(
            timeout=httpx.Timeout(300.0, connect=30.0),
            follow_redirects=True
        )
        _shared_openai_client = OpenAI(
            api_key=current_key,
            base_url=current_base,
            http_client=_shared_http_client,
            timeout=300.0
        )
        _shared_openai_client._cached_key = current_key
        _shared_openai_client._cached_base = current_base
    
    return _shared_openai_client


class BaseAgent:
    """基础Agent类，所有专业Agent的父类"""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.conversation_history = []
    
    def _get_client(self):
        """获取共享OpenAI客户端"""
        return get_shared_client()
    
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
        
        # 兼容不同API的响应格式（content 或 reasoning_content）
        msg = response.choices[0].message
        assistant_message = getattr(msg, 'content', None) or getattr(msg, 'reasoning_content', '') or ''
        
        # 保存对话历史
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def reset(self):
        """重置对话历史（不销毁共享客户端）"""
        self.conversation_history = []

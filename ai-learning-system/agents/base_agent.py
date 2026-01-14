"""
基础Agent类
参考 AutoGen 框架的多智能体设计模式
"""
import os
import httpx
from openai import OpenAI
from config import AI_CONFIG, OAUTH_CONFIG
from datetime import datetime, timedelta

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
        self.current_username = None
        self.oauth_tokens = None
    
    def _refresh_oauth_token(self, username: str) -> bool:
        """刷新 OAuth token"""
        try:
            # 动态导入 database 模块避免循环导入
            import database as db
            tokens = db.get_oauth_tokens(username)
            if not tokens:
                return False
            
            # 检查 token 是否即将过期（5分钟内）
            expires_at = tokens['expires_at']
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            
            if datetime.now() < expires_at - timedelta(minutes=5):
                # token 仍然有效，直接使用
                OAUTH_CONFIG["access_token"] = tokens['access_token']
                OAUTH_CONFIG["refresh_token"] = tokens['refresh_token']
                return True
            
            # token 需要刷新
            async with httpx.AsyncClient() as client:
                refresh_response = await client.post(
                    OAUTH_CONFIG["token_url"],
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": tokens["refresh_token"],
                        "client_id": OAUTH_CONFIG["client_id"],
                        "client_secret": OAUTH_CONFIG["client_secret"],
                    }
                )
                refresh_data = refresh_response.json()
                
                if "error" in refresh_data:
                    return False
                
                new_access_token = refresh_data.get("access_token")
                new_refresh_token = refresh_data.get("refresh_token", tokens["refresh_token"])
                expires_in = refresh_data.get("expires_in", 3600)
                
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                db.update_oauth_tokens(username, new_access_token, new_refresh_token, expires_at)
                
                OAUTH_CONFIG["access_token"] = new_access_token
                OAUTH_CONFIG["refresh_token"] = new_refresh_token
                return True
        except Exception as e:
            print(f"刷新 OAuth token 失败: {e}")
            return False
    
    def set_user(self, username: str):
        """设置当前用户，用于 OAuth token 刷新"""
        self.current_username = username
        if OAUTH_CONFIG["enabled"]:
            self._refresh_oauth_token(username)
    
    def _get_client(self):
        """获取OpenAI客户端"""
        if self.client is None:
            # 如果启用了 OAuth，使用 OAuth access_token
            api_key = AI_CONFIG["api_key"]
            if OAUTH_CONFIG["enabled"] and OAUTH_CONFIG["access_token"]:
                api_key = OAUTH_CONFIG["access_token"]
            
            # 创建不使用代理的 httpx 客户端，增加超时时间
            http_client = httpx.Client(
                timeout=httpx.Timeout(300.0, connect=30.0),  # 5分钟超时
                follow_redirects=True
            )
            self.client = OpenAI(
                api_key=api_key,
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

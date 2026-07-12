"""
LLM引擎 - 大模型API统一封装
支持OpenAI、Claude、Ollama等多种后端
"""
import os
import json
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str

class LLMEngine:
    """LLM引擎"""
    
    def __init__(self, config_path: str = None):
        """初始化LLM引擎"""
        self.config = self._load_config(config_path)
        self.provider = self._init_provider()
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认配置 - 使用环境变量
        return {
            "provider": os.getenv("LLM_PROVIDER", "openai"),
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "model": os.getenv("LLM_MODEL", "gpt-4"),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "temperature": 0.7,
            "max_tokens": 4096
        }
    
    def _init_provider(self):
        """初始化LLM提供者"""
        provider = self.config.get("provider", "openai")
        
        if provider == "openai":
            return OpenAIProvider(
                api_key=self.config.get("api_key", ""),
                model=self.config.get("model", "gpt-4"),
                base_url=self.config.get("base_url", "https://api.openai.com/v1")
            )
        elif provider == "claude":
            return ClaudeProvider(
                api_key=self.config.get("api_key", ""),
                model=self.config.get("model", "claude-3-sonnet-20240229")
            )
        elif provider == "ollama":
            return OllamaProvider(
                model=self.config.get("model", "llama2"),
                base_url=self.config.get("base_url", "http://localhost:11434")
            )
        else:
            raise ValueError(f"不支持的LLM提供者: {provider}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            LLMResponse对象
        """
        return await self.provider.chat(messages, **kwargs)
    
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """
        流式聊天
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Yields:
            流式响应内容
        """
        async for chunk in self.provider.stream_chat(messages, **kwargs):
            yield chunk

class OpenAIProvider:
    """OpenAI提供者"""
    
    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """发送聊天请求"""
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4096)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error = await response.text()
                        raise Exception(f"OpenAI API错误: {error}")
                    
                    result = await response.json()
                    
                    return LLMResponse(
                        content=result["choices"][0]["message"]["content"],
                        model=result["model"],
                        usage=result.get("usage", {}),
                        finish_reason=result["choices"][0]["finish_reason"]
                    )
        
        except ImportError:
            raise ImportError("请安装aiohttp: pip install aiohttp")
    
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """流式聊天"""
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4096),
                "stream": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            line = line[6:]
                            if line == '[DONE]':
                                break
                            try:
                                chunk = json.loads(line)
                                if 'choices' in chunk and chunk['choices']:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
        
        except ImportError:
            raise ImportError("请安装aiohttp: pip install aiohttp")

class ClaudeProvider:
    """Claude提供者"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """发送聊天请求"""
        try:
            import aiohttp
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # 转换消息格式
            claude_messages = []
            system_message = None
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            data = {
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "messages": claude_messages
            }
            
            if system_message:
                data["system"] = system_message
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error = await response.text()
                        raise Exception(f"Claude API错误: {error}")
                    
                    result = await response.json()
                    
                    return LLMResponse(
                        content=result["content"][0]["text"],
                        model=result["model"],
                        usage=result.get("usage", {}),
                        finish_reason=result["stop_reason"]
                    )
        
        except ImportError:
            raise ImportError("请安装aiohttp: pip install aiohttp")
    
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """流式聊天"""
        yield "Claude流式API暂未实现"

class OllamaProvider:
    """Ollama提供者"""
    
    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """发送聊天请求"""
        try:
            import aiohttp
            
            data = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7)
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=data
                ) as response:
                    if response.status != 200:
                        error = await response.text()
                        raise Exception(f"Ollama API错误: {error}")
                    
                    result = await response.json()
                    
                    return LLMResponse(
                        content=result["message"]["content"],
                        model=result["model"],
                        usage={
                            "prompt_tokens": result.get("prompt_eval_count", 0),
                            "completion_tokens": result.get("eval_count", 0)
                        },
                        finish_reason="stop"
                    )
        
        except ImportError:
            raise ImportError("请安装aiohttp: pip install aiohttp")
    
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """流式聊天"""
        try:
            import aiohttp
            
            data = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7)
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=data
                ) as response:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line:
                            try:
                                chunk = json.loads(line)
                                if 'message' in chunk and 'content' in chunk['message']:
                                    yield chunk['message']['content']
                            except json.JSONDecodeError:
                                continue
        
        except ImportError:
            raise ImportError("请安装aiohttp: pip install aiohttp")

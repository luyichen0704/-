"""
Open WebUI 适配层 - 将取证Agent集成到Open WebUI
通过Pipelines或Functions接口与Open WebUI交互
"""
import os
import json
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ForensicTask:
    """取证任务"""
    task_id: str
    task_type: str
    evidence_path: str
    description: str
    status: str = "pending"
    progress: float = 0.0
    results: List[Dict[str, Any]] = None

class ForensicPipeline:
    """
    Open WebUI Pipeline 接口
    可以作为Open WebUI的自定义Pipeline加载
    """
    
    # Pipeline元数据
    id = "forensic_agent"
    name = "取证AI助手"
    description = "基于大模型的自动化取证分析"
    version = "0.1.0"
    
    # 支持的模型
    models = ["forensic-expert"]
    
    def __init__(self):
        """初始化Pipeline"""
        from ..agent.core import ForensicAgent
        from ..agent.tools.registry import registry
        from ..agent.tools.executor import executor
        from ..agent.parsers.output_parser import parser_registry
        
        self.agent = ForensicAgent()
        self.tool_registry = registry
        self.executor = executor
        self.parser_registry = parser_registry
        
        logger.info("取证Pipeline初始化完成")
    
    async def on_startup(self):
        """启动时执行"""
        logger.info("取证Pipeline启动")
    
    async def on_shutdown(self):
        """关闭时执行"""
        logger.info("取证Pipeline关闭")
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        tools_info = []
        for tool in self.tool_registry.get_all_tools():
            tools_info.append(f"- {tool.name}: {tool.description}")
        
        tools_list = "\n".join(tools_info)
        
        return f"""你是一个专业的电子取证专家AI助手。你的任务是帮助用户分析电子证据，找出关键信息。

你可以使用以下取证工具：
{tools_list}

分析流程：
1. 理解用户的取证需求
2. 识别证据文件类型
3. 选择合适的取证工具
4. 执行分析命令
5. 解析工具输出
6. 总结发现的关键信息

回答要求：
- 使用中文回答
- 提供清晰的分析步骤
- 列出发现的关键证据
- 给出专业的取证结论
- 所有结论必须有证据支持

当用户提供证据文件时，自动执行分析流程并返回结果。
"""
    
    async def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[Dict[str, str]],
        body: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Open WebUI Pipeline 接口
        
        Args:
            user_message: 用户消息
            model_id: 模型ID
            messages: 对话历史
            body: 请求体
            
        Yields:
            流式响应
        """
        try:
            # 检查是否包含证据文件路径
            evidence_path = self._extract_evidence_path(user_message)
            
            if evidence_path:
                # 执行取证分析
                async for chunk in self._analyze_evidence(user_message, evidence_path):
                    yield chunk
            else:
                # 普通对话
                async for chunk in self._chat(user_message, messages):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Pipeline执行错误: {e}")
            yield f"抱歉，处理过程中出现错误: {str(e)}"
    
    def _extract_evidence_path(self, message: str) -> Optional[str]:
        """从消息中提取证据文件路径"""
        import re
        
        # 匹配常见证据文件路径
        patterns = [
            r'[A-Za-z]:\\[^\s]+\.(?:E01|raw|dd|img|pcap|pcapng|mem|apk)',
            r'/[^\s]+\.(?:E01|raw|dd|img|pcap|pcapng|mem|apk)',
            r'[^\s]+\.(?:E01|raw|dd|img|pcap|pcapng|mem|apk)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    async def _analyze_evidence(self, question: str, evidence_path: str) -> AsyncGenerator[str, None]:
        """执行取证分析"""
        yield f"## 🔍 开始取证分析\n\n"
        yield f"**证据文件:** `{evidence_path}`\n"
        yield f"**分析问题:** {question}\n\n"
        
        # 检测证据类型
        evidence_type = self._detect_evidence_type(evidence_path)
        yield f"**证据类型:** {evidence_type}\n\n"
        
        # 获取分析计划
        yield "### 📋 分析计划\n\n"
        plan = await self.agent.create_plan(question, evidence_path)
        
        for i, step in enumerate(plan.steps):
            yield f"{i+1}. {step.description}\n"
        yield "\n"
        
        # 执行分析
        yield "### ⚙️ 执行分析\n\n"
        
        results = []
        for i, step in enumerate(plan.steps):
            yield f"**步骤 {i+1}:** {step.description}\n"
            
            for tool_name in step.tools:
                # 执行工具
                result = self.executor.execute_tool(
                    tool_name=tool_name,
                    evidence_path=evidence_path,
                    args=" ".join(step.commands[0].split()[1:]) if step.commands else ""
                )
                
                if result.success:
                    # 解析输出
                    parsed = self.parser_registry.parse(tool_name, result.stdout)
                    
                    yield f"✅ {tool_name}: {parsed.summary}\n"
                    
                    for finding in parsed.findings[:3]:
                        yield f"   - {finding}\n"
                    
                    results.append({
                        "tool": tool_name,
                        "parsed": parsed.parsed_data,
                        "findings": parsed.findings
                    })
                else:
                    yield f"❌ {tool_name}: 执行失败\n"
                    yield f"   错误: {result.stderr[:100]}\n"
            
            yield "\n"
        
        # 总结发现
        yield "### 📊 分析结果总结\n\n"
        
        all_findings = []
        for r in results:
            all_findings.extend(r.get("findings", []))
        
        if all_findings:
            yield "**关键发现:**\n\n"
            for i, finding in enumerate(all_findings[:10], 1):
                yield f"{i}. {finding}\n"
        else:
            yield "未发现明显的关键信息。\n"
        
        yield "\n### 💡 专业建议\n\n"
        yield "基于以上分析，建议进一步检查：\n"
        yield "1. 关键文件的内容和时间戳\n"
        yield "2. 异常网络连接的目的地\n"
        yield "3. 可疑进程的父子关系\n"
    
    async def _chat(self, message: str, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """普通对话"""
        # 使用LLM回答取证相关问题
        system_prompt = self._build_system_prompt()
        
        full_messages = [{"role": "system", "content": system_prompt}]
        full_messages.extend(messages[-5:])  # 保留最近5条消息
        full_messages.append({"role": "user", "content": message})
        
        # 调用LLM
        response = await self.agent.llm.chat(full_messages)
        
        # 流式输出
        for char in response.content:
            yield char
            await asyncio.sleep(0.01)  # 模拟流式效果
    
    def _detect_evidence_type(self, path: str) -> str:
        """检测证据类型"""
        ext = os.path.splitext(path)[1].lower()
        
        type_map = {
            ".E01": "磁盘镜像 (E01格式)",
            ".raw": "原始磁盘镜像/内存转储",
            ".dd": "磁盘镜像 (dd格式)",
            ".img": "磁盘镜像",
            ".pcap": "网络流量包",
            ".pcapng": "网络流量包 (pcapng格式)",
            ".mem": "内存转储",
            ".apk": "Android应用包",
            ".exe": "Windows可执行文件",
            ".elf": "Linux可执行文件"
        }
        
        return type_map.get(ext, "未知类型")

class ForensicFunction:
    """
    Open WebUI Function 接口
    可以注册为Open WebUI的自定义函数
    """
    
    def __init__(self):
        from ..agent.tools.registry import registry
        from ..agent.tools.executor import executor
        
        self.tool_registry = registry
        self.executor = executor
    
    def check_tools(self) -> str:
        """检查工具状态"""
        status = self.tool_registry.check_all_tools()
        
        result = "## 🛠 取证工具状态\n\n"
        result += "| 工具 | 状态 |\n"
        result += "|------|------|\n"
        
        for name, available in status.items():
            emoji = "✅" if available else "❌"
            result += f"| {name} | {emoji} |\n"
        
        available = sum(1 for v in status.values() if v)
        total = len(status)
        result += f"\n**可用工具:** {available}/{total}\n"
        
        return result
    
    def install_missing_tools(self) -> str:
        """安装缺失工具"""
        missing = self.tool_registry.get_missing_tools()
        
        if not missing:
            return "✅ 所有工具已安装！"
        
        result = "## 📦 缺失工具安装指南\n\n"
        
        for tool in missing:
            result += f"### {tool.name}\n"
            result += f"- **描述:** {tool.description}\n"
            result += f"- **安装命令:** `{tool.install_command}`\n\n"
        
        return result
    
    def analyze_file(self, file_path: str, question: str = None) -> str:
        """分析文件"""
        if not os.path.exists(file_path):
            return f"❌ 文件不存在: {file_path}"
        
        # 检测文件类型
        file_result = self.executor.execute_tool("file", file_path)
        
        result = "## 📁 文件分析结果\n\n"
        result += f"**文件路径:** `{file_path}`\n"
        
        if file_result.success:
            from ..agent.parsers.output_parser import parser_registry
            parsed = parser_registry.parse("file", file_result.stdout)
            result += f"**文件类型:** {parsed.parsed_data.get('file_type', '未知')}\n\n"
        
        # 提取字符串
        strings_result = self.executor.execute_tool("strings", file_path, args="-n 8")
        if strings_result.success:
            from ..agent.parsers.output_parser import parser_registry
            parsed = parser_registry.parse("strings", strings_result.stdout)
            
            result += "### 字符串分析\n\n"
            for finding in parsed.findings[:5]:
                result += f"- {finding}\n"
        
        return result

# Open WebUI Pipeline 注册格式
PIPELINE_DEFINITION = {
    "id": "forensic_agent",
    "name": "取证AI助手",
    "description": "基于大模型的自动化取证分析",
    "version": "0.1.0",
    "type": "pipe",
    "models": ["forensic-expert"],
    "parameters": {
        "type": "object",
        "properties": {
            "evidence_path": {
                "type": "string",
                "description": "证据文件路径"
            },
            "analysis_type": {
                "type": "string",
                "enum": ["disk", "network", "memory", "file", "auto"],
                "description": "分析类型"
            }
        }
    }
}

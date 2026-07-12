"""
取证Agent核心 - 协调LLM、工具和知识库
"""
import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class AnalysisStep:
    """分析步骤"""
    step_id: int
    description: str
    tools: List[str]
    commands: List[str]
    expected_output: str
    priority: int = 1
    dependencies: List[int] = None

@dataclass
class AnalysisPlan:
    """分析计划"""
    task_type: str
    description: str
    steps: List[AnalysisStep]
    total_estimated_time: int
    confidence: float

class ForensicAgent:
    """取证Agent"""
    
    def __init__(self, config_path: str = None):
        """初始化Agent"""
        from .llm import LLMEngine
        from .tools.registry import registry
        from .tools.executor import executor
        from .parsers.output_parser import parser_registry
        from .knowledge_base import KnowledgeBase
        
        self.llm = LLMEngine(config_path)
        self.tool_registry = registry
        self.executor = executor
        self.parser_registry = parser_registry
        self.knowledge_base = KnowledgeBase()
        
        logger.info("取证Agent初始化完成")
    
    async def create_plan(self, question: str, evidence_path: str = None) -> AnalysisPlan:
        """
        创建分析计划
        
        Args:
            question: 用户问题
            evidence_path: 证据文件路径
            
        Returns:
            AnalysisPlan对象
        """
        # 检测任务类型
        task_type = self._detect_task_type(question, evidence_path)
        
        # 使用LLM生成分析步骤
        system_prompt = """你是一个专业的电子取证专家。根据用户的问题和证据类型，生成详细的分析步骤。

每个步骤应该包含：
1. 步骤描述
2. 需要使用的工具
3. 具体的命令
4. 预期输出

请以JSON格式返回。"""
        
        user_prompt = f"""
问题: {question}
证据文件: {evidence_path or '未知'}
任务类型: {task_type}

请生成分析步骤，返回JSON格式：
{{
    "steps": [
        {{
            "step_id": 1,
            "description": "步骤描述",
            "tools": ["工具名称"],
            "commands": ["命令"],
            "expected_output": "预期输出"
        }}
    ]
}}"""
        
        try:
            response = await self.llm.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # 解析响应
            result = json.loads(response.content)
            
            steps = []
            for step_data in result.get("steps", []):
                step = AnalysisStep(
                    step_id=step_data["step_id"],
                    description=step_data["description"],
                    tools=step_data["tools"],
                    commands=step_data["commands"],
                    expected_output=step_data["expected_output"],
                    priority=step_data.get("priority", 1),
                    dependencies=step_data.get("dependencies", [])
                )
                steps.append(step)
            
            return AnalysisPlan(
                task_type=task_type,
                description=question,
                steps=steps,
                total_estimated_time=len(steps) * 60,
                confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"创建分析计划失败: {e}")
            return self._get_default_plan(task_type, question, evidence_path)
    
    def _detect_task_type(self, question: str, evidence_path: str = None) -> str:
        """检测任务类型"""
        question_lower = question.lower()
        
        # 关键词匹配
        keywords = {
            "disk": ["E01", "磁盘", "镜像", "分区", "文件系统"],
            "network": ["PCAP", "流量", "网络", "HTTP", "DNS"],
            "memory": ["内存", "RAM", "dump", "进程"],
            "android": ["APK", "安卓", "APP", "手机"],
            "crypto": ["加密", "解密", "RSA", "AES", "密码"],
            "stego": ["隐写", "图片", "LSB", "隐藏"],
            "reverse": ["逆向", "二进制", "PE", "ELF"]
        }
        
        for task_type, kws in keywords.items():
            for kw in kws:
                if kw in question_lower:
                    return task_type
        
        # 根据文件扩展名判断
        if evidence_path:
            ext = os.path.splitext(evidence_path)[1].lower()
            ext_map = {
                ".E01": "disk", ".raw": "disk", ".dd": "disk",
                ".pcap": "network", ".pcapng": "network",
                ".mem": "memory",
                ".apk": "android",
                ".exe": "reverse", ".elf": "reverse"
            }
            if ext in ext_map:
                return ext_map[ext]
        
        return "general"
    
    def _get_default_plan(self, task_type: str, question: str, 
                         evidence_path: str = None) -> AnalysisPlan:
        """获取默认分析计划"""
        default_steps = {
            "disk": [
                AnalysisStep(1, "获取镜像基本信息", ["file", "exiftool"], 
                            ["file {evidence}", "exiftool {evidence}"], "文件信息"),
                AnalysisStep(2, "分析分区结构", ["sleuthkit"], 
                            ["mmls {evidence}"], "分区表"),
                AnalysisStep(3, "提取文件列表", ["sleuthkit"], 
                            ["fls -r {evidence}"], "文件列表"),
            ],
            "network": [
                AnalysisStep(1, "获取流量包信息", ["tshark"], 
                            ["capinfos {evidence}"], "流量包统计"),
                AnalysisStep(2, "分析协议分布", ["tshark"], 
                            ["tshark -r {evidence} -q -z io,phs"], "协议统计"),
                AnalysisStep(3, "提取HTTP请求", ["tshark"], 
                            ["tshark -r {evidence} -Y http.request"], "HTTP请求"),
            ],
            "memory": [
                AnalysisStep(1, "获取系统信息", ["volatility3"], 
                            ["vol -f {evidence} windows.info"], "系统信息"),
                AnalysisStep(2, "列出进程", ["volatility3"], 
                            ["vol -f {evidence} windows.pslist"], "进程列表"),
                AnalysisStep(3, "检查网络连接", ["volatility3"], 
                            ["vol -f {evidence} windows.netscan"], "网络连接"),
            ],
            "android": [
                AnalysisStep(1, "反编译APK", ["jadx"], 
                            ["jadx -d output {evidence}"], "源代码"),
                AnalysisStep(2, "提取应用信息", ["exiftool"], 
                            ["exiftool {evidence}"], "应用元数据"),
            ],
            "general": [
                AnalysisStep(1, "文件类型识别", ["file"], 
                            ["file {evidence}"], "文件类型"),
                AnalysisStep(2, "提取字符串", ["strings"], 
                            ["strings -n 8 {evidence}"], "可读字符串"),
                AnalysisStep(3, "查看十六进制", ["xxd"], 
                            ["xxd {evidence} | head -100"], "十六进制内容"),
            ]
        }
        
        steps = default_steps.get(task_type, default_steps["general"])
        
        return AnalysisPlan(
            task_type=task_type,
            description=question,
            steps=steps,
            total_estimated_time=len(steps) * 60,
            confidence=0.7
        )
    
    async def analyze(self, question: str, evidence_path: str = None) -> Dict[str, Any]:
        """
        执行取证分析
        
        Args:
            question: 用户问题
            evidence_path: 证据文件路径
            
        Returns:
            分析结果字典
        """
        results = {
            "question": question,
            "evidence_path": evidence_path,
            "findings": [],
            "artifacts": [],
            "summary": ""
        }
        
        # 创建分析计划
        plan = await self.create_plan(question, evidence_path)
        results["plan"] = {
            "task_type": plan.task_type,
            "steps": len(plan.steps),
            "confidence": plan.confidence
        }
        
        # 执行分析步骤
        all_findings = []
        all_artifacts = []
        
        for step in plan.steps:
            logger.info(f"执行步骤 {step.step_id}: {step.description}")
            
            for tool_name in step.tools:
                # 执行工具
                result = self.executor.execute_tool(
                    tool_name=tool_name,
                    evidence_path=evidence_path
                )
                
                if result.success:
                    # 解析输出
                    parsed = self.parser_registry.parse(tool_name, result.stdout)
                    
                    all_findings.extend(parsed.findings)
                    all_artifacts.extend(parsed.artifacts)
                    
                    results["findings"].extend(parsed.findings)
                    results["artifacts"].extend(parsed.artifacts)
        
        # 使用LLM生成总结
        if all_findings:
            summary_prompt = f"""
基于以下取证分析发现，生成专业的分析总结：

问题: {question}
证据: {evidence_path}

发现:
{chr(10).join(f'- {f}' for f in all_findings[:20])}

请提供：
1. 关键发现总结
2. 证据链分析
3. 专业结论
4. 进一步建议
"""
            
            summary_response = await self.llm.chat([
                {"role": "system", "content": "你是专业取证专家，请用中文回答。"},
                {"role": "user", "content": summary_prompt}
            ])
            
            results["summary"] = summary_response.content
        else:
            results["summary"] = "未发现明显的关键信息，建议使用更具体的分析工具或问题。"
        
        return results
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        tools = []
        for tool in self.tool_registry.get_all_tools():
            tools.append({
                "name": tool.name,
                "category": tool.category.value,
                "description": tool.description,
                "available": self.tool_registry.check_tool_available(tool.name)
            })
        return tools
    
    def get_tool_status(self) -> str:
        """获取工具状态报告"""
        status = self.tool_registry.check_all_tools()
        
        report = "## 🛠 取证工具状态\n\n"
        report += "| 工具 | 类别 | 状态 | 描述 |\n"
        report += "|------|------|------|------|\n"
        
        for tool in self.tool_registry.get_all_tools():
            available = status.get(tool.name, False)
            emoji = "✅" if available else "❌"
            report += f"| {tool.name} | {tool.category.value} | {emoji} | {tool.description} |\n"
        
        available_count = sum(1 for v in status.values() if v)
        total_count = len(status)
        
        report += f"\n**总计:** {available_count}/{total_count} 工具可用\n"
        
        return report

"""
工具执行器 - 执行取证工具命令并收集输出
"""
import os
import subprocess
import tempfile
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
import shlex

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """执行结果"""
    tool_name: str
    command: str
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    success: bool
    output_file: Optional[str] = None
    metadata: Dict[str, Any] = None

class ToolExecutor:
    """工具执行器"""
    
    def __init__(self, working_dir: str = None, timeout: int = 300):
        """
        初始化执行器
        
        Args:
            working_dir: 工作目录
            timeout: 命令超时时间(秒)
        """
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="forensic_")
        self.timeout = timeout
        self.execution_history: List[ExecutionResult] = []
        
        # 确保工作目录存在
        os.makedirs(self.working_dir, exist_ok=True)
    
    def execute(self, command: str, tool_name: str = None, 
                evidence_path: str = None, **kwargs) -> ExecutionResult:
        """
        执行命令
        
        Args:
            command: 要执行的命令
            tool_name: 工具名称(用于记录)
            evidence_path: 证据文件路径
            **kwargs: 其他参数
            
        Returns:
            ExecutionResult对象
        """
        # 替换命令模板中的变量
        if evidence_path:
            command = command.replace("{evidence_path}", evidence_path)
        
        # 替换其他变量
        for key, value in kwargs.items():
            command = command.replace(f"{{{key}}}", str(value))
        
        logger.info(f"执行命令: {command}")
        
        start_time = time.time()
        
        try:
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_dir
            )
            
            execution_time = time.time() - start_time
            
            exec_result = ExecutionResult(
                tool_name=tool_name or "unknown",
                command=command,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                success=result.returncode == 0,
                metadata={
                    "working_dir": self.working_dir,
                    "timeout": self.timeout
                }
            )
            
            self.execution_history.append(exec_result)
            
            if exec_result.success:
                logger.info(f"命令执行成功 ({execution_time:.2f}s)")
            else:
                logger.warning(f"命令执行失败: {result.stderr}")
            
            return exec_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"命令执行超时 ({self.timeout}s)")
            
            exec_result = ExecutionResult(
                tool_name=tool_name or "unknown",
                command=command,
                return_code=-1,
                stdout="",
                stderr=f"命令执行超时 ({self.timeout}秒)",
                execution_time=execution_time,
                success=False,
                metadata={"timeout": True}
            )
            
            self.execution_history.append(exec_result)
            return exec_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"命令执行异常: {e}")
            
            exec_result = ExecutionResult(
                tool_name=tool_name or "unknown",
                command=command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                success=False,
                metadata={"error": str(e)}
            )
            
            self.execution_history.append(exec_result)
            return exec_result
    
    def execute_tool(self, tool_name: str, evidence_path: str, 
                     args: str = "", **kwargs) -> ExecutionResult:
        """
        执行指定工具
        
        Args:
            tool_name: 工具名称
            evidence_path: 证据文件路径
            args: 额外参数
            **kwargs: 其他变量
            
        Returns:
            ExecutionResult对象
        """
        from .registry import registry
        
        tool = registry.get_tool(tool_name)
        if not tool:
            return ExecutionResult(
                tool_name=tool_name,
                command="",
                return_code=-1,
                stdout="",
                stderr=f"工具 {tool_name} 未注册",
                execution_time=0,
                success=False
            )
        
        # 构建命令
        command = tool.command_template
        command = command.replace("{evidence_path}", evidence_path)
        command = command.replace("{args}", args)
        
        # 替换其他变量
        for key, value in kwargs.items():
            command = command.replace(f"{{{key}}}", str(value))
        
        return self.execute(command, tool_name=tool_name, **kwargs)
    
    def execute_pipeline(self, steps: List[Dict[str, Any]]) -> List[ExecutionResult]:
        """
        执行工具管道
        
        Args:
            steps: 步骤列表，每个步骤包含tool_name, evidence_path, args等
            
        Returns:
            ExecutionResult列表
        """
        results = []
        
        for i, step in enumerate(steps):
            logger.info(f"执行步骤 {i+1}/{len(steps)}: {step.get('tool_name', 'unknown')}")
            
            result = self.execute_tool(
                tool_name=step.get("tool_name"),
                evidence_path=step.get("evidence_path"),
                args=step.get("args", ""),
                **step.get("kwargs", {})
            )
            
            results.append(result)
            
            # 如果步骤失败且标记为关键步骤，停止执行
            if not result.success and step.get("critical", False):
                logger.error(f"关键步骤 {i+1} 执行失败，停止管道")
                break
        
        return results
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        if not self.execution_history:
            return {"total": 0, "success": 0, "failed": 0}
        
        total = len(self.execution_history)
        success = sum(1 for r in self.execution_history if r.success)
        failed = total - success
        total_time = sum(r.execution_time for r in self.execution_history)
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "total_time": total_time,
            "average_time": total_time / total if total > 0 else 0
        }
    
    def clear_history(self):
        """清除执行历史"""
        self.execution_history.clear()
    
    def save_output(self, result: ExecutionResult, output_path: str = None) -> str:
        """保存输出到文件"""
        if output_path is None:
            output_path = os.path.join(
                self.working_dir,
                f"{result.tool_name}_{int(time.time())}.txt"
            )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Tool: {result.tool_name}\n")
            f.write(f"Command: {result.command}\n")
            f.write(f"Return Code: {result.return_code}\n")
            f.write(f"Execution Time: {result.execution_time:.2f}s\n")
            f.write(f"Success: {result.success}\n")
            f.write(f"\n{'='*60}\n")
            f.write(f"STDOUT:\n{result.stdout}\n")
            f.write(f"\n{'='*60}\n")
            f.write(f"STDERR:\n{result.stderr}\n")
        
        return output_path

# 全局实例
executor = ToolExecutor()

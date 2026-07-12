"""
示例插件 - YARA规则扫描器
演示如何创建取证平台插件
"""
import os
import subprocess
from typing import Dict, Any, List
from plugins.manager import ForensicPlugin, PluginMeta

class YaraScannerPlugin(ForensicPlugin):
    """YARA规则扫描器插件"""
    
    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="yara-scanner",
            version="1.0.0",
            description="使用YARA规则扫描文件，检测恶意代码和特征",
            author="Forensic AI Platform",
            dependencies=["yara-python"],
            hooks=["pre_analysis", "post_analysis"]
        )
    
    def initialize(self, agent) -> bool:
        """初始化插件"""
        self.agent = agent
        self.rules_dir = os.path.join(os.path.dirname(__file__), "rules")
        os.makedirs(self.rules_dir, exist_ok=True)
        
        # 检查YARA是否可用
        try:
            import yara
            self.yara_available = True
        except ImportError:
            self.yara_available = False
            print("警告: yara-python未安装，插件功能受限")
        
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行YARA扫描
        
        参数:
            target: 目标文件或目录
            rules: YARA规则文件路径（可选）
        """
        target = kwargs.get("target")
        rules_path = kwargs.get("rules")
        
        if not target:
            return {"error": "未指定扫描目标"}
        
        if not os.path.exists(target):
            return {"error": f"目标不存在: {target}"}
        
        # 使用YARA命令行工具扫描
        return self._scan_with_cli(target, rules_path)
    
    def _scan_with_cli(self, target: str, rules_path: str = None) -> Dict[str, Any]:
        """使用YARA命令行工具扫描"""
        results = {
            "target": target,
            "matches": [],
            "errors": []
        }
        
        # 默认规则路径
        if not rules_path:
            rules_path = self.rules_dir
        
        # 构建命令
        cmd = ["yara", "-r"]
        
        if os.path.isdir(rules_path):
            # 扫描规则目录
            for rule_file in os.listdir(rules_path):
                if rule_file.endswith((".yar", ".yara")):
                    rule_path = os.path.join(rules_path, rule_file)
                    try:
                        result = subprocess.run(
                            ["yara", "-r", rule_path, target],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        
                        if result.stdout:
                            for line in result.stdout.strip().split("\n"):
                                if line:
                                    parts = line.split(" ", 1)
                                    if len(parts) == 2:
                                        results["matches"].append({
                                            "rule": parts[0],
                                            "file": parts[1]
                                        })
                        
                        if result.stderr:
                            results["errors"].append(result.stderr)
                            
                    except subprocess.TimeoutExpired:
                        results["errors"].append(f"扫描超时: {rule_file}")
                    except Exception as e:
                        results["errors"].append(str(e))
        
        elif os.path.isfile(rules_path):
            # 单个规则文件
            try:
                result = subprocess.run(
                    ["yara", "-r", rules_path, target],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.stdout:
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            parts = line.split(" ", 1)
                            if len(parts) == 2:
                                results["matches"].append({
                                    "rule": parts[0],
                                    "file": parts[1]
                                })
                
            except Exception as e:
                results["errors"].append(str(e))
        
        results["total_matches"] = len(results["matches"])
        
        return results
    
    def pre_analysis(self, **kwargs):
        """分析前钩子 - 预扫描文件"""
        evidence_path = kwargs.get("evidence_path")
        if evidence_path and os.path.isfile(evidence_path):
            # 快速扫描
            result = self.execute(target=evidence_path)
            if result.get("matches"):
                return {
                    "action": "warn",
                    "message": f"发现 {len(result['matches'])} 条YARA规则匹配",
                    "matches": result["matches"]
                }
        return None
    
    def post_analysis(self, **kwargs):
        """分析后钩子 - 深度扫描发现的文件"""
        artifacts = kwargs.get("artifacts", [])
        findings = []
        
        for artifact in artifacts:
            if artifact.get("type") == "file" and artifact.get("path"):
                result = self.execute(target=artifact["path"])
                if result.get("matches"):
                    findings.extend(result["matches"])
        
        if findings:
            return {
                "action": "append",
                "findings": findings
            }
        return None
    
    def cleanup(self):
        """清理资源"""
        pass

# 插件入口点
def create_plugin():
    """创建插件实例"""
    return YaraScannerPlugin()

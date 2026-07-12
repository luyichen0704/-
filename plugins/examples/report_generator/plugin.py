"""
示例插件 - 自动报告生成器
自动生成取证分析报告
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List
from plugins.manager import ForensicPlugin, PluginMeta

class ReportGeneratorPlugin(ForensicPlugin):
    """自动报告生成器插件"""
    
    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="report-generator",
            version="1.0.0",
            description="自动生成取证分析报告，支持Markdown和HTML格式",
            author="Forensic AI Platform",
            hooks=["post_analysis"]
        )
    
    def initialize(self, agent) -> bool:
        """初始化插件"""
        self.agent = agent
        self.reports_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        生成报告
        
        参数:
            analysis_result: 分析结果
            format: 报告格式 (markdown/html)
            output_path: 输出路径（可选）
        """
        analysis_result = kwargs.get("analysis_result", {})
        format = kwargs.get("format", "markdown")
        output_path = kwargs.get("output_path")
        
        if format == "markdown":
            content = self._generate_markdown(analysis_result)
        elif format == "html":
            content = self._generate_html(analysis_result)
        else:
            return {"error": f"不支持的格式: {format}"}
        
        # 保存报告
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.{format}"
            output_path = os.path.join(self.reports_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "path": output_path,
            "format": format,
            "size": len(content)
        }
    
    def _generate_markdown(self, result: dict) -> str:
        """生成Markdown报告"""
        report = []
        
        # 标题
        report.append("# 🔍 取证分析报告\n")
        report.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 基本信息
        if result.get("question"):
            report.append(f"**分析问题:** {result['question']}\n")
        if result.get("evidence_path"):
            report.append(f"**证据文件:** `{result['evidence_path']}`\n")
        
        report.append("---\n")
        
        # 分析计划
        if result.get("plan"):
            plan = result["plan"]
            report.append("## 📋 分析计划\n")
            report.append(f"- **任务类型:** {plan.get('task_type', '未知')}")
            report.append(f"- **分析步骤:** {plan.get('steps', 0)} 步")
            report.append(f"- **置信度:** {plan.get('confidence', 0):.0%}\n")
        
        # 关键发现
        if result.get("findings"):
            report.append("## 🔍 关键发现\n")
            for i, finding in enumerate(result["findings"], 1):
                report.append(f"{i}. {finding}")
            report.append("")
        
        # 提取的证据
        if result.get("artifacts"):
            report.append("## 📦 提取的证据\n")
            report.append("| 类型 | 值 | 备注 |")
            report.append("|------|-----|------|")
            for artifact in result["artifacts"]:
                artifact_type = artifact.get("type", "未知")
                value = artifact.get("value", artifact.get("name", "N/A"))
                note = artifact.get("note", "")
                report.append(f"| {artifact_type} | `{value}` | {note} |")
            report.append("")
        
        # 分析总结
        if result.get("summary"):
            report.append("## 📝 分析总结\n")
            report.append(result["summary"])
            report.append("")
        
        # 页脚
        report.append("---\n")
        report.append("*本报告由取证AI平台自动生成*")
        
        return "\n".join(report)
    
    def _generate_html(self, result: dict) -> str:
        """生成HTML报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>取证分析报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1e3a5f;
            border-bottom: 3px solid #2d5a87;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2d5a87;
            margin-top: 30px;
        }}
        .meta {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .finding {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 10px 15px;
            margin: 10px 0;
        }}
        .artifact {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 10px 15px;
            margin: 10px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #2d5a87;
            color: white;
        }}
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 取证分析报告</h1>
        
        <div class="meta">
            <strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
"""
        
        if result.get("question"):
            html += f'            <strong>分析问题:</strong> {result["question"]}<br>\n'
        if result.get("evidence_path"):
            html += f'            <strong>证据文件:</strong> <code>{result["evidence_path"]}</code><br>\n'
        
        html += """        </div>
"""
        
        # 关键发现
        if result.get("findings"):
            html += """
        <h2>🔍 关键发现</h2>
"""
            for i, finding in enumerate(result["findings"], 1):
                html += f'        <div class="finding">{i}. {finding}</div>\n'
        
        # 提取的证据
        if result.get("artifacts"):
            html += """
        <h2>📦 提取的证据</h2>
        <table>
            <tr><th>类型</th><th>值</th><th>备注</th></tr>
"""
            for artifact in result["artifacts"]:
                artifact_type = artifact.get("type", "未知")
                value = artifact.get("value", artifact.get("name", "N/A"))
                note = artifact.get("note", "")
                html += f'            <tr><td>{artifact_type}</td><td><code>{value}</code></td><td>{note}</td></tr>\n'
            html += "        </table>\n"
        
        # 分析总结
        if result.get("summary"):
            html += f"""
        <h2>📝 分析总结</h2>
        <p>{result["summary"]}</p>
"""
        
        html += """
        <div class="footer">
            <em>本报告由取证AI平台自动生成</em>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def post_analysis(self, **kwargs):
        """分析后钩子 - 自动生成报告"""
        result = kwargs.get("result")
        if result:
            report_result = self.execute(
                analysis_result=result,
                format="markdown"
            )
            if report_result.get("success"):
                return {
                    "action": "append",
                    "message": f"报告已生成: {report_result['path']}"
                }
        return None
    
    def cleanup(self):
        """清理资源"""
        pass

def create_plugin():
    """创建插件实例"""
    return ReportGeneratorPlugin()

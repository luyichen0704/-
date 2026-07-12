"""
输出解析器 - 解析取证工具的输出结果
"""
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParsedOutput:
    """解析后的输出"""
    tool_name: str
    raw_output: str
    parsed_data: Dict[str, Any]
    summary: str
    findings: List[str]
    artifacts: List[Dict[str, Any]]
    confidence: float

class OutputParser:
    """输出解析器基类"""
    
    def parse(self, tool_name: str, output: str) -> ParsedOutput:
        """解析输出"""
        raise NotImplementedError

class TsharkParser(OutputParser):
    """TShark输出解析器"""
    
    def parse(self, tool_name: str, output: str) -> ParsedOutput:
        findings = []
        artifacts = []
        parsed_data = {}
        
        # 提取协议统计
        protocol_pattern = r'(\w+)\s+(\d+)\s+(\d+)'
        protocols = re.findall(protocol_pattern, output)
        if protocols:
            parsed_data["protocols"] = [
                {"name": p[0], "packets": int(p[1]), "bytes": int(p[2])}
                for p in protocols
            ]
            findings.append(f"发现 {len(protocols)} 种协议")
        
        # 提取IP地址
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = list(set(re.findall(ip_pattern, output)))
        if ips:
            parsed_data["ip_addresses"] = ips
            findings.append(f"发现 {len(ips)} 个IP地址")
        
        # 提取HTTP请求
        http_pattern = r'(GET|POST|PUT|DELETE)\s+([^\s]+)'
        http_requests = re.findall(http_pattern, output)
        if http_requests:
            parsed_data["http_requests"] = [
                {"method": m, "path": p} for m, p in http_requests
            ]
            findings.append(f"发现 {len(http_requests)} 个HTTP请求")
            for method, path in http_requests[:5]:
                artifacts.append({
                    "type": "http_request",
                    "method": method,
                    "path": path
                })
        
        # 提取域名
        domain_pattern = r'(?<=Host:\s)([^\s]+)'
        domains = list(set(re.findall(domain_pattern, output)))
        if domains:
            parsed_data["domains"] = domains
            findings.append(f"发现 {len(domains)} 个域名")
        
        summary = f"网络流量分析完成: {len(findings)} 项发现"
        
        return ParsedOutput(
            tool_name="tshark",
            raw_output=output,
            parsed_data=parsed_data,
            summary=summary,
            findings=findings,
            artifacts=artifacts,
            confidence=0.8
        )

class SleuthKitParser(OutputParser):
    """Sleuth Kit输出解析器"""
    
    def parse(self, tool_name: str, output: str) -> ParsedOutput:
        findings = []
        artifacts = []
        parsed_data = {}
        
        # 提取文件列表
        file_pattern = r'([drwx-]+)\s+(\d+)\s+(\w+)\s+(\w+)\s+(\d+)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s+(.+)'
        files = re.findall(file_pattern, output)
        if files:
            parsed_data["files"] = [
                {
                    "permissions": f[0],
                    "inode": f[1],
                    "user": f[2],
                    "group": f[3],
                    "size": f[4],
                    "date": f[5],
                    "name": f[6]
                }
                for f in files
            ]
            findings.append(f"发现 {len(files)} 个文件")
            
            # 提取特殊文件
            for f in files:
                name = f[6]
                if any(ext in name.lower() for ext in ['.txt', '.log', '.conf', '.key', '.pem']):
                    artifacts.append({
                        "type": "interesting_file",
                        "name": name,
                        "size": f[4],
                        "date": f[5]
                    })
        
        # 提取删除的文件
        deleted_pattern = r'\*\s+(.+)'
        deleted = re.findall(deleted_pattern, output)
        if deleted:
            parsed_data["deleted_files"] = deleted
            findings.append(f"发现 {len(deleted)} 个已删除文件")
            for d in deleted:
                artifacts.append({
                    "type": "deleted_file",
                    "name": d
                })
        
        # 提取分区信息
        partition_pattern = r'(\d+):\s+(\d+)\s+(\d+)\s+(\d+)\s+(\w+)'
        partitions = re.findall(partition_pattern, output)
        if partitions:
            parsed_data["partitions"] = [
                {
                    "slot": p[0],
                    "start": p[1],
                    "end": p[2],
                    "length": p[3],
                    "type": p[4]
                }
                for p in partitions
            ]
            findings.append(f"发现 {len(partitions)} 个分区")
        
        summary = f"磁盘取证分析完成: {len(findings)} 项发现"
        
        return ParsedOutput(
            tool_name="sleuthkit",
            raw_output=output,
            parsed_data=parsed_data,
            summary=summary,
            findings=findings,
            artifacts=artifacts,
            confidence=0.85
        )

class VolatilityParser(OutputParser):
    """Volatility输出解析器"""
    
    def parse(self, tool_name: str, output: str) -> ParsedOutput:
        findings = []
        artifacts = []
        parsed_data = {}
        
        # 提取进程列表
        process_pattern = r'(\d+)\s+(\d+)\s+(\w+)\s+(\d+)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\d+|-)\s+(.+)'
        processes = re.findall(process_pattern, output)
        if processes:
            parsed_data["processes"] = [
                {
                    "pid": p[0],
                    "ppid": p[1],
                    "image": p[2],
                    "offset": p[3],
                    "time": p[4],
                    "handles": p[5],
                    "name": p[6]
                }
                for p in processes
            ]
            findings.append(f"发现 {len(processes)} 个进程")
            
            # 检查可疑进程
            suspicious = ['cmd.exe', 'powershell', 'wscript', 'cscript', 'mshta', 'regsvr32']
            for p in processes:
                if any(s in p[6].lower() for s in suspicious):
                    artifacts.append({
                        "type": "suspicious_process",
                        "pid": p[0],
                        "name": p[6],
                        "time": p[4]
                    })
        
        # 提取网络连接
        net_pattern = r'(\d+)\s+(\w+)\s+([\d\.]+):(\d+)\s+([\d\.]+):(\d+)\s+(\w+)'
        connections = re.findall(net_pattern, output)
        if connections:
            parsed_data["network_connections"] = [
                {
                    "pid": c[0],
                    "protocol": c[1],
                    "local_addr": c[2],
                    "local_port": c[3],
                    "remote_addr": c[4],
                    "remote_port": c[5],
                    "state": c[6]
                }
                for c in connections
            ]
            findings.append(f"发现 {len(connections)} 个网络连接")
            
            # 标记外联连接
            for c in connections:
                if c[4] not in ['0.0.0.0', '127.0.0.1', '::']:
                    artifacts.append({
                        "type": "outbound_connection",
                        "remote": f"{c[4]}:{c[5]}",
                        "pid": c[0],
                        "protocol": c[1]
                    })
        
        summary = f"内存取证分析完成: {len(findings)} 项发现"
        
        return ParsedOutput(
            tool_name="volatility3",
            raw_output=output,
            parsed_data=parsed_data,
            summary=summary,
            findings=findings,
            artifacts=artifacts,
            confidence=0.85
        )

class FileParser(OutputParser):
    """file命令输出解析器"""
    
    def parse(self, tool_name: str, output: str) -> ParsedOutput:
        findings = []
        artifacts = []
        parsed_data = {}
        
        # 解析文件类型
        if ':' in output:
            parts = output.split(':', 1)
            file_path = parts[0].strip()
            file_type = parts[1].strip() if len(parts) > 1 else "unknown"
            
            parsed_data["file_path"] = file_path
            parsed_data["file_type"] = file_type
            findings.append(f"文件类型: {file_type}")
            
            # 检查是否是加密或压缩文件
            if any(keyword in file_type.lower() for keyword in ['encrypted', 'compressed', 'archive']):
                artifacts.append({
                    "type": "encrypted_compressed",
                    "file": file_path,
                    "description": file_type
                })
            
            # 检查是否是可执行文件
            if any(keyword in file_type.lower() for keyword in ['executable', 'elf', 'pe32']):
                artifacts.append({
                    "type": "executable",
                    "file": file_path,
                    "description": file_type
                })
        
        summary = f"文件类型识别完成"
        
        return ParsedOutput(
            tool_name="file",
            raw_output=output,
            parsed_data=parsed_data,
            summary=summary,
            findings=findings,
            artifacts=artifacts,
            confidence=0.95
        )

class StringsParser(OutputParser):
    """strings命令输出解析器"""
    
    def parse(self, tool_name: str, output: str) -> ParsedOutput:
        findings = []
        artifacts = []
        parsed_data = {}
        
        lines = output.split('\n')
        parsed_data["total_strings"] = len(lines)
        
        # 提取URL
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = list(set(re.findall(url_pattern, output)))
        if urls:
            parsed_data["urls"] = urls
            findings.append(f"发现 {len(urls)} 个URL")
            for url in urls[:10]:
                artifacts.append({"type": "url", "value": url})
        
        # 提取IP地址
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = list(set(re.findall(ip_pattern, output)))
        if ips:
            parsed_data["ip_addresses"] = ips
            findings.append(f"发现 {len(ips)} 个IP地址")
        
        # 提取邮箱
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = list(set(re.findall(email_pattern, output)))
        if emails:
            parsed_data["emails"] = emails
            findings.append(f"发现 {len(emails)} 个邮箱地址")
        
        # 提取可能的密码/密钥
        key_patterns = [
            r'(?i)password[:=]\s*(\S+)',
            r'(?i)key[:=]\s*(\S+)',
            r'(?i)secret[:=]\s*(\S+)',
            r'(?i)token[:=]\s*(\S+)'
        ]
        for pattern in key_patterns:
            matches = re.findall(pattern, output)
            if matches:
                findings.append(f"发现可能的敏感信息")
                for m in matches[:5]:
                    artifacts.append({"type": "potential_secret", "value": m[:20] + "..."})
        
        summary = f"字符串分析完成: {len(findings)} 项发现"
        
        return ParsedOutput(
            tool_name="strings",
            raw_output=output,
            parsed_data=parsed_data,
            summary=summary,
            findings=findings,
            artifacts=artifacts,
            confidence=0.7
        )

class ExifToolParser(OutputParser):
    """ExifTool输出解析器"""
    
    def parse(self, tool_name: str, output: str) -> ParsedOutput:
        findings = []
        artifacts = []
        parsed_data = {}
        
        # 解析键值对
        for line in output.split('\n'):
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip()
                value = value.strip()
                
                if key and value:
                    parsed_data[key] = value
                    
                    # 检查GPS信息
                    if 'gps' in key.lower() or 'latitude' in key.lower() or 'longitude' in key.lower():
                        findings.append(f"发现GPS信息: {key}={value}")
                        artifacts.append({"type": "gps", "key": key, "value": value})
                    
                    # 检查软件信息
                    if 'software' in key.lower() or 'creator' in key.lower():
                        findings.append(f"发现创建者信息: {value}")
        
        summary = f"元数据分析完成: {len(findings)} 项发现"
        
        return ParsedOutput(
            tool_name="exiftool",
            raw_output=output,
            parsed_data=parsed_data,
            summary=summary,
            findings=findings,
            artifacts=artifacts,
            confidence=0.9
        )

class GenericParser(OutputParser):
    """通用解析器"""
    
    def parse(self, tool_name: str, output: str) -> ParsedOutput:
        findings = []
        artifacts = []
        parsed_data = {"raw_lines": len(output.split('\n'))}
        
        # 基本统计
        findings.append(f"输出共 {len(output)} 字符")
        
        summary = f"{tool_name} 分析完成"
        
        return ParsedOutput(
            tool_name=tool_name,
            raw_output=output,
            parsed_data=parsed_data,
            summary=summary,
            findings=findings,
            artifacts=artifacts,
            confidence=0.5
        )

class ParserRegistry:
    """解析器注册表"""
    
    def __init__(self):
        self.parsers: Dict[str, OutputParser] = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """注册默认解析器"""
        self.parsers["tshark"] = TsharkParser()
        self.parsers["sleuthkit"] = SleuthKitParser()
        self.parsers["fls"] = SleuthKitParser()
        self.parsers["mmls"] = SleuthKitParser()
        self.parsers["volatility3"] = VolatilityParser()
        self.parsers["vol"] = VolatilityParser()
        self.parsers["file"] = FileParser()
        self.parsers["strings"] = StringsParser()
        self.parsers["exiftool"] = ExifToolParser()
        self.parsers["generic"] = GenericParser()
    
    def get_parser(self, tool_name: str) -> OutputParser:
        """获取解析器"""
        return self.parsers.get(tool_name, self.parsers["generic"])
    
    def parse(self, tool_name: str, output: str) -> ParsedOutput:
        """解析输出"""
        parser = self.get_parser(tool_name)
        return parser.parse(tool_name, output)

# 全局实例
parser_registry = ParserRegistry()

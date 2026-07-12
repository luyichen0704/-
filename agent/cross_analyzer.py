"""
跨检材分析器 - 关联分析多个检材之间的关系
支持: 手机+电脑、电脑+服务器、多台服务器等组合
"""
import os
import json
import hashlib
from typing import Dict, List, Any, Set
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class CrossEvidence:
    """跨检材关联证据"""
    evidence_id: str
    source_type: str  # android, ios, windows, linux
    artifact_type: str  # ip, account, file, time, behavior
    value: str
    timestamp: str = None
    context: str = None

class CrossEvidenceAnalyzer:
    """跨检材分析器"""
    
    def __init__(self):
        self.evidence_pool: List[CrossEvidence] = []
        self.correlations: List[Dict[str, Any]] = []
    
    def add_evidence(self, evidence: CrossEvidence):
        """添加证据"""
        self.evidence_pool.append(evidence)
    
    def analyze_ip_correlation(self) -> List[Dict[str, Any]]:
        """分析IP关联"""
        ip_map = {}
        
        for ev in self.evidence_pool:
            if ev.artifact_type == "ip":
                if ev.value not in ip_map:
                    ip_map[ev.value] = []
                ip_map[ev.value].append(ev)
        
        # 找出在多个检材中出现的IP
        correlations = []
        for ip, evidences in ip_map.items():
            sources = set(e.source_type for e in evidences)
            if len(sources) > 1:
                correlations.append({
                    "type": "IP关联",
                    "value": ip,
                    "sources": list(sources),
                    "count": len(evidences),
                    "details": [
                        {
                            "source": e.source_type,
                            "context": e.context,
                            "timestamp": e.timestamp
                        }
                        for e in evidences
                    ]
                })
        
        self.correlations.extend(correlations)
        return correlations
    
    def analyze_account_correlation(self) -> List[Dict[str, Any]]:
        """分析账号关联"""
        account_map = {}
        
        for ev in self.evidence_pool:
            if ev.artifact_type == "account":
                if ev.value not in account_map:
                    account_map[ev.value] = []
                account_map[ev.value].append(ev)
        
        correlations = []
        for account, evidences in account_map.items():
            sources = set(e.source_type for e in evidences)
            if len(sources) > 1:
                correlations.append({
                    "type": "账号关联",
                    "value": account,
                    "sources": list(sources),
                    "count": len(evidences),
                    "details": [
                        {
                            "source": e.source_type,
                            "context": e.context,
                            "timestamp": e.timestamp
                        }
                        for e in evidences
                    ]
                })
        
        self.correlations.extend(correlations)
        return correlations
    
    def analyze_file_correlation(self) -> List[Dict[str, Any]]:
        """分析文件关联（基于哈希）"""
        hash_map = {}
        
        for ev in self.evidence_pool:
            if ev.artifact_type == "file_hash":
                if ev.value not in hash_map:
                    hash_map[ev.value] = []
                hash_map[ev.value].append(ev)
        
        correlations = []
        for file_hash, evidences in hash_map.items():
            sources = set(e.source_type for e in evidences)
            if len(sources) > 1:
                correlations.append({
                    "type": "文件关联",
                    "hash": file_hash,
                    "sources": list(sources),
                    "count": len(evidences),
                    "details": [
                        {
                            "source": e.source_type,
                            "context": e.context,
                            "timestamp": e.timestamp
                        }
                        for e in evidences
                    ]
                })
        
        self.correlations.extend(correlations)
        return correlations
    
    def analyze_time_correlation(self, time_window: int = 300) -> List[Dict[str, Any]]:
        """分析时间关联（默认5分钟窗口）"""
        # 按时间排序
        timed_evidence = [
            ev for ev in self.evidence_pool 
            if ev.timestamp
        ]
        
        if not timed_evidence:
            return []
        
        # 解析时间
        for ev in timed_evidence:
            try:
                ev._parsed_time = datetime.fromisoformat(ev.timestamp.replace('Z', '+00:00'))
            except:
                ev._parsed_time = None
        
        # 按时间排序
        timed_evidence.sort(key=lambda x: x._parsed_time if x._parsed_time else datetime.min)
        
        # 找出时间窗口内的关联事件
        correlations = []
        for i in range(len(timed_evidence)):
            window_events = [timed_evidence[i]]
            
            for j in range(i + 1, len(timed_evidence)):
                if timed_evidence[j]._parsed_time and timed_evidence[i]._parsed_time:
                    diff = abs((timed_evidence[j]._parsed_time - timed_evidence[i]._parsed_time).total_seconds())
                    if diff <= time_window:
                        window_events.append(timed_evidence[j])
                    else:
                        break
            
            if len(window_events) > 1:
                sources = set(e.source_type for e in window_events)
                if len(sources) > 1:
                    correlations.append({
                        "type": "时间关联",
                        "time_window": f"{time_window}秒",
                        "sources": list(sources),
                        "count": len(window_events),
                        "details": [
                            {
                                "source": e.source_type,
                                "artifact_type": e.artifact_type,
                                "value": e.value[:100],
                                "timestamp": e.timestamp,
                                "context": e.context
                            }
                            for e in window_events
                        ]
                    })
        
        self.correlations.extend(correlations)
        return correlations
    
    def generate_attack_timeline(self) -> List[Dict[str, Any]]:
        """生成攻击时间线"""
        # 收集所有有时间戳的证据
        timed_evidence = [
            ev for ev in self.evidence_pool 
            if ev.timestamp
        ]
        
        # 解析时间并排序
        for ev in timed_evidence:
            try:
                ev._parsed_time = datetime.fromisoformat(ev.timestamp.replace('Z', '+00:00'))
            except:
                ev._parsed_time = None
        
        timed_evidence.sort(key=lambda x: x._parsed_time if x._parsed_time else datetime.min)
        
        # 生成时间线
        timeline = []
        for ev in timed_evidence:
            timeline.append({
                "timestamp": ev.timestamp,
                "source": ev.source_type,
                "type": ev.artifact_type,
                "value": ev.value[:200],
                "context": ev.context
            })
        
        return timeline
    
    def generate_report(self) -> Dict[str, Any]:
        """生成跨检材分析报告"""
        report = {
            "summary": {
                "total_evidence": len(self.evidence_pool),
                "sources": list(set(ev.source_type for ev in self.evidence_pool)),
                "correlations_found": len(self.correlations)
            },
            "ip_correlations": self.analyze_ip_correlation(),
            "account_correlations": self.analyze_account_correlation(),
            "file_correlations": self.analyze_file_correlation(),
            "time_correlations": self.analyze_time_correlation(),
            "attack_timeline": self.generate_attack_timeline()[:50]
        }
        
        return report

class EvidenceExtractor:
    """证据提取器 - 从分析结果中提取跨检材关联证据"""
    
    @staticmethod
    def extract_ips(text: str, source_type: str) -> List[CrossEvidence]:
        """提取IP地址"""
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, text)
        
        evidences = []
        for ip in ips:
            # 过滤掉常见非目标IP
            if not ip.startswith(('127.', '0.', '255.')):
                evidences.append(CrossEvidence(
                    evidence_id=f"{source_type}_ip_{ip}",
                    source_type=source_type,
                    artifact_type="ip",
                    value=ip,
                    context=f"从{source_type}提取"
                ))
        
        return evidences
    
    @staticmethod
    def extract_accounts(text: str, source_type: str) -> List[CrossEvidence]:
        """提取账号"""
        accounts = []
        
        # 邮箱
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        accounts.extend(emails)
        
        # 用户名模式
        user_pattern = r'(?:user|username|login|account)[:=]\s*(\S+)'
        users = re.findall(user_pattern, text, re.IGNORECASE)
        accounts.extend(users)
        
        evidences = []
        for account in set(accounts):
            evidences.append(CrossEvidence(
                evidence_id=f"{source_type}_account_{account}",
                source_type=source_type,
                artifact_type="account",
                value=account,
                context=f"从{source_type}提取"
            ))
        
        return evidences
    
    @staticmethod
    def extract_file_hashes(text: str, source_type: str) -> List[CrossEvidence]:
        """提取文件哈希"""
        hashes = []
        
        # MD5
        md5_pattern = r'\b[a-fA-F0-9]{32}\b'
        hashes.extend(re.findall(md5_pattern, text))
        
        # SHA1
        sha1_pattern = r'\b[a-fA-F0-9]{40}\b'
        hashes.extend(re.findall(sha1_pattern, text))
        
        # SHA256
        sha256_pattern = r'\b[a-fA-F0-9]{64}\b'
        hashes.extend(re.findall(sha256_pattern, text))
        
        evidences = []
        for h in set(hashes):
            evidences.append(CrossEvidence(
                evidence_id=f"{source_type}_hash_{h[:16]}",
                source_type=source_type,
                artifact_type="file_hash",
                value=h,
                context=f"从{source_type}提取"
            ))
        
        return evidences

def main():
    """演示跨检材分析"""
    analyzer = CrossEvidenceAnalyzer()
    
    # 模拟从不同检材提取的证据
    # 手机证据
    analyzer.add_evidence(CrossEvidence(
        evidence_id="android_ip_1",
        source_type="android",
        artifact_type="ip",
        value="192.168.1.100",
        timestamp="2024-01-15T10:30:00",
        context="WiFi连接"
    ))
    
    # 电脑证据
    analyzer.add_evidence(CrossEvidence(
        evidence_id="windows_ip_1",
        source_type="windows",
        artifact_type="ip",
        value="192.168.1.100",
        timestamp="2024-01-15T10:35:00",
        context="远程桌面连接"
    ))
    
    # 服务器证据
    analyzer.add_evidence(CrossEvidence(
        evidence_id="linux_ip_1",
        source_type="linux",
        artifact_type="ip",
        value="192.168.1.100",
        timestamp="2024-01-15T10:40:00",
        context="SSH登录"
    ))
    
    # 生成报告
    report = analyzer.generate_report()
    
    print("=" * 60)
    print("跨检材分析报告")
    print("=" * 60)
    
    print(f"\n总证据数: {report['summary']['total_evidence']}")
    print(f"检材来源: {', '.join(report['summary']['sources'])}")
    print(f"发现关联: {report['summary']['correlations_found']}")
    
    print("\nIP关联:")
    for corr in report['ip_correlations']:
        print(f"  IP: {corr['value']}")
        print(f"  来源: {', '.join(corr['sources'])}")

if __name__ == "__main__":
    main()

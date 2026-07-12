"""
案例提取器 - 从Writeup中提取取证案例数据
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class ForensicCase:
    """取证案例"""
    case_id: str
    title: str
    category: str
    competition: str
    year: int
    difficulty: str
    tools_used: List[str]
    techniques: List[str]
    description: str
    solution_steps: List[str]
    key_findings: List[str]
    flags: List[str]
    tags: List[str]
    content_hash: str

class CaseExtractor:
    """案例提取器"""
    
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.cases: List[ForensicCase] = []
        
        # 取证类别映射
        self.category_mapping = {
            "磁盘取证": ["E01", "磁盘", "镜像", "分区", "文件系统", "NTFS", "FAT"],
            "网络取证": ["PCAP", "流量", "网络", "HTTP", "DNS", "TCP", "Wireshark"],
            "内存取证": ["内存", "RAM", "dump", "Volatility", "进程"],
            "移动取证": ["APK", "安卓", "Android", "手机", "APP"],
            "密码学": ["加密", "解密", "RSA", "AES", "Base64", "哈希"],
            "隐写分析": ["隐写", "图片", "LSB", "steghide", "音频"],
            "逆向工程": ["逆向", "二进制", "PE", "ELF", "反编译"],
            "服务器取证": ["服务器", "Web", "日志", "Linux", "数据库"],
            "应急响应": ["挖矿", "勒索", "Webshell", "后门", "入侵"],
            "电子取证": ["手机", "APP", "聊天记录", "通话"],
        }
        
        # 工具识别
        self.tool_patterns = {
            "volatility": r"vol(?:atility)?[\s\-]",
            "tshark": r"tshark[\s\-]",
            "wireshark": r"wireshark",
            "sleuthkit": r"(?:fls|icat|mmls|tsk)",
            "autopsy": r"autopsy",
            "foremost": r"foremost",
            "binwalk": r"binwalk",
            "strings": r"strings[\s\-]",
            "exiftool": r"exiftool",
            "steghide": r"steghide",
            "zsteg": r"zsteg",
            "stegsolve": r"stegsolve",
            "jadx": r"jadx",
            "apktool": r"apktool",
            "hashcat": r"hashcat",
            "john": r"john",
            "openssl": r"openssl",
            "xxd": r"xxd",
            "hexedit": r"hexedit",
            "010editor": r"010\s*editor",
            "diskgenius": r"diskgenius",
            "取证大师": r"取证大师",
            "火眼": r"火眼",
        }
    
    def extract_from_directory(self):
        """从目录中提取所有案例"""
        print(f"开始扫描目录: {self.source_dir}")
        
        # 遍历所有比赛目录
        for comp_dir in self.source_dir.iterdir():
            if comp_dir.is_dir() and not comp_dir.name.startswith('.'):
                print(f"处理比赛: {comp_dir.name}")
                self._extract_from_competition(comp_dir)
        
        print(f"共提取 {len(self.cases)} 个案例")
    
    def _extract_from_competition(self, comp_dir: Path):
        """从比赛目录提取案例"""
        comp_name = comp_dir.name
        
        # 解析比赛名称和年份
        year = self._extract_year(comp_name)
        comp_type = self._identify_competition_type(comp_name)
        
        # 遍历所有Markdown文件
        for md_file in comp_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # 跳过太短的文件
                if len(content) < 100:
                    continue
                
                # 提取案例
                case = self._extract_case_from_content(
                    content, comp_name, year, comp_type, md_file
                )
                
                if case:
                    self.cases.append(case)
                    
            except Exception as e:
                print(f"  处理文件失败 {md_file}: {e}")
    
    def _extract_year(self, name: str) -> int:
        """提取年份"""
        match = re.search(r'(20\d{2})', name)
        return int(match.group(1)) if match else 2025
    
    def _identify_competition_type(self, name: str) -> str:
        """识别比赛类型"""
        if "美亚" in name:
            return "美亚杯"
        elif "FIC" in name:
            return "FIC"
        elif "数证" in name:
            return "数证杯"
        elif "盘古石" in name:
            return "盘古石"
        elif "平航" in name:
            return "平航杯"
        elif "SPC" in name:
            return "SPC"
        elif "警铮" in name:
            return "警铮杯"
        elif "獬豸" in name:
            return "獬豸杯"
        elif "NSSCTF" in name:
            return "NSSCTF"
        elif "CTF" in name:
            return "CTF"
        else:
            return "其他"
    
    def _extract_case_from_content(self, content: str, comp_name: str, 
                                   year: int, comp_type: str, 
                                   file_path: Path) -> ForensicCase:
        """从内容中提取案例"""
        # 提取标题
        title = self._extract_title(content, file_path)
        
        # 检查是否是取证相关
        category = self._identify_category(content)
        if not category:
            return None
        
        # 提取工具
        tools = self._extract_tools(content)
        
        # 提取技术
        techniques = self._extract_techniques(content)
        
        # 提取解题步骤
        steps = self._extract_solution_steps(content)
        
        # 提取关键发现
        findings = self._extract_findings(content)
        
        # 提取Flag
        flags = self._extract_flags(content)
        
        # 生成标签
        tags = self._generate_tags(content, category, tools)
        
        # 生成ID
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        case_id = f"{comp_type}_{year}_{content_hash}"
        
        return ForensicCase(
            case_id=case_id,
            title=title,
            category=category,
            competition=comp_type,
            year=year,
            difficulty=self._estimate_difficulty(content),
            tools_used=tools,
            techniques=techniques,
            description=self._extract_description(content),
            solution_steps=steps,
            key_findings=findings,
            flags=flags,
            tags=tags,
            content_hash=content_hash
        )
    
    def _extract_title(self, content: str, file_path: Path) -> str:
        """提取标题"""
        # 尝试从Markdown标题提取
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # 使用文件名
        return file_path.stem
    
    def _identify_category(self, content: str) -> str:
        """识别取证类别"""
        content_lower = content.lower()
        
        for category, keywords in self.category_mapping.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    return category
        
        return None
    
    def _extract_tools(self, content: str) -> List[str]:
        """提取使用的工具"""
        tools = []
        
        for tool_name, pattern in self.tool_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                tools.append(tool_name)
        
        return list(set(tools))
    
    def _extract_techniques(self, content: str) -> List[str]:
        """提取技术点"""
        techniques = []
        
        patterns = {
            "文件恢复": r"(?:恢复|还原|提取).*(?:文件|数据)",
            "流量分析": r"(?:流量|抓包|PCAP).*(?:分析|提取)",
            "内存分析": r"(?:内存|进程|句柄).*(?:分析|提取)",
            "密码破解": r"(?:破解|爆破|解密).*(?:密码|口令)",
            "隐写提取": r"(?:隐写|隐藏).*(?:提取|解密)",
            "日志分析": r"(?:日志|log).*(?:分析|审计)",
            "时间线分析": r"(?:时间线|时间戳).*(?:分析|还原)",
            "注册表分析": r"(?:注册表|reg).*(?:分析|提取)",
            "网络连接分析": r"(?:网络|连接|通信).*(?:分析|追踪)",
        }
        
        for technique, pattern in patterns.items():
            if re.search(pattern, content):
                techniques.append(technique)
        
        return techniques
    
    def _extract_solution_steps(self, content: str) -> List[str]:
        """提取解题步骤"""
        steps = []
        
        # 查找有序列表
        step_pattern = r'(?:^|\n)(?:\d+[\.\)、]|步骤\d+)[：:]*\s*(.+?)(?=\n\d+[\.\)、]|步骤\d|$)'
        matches = re.findall(step_pattern, content, re.DOTALL)
        
        if matches:
            steps = [m.strip() for m in matches if m.strip()]
        
        return steps[:10]  # 最多10步
    
    def _extract_findings(self, content: str) -> List[str]:
        """提取关键发现"""
        findings = []
        
        # 查找flag相关内容
        flag_pattern = r'(?:flag|Flag|FLAG|答案|key)[：:]*\s*[`"\']*([^\s`"\'}\n]+)'
        matches = re.findall(flag_pattern, content)
        findings.extend(matches[:5])
        
        return findings
    
    def _extract_flags(self, content: str) -> List[str]:
        """提取Flag"""
        flags = []
        
        patterns = [
            r'flag\{[^}]+\}',
            r'FLAG\{[^}]+\}',
            r'Flag\{[^}]+\}',
            r'ctf\{[^}]+\}',
            r'CTF\{[^}]+\}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            flags.extend(matches)
        
        return list(set(flags))
    
    def _generate_tags(self, content: str, category: str, 
                       tools: List[str]) -> List[str]:
        """生成标签"""
        tags = [category] if category else []
        tags.extend(tools[:5])  # 最多5个工具标签
        
        # 添加其他关键词
        keywords = {
            "取证": "取证",
            "CTF": "CTF",
            "比赛": "竞赛",
            "Writeup": "解题",
        }
        
        for tag, keyword in keywords.items():
            if keyword in content:
                tags.append(tag)
        
        return list(set(tags))[:10]
    
    def _estimate_difficulty(self, content: str) -> str:
        """估算难度"""
        # 简单的难度估算
        if len(content) > 5000:
            return "hard"
        elif len(content) > 2000:
            return "medium"
        else:
            return "easy"
    
    def _extract_description(self, content: str) -> str:
        """提取描述"""
        # 提取前200字作为描述
        lines = content.split('\n')
        desc_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('!'):
                desc_lines.append(line)
                if len(' '.join(desc_lines)) > 200:
                    break
        
        return ' '.join(desc_lines)[:300]
    
    def save_cases(self):
        """保存案例"""
        # 保存原始数据
        raw_file = self.output_dir / "raw" / "all_cases.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(c) for c in self.cases], f, 
                     ensure_ascii=False, indent=2)
        
        # 按类别保存
        categories = {}
        for case in self.cases:
            if case.category not in categories:
                categories[case.category] = []
            categories[case.category].append(asdict(case))
        
        for category, cases in categories.items():
            cat_file = self.output_dir / "processed" / f"{category}.json"
            with open(cat_file, 'w', encoding='utf-8') as f:
                json.dump(cases, f, ensure_ascii=False, indent=2)
        
        # 生成索引
        index = {
            "total_cases": len(self.cases),
            "categories": {cat: len(cases) for cat, cases in categories.items()},
            "competitions": list(set(c.competition for c in self.cases)),
            "years": sorted(list(set(c.year for c in self.cases))),
            "tools": list(set(tool for c in self.cases for tool in c.tools_used))
        }
        
        index_file = self.output_dir / "index" / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        print(f"保存完成:")
        print(f"  - 原始数据: {raw_file}")
        print(f"  - 分类数据: {len(categories)} 个类别")
        print(f"  - 索引文件: {index_file}")

def main():
    """主函数"""
    source_dir = r"E:\temp_forensics_source"
    output_dir = r"E:\forensic-ai-platform\cases"
    
    extractor = CaseExtractor(source_dir, output_dir)
    extractor.extract_from_directory()
    extractor.save_cases()

if __name__ == "__main__":
    main()

"""
HTML案例提取器 - 从Hexo博客HTML中提取取证案例
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
    source_url: str

class HTMLCaseExtractor:
    """HTML案例提取器"""
    
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.cases: List[ForensicCase] = []
        self.processed_urls = set()
        
        # 取证相关关键词
        self.forensic_keywords = [
            "取证", "美亚", "数证", "FIC", "盘古石", "平航", "SPC", 
            "警铮", "獬豸", "E01", "磁盘", "内存", "流量", "PCAP",
            "APK", "逆向", "隐写", "密码", "Volatility", "tshark"
        ]
        
        # 工具识别
        self.tool_patterns = {
            "volatility": r"vol(?:atility)?[\s\-]",
            "tshark": r"tshark[\s\-]",
            "wireshark": r"wireshark",
            "sleuthkit": r"(?:fls|icat|mmls|tsk)",
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
            "010editor": r"010\s*editor",
            "diskgenius": r"diskgenius",
            "取证大师": r"取证大师",
            "火眼": r"火眼",
        }
    
    def extract_from_html_files(self):
        """从HTML文件中提取案例"""
        print(f"开始扫描目录: {self.source_dir}")
        
        # 扫描所有HTML文件
        html_files = list(self.source_dir.rglob("*.html"))
        print(f"找到 {len(html_files)} 个HTML文件")
        
        for html_file in html_files:
            try:
                # 检查是否是取证相关
                if self._is_forensic_related(html_file):
                    self._extract_from_html(html_file)
            except Exception as e:
                print(f"处理文件失败 {html_file}: {e}")
        
        # 也扫描比赛目录中的图片描述
        self._extract_from_competition_dirs()
        
        print(f"共提取 {len(self.cases)} 个案例")
    
    def _is_forensic_related(self, file_path: Path) -> bool:
        """检查文件是否与取证相关"""
        path_str = str(file_path).lower()
        
        # 检查路径中的关键词
        for keyword in self.forensic_keywords:
            if keyword.lower() in path_str:
                return True
        
        # 检查文件内容
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            
            for keyword in self.forensic_keywords:
                if keyword.lower() in content_lower:
                    return True
        except:
            pass
        
        return False
    
    def _extract_from_html(self, html_file: Path):
        """从HTML文件提取案例"""
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # 提取标题
            title = self._extract_title(content, html_file)
            if not title:
                return
            
            # 检查是否已处理
            content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
            if content_hash in self.processed_urls:
                return
            self.processed_urls.add(content_hash)
            
            # 提取类别
            category = self._identify_category(content)
            
            # 提取工具
            tools = self._extract_tools(content)
            
            # 提取技术
            techniques = self._extract_techniques(content)
            
            # 提取描述
            description = self._extract_description(content)
            
            # 提取解题步骤
            steps = self._extract_solution_steps(content)
            
            # 提取Flag
            flags = self._extract_flags(content)
            
            # 提取关键发现
            findings = self._extract_findings(content)
            
            # 生成标签
            tags = self._generate_tags(content, category, tools)
            
            # 识别比赛
            competition = self._identify_competition(str(html_file), content)
            year = self._extract_year(str(html_file), content)
            
            # 生成ID
            case_id = f"{competition}_{year}_{content_hash}"
            
            # 生成URL
            source_url = self._generate_url(html_file)
            
            case = ForensicCase(
                case_id=case_id,
                title=title,
                category=category or "电子取证",
                competition=competition,
                year=year,
                difficulty=self._estimate_difficulty(content),
                tools_used=tools,
                techniques=techniques,
                description=description,
                solution_steps=steps,
                key_findings=findings,
                flags=flags,
                tags=tags,
                content_hash=content_hash,
                source_url=source_url
            )
            
            self.cases.append(case)
            print(f"  提取案例: {title}")
            
        except Exception as e:
            print(f"  提取失败: {e}")
    
    def _extract_from_competition_dirs(self):
        """从比赛目录提取案例"""
        # 识别比赛目录
        comp_dirs = []
        for dir_name in self.source_dir.iterdir():
            if dir_name.is_dir():
                dir_name_str = dir_name.name
                for keyword in self.forensic_keywords:
                    if keyword in dir_name_str:
                        comp_dirs.append(dir_name)
                        break
        
        print(f"找到 {len(comp_dirs)} 个比赛目录")
        
        for comp_dir in comp_dirs:
            self._process_competition_dir(comp_dir)
    
    def _process_competition_dir(self, comp_dir: Path):
        """处理比赛目录"""
        comp_name = comp_dir.name
        year = self._extract_year(comp_name, "")
        competition = self._identify_competition(comp_name, "")
        
        # 检查目录中的图片数量（作为案例复杂度的指标）
        images = list(comp_dir.glob("*.png")) + list(comp_dir.glob("*.jpg"))
        
        if len(images) > 10:  # 有足够的图片，可能是一个完整的案例
            # 创建一个基于目录的案例
            case_id = f"{competition}_{year}_dir_{comp_name}"
            
            # 尝试从目录名提取信息
            title = comp_name
            category = self._identify_category_from_name(comp_name)
            
            case = ForensicCase(
                case_id=case_id,
                title=title,
                category=category or "电子取证",
                competition=competition,
                year=year,
                difficulty="medium",
                tools_used=[],
                techniques=[],
                description=f"包含 {len(images)} 张截图的取证案例",
                solution_steps=[],
                key_findings=[],
                flags=[],
                tags=[category, competition] if category else [competition],
                content_hash=hashlib.md5(comp_name.encode()).hexdigest()[:16],
                source_url=""
            )
            
            self.cases.append(case)
            print(f"  提取目录案例: {comp_name} ({len(images)} 张图片)")
    
    def _extract_title(self, content: str, file_path: Path) -> str:
        """提取标题"""
        # 从HTML title标签提取
        match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # 清理标题
            title = title.replace(' - 玫幽倩的小博客', '').strip()
            if title and title != '玫幽倩的小博客':
                return title
        
        # 从h1标签提取
        match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # 使用文件名
        return file_path.stem
    
    def _identify_category(self, content: str) -> str:
        """识别取证类别"""
        content_lower = content.lower()
        
        category_keywords = {
            "磁盘取证": ["E01", "磁盘", "镜像", "分区", "文件系统", "NTFS", "FAT", "diskgenius"],
            "网络取证": ["PCAP", "流量", "网络", "HTTP", "DNS", "TCP", "Wireshark", "tshark"],
            "内存取证": ["内存", "RAM", "dump", "Volatility", "进程"],
            "移动取证": ["APK", "安卓", "Android", "手机", "APP"],
            "密码学": ["加密", "解密", "RSA", "AES", "Base64", "哈希", "hashcat"],
            "隐写分析": ["隐写", "图片", "LSB", "steghide", "音频", "zsteg"],
            "逆向工程": ["逆向", "二进制", "PE", "ELF", "反编译"],
            "服务器取证": ["服务器", "Web", "日志", "Linux", "数据库"],
            "应急响应": ["挖矿", "勒索", "Webshell", "后门", "入侵"],
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    return category
        
        return None
    
    def _identify_category_from_name(self, name: str) -> str:
        """从名称识别类别"""
        name_lower = name.lower()
        
        if any(kw in name_lower for kw in ["取证", "美亚", "数证", "FIC", "盘古石", "平航", "SPC"]):
            return "电子取证"
        if any(kw in name_lower for kw in ["流量", "网络", "PCAP"]):
            return "网络取证"
        if any(kw in name_lower for kw in ["内存", "dump"]):
            return "内存取证"
        if any(kw in name_lower for kw in ["APK", "安卓", "Android"]):
            return "移动取证"
        
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
        }
        
        for technique, pattern in patterns.items():
            if re.search(pattern, content):
                techniques.append(technique)
        
        return techniques
    
    def _extract_description(self, content: str) -> str:
        """提取描述"""
        # 提取文章摘要
        match = re.search(r'<div[^>]*class="[^"]*excerpt[^"]*"[^>]*>(.*?)</div>', content, re.DOTALL | re.IGNORECASE)
        if match:
            desc = re.sub(r'<[^>]+>', '', match.group(1))
            return desc.strip()[:300]
        
        # 提取前200字
        text = re.sub(r'<[^>]+>', ' ', content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:300] if len(text) > 300 else text
    
    def _extract_solution_steps(self, content: str) -> List[str]:
        """提取解题步骤"""
        steps = []
        
        # 查找有序列表
        step_pattern = r'<li[^>]*>(.*?)</li>'
        matches = re.findall(step_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in matches[:10]:
            step = re.sub(r'<[^>]+>', '', match).strip()
            if step and len(step) > 10:
                steps.append(step)
        
        return steps
    
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
            matches = re.findall(pattern, content, re.IGNORECASE)
            flags.extend(matches)
        
        return list(set(flags))
    
    def _extract_findings(self, content: str) -> List[str]:
        """提取关键发现"""
        findings = []
        
        # 查找代码块中的关键信息
        code_blocks = re.findall(r'<code[^>]*>(.*?)</code>', content, re.DOTALL)
        for code in code_blocks[:5]:
            code = re.sub(r'<[^>]+>', '', code).strip()
            if code and len(code) > 5:
                findings.append(code)
        
        return findings
    
    def _generate_tags(self, content: str, category: str, tools: List[str]) -> List[str]:
        """生成标签"""
        tags = []
        
        if category:
            tags.append(category)
        
        tags.extend(tools[:3])
        
        # 添加其他标签
        if "CTF" in content:
            tags.append("CTF")
        if "Writeup" in content or "writeup" in content.lower():
            tags.append("Writeup")
        
        return list(set(tags))[:10]
    
    def _identify_competition(self, path: str, content: str) -> str:
        """识别比赛"""
        path_lower = path.lower()
        content_lower = content.lower()
        
        competitions = {
            "美亚杯": ["美亚"],
            "FIC": ["fic"],
            "数证杯": ["数证"],
            "盘古石": ["盘古石"],
            "平航杯": ["平航"],
            "SPC": ["spc"],
            "警铮杯": ["警铮"],
            "獬豸杯": ["獬豸"],
            "NSSCTF": ["nssctf"],
            "CTFshow": ["ctfshow"],
        }
        
        for comp, keywords in competitions.items():
            for keyword in keywords:
                if keyword in path_lower or keyword in content_lower:
                    return comp
        
        return "其他"
    
    def _extract_year(self, path: str, content: str) -> int:
        """提取年份"""
        match = re.search(r'(20\d{2})', path)
        if match:
            return int(match.group(1))
        
        match = re.search(r'(20\d{2})', content)
        if match:
            return int(match.group(1))
        
        return 2025
    
    def _estimate_difficulty(self, content: str) -> str:
        """估算难度"""
        if len(content) > 10000:
            return "hard"
        elif len(content) > 3000:
            return "medium"
        else:
            return "easy"
    
    def _generate_url(self, file_path: Path) -> str:
        """生成URL"""
        # 将文件路径转换为URL格式
        rel_path = file_path.relative_to(self.source_dir)
        url_path = str(rel_path).replace('\\', '/').replace('.html', '')
        return f"https://mei-you-qian.github.io/{url_path}"
    
    def save_cases(self):
        """保存案例"""
        # 保存原始数据
        raw_file = self.output_dir / "raw" / "all_cases.json"
        os.makedirs(raw_file.parent, exist_ok=True)
        
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
            os.makedirs(cat_file.parent, exist_ok=True)
            with open(cat_file, 'w', encoding='utf-8') as f:
                json.dump(cases, f, ensure_ascii=False, indent=2)
        
        # 按比赛保存
        competitions = {}
        for case in self.cases:
            if case.competition not in competitions:
                competitions[case.competition] = []
            competitions[case.competition].append(asdict(case))
        
        for comp, cases in competitions.items():
            comp_file = self.output_dir / "processed" / f"competition_{comp}.json"
            os.makedirs(comp_file.parent, exist_ok=True)
            with open(comp_file, 'w', encoding='utf-8') as f:
                json.dump(cases, f, ensure_ascii=False, indent=2)
        
        # 生成索引
        index = {
            "total_cases": len(self.cases),
            "categories": {cat: len(cases) for cat, cases in categories.items()},
            "competitions": {comp: len(cases) for comp, cases in competitions.items()},
            "years": sorted(list(set(c.year for c in self.cases))),
            "tools": list(set(tool for c in self.cases for tool in c.tools_used))
        }
        
        index_file = self.output_dir / "index" / "index.json"
        os.makedirs(index_file.parent, exist_ok=True)
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        print(f"\n保存完成:")
        print(f"  - 总案例数: {len(self.cases)}")
        print(f"  - 原始数据: {raw_file}")
        print(f"  - 分类数据: {len(categories)} 个类别")
        print(f"  - 比赛数据: {len(competitions)} 个比赛")
        print(f"  - 索引文件: {index_file}")

def main():
    """主函数"""
    source_dir = r"E:\temp_forensics_source"
    output_dir = r"E:\forensic-ai-platform\cases"
    
    extractor = HTMLCaseExtractor(source_dir, output_dir)
    extractor.extract_from_html_files()
    extractor.save_cases()

if __name__ == "__main__":
    main()

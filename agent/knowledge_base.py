"""
知识库管理 - 管理取证技能文档和案例
"""
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class SkillDocument:
    """技能文档"""
    skill_id: str
    name: str
    category: str
    content: str
    file_path: str
    tags: List[str] = None

class KnowledgeBase:
    """知识库"""
    
    def __init__(self, skills_dir: str = None):
        """初始化知识库"""
        self.skills_dir = skills_dir or self._find_skills_dir()
        self.skills: Dict[str, SkillDocument] = {}
        self._load_skills()
    
    def _find_skills_dir(self) -> str:
        """查找技能目录"""
        possible_paths = [
            Path(__file__).parent.parent / "skills",
            Path("skills"),
            Path.home() / "forensic-ai-platform" / "skills"
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                return str(path)
        
        return ""
    
    def _load_skills(self):
        """加载技能文档"""
        if not self.skills_dir or not os.path.exists(self.skills_dir):
            logger.warning(f"技能目录不存在: {self.skills_dir}")
            return
        
        skills_path = Path(self.skills_dir)
        
        for md_file in skills_path.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # 提取技能信息
                skill_id = md_file.stem
                name = self._extract_name(content, md_file)
                category = self._extract_category(content)
                tags = self._extract_tags(content)
                
                skill = SkillDocument(
                    skill_id=skill_id,
                    name=name,
                    category=category,
                    content=content,
                    file_path=str(md_file),
                    tags=tags
                )
                
                self.skills[skill_id] = skill
                
            except Exception as e:
                logger.error(f"加载技能失败 {md_file}: {e}")
        
        logger.info(f"加载了 {len(self.skills)} 个技能文档")
    
    def _extract_name(self, content: str, file_path: Path) -> str:
        """提取技能名称"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return file_path.stem.replace('-', ' ').title()
    
    def _extract_category(self, content: str) -> str:
        """提取类别"""
        keywords = {
            "disk": ["磁盘", "E01", "镜像", "分区"],
            "network": ["网络", "流量", "PCAP", "HTTP"],
            "memory": ["内存", "RAM", "dump", "进程"],
            "android": ["Android", "APK", "手机"],
            "crypto": ["加密", "解密", "密码", "RSA"],
            "stego": ["隐写", "图片", "LSB"],
            "reverse": ["逆向", "二进制", "反编译"]
        }
        
        content_lower = content.lower()
        for category, kws in keywords.items():
            for kw in kws:
                if kw.lower() in content_lower:
                    return category
        
        return "general"
    
    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = []
        
        # 从内容中提取工具名
        tools = ["tshark", "sleuthkit", "volatility", "jadx", "exiftool", 
                 "strings", "file", "binwalk", "steghide", "hashcat"]
        
        content_lower = content.lower()
        for tool in tools:
            if tool in content_lower:
                tags.append(tool)
        
        return tags
    
    def search(self, query: str, top_k: int = 5) -> List[SkillDocument]:
        """搜索技能"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        for skill in self.skills.values():
            # 计算匹配分数
            score = 0.0
            
            # 名称匹配
            if query_lower in skill.name.lower():
                score += 3.0
            
            # 内容匹配
            content_lower = skill.content.lower()
            if query_lower in content_lower:
                score += 2.0
            
            # 单词匹配
            for word in query_words:
                if word in content_lower:
                    score += 1.0
            
            # 标签匹配
            if skill.tags:
                for tag in skill.tags:
                    if tag in query_lower:
                        score += 2.0
            
            if score > 0:
                results.append((score, skill))
        
        # 排序并返回top_k
        results.sort(key=lambda x: x[0], reverse=True)
        return [skill for _, skill in results[:top_k]]
    
    def get_skill(self, skill_id: str) -> Optional[SkillDocument]:
        """获取指定技能"""
        return self.skills.get(skill_id)
    
    def get_skills_by_category(self, category: str) -> List[SkillDocument]:
        """按类别获取技能"""
        return [s for s in self.skills.values() if s.category == category]
    
    def get_all_categories(self) -> List[str]:
        """获取所有类别"""
        return list(set(s.category for s in self.skills.values()))
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        categories = {}
        for skill in self.skills.values():
            categories[skill.category] = categories.get(skill.category, 0) + 1
        
        return {
            "total_skills": len(self.skills),
            "categories": categories
        }

"""
案例库管理 - 管理取证案例数据
支持检索、过滤、统计等功能
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CaseQuery:
    """案例查询"""
    keyword: str = None
    category: str = None
    competition: str = None
    year: int = None
    difficulty: str = None
    tools: List[str] = None
    tags: List[str] = None
    limit: int = 10

class CaseLibrary:
    """案例库"""
    
    def __init__(self, cases_dir: str = None):
        """初始化案例库"""
        self.cases_dir = cases_dir or self._find_cases_dir()
        self.cases: List[Dict[str, Any]] = []
        self.index: Dict[str, Any] = {}
        self._load_cases()
    
    def _find_cases_dir(self) -> str:
        """查找案例目录"""
        possible_paths = [
            Path(__file__).parent.parent / "cases",
            Path("cases"),
            Path.home() / "forensic-ai-platform" / "cases"
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                return str(path)
        
        return ""
    
    def _load_cases(self):
        """加载案例"""
        if not self.cases_dir or not os.path.exists(self.cases_dir):
            logger.warning(f"案例目录不存在: {self.cases_dir}")
            return
        
        # 加载索引
        index_file = Path(self.cases_dir) / "index" / "index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        
        # 加载所有案例
        raw_file = Path(self.cases_dir) / "raw" / "all_cases.json"
        if raw_file.exists():
            with open(raw_file, 'r', encoding='utf-8') as f:
                self.cases = json.load(f)
        
        logger.info(f"加载了 {len(self.cases)} 个案例")
    
    def search(self, query: CaseQuery) -> List[Dict[str, Any]]:
        """搜索案例"""
        results = []
        
        for case in self.cases:
            score = self._calculate_score(case, query)
            if score > 0:
                results.append((score, case))
        
        # 按分数排序
        results.sort(key=lambda x: x[0], reverse=True)
        
        # 返回指定数量的结果
        return [case for _, case in results[:query.limit]]
    
    def _calculate_score(self, case: Dict[str, Any], query: CaseQuery) -> float:
        """计算匹配分数"""
        score = 0.0
        
        # 关键词匹配
        if query.keyword:
            keyword_lower = query.keyword.lower()
            
            # 标题匹配
            if keyword_lower in case.get("title", "").lower():
                score += 3.0
            
            # 描述匹配
            if keyword_lower in case.get("description", "").lower():
                score += 2.0
            
            # 标签匹配
            for tag in case.get("tags", []):
                if keyword_lower in tag.lower():
                    score += 1.0
        
        # 类别匹配
        if query.category:
            if case.get("category") == query.category:
                score += 2.0
        
        # 比赛匹配
        if query.competition:
            if case.get("competition") == query.competition:
                score += 2.0
        
        # 年份匹配
        if query.year:
            if case.get("year") == query.year:
                score += 1.0
        
        # 难度匹配
        if query.difficulty:
            if case.get("difficulty") == query.difficulty:
                score += 1.0
        
        # 工具匹配
        if query.tools:
            case_tools = set(case.get("tools_used", []))
            query_tools = set(query.tools)
            overlap = case_tools & query_tools
            score += len(overlap) * 0.5
        
        # 标签匹配
        if query.tags:
            case_tags = set(case.get("tags", []))
            query_tags = set(query.tags)
            overlap = case_tags & query_tags
            score += len(overlap) * 0.5
        
        return score
    
    def get_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取案例"""
        for case in self.cases:
            if case.get("case_id") == case_id:
                return case
        return None
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按类别获取案例"""
        return [c for c in self.cases if c.get("category") == category]
    
    def get_by_competition(self, competition: str) -> List[Dict[str, Any]]:
        """按比赛获取案例"""
        return [c for c in self.cases if c.get("competition") == competition]
    
    def get_categories(self) -> List[str]:
        """获取所有类别"""
        return list(set(c.get("category") for c in self.cases if c.get("category")))
    
    def get_competitions(self) -> List[str]:
        """获取所有比赛"""
        return list(set(c.get("competition") for c in self.cases if c.get("competition")))
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.index or {
            "total_cases": len(self.cases),
            "categories": {},
            "competitions": {},
            "years": [],
            "tools": []
        }
    
    def add_case(self, case: Dict[str, Any]):
        """添加案例"""
        # 生成ID
        if "case_id" not in case:
            import hashlib
            content = json.dumps(case, sort_keys=True)
            case["case_id"] = hashlib.md5(content.encode()).hexdigest()[:16]
        
        self.cases.append(case)
        self._save_cases()
    
    def _save_cases(self):
        """保存案例"""
        raw_file = Path(self.cases_dir) / "raw" / "all_cases.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(self.cases, f, ensure_ascii=False, indent=2)
        
        # 更新索引
        self._update_index()
    
    def _update_index(self):
        """更新索引"""
        categories = {}
        competitions = {}
        years = set()
        tools = set()
        
        for case in self.cases:
            cat = case.get("category")
            if cat:
                categories[cat] = categories.get(cat, 0) + 1
            
            comp = case.get("competition")
            if comp:
                competitions[comp] = competitions.get(comp, 0) + 1
            
            year = case.get("year")
            if year:
                years.add(year)
            
            for tool in case.get("tools_used", []):
                tools.add(tool)
        
        self.index = {
            "total_cases": len(self.cases),
            "categories": categories,
            "competitions": competitions,
            "years": sorted(list(years)),
            "tools": list(tools)
        }
        
        index_file = Path(self.cases_dir) / "index" / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def export_for_training(self, output_path: str, format: str = "jsonl"):
        """导出训练数据"""
        training_data = []
        
        for case in self.cases:
            # 生成问答对
            qa_pairs = self._generate_qa_pairs(case)
            training_data.extend(qa_pairs)
        
        if format == "jsonl":
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in training_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"导出 {len(training_data)} 条训练数据到 {output_path}")
        return len(training_data)
    
    def _generate_qa_pairs(self, case: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成问答对"""
        qa_pairs = []
        
        # 基本信息问答
        if case.get("title"):
            qa_pairs.append({
                "question": f"介绍一下{case['title']}这个案例",
                "answer": self._format_case_answer(case)
            })
        
        # 工具相关问答
        if case.get("tools_used"):
            tools_str = "、".join(case["tools_used"])
            qa_pairs.append({
                "question": f"{case.get('category', '取证')}分析通常使用哪些工具？",
                "answer": f"根据案例经验，{case.get('category', '取证')}分析通常使用以下工具：{tools_str}"
            })
        
        # 技术相关问答
        if case.get("techniques"):
            tech_str = "、".join(case["techniques"])
            qa_pairs.append({
                "question": f"{case.get('category', '取证')}有哪些常用技术？",
                "answer": f"根据案例经验，{case.get('category', '取证')}常用技术包括：{tech_str}"
            })
        
        return qa_pairs
    
    def _format_case_answer(self, case: Dict[str, Any]) -> str:
        """格式化案例答案"""
        parts = []
        
        parts.append(f"案例名称：{case.get('title', '未知')}")
        parts.append(f"类别：{case.get('category', '未知')}")
        parts.append(f"比赛：{case.get('competition', '未知')}")
        parts.append(f"年份：{case.get('year', '未知')}")
        
        if case.get("description"):
            parts.append(f"\n描述：{case['description']}")
        
        if case.get("tools_used"):
            tools_str = "、".join(case["tools_used"])
            parts.append(f"\n使用工具：{tools_str}")
        
        if case.get("techniques"):
            tech_str = "、".join(case["techniques"])
            parts.append(f"\n涉及技术：{tech_str}")
        
        return "\n".join(parts)

# 全局实例
case_library = CaseLibrary()

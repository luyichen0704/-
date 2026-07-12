"""
GitHub Writeup搜索器 - 搜索GitHub上的取证比赛Writeup
"""
import os
import json
import re
import requests
from typing import List, Dict, Any
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)

class GitHubWriteupSearcher:
    """GitHub Writeup搜索器"""
    
    def __init__(self, output_dir: str = None):
        """初始化搜索器"""
        self.output_dir = output_dir or r"E:\forensic-ai-platform\cases\github"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # GitHub API配置
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.headers = {}
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
        
        # 取证相关搜索关键词
        self.search_queries = [
            "forensics writeup CTF",
            "digital forensics writeup",
            "电子取证 writeup",
            "美亚杯 writeup",
            "FIC 取证 writeup",
            "数证杯 writeup",
            "盘古石 取证",
            "memory forensics writeup",
            "disk forensics writeup",
            "network forensics writeup",
            "malware analysis writeup",
            "incident response writeup",
        ]
        
        # 取证相关GitHub仓库
        self.forensic_repos = [
            "chiwent/ctf-writeups",
            "ForensicWiki/forensicwiki",
            "dfir-notes/dfir-notes",
            "digital-forensics/forensics-wiki",
        ]
    
    def search_writeups(self, max_results: int = 100):
        """搜索Writeup"""
        all_writeups = []
        
        print("开始搜索GitHub取证Writeup...")
        
        for query in self.search_queries:
            print(f"\n搜索: {query}")
            writeups = self._search_code(query, max_results // len(self.search_queries))
            all_writeups.extend(writeups)
            
            # 避免API限制
            time.sleep(2)
        
        # 去重
        unique_writeups = self._deduplicate(all_writeups)
        
        print(f"\n共找到 {len(unique_writeups)} 个Writeup")
        
        # 保存结果
        self._save_writeups(unique_writeups)
        
        return unique_writeups
    
    def _search_code(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """搜索GitHub代码"""
        writeups = []
        
        try:
            # 使用GitHub搜索API
            url = "https://api.github.com/search/code"
            params = {
                "q": f"{query} language:markdown",
                "sort": "indexed",
                "order": "desc",
                "per_page": min(max_results, 30)
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("items", []):
                    writeup = {
                        "title": item.get("name", "").replace(".md", ""),
                        "repo": item.get("repository", {}).get("full_name", ""),
                        "path": item.get("path", ""),
                        "url": item.get("html_url", ""),
                        "score": item.get("score", 0)
                    }
                    
                    # 检查是否是取证相关
                    if self._is_forensic_related(writeup):
                        writeups.append(writeup)
            
            else:
                print(f"  API请求失败: {response.status_code}")
        
        except Exception as e:
            print(f"  搜索失败: {e}")
        
        return writeups
    
    def _is_forensic_related(self, writeup: Dict[str, Any]) -> bool:
        """检查是否是取证相关"""
        forensic_keywords = [
            "forensic", "取证", "美亚", "FIC", "数证", "盘古石",
            "memory", "disk", "network", "malware", "incident",
            "volatility", "autopsy", "sleuthkit", "tshark"
        ]
        
        title_lower = writeup.get("title", "").lower()
        path_lower = writeup.get("path", "").lower()
        
        for keyword in forensic_keywords:
            if keyword.lower() in title_lower or keyword.lower() in path_lower:
                return True
        
        return False
    
    def _deduplicate(self, writeups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重"""
        seen = set()
        unique = []
        
        for w in writeups:
            key = w.get("url", "")
            if key not in seen:
                seen.add(key)
                unique.append(w)
        
        return unique
    
    def _save_writeups(self, writeups: List[Dict[str, Any]]):
        """保存Writeup"""
        output_file = os.path.join(self.output_dir, "github_writeups.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(writeups, f, ensure_ascii=False, indent=2)
        
        print(f"保存到: {output_file}")
        
        # 生成统计信息
        stats = {
            "total": len(writeups),
            "repos": list(set(w.get("repo") for w in writeups if w.get("repo"))),
            "by_repo": {}
        }
        
        for w in writeups:
            repo = w.get("repo", "unknown")
            stats["by_repo"][repo] = stats["by_repo"].get(repo, 0) + 1
        
        stats_file = os.path.join(self.output_dir, "search_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    
    def fetch_writeup_content(self, writeup: Dict[str, Any]) -> str:
        """获取Writeup内容"""
        try:
            # 尝试直接访问原始文件
            raw_url = writeup.get("url", "").replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            
            response = requests.get(raw_url, headers=self.headers)
            
            if response.status_code == 200:
                return response.text
            
        except Exception as e:
            logger.error(f"获取内容失败: {e}")
        
        return ""

def main():
    """主函数"""
    searcher = GitHubWriteupSearcher()
    writeups = searcher.search_writeups(max_results=50)
    
    print(f"\n搜索完成，共找到 {len(writeups)} 个Writeup")

if __name__ == "__main__":
    main()

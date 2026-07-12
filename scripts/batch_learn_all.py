"""
批量学习所有待学习的仓库
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.extract_batch_writeups import BatchWriteupExtractor

# 待学习的CTF Writeup仓库
CTF_REPOS = [
    ("https://github.com/ctfs/write-ups-2013.git", 2013),
    ("https://github.com/ctfs/write-ups-2014.git", 2014),
    ("https://github.com/ctfs/write-ups-2018.git", 2018),
    ("https://github.com/ctfs/write-ups-2019.git", 2019),
    ("https://github.com/ctfs/write-ups-2020.git", 2020),
    ("https://github.com/ctfs/write-ups-2021.git", 2021),
    ("https://github.com/ctfs/write-ups-2022.git", 2022),
    ("https://github.com/ctfs/write-ups-2023.git", 2023),
    ("https://github.com/ctfs/write-ups-2024.git", 2024),
]

def main():
    output_dir = r"E:\forensic-ai-platform\cases"
    
    print("=" * 60)
    print("批量学习所有待学习的CTF Writeup仓库")
    print("=" * 60)
    
    total_cases = 0
    
    for repo_url, year in CTF_REPOS:
        print(f"\n{'='*60}")
        print(f"学习 {year} 年CTF Writeup")
        print(f"{'='*60}")
        
        try:
            extractor = BatchWriteupExtractor(output_dir)
            extractor.extract_from_repo(repo_url, year)
            extractor.save_cases()
            
            total_cases += len(extractor.cases)
            print(f"完成: {len(extractor.cases)} 个案例")
            
        except Exception as e:
            print(f"失败: {e}")
    
    print(f"\n{'='*60}")
    print(f"批量学习完成")
    print(f"共提取: {total_cases} 个案例")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

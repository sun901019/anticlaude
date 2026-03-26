import os
import glob
import re
from pathlib import Path

# 目標目錄
HUB_DIR = Path("c:/Users/sun90/Anticlaude/_hub")
SKILLS_LIB = HUB_DIR / "skills_library"
OUTPUT_REPORT = HUB_DIR / "extracted_capabilities.md"

# 九大核心分類關鍵字
CATEGORIES = {
    "research_analysis": ["research", "analysis", "competitor", "trend", "調查", "分析", "趨勢", "競品"],
    "marketing_strategy": ["marketing", "strategy", "campaign", "audience", "行銷", "策略", "受眾"],
    "content_creation": ["content", "writer", "copywriting", "blog", "post", "threads", "文案", "寫手", "貼文", "文章"],
    "seo_optimization": ["seo", "keyword", "ranking", "search", "優化", "關鍵字", "排名"],
    "text_humanization": ["humanize", "natural", "tone", "ai", "人性化", "降重", "去ai", "語氣"],
    "presentation_ui": ["presentation", "slides", "ui", "design", "frontend", "簡報", "設計", "前端", "介面"],
    "data_processing": ["data", "processing", "clean", "format", "json", "csv", "數據", "處理", "清理", "格式", "toonify"],
    "project_planning": ["planning", "project", "manager", "pm", "task", "專案", "計畫", "拆解", "管理"],
    "coding_agent": ["code", "developer", "backend", "devops", "script", "開發", "後端", "程式", "腳本"]
}

def scan_repositories():
    if not SKILLS_LIB.exists():
        print(f"Directory not found: {SKILLS_LIB}")
        return

    report = []
    report.append("# 🧠 原始技能庫盤點報告 (Raw Capability Extraction)")
    report.append("\n> 本文件由掃描腳本自動生成，列出 9 個庫中所有被抓取到的 Markdown 檔案，以作為後續手動融合 (Composite) 的材料清單。\n")

    total_files = 0

    for repo_dir in SKILLS_LIB.iterdir():
        if not repo_dir.is_dir():
            continue
            
        repo_name = repo_dir.name
        report.append(f"## 📦 Repository: {repo_name}")
        
        # 尋找所有 .md 檔案 (排除 README 跟一些常見的非技能檔)
        md_files = []
        for root, _, files in os.walk(repo_dir):
            for f in files:
                if f.endswith('.md') and f.lower() not in ['readme.md', 'license.md', 'contributing.md', 'changelog.md']:
                    md_files.append(Path(root) / f)
        
        if not md_files:
            report.append("- `[無可萃取的 Markdown 技能檔]`\n")
            continue
            
        report.append(f"*共發現 {len(md_files)} 個潛在技能檔案*\n")
        total_files += len(md_files)
        
        for md_path in md_files:
            # 讀取前 20 行來判斷功能
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    preview = f.read(1000) # 取前 1000 字元掃描關鍵字
            except Exception:
                preview = ""
                
            # 簡單判斷這屬於哪個 Category
            rel_path = md_path.relative_to(repo_dir)
            file_name = md_path.name
            search_text = (file_name + " " + preview).lower()
            
            # 使用關鍵字推測分類
            matched_categories = []
            for cat, keywords in CATEGORIES.items():
                if any(kw in search_text for kw in keywords):
                    matched_categories.append(cat)
            
            if not matched_categories:
                matched_categories = ["uncategorized"]
                
            cat_str = ", ".join(matched_categories)
            report.append(f"- **{file_name}** (`{rel_path}`) → 🏷️ 推測分類：`{cat_str}`")
            
        report.append("\n---\n")

    report.insert(2, f"**總共掃描到: {total_files} 個潛在技能檔案**\n")
    
    # 寫入報告
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
        
    print(f"Extraction report generated at: {OUTPUT_REPORT}")
    print(f"Total skills scanned: {total_files}")

if __name__ == "__main__":
    scan_repositories()

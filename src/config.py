"""
環境變數讀取與驗證
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # === 資料來源 ===
    serper_api_key: Optional[str] = None
    pplx_api_key: Optional[str] = None

    # === AI 模型 API Keys ===
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # === Model Routing（可透過 .env 覆蓋，預設最佳化配置）===
    # 聚類：模式識別，不需複雜推理 → Haiku 節省成本
    model_cluster: str = "claude-haiku-4-5-20251001"
    # 評分：多維度複雜判斷 → Sonnet 保持品質
    model_score: str = "claude-sonnet-4-6"
    # 文案生成：創意寫作，品質優先 → Sonnet
    model_write: str = "claude-sonnet-4-6"
    # 文案驗證：規則檢查，不需複雜推理 → Haiku 節省成本
    model_verify: str = "claude-haiku-4-5-20251001"
    # 選題策略：多樣性推理 → GPT-4o
    model_strategy: str = "gpt-4o"
    # 週報生成：長文整理 → Sonnet
    model_weekly: str = "claude-sonnet-4-6"

    # === Threads ===
    threads_app_id: str = "2047745122833004"
    threads_access_token: Optional[str] = None
    threads_user_id: Optional[str] = None

    # === LINE Messaging API ===
    line_channel_access_token: Optional[str] = None
    line_user_id: Optional[str] = None

    # === Figma ===
    figma_api_token: Optional[str] = None      # Personal Access Token (read-only)

    # === X (Twitter) ===
    x_api_key: Optional[str] = None
    x_api_key_secret: Optional[str] = None
    x_access_token: Optional[str] = None
    x_access_token_secret: Optional[str] = None
    x_bearer_token: Optional[str] = None       # App-only, for search/analytics

    # === Browser / CDP ===
    browser_headless: bool = True              # always headless in production
    browser_profile_dir: Optional[str] = None  # isolated profile path

    # === 可選 ===
    notebooklm_api_key: Optional[str] = None

    # === 競品監控 ===
    # 逗號分隔的商品關鍵字，例如 "無線耳機,藍牙音箱,行動電源"
    # 設定後會在每日 20:00 自動監控競品價格並發 LINE 通知
    competitor_keywords_raw: Optional[str] = None

    @property
    def competitor_keywords(self) -> list[str]:
        if not self.competitor_keywords_raw:
            return []
        return [k.strip() for k in self.competitor_keywords_raw.split(",") if k.strip()]

    model_config = {"env_file": BASE_DIR / ".env", "case_sensitive": False}

    def check_required(self) -> list[str]:
        """回傳尚未設定的必要 Key 清單"""
        missing = []
        if not self.serper_api_key:
            missing.append("SERPER_API_KEY")
        if not self.pplx_api_key:
            missing.append("PPLX_API_KEY")
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.threads_access_token:
            missing.append("THREADS_ACCESS_TOKEN")
        if not self.threads_user_id:
            missing.append("THREADS_USER_ID")
        return missing


settings = Settings()

# 路徑常數
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
CONTEXT_DIR = BASE_DIR / "_context"
LOGS_DIR = BASE_DIR / "logs"

ABOUT_ME_PATH = CONTEXT_DIR / "about_me.md"
WORKFLOW_PATH = CONTEXT_DIR / "workflow.md"

DAILY_REPORTS_DIR = OUTPUTS_DIR / "daily_reports"
DRAFTS_DIR = OUTPUTS_DIR / "drafts"
THREADS_METRICS_DIR = OUTPUTS_DIR / "threads_metrics"
WEEKLY_REPORTS_DIR = OUTPUTS_DIR / "weekly_reports"
RAW_FEED_DIR = UPLOADS_DIR


if __name__ == "__main__":
    missing = settings.check_required()
    if missing:
        print(f"⚠️  尚未設定的 API Key：{', '.join(missing)}")
        print("請複製 .env.example 為 .env 並填入對應的值")
    else:
        print("✅ 所有 API Key 已設定")
    print(f"BASE_DIR: {BASE_DIR}")

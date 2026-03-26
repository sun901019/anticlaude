# plan_20260315_office_light_theme.md
> 建立日期：2026-03-15

## 目標
讓 AI Office 頁面與網站其他頁面風格統一（暖白主題），並修正卡片結構、英文文字與 demo 殘留問題。

## 變更清單

### 1. src/api/agent_status.py
- `desc` 欄位全部改中文
- `restore_today_state()` 加時間檢查：`updated_at` 超過 30 分鐘不恢復（消除 demo 殘留）

### 2. dashboard/src/app/office/page.tsx（視覺整體重構）

#### 色彩系統替換
- 背景 `#09090f` → `var(--bg)` (#faf9f7 暖米白)
- 卡片 dark rgba → `var(--surface)` / `var(--border)`
- 文字 `text-white` / `rgba(255,255,255,0.XX)` → `var(--text-1/2/3)`
- 狀態色：保留語意（紫/橙/綠/琥珀），調成適合淺色背景的深色版本
  - working: accent 紫 `#7c5cbf`
  - blocked: 橙 `#b45309`
  - done: 綠 `#16a34a`
  - awaiting_human: 琥珀 `#b45309`
  - handoff_pending: 紫

#### AgentCard 結構重構
舊（窄）：
```
[頭像] [名字/角色] [badge]
       [desc]
       [任務黑框] ← 只佔右欄
```
新（全寬）：
```
[頭像] [名字/角色]        [badge]
[desc - 全寬]
[任務框 - 全寬]
  任務標題
  來源 | 下一棒 | 已進行
  產出
[今日區塊 - 全寬]
```

#### 其他 UI 元件
- SystemHealthPanel：改淺色卡片風格
- 進行中面板：改淺色
- 活動流：改淺色
- scanline 動畫：改 accent 色（紫色光帶）

## 驗收條件
- [x] 頁面背景、卡片與其他頁面視覺一致（程式碼已改，需重啟後確認）
- [x] 所有 agent 描述顯示中文（agent_status.py 已改，需重啟後確認）
- [x] 任務區塊與產出佔滿卡片整行寬度
- [x] 重啟後 demo 數據不再復原（restore_today_state 加 30 分鐘檢查）

> 備註：start.ps1 舊版本不會自動 kill 舊程序，導致重啟後仍跑舊 server。
> 已修正 start.ps1（2026-03-15），下次用 .\start.ps1 重啟即可全部生效。

"""
Adapters Layer — 外部系統汙染隔離層
======================================
所有外部系統整合必須透過此層，禁止在 agent/route 直接呼叫外部 SDK。

規則（來自 aitos_token_memory_skill_integration_consolidation_20260319.md §7）：
  - zero-contamination boundary
  - Pydantic-typed I/O
  - timeout + exception shielding
  - normalized error result
  - risk_level 定義

目錄結構：
  base.py      — AdapterBase ABC + AdapterResult Pydantic model
  registry.py  — ADAPTER_REGISTRY 全局登記表
  x_adapter.py — X（Twitter）發文適配器（stub，待 token）
  figma_adapter.py — Figma API 適配器（stub，待 token）
"""

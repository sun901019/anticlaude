"""
Flow Lab 電商 API Router
掛載到 FastAPI：app.include_router(ecommerce_router, prefix="/api/ecommerce")
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db.connection import db

from src.ecommerce.selection import selection_router

router = APIRouter(tags=["ecommerce"])
router.include_router(selection_router)

# ─── 預設參數（DB 優先，DB 無資料時 fallback 這裡）──────────────────────────
# 2026 蝦皮費率全面更新
_DEFAULT_SETTINGS = {
    # 匯率
    "exchange_rate":            ("4.5",   "人民幣匯率",                   "RMB→TWD"),
    # 蝦皮費率（2026）
    "commission_fee":           ("0.06",  "基礎成交手續費（平日）",         "%"),
    "transaction_fee":          ("0.025", "金流服務費（2026）",             "%"),
    "fss_pct":                  ("0.06",  "免運服務費-百分比制",             "%"),
    "fss_fixed":                ("60",    "免運服務費-固定金額制",           "NT$/單"),
    "fss_threshold":            ("1000",  "FSS切換門檻（售價>此值用固定制）","NT$"),
    "promo_surcharge":          ("0.02",  "促銷日加成手續費（未參加CCB10時）","%"),
    "fulfillment_penalty":      ("0.03",  "備貨>2天懲罰費率",               "%"),
    # 末端物流
    "shipping_per_kg":          ("40",    "末端配送費（蝦皮官方物流）",       "NT$/kg"),
    # 集運費率
    "air_freight_per_kg":       ("115",   "空運費率（3-5天）",               "TWD/kg"),
    "sea_fast_per_kg":          ("45",    "海快費率（5-8天，主流）",          "TWD/kg"),
    "sea_regular_per_kg":       ("20",    "海運費率（12-15天）",              "TWD/kg"),
    "special_goods_surcharge":  ("15",    "特貨加成（帶電/磁性/液體）",       "TWD/kg"),
    # 其他
    "low_stock_days":           ("7",     "低庫存警示天數",                  "天"),
    "default_return_rate":      ("0.02",  "預設退貨率",                      "%"),
    "default_damage_rate":      ("0.01",  "預設破損率",                      "%"),
    # 角色毛利門檻（可調節）
    "traffic_margin_target":    ("0.25",  "引流款目標毛利率",                 "%"),
    "core_margin_target":       ("0.40",  "毛利款目標毛利率",                 "%"),
    "profit_margin_target":     ("0.55",  "主力款目標毛利率",                 "%"),
    # QQL 採購代理設定
    "qql_exchange_rate":        ("4.5",   "QQL 人民幣匯率",                  "RMB→TWD"),
    "qql_service_fee":          ("0.03",  "QQL 代購服務費",                  "%"),
    "sea_express_rate":         ("45",    "QQL 海快集運費率",                 "TWD/kg"),
    "volumetric_divisor":       ("6000",  "體積重計算除數",                   "cm³/kg"),
    # 舊欄位保留向下相容
    "platform_fee":             ("0.06",  "平台手續費（舊，同commission_fee）","%"),
    "payment_fee":              ("0.025", "金流手續費（舊，同transaction_fee）","%"),
    "campaign_fee":             ("0",     "其他活動費",                      "%"),
    "last_mile_fee":            ("0",     "末端配送費（平台包運填0）",         "NT$/件"),
}

EXCHANGE_RATE = 4.5
PLATFORM_FEE = 0.06
PAYMENT_FEE = 0.025

# CCB 方案費率對照
CCB_RATES = {"none": 0.0, "ccb5": 0.015, "ccb10": 0.025}

# 集運費率 key 對照
FREIGHT_TYPE_KEYS = {
    "air":          "air_freight_per_kg",
    "sea_fast":     "sea_fast_per_kg",
    "sea_regular":  "sea_regular_per_kg",
}

# 商品生命週期 10 階段（舊 active → listed，舊 archived → stopped）
PRODUCT_STATUSES = [
    "idea",           # 靈感發現
    "investigating",  # 調查中
    "sample_pending", # 可進樣
    "sample_received",# 已進樣
    "evaluating",     # 待評估
    "ready",          # 可上架
    "listed",         # 已上架
    "testing_ads",    # 廣告測試中
    "scaling",        # 放大中
    "stopped",        # 停止/淘汰
]
PRODUCT_STATUS_LABELS = {
    "idea":            "靈感發現",
    "investigating":   "調查中",
    "sample_pending":  "可進樣",
    "sample_received": "已進樣",
    "evaluating":      "待評估",
    "ready":           "可上架",
    "listed":          "已上架",
    "testing_ads":     "廣告測試中",
    "scaling":         "放大中",
    "stopped":         "停止/淘汰",
    # 向下相容舊值
    "active":          "已上架",
    "archived":        "停止/淘汰",
}


def _get_settings() -> dict:
    """從 DB 讀取設定，第一次呼叫時自動寫入預設值。"""
    with db() as conn:
        rows = conn.execute("SELECT key, value FROM fl_settings").fetchall()
        settings = {r["key"]: r["value"] for r in rows}
        # 補齊缺少的預設值
        for k, (default_v, label, unit) in _DEFAULT_SETTINGS.items():
            if k not in settings:
                conn.execute(
                    "INSERT OR IGNORE INTO fl_settings (key, value, label, unit) VALUES (?,?,?,?)",
                    (k, default_v, label, unit),
                )
                settings[k] = default_v
    return {k: float(v) for k, v in settings.items()}


def _migrate_schema():
    """安全地補充缺少的欄位，不影響現有資料。"""
    cols = [
        ("family_id",    "TEXT"),
        ("family_name",  "TEXT"),
        ("variant_name", "TEXT"),
    ]
    with db() as conn:
        for col, defn in cols:
            try:
                conn.execute(f"ALTER TABLE fl_products ADD COLUMN {col} {defn}")
            except Exception:
                pass  # column already exists

_migrate_schema()


# ─── Models ───────────────────────────────────────────────

class ProductCreate(BaseModel):
    sku: str
    name: str
    # 成本（必填組）
    cost_rmb: Optional[float] = None
    head_freight_rmb: Optional[float] = None    # 1688境內運費（RMB）
    # 集運
    freight_type: Optional[str] = "sea_fast"    # air / sea_fast / sea_regular
    cross_border_twd: Optional[float] = None    # 已估算的集運費TWD（存檔用）
    is_special_goods: Optional[bool] = False    # 特貨
    # QQL 採購模式
    procurement_mode: Optional[str] = "standard_1688"  # standard_1688 / qql_agent
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    # 售價（選填）
    target_price: Optional[float] = None
    market_price_low: Optional[float] = None
    market_price_high: Optional[float] = None
    # 蝦皮費率選項（選填，預設最保守）
    ccb_plan: Optional[str] = "none"            # none / ccb5 / ccb10
    is_promo_day: Optional[bool] = False
    fulfillment_days: Optional[int] = 1
    # 商品細項（後填）
    weight_kg: Optional[float] = None
    packaging_cost: Optional[float] = None
    return_rate: Optional[float] = None
    damage_rate: Optional[float] = None
    coupon_rate: Optional[float] = None
    # 分類 & 角色
    role: Optional[str] = None                  # None = AI建議
    role_confirmed: Optional[bool] = None
    product_type: Optional[str] = None
    scene: Optional[str] = None
    keyword: Optional[str] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None
    family_id: Optional[str] = None
    family_name: Optional[str] = None
    variant_name: Optional[str] = None


class InventoryCreate(BaseModel):
    sku: str
    purchase_date: Optional[str] = None
    cost_rmb: float
    exchange_rate: float = EXCHANGE_RATE
    quantity: int
    lead_days: Optional[int] = None
    supplier: Optional[str] = None
    batch_note: Optional[str] = None


class PerformanceUpdate(BaseModel):
    sku: str
    current_price: float          # 目前售價
    sales_7d: int                 # 7天銷量
    ad_spend_7d: float = 0        # 廣告花費（沒打廣告填 0）
    current_stock: int = 0        # 目前庫存


# ─── 智能計算邏輯 ──────────────────────────────────────────

def calc_full_cost(
    cost_rmb: float,
    selling_price: float,
    settings: dict,
    weight_kg: float = 0,
    packaging_cost: float = 0,
    return_rate: float = None,
    damage_rate: float = None,
    coupon_rate: float = 0,
    head_freight_rmb: float = 0,
    cross_border_twd: float = 0,       # 已算好的跨境集運費（TWD），優先使用
    ccb_plan: str = "none",            # none / ccb5 / ccb10
    is_promo_day: bool = False,        # 是否促銷日（影響 +2% 加成）
    fulfillment_days: int = 1,         # 備貨天數（>2天 +3%）
) -> dict:
    """
    2026 蝦皮完整成本計算

    固定成本：進貨(TWD) + 集運費 + 末端配送 + 包材 + FSS（免運服務費）
    變動成本：成交手續費 + 金流費 + CCB費 + 促銷加成 + 備貨懲罰 + 退貨破損 + 折扣
    FSS自動切換：售價 > fss_threshold 用固定制(NT$60)，否則用百分比制(6%)
    """
    exchange_rate   = settings.get("exchange_rate", 4.5)
    shipping_per_kg = settings.get("shipping_per_kg", 40)
    if return_rate is None:
        return_rate = settings.get("default_return_rate", 0.02)
    if damage_rate is None:
        damage_rate = settings.get("default_damage_rate", 0.01)

    # ── 費率讀取（新 key 優先，舊 key 向下相容）──────────────────────────────
    commission_rate = settings.get("commission_fee", settings.get("platform_fee", 0.06))
    transaction_rate = settings.get("transaction_fee", settings.get("payment_fee", 0.025))
    fss_pct         = settings.get("fss_pct", 0.06)
    fss_fixed       = settings.get("fss_fixed", 60)
    fss_threshold   = settings.get("fss_threshold", 1000)
    promo_rate      = settings.get("promo_surcharge", 0.02)
    penalty_rate    = settings.get("fulfillment_penalty", 0.03)
    ccb_rate        = CCB_RATES.get(ccb_plan, 0.0)

    # ── 進貨成本 ─────────────────────────────────────────────────────────────
    cost_twd  = cost_rmb * exchange_rate
    # 集運費：優先用 cross_border_twd（前端已算好），否則用 head_freight_rmb 折算
    freight   = cross_border_twd if cross_border_twd > 0 else head_freight_rmb * exchange_rate
    shipping  = weight_kg * shipping_per_kg                 # 末端配送（蝦皮官方物流）

    # ── FSS（免運服務費）自動切換 ────────────────────────────────────────────
    if selling_price > fss_threshold:
        fss_cost = fss_fixed                                # 固定制 NT$60
        fss_plan = "fixed"
    else:
        fss_cost = selling_price * fss_pct                  # 百分比制 6%
        fss_plan = "pct"

    # ── 固定成本加總 ──────────────────────────────────────────────────────────
    fixed_cost = cost_twd + freight + shipping + packaging_cost + fss_cost

    # ── 變動成本（基於售價）──────────────────────────────────────────────────
    commission_cost  = selling_price * commission_rate
    transaction_cost = selling_price * transaction_rate
    ccb_cost         = selling_price * ccb_rate
    # 促銷日加成：僅在促銷日 且 非 CCB10 方案時加收
    promo_cost       = selling_price * promo_rate if (is_promo_day and ccb_plan != "ccb10") else 0
    # 備貨懲罰：備貨天數 > 2 天加收
    penalty_cost     = selling_price * penalty_rate if fulfillment_days > 2 else 0
    risk_cost        = selling_price * (return_rate + damage_rate)
    coupon_cost      = selling_price * coupon_rate

    variable_cost = (commission_cost + transaction_cost + ccb_cost +
                     promo_cost + penalty_cost + risk_cost + coupon_cost)

    total_cost   = fixed_cost + variable_cost
    profit       = selling_price - total_cost
    gross_margin = profit / selling_price if selling_price else 0

    # ── 逆推建議售價（兩次迭代處理 FSS 切換）────────────────────────────────
    # 固定底部（不含 FSS）
    fixed_base = cost_twd + freight + shipping + packaging_cost
    # 變動費率（不含 FSS pct）
    var_rate = (commission_rate + transaction_rate + ccb_rate +
                (promo_rate if is_promo_day and ccb_plan != "ccb10" else 0) +
                (penalty_rate if fulfillment_days > 2 else 0) +
                return_rate + damage_rate + coupon_rate)

    def suggest_price(target_margin: float, ad_rate: float) -> int:
        """逆推建議售價，兩次迭代正確處理 FSS 切換"""
        d1 = max(1 - var_rate - fss_pct - target_margin - ad_rate, 0.01)
        est = fixed_base / d1
        if est > fss_threshold:
            d2 = max(1 - var_rate - target_margin - ad_rate, 0.01)
            price = (fixed_base + fss_fixed) / d2
        else:
            price = est
        return round(price / 10) * 10

    # 角色毛利門檻（讀 settings，保留後備預設值）
    m_traffic = settings.get("traffic_margin_target", 0.25)
    m_core    = settings.get("core_margin_target",    0.40)
    m_profit  = settings.get("profit_margin_target",  0.55)

    price_traffic = suggest_price(m_traffic, 0.10)
    price_core    = suggest_price(m_core,    0.15)
    price_profit  = suggest_price(m_profit,  0.05)

    # 向下相容舊欄位
    recommended  = price_core
    conservative = round(fixed_cost * 3 / 10) * 10

    # ── 角色判斷（4 段門檻，從 settings 讀）──────────────────────────────────
    if gross_margin >= m_profit:
        suggested_role  = "主力款"
        viability       = "profit"
        role_reasoning  = f"毛利率 {gross_margin:.0%}，可作為賣場主打商品，適合廣告投放。"
        role_confidence = 85
    elif gross_margin >= m_core:
        suggested_role  = "毛利款"
        viability       = "core"
        role_reasoning  = f"毛利率 {gross_margin:.0%}，適合搭配引流款帶買，是主要獲利來源。"
        role_confidence = 80
    elif gross_margin >= m_traffic:
        suggested_role  = "引流款"
        viability       = "traffic"
        role_reasoning  = f"毛利率 {gross_margin:.0%}，適合引流帶流量，搭配毛利款提升整體獲利。"
        role_confidence = 70
    else:
        suggested_role  = "不建議"
        viability       = "not_suitable"
        role_reasoning  = f"毛利率 {gross_margin:.0%} 低於最低門檻 25%，建議提高售價或降低成本後再評估。"
        role_confidence = 40

    return {
        "breakdown": {
            "cost_twd":           round(cost_twd, 1),
            "cross_border_freight": round(freight, 1),
            "shipping_cost":      round(shipping, 1),
            "packaging_cost":     round(packaging_cost, 1),
            "fss_cost":           round(fss_cost, 1),
            "fss_plan":           fss_plan,
            "commission_cost":    round(commission_cost, 1),
            "transaction_cost":   round(transaction_cost, 1),
            "ccb_cost":           round(ccb_cost, 1),
            "promo_cost":         round(promo_cost, 1),
            "penalty_cost":       round(penalty_cost, 1),
            "risk_cost":          round(risk_cost, 1),
            "coupon_cost":        round(coupon_cost, 1),
        },
        "fixed_cost":         round(fixed_cost, 1),
        "variable_cost":      round(variable_cost, 1),
        "total_cost":         round(total_cost, 1),
        "profit":             round(profit, 1),
        "gross_margin":       round(gross_margin, 4),
        "safe_cpa":           round(max(profit, 0), 1),
        # 落地成本（進貨+集運+末端配送+包材，不含平台費）
        "landed_cost":        round(fixed_base, 1),
        # 平台費率（手續費+金流+FSS%，含 FSS 百分比制估算）
        "platform_fee_rate":  round(commission_rate + transaction_rate + fss_pct, 4),
        # 三段建議售價
        "price_traffic":      price_traffic,
        "price_core":         price_core,
        "price_profit":       price_profit,
        "recommended_price":  recommended,
        "conservative_price": conservative,
        # 角色判斷
        "suggested_role":     suggested_role,
        "viability":          viability,
        "role_reasoning":     role_reasoning,
        "role_confidence":    role_confidence,
        # 向下相容
        "cost_twd":           round(cost_twd, 1),
        "min_price":          round(fixed_base / max(1 - var_rate - fss_pct - 0.40, 0.01), 1),
        "suggested_price":    recommended,
        "target_margin":      0.40,
        "est_gross_margin":   round(gross_margin, 4),
        # 平台費舊欄位（相容前端）
        "platform_cost":      round(commission_cost, 1),
        "payment_cost":       round(transaction_cost, 1),
    }


def calc_restock_qty(sales_7d: int, current_stock: int, lead_days: int = 14) -> int:
    """建議補貨量"""
    if sales_7d <= 0:
        return 0
    daily_sales = sales_7d / 7
    safety_days = lead_days + 7
    needed = daily_sales * safety_days - current_stock
    return max(0, round(needed))


# ─── Endpoints ────────────────────────────────────────────

@router.get("/funnel")
def get_selection_funnel():
    """選品漏斗：各生命週期階段商品數量"""
    with db() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) as count FROM fl_products GROUP BY status"
        ).fetchall()
    counts = {r["status"]: r["count"] for r in rows}
    # 對應 active → listed，archived → stopped
    counts["listed"] = counts.get("listed", 0) + counts.pop("active", 0)
    counts["stopped"] = counts.get("stopped", 0) + counts.pop("archived", 0)
    funnel = [
        {"stage": s, "label": PRODUCT_STATUS_LABELS.get(s, s), "count": counts.get(s, 0)}
        for s in PRODUCT_STATUSES
    ]
    return {"funnel": funnel, "total": sum(c["count"] for c in funnel)}


@router.get("/products/statuses")
def get_product_statuses():
    """回傳 10 階段商品生命週期定義 + 目前各階段數量"""
    with db() as conn:
        counts_raw = conn.execute(
            "SELECT status, COUNT(*) as n FROM fl_products GROUP BY status"
        ).fetchall()
    counts: dict[str, int] = {}
    for r in counts_raw:
        s = r["status"]
        # 向下相容：active → listed, archived → stopped
        if s == "active":
            s = "listed"
        elif s == "archived":
            s = "stopped"
        counts[s] = counts.get(s, 0) + r["n"]

    return {
        "statuses": [
            {"code": s, "label": PRODUCT_STATUS_LABELS[s], "count": counts.get(s, 0)}
            for s in PRODUCT_STATUSES
        ]
    }


@router.get("/products")
def list_products(status: Optional[str] = None):
    """列出商品。status 可傳逗號分隔的多個值，例如 listed,testing_ads,scaling
    不傳則回傳所有非 stopped 商品（兼容舊 active 值）。"""
    cfg = _get_settings()
    with db() as conn:
        if status:
            # 支援逗號分隔多狀態，同時將 active→listed、archived→stopped 向下相容
            statuses = []
            for s in status.split(","):
                s = s.strip()
                if s == "active":
                    statuses.append("listed")
                elif s == "archived":
                    statuses.append("stopped")
                else:
                    statuses.append(s)
            placeholders = ",".join("?" * len(statuses))
            rows = conn.execute(f"""
                SELECT p.*,
                       COALESCE(SUM(i.quantity), 0) as total_stock
                FROM fl_products p
                LEFT JOIN fl_inventory i ON p.sku = i.sku
                WHERE p.status IN ({placeholders}) OR (p.status = 'active' AND 'listed' IN ({placeholders}))
                GROUP BY p.sku
                ORDER BY p.role, p.sku
            """, statuses + statuses).fetchall()
        else:
            # 預設：排除 stopped（同時兼容舊 archived 值）
            rows = conn.execute("""
                SELECT p.*,
                       COALESCE(SUM(i.quantity), 0) as total_stock
                FROM fl_products p
                LEFT JOIN fl_inventory i ON p.sku = i.sku
                WHERE p.status NOT IN ('stopped', 'archived')
                GROUP BY p.sku
                ORDER BY p.role, p.sku
            """).fetchall()

    result = []
    for r in rows:
        d = dict(r)
        # 估算毛利率（用 target_price，若無則為 None）
        if d.get("cost_rmb") and d.get("target_price"):
            try:
                fc = calc_full_cost(
                    d["cost_rmb"], d["target_price"], cfg,
                    weight_kg=d.get("weight_kg") or 0,
                    packaging_cost=d.get("packaging_cost") or 0,
                    return_rate=d.get("return_rate"),
                    damage_rate=d.get("damage_rate"),
                    coupon_rate=d.get("coupon_rate") or 0,
                    head_freight_rmb=d.get("head_freight_rmb") or 0,
                )
                d["gross_margin_est"] = fc["gross_margin"]
            except Exception:
                d["gross_margin_est"] = None
        else:
            d["gross_margin_est"] = None
        result.append(d)
    return result


@router.get("/products/families")
def get_product_families():
    """商品依家族分組。有 family_id 的聚合為家族列；無 family_id 的各自獨立。"""
    with db() as conn:
        rows = conn.execute("""
            SELECT p.*,
                   COALESCE(SUM(i.quantity), 0) as total_stock,
                   (SELECT f.gross_margin FROM fl_performance f
                    WHERE f.sku = p.sku ORDER BY f.record_date DESC LIMIT 1) as gross_margin_est
            FROM fl_products p
            LEFT JOIN fl_inventory i ON i.sku = p.sku
            WHERE p.status NOT IN ('stopped', 'archived')
            GROUP BY p.sku
            ORDER BY p.family_name NULLS LAST, p.family_id NULLS LAST, p.created_at
        """).fetchall()

    products = [dict(r) for r in rows]

    from collections import defaultdict
    family_map: dict = defaultdict(list)
    ungrouped = []
    for p in products:
        if p.get("family_id"):
            family_map[p["family_id"]].append(p)
        else:
            ungrouped.append(p)

    result = []
    for fid, members in family_map.items():
        best_margin = max((m.get("gross_margin_est") or 0 for m in members), default=0)
        result.append({
            "family_id": fid,
            "family_name": members[0].get("family_name") or members[0]["name"],
            "variant_count": len(members),
            "total_stock": sum(m.get("total_stock") or 0 for m in members),
            "best_margin": best_margin,
            "products": members,
        })

    for p in ungrouped:
        result.append({
            "family_id": None,
            "family_name": p["name"],
            "variant_count": 1,
            "total_stock": p.get("total_stock") or 0,
            "best_margin": p.get("gross_margin_est"),
            "products": [p],
        })

    return result


@router.get("/bundles")
def get_product_bundles():
    """取得所有設定了關聯的商品組合（fl_product_relations）。"""
    with db() as conn:
        rows = conn.execute("""
            SELECT r.*,
                   p.name as source_name, p.role as source_role,
                   p.target_price as source_price, p.status as source_status
            FROM fl_product_relations r
            JOIN fl_products p ON r.sku = p.sku
            ORDER BY r.sku, r.relation_type
        """).fetchall()

    from collections import defaultdict
    groups: dict = defaultdict(list)
    for r in rows:
        d = dict(r)
        groups[d["sku"]].append(d)

    return [
        {
            "sku": sku,
            "source_name": relations[0]["source_name"],
            "source_role": relations[0]["source_role"],
            "source_price": relations[0]["source_price"],
            "relations": relations,
        }
        for sku, relations in groups.items()
    ]


@router.get("/products/{sku}")
def get_product(sku: str):
    with db() as conn:
        p = conn.execute("SELECT * FROM fl_products WHERE sku=?", (sku,)).fetchone()
        if not p:
            raise HTTPException(404, f"SKU {sku} 不存在")
        perf = conn.execute("""
            SELECT * FROM fl_performance WHERE sku=? ORDER BY record_date DESC LIMIT 1
        """, (sku,)).fetchone()
        inv = conn.execute("""
            SELECT * FROM fl_inventory WHERE sku=? ORDER BY created_at DESC
        """, (sku,)).fetchall()
    return {
        "product": dict(p),
        "latest_performance": dict(perf) if perf else None,
        "inventory_history": [dict(r) for r in inv],
    }


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    product_type: Optional[str] = None
    scene: Optional[str] = None
    keyword: Optional[str] = None
    role: Optional[str] = None
    market_price_low: Optional[float] = None
    market_price_high: Optional[float] = None
    supplier: Optional[str] = None
    cost_rmb: Optional[float] = None
    head_freight_rmb: Optional[float] = None
    target_price: Optional[float] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    weight_kg: Optional[float] = None
    packaging_cost: Optional[float] = None
    return_rate: Optional[float] = None
    damage_rate: Optional[float] = None
    coupon_rate: Optional[float] = None
    role_confirmed: Optional[bool] = None
    freight_type: Optional[str] = None       # air / sea_fast / sea_regular
    is_special_goods: Optional[bool] = None  # 特貨
    ccb_plan: Optional[str] = None           # none / ccb5 / ccb10
    is_promo_day: Optional[bool] = None
    fulfillment_days: Optional[int] = None
    procurement_mode: Optional[str] = None   # standard_1688 / qql_agent
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    family_id: Optional[str] = None
    family_name: Optional[str] = None
    variant_name: Optional[str] = None


@router.put("/products/{sku}")
def update_product(sku: str, body: ProductUpdate):
    with db() as conn:
        p = conn.execute("SELECT * FROM fl_products WHERE sku=?", (sku,)).fetchone()
        if not p:
            raise HTTPException(404, f"SKU {sku} 不存在")
        updates = {k: v for k, v in body.model_dump().items() if v is not None}
        if "cost_rmb" in updates or "head_freight_rmb" in updates:
            # 重新計算 cost_twd（合併現有值與本次更新值）
            existing = conn.execute("SELECT cost_rmb, head_freight_rmb FROM fl_products WHERE sku=?", (sku,)).fetchone()
            base_cost = updates.get("cost_rmb", existing["cost_rmb"] or 0)
            head_freight = updates.get("head_freight_rmb", existing["head_freight_rmb"] or 0)
            updates["cost_twd"] = (base_cost + head_freight) * EXCHANGE_RATE
        if not updates:
            return {"ok": True, "sku": sku}
        sets = ", ".join(f"{k}=?" for k in updates)
        conn.execute(
            f"UPDATE fl_products SET {sets}, updated_at=CURRENT_TIMESTAMP WHERE sku=?",
            [*updates.values(), sku]
        )
    return {"ok": True, "sku": sku}


class StockSet(BaseModel):
    quantity: int  # 設定為此總庫存量（自動計算 delta 插入調整記錄）


@router.put("/products/{sku}/stock")
def set_stock(sku: str, body: StockSet):
    """直接設定商品總庫存，以差值插入一筆調整記錄。"""
    with db() as conn:
        p = conn.execute("SELECT sku FROM fl_products WHERE sku=?", (sku,)).fetchone()
        if not p:
            raise HTTPException(404, f"SKU {sku} 不存在")
        current = conn.execute(
            "SELECT COALESCE(SUM(quantity),0) as n FROM fl_inventory WHERE sku=?", (sku,)
        ).fetchone()["n"]
        delta = body.quantity - current
        if delta == 0:
            return {"ok": True, "sku": sku, "total": body.quantity}
        conn.execute(
            "INSERT INTO fl_inventory (sku, cost_rmb, exchange_rate, cost_twd, quantity, batch_note) VALUES (?,0,?,0,?,?)",
            (sku, EXCHANGE_RATE, delta, "手動調整")
        )
    return {"ok": True, "sku": sku, "total": body.quantity}


@router.get("/products/{sku}/relations")
def get_product_relations(sku: str):
    """取得商品的所有關聯商品（場景搭配/組合包/加價購）"""
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM fl_product_relations WHERE sku=? ORDER BY relation_type, created_at",
            (sku,)
        ).fetchall()
    return [dict(r) for r in rows]


class RelationCreate(BaseModel):
    related_sku: Optional[str] = None
    related_name: Optional[str] = None
    relation_type: str  # bundle | cross_sell | upsell | scene_partner
    scene: Optional[str] = None
    is_bundle_candidate: bool = False
    notes: Optional[str] = None


@router.post("/products/{sku}/relations")
def add_product_relation(sku: str, body: RelationCreate):
    """新增商品關聯"""
    with db() as conn:
        conn.execute("SELECT sku FROM fl_products WHERE sku=?", (sku,))
        conn.execute(
            "INSERT INTO fl_product_relations (sku, related_sku, related_name, relation_type, scene, is_bundle_candidate, notes) VALUES (?,?,?,?,?,?,?)",
            (sku, body.related_sku, body.related_name, body.relation_type, body.scene, 1 if body.is_bundle_candidate else 0, body.notes)
        )
    return {"ok": True, "sku": sku}


@router.delete("/products/{sku}/relations/{relation_id}")
def delete_product_relation(sku: str, relation_id: int):
    """刪除商品關聯"""
    with db() as conn:
        conn.execute("DELETE FROM fl_product_relations WHERE id=? AND sku=?", (relation_id, sku))
    return {"ok": True}


class RelationStatusUpdate(BaseModel):
    bundle_status: str  # draft | testing | active | rejected


@router.patch("/products/{sku}/relations/{relation_id}")
def update_relation_status(sku: str, relation_id: int, body: RelationStatusUpdate):
    """更新組合關聯的 bundle_status（draft/testing/active/rejected）"""
    allowed = {"draft", "testing", "active", "rejected"}
    if body.bundle_status not in allowed:
        raise HTTPException(status_code=400, detail=f"bundle_status must be one of {allowed}")
    with db() as conn:
        conn.execute(
            "UPDATE fl_product_relations SET bundle_status=? WHERE id=? AND sku=?",
            (body.bundle_status, relation_id, sku),
        )
    return {"ok": True}


@router.delete("/products/{sku}")
def delete_product(sku: str):
    with db() as conn:
        conn.execute("DELETE FROM fl_performance WHERE sku=?", (sku,))
        conn.execute("DELETE FROM fl_inventory WHERE sku=?", (sku,))
        conn.execute("DELETE FROM fl_products WHERE sku=?", (sku,))
    return {"ok": True, "sku": sku}


@router.post("/products")
def create_product(body: ProductCreate):
    cfg = _get_settings()
    head_freight = body.head_freight_rmb or 0
    cost_twd = (body.cost_rmb + head_freight) * cfg.get("exchange_rate", EXCHANGE_RATE) if body.cost_rmb else None
    with db() as conn:
        conn.execute("""
            INSERT INTO fl_products
            (sku, name, product_type, scene, keyword, role, role_confirmed,
             market_price_low, market_price_high, supplier, cost_rmb, head_freight_rmb, cost_twd, target_price, notes,
             weight_kg, packaging_cost, return_rate, damage_rate, coupon_rate,
             freight_type, is_special_goods, ccb_plan, is_promo_day, fulfillment_days,
             procurement_mode, length_cm, width_cm, height_cm,
             family_id, family_name, variant_name)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (body.sku, body.name, body.product_type, body.scene, body.keyword,
              body.role, 1 if body.role_confirmed else 0,
              body.market_price_low, body.market_price_high,
              body.supplier, body.cost_rmb, head_freight, cost_twd, body.target_price, body.notes,
              body.weight_kg or 0, body.packaging_cost or 0,
              body.return_rate, body.damage_rate, body.coupon_rate or 0,
              body.freight_type or "sea_fast", 1 if body.is_special_goods else 0,
              body.ccb_plan or "none", 1 if body.is_promo_day else 0, body.fulfillment_days or 1,
              body.procurement_mode or "standard_1688",
              body.length_cm, body.width_cm, body.height_cm,
              body.family_id, body.family_name, body.variant_name))
    return {"ok": True, "sku": body.sku}


@router.post("/inventory")
def add_inventory(body: InventoryCreate):
    cost_twd = body.cost_rmb * body.exchange_rate
    with db() as conn:
        conn.execute("""
            INSERT INTO fl_inventory
            (sku, purchase_date, cost_rmb, exchange_rate, cost_twd, quantity, lead_days, supplier, batch_note)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (body.sku, body.purchase_date, body.cost_rmb, body.exchange_rate,
              cost_twd, body.quantity, body.lead_days, body.supplier, body.batch_note))
        # 同步更新商品主檔成本
        conn.execute("""
            UPDATE fl_products SET cost_rmb=?, cost_twd=?, updated_at=CURRENT_TIMESTAMP WHERE sku=?
        """, (body.cost_rmb, cost_twd, body.sku))
    return {"ok": True, "cost_twd": round(cost_twd, 1)}


@router.delete("/performance/{sku}")
def delete_performance(sku: str):
    """清除指定 SKU 的所有週績效紀錄"""
    with db() as conn:
        conn.execute("DELETE FROM fl_performance WHERE sku=?", (sku,))
    return {"ok": True, "sku": sku}


@router.post("/performance")
def update_performance(body: PerformanceUpdate):
    today = date.today().isoformat()
    cfg = _get_settings()

    # 取商品成本
    with db() as conn:
        p = conn.execute("SELECT cost_twd FROM fl_products WHERE sku=?", (body.sku,)).fetchone()
    cost_twd = dict(p)["cost_twd"] if p and p["cost_twd"] else 0

    # 自動計算
    revenue_7d = body.current_price * body.sales_7d
    total_fee_amt = revenue_7d * (cfg["platform_fee"] + cfg["payment_fee"])
    cogs = cost_twd * body.sales_7d
    gross_profit = revenue_7d - cogs - total_fee_amt - body.ad_spend_7d
    gross_margin = gross_profit / revenue_7d if revenue_7d > 0 else 0
    roas = revenue_7d / body.ad_spend_7d if body.ad_spend_7d > 0 else None

    # 下一步策略
    if gross_margin >= 0.3 and (roas is None or roas >= 2):
        next_action = "放大 (補貨/加預算)"
    elif gross_margin > 0:
        next_action = "觀察 (優化圖文)"
    else:
        next_action = "停售 (出清庫存)"

    with db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO fl_performance
            (sku, record_date, current_price, sales_7d, revenue_7d,
             ad_spend_7d, current_stock, roas, gross_profit, gross_margin, next_action)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (body.sku, today, body.current_price, body.sales_7d,
              round(revenue_7d, 1), body.ad_spend_7d, body.current_stock,
              round(roas, 2) if roas else None,
              round(gross_profit, 1), round(gross_margin, 4), next_action))

    return {
        "ok": True,
        "revenue_7d": round(revenue_7d, 1),
        "gross_profit": round(gross_profit, 1),
        "gross_margin": f"{gross_margin*100:.1f}%",
        "next_action": next_action,
    }


@router.get("/performance/latest")
def get_latest_performance():
    """每個 SKU 取最新一筆績效資料，供週績效表使用"""
    with db() as conn:
        rows = conn.execute("""
            SELECT p.sku, p.record_date, p.current_price, p.sales_7d, p.revenue_7d,
                   p.ad_spend_7d, p.current_stock, p.roas, p.gross_profit, p.gross_margin, p.next_action
            FROM fl_performance p
            INNER JOIN (
                SELECT sku, MAX(record_date) as max_date
                FROM fl_performance
                GROUP BY sku
            ) latest ON p.sku = latest.sku AND p.record_date = latest.max_date
            ORDER BY p.revenue_7d DESC
        """).fetchall()
    return [dict(r) for r in rows]


@router.get("/decision/{sku}")
def get_decision(sku: str):
    """智能定價決策：給 SKU，回傳完整成本明細 + 建議售價 + 補貨量"""
    with db() as conn:
        p = conn.execute("SELECT * FROM fl_products WHERE sku=?", (sku,)).fetchone()
        if not p:
            raise HTTPException(404, f"SKU {sku} 不存在")
        perf = conn.execute("""
            SELECT * FROM fl_performance WHERE sku=? ORDER BY record_date DESC LIMIT 1
        """, (sku,)).fetchone()
        inv = conn.execute("""
            SELECT COALESCE(SUM(quantity), 0) as total FROM fl_inventory WHERE sku=?
        """, (sku,)).fetchone()

    p = dict(p)
    perf = dict(perf) if perf else {}
    total_stock = dict(inv)["total"] if inv else 0

    cfg = _get_settings()
    pricing = None
    if p.get("cost_rmb"):
        selling = p.get("target_price") or 0
        pricing = calc_full_cost(
            p["cost_rmb"], selling, cfg,
            weight_kg=p.get("weight_kg") or 0,
            packaging_cost=p.get("packaging_cost") or 0,
            return_rate=p.get("return_rate"),
            damage_rate=p.get("damage_rate"),
            coupon_rate=p.get("coupon_rate") or 0,
            head_freight_rmb=p.get("head_freight_rmb") or 0,
        )

    restock = calc_restock_qty(
        perf.get("sales_7d", 0),
        perf.get("current_stock", total_stock),
        14
    )

    return {
        "sku": sku,
        "name": p["name"],
        "role": p.get("role"),
        "pricing": pricing,
        "restock_qty": restock,
        "current_stock": perf.get("current_stock", total_stock),
        "gross_margin": perf.get("gross_margin"),
        "next_action": perf.get("next_action"),
        "product": p,
    }


class FreightCalcRequest(BaseModel):
    weight_kg: float
    freight_type: str = "sea_fast"   # air / sea_fast / sea_regular
    is_special_goods: bool = False   # 特貨（帶電/磁/液體）加收


@router.post("/calc-freight")
def calc_freight(body: FreightCalcRequest):
    """
    估算跨境集運費（TWD）。
    freight_type: air=空運 / sea_fast=海快（推薦） / sea_regular=海運
    is_special_goods: 特貨每公斤加收 NT$15
    """
    cfg = _get_settings()
    key = FREIGHT_TYPE_KEYS.get(body.freight_type, "sea_fast_per_kg")
    rate = cfg.get(key, 45)
    surcharge = cfg.get("special_goods_surcharge", 15) if body.is_special_goods else 0
    total_rate = rate + surcharge
    total = round(body.weight_kg * total_rate, 1)
    return {
        "freight_twd":      total,
        "rate_per_kg":      total_rate,
        "freight_type":     body.freight_type,
        "is_special_goods": body.is_special_goods,
        "labels": {
            "air":          "空運（3-5天）",
            "sea_fast":     "海快（5-8天）",
            "sea_regular":  "海運（12-15天）",
        }.get(body.freight_type, body.freight_type),
    }


class CalcCostRequest(BaseModel):
    cost_rmb: float
    selling_price: float
    weight_kg: float = 0
    packaging_cost: float = 0
    head_freight_rmb: float = 0
    cross_border_twd: float = 0      # 已算好的集運費（TWD），優先使用
    return_rate: Optional[float] = None
    damage_rate: Optional[float] = None
    coupon_rate: float = 0
    ccb_plan: str = "none"           # none / ccb5 / ccb10
    is_promo_day: bool = False
    fulfillment_days: int = 1
    # QQL 採購模式
    procurement_mode: str = "standard_1688"   # standard_1688 | qql_agent
    freight_type: str = "sea_fast"            # sea_fast | sea_regular | air（standard 模式用）
    is_special_goods: bool = False
    length_cm: Optional[float] = None
    width_cm:  Optional[float] = None
    height_cm: Optional[float] = None
    market_price_high: Optional[float] = None


def _calc_ceiling(market_price_high: float, cfg: dict,
                  weight_kg: float = 0, packaging_cost: float = 0,
                  coupon_rate: float = 0, ccb_plan: str = "none",
                  is_promo_day: bool = False, fulfillment_days: int = 1,
                  procurement_mode: str = "standard_1688") -> dict:
    """
    反推：給定市場天花板售價，計算三個角色各自最高可承受的落地成本（landed_cost）
    及最高 1688 報價（RMB）。

    公式推導自 suggest_price 的反向：
      price = fixed_base / d1  (FSS 百分比制)
      → fixed_base = price × d1
      price = (fixed_base + fss_fixed) / d2  (FSS 固定制)
      → fixed_base = price × d2 - fss_fixed

    RMB 反推：
      standard_1688: remaining / exchange_rate
      qql_agent:     remaining / (qql_exchange_rate × (1 + qql_service_fee))
                     因為 QQL 採購成本 TWD = RMB × qql_exr × (1 + qql_fee)
    """
    price = market_price_high

    commission_rate  = cfg.get("commission_fee",        0.06)
    transaction_rate = cfg.get("transaction_fee",        0.025)
    fss_pct          = cfg.get("fss_pct",                0.06)
    fss_fixed        = cfg.get("fss_fixed",              60)
    fss_threshold    = cfg.get("fss_threshold",          1000)
    promo_rate       = cfg.get("promo_surcharge",        0.02) if (is_promo_day and ccb_plan != "ccb10") else 0
    penalty_rate     = cfg.get("fulfillment_penalty",    0.03) if fulfillment_days > 2 else 0
    ccb_rate         = CCB_RATES.get(ccb_plan, 0.0)
    return_rate      = cfg.get("default_return_rate",    0.02)
    damage_rate      = cfg.get("default_damage_rate",    0.01)

    var_rate = (commission_rate + transaction_rate + ccb_rate +
                promo_rate + penalty_rate + return_rate + damage_rate + coupon_rate)

    m_traffic = cfg.get("traffic_margin_target", 0.25)
    m_core    = cfg.get("core_margin_target",    0.40)
    m_profit  = cfg.get("profit_margin_target",  0.55)

    def _ceiling(target_margin: float, ad_rate: float) -> float:
        if price <= fss_threshold:
            d = max(1 - var_rate - fss_pct - target_margin - ad_rate, 0.01)
            return max(price * d, 0)
        else:
            d = max(1 - var_rate - target_margin - ad_rate, 0.01)
            return max(price * d - fss_fixed, 0)

    c_traffic = _ceiling(m_traffic, 0.10)
    c_core    = _ceiling(m_core,    0.15)
    c_profit  = _ceiling(m_profit,  0.05)

    exchange_rate  = cfg.get("exchange_rate",    4.5)
    qql_exr        = cfg.get("qql_exchange_rate", 4.5)
    qql_fee        = cfg.get("qql_service_fee",   0.03)
    shipping       = weight_kg * cfg.get("shipping_per_kg", 40)
    pkg            = packaging_cost

    def _max_rmb(ceiling: float) -> float:
        remaining = ceiling - shipping - pkg
        if remaining <= 0:
            return 0.0
        if procurement_mode == "qql_agent":
            # QQL: RMB × qql_exr × (1 + qql_fee) = TWD → RMB = TWD / (qql_exr × (1 + qql_fee))
            return round(remaining / (qql_exr * (1 + qql_fee)), 1)
        return round(remaining / exchange_rate, 1)

    return {
        "ceiling_traffic": round(c_traffic),
        "ceiling_core":    round(c_core),
        "ceiling_profit":  round(c_profit),
        "max_rmb_traffic": _max_rmb(c_traffic),
        "max_rmb_core":    _max_rmb(c_core),
        "max_rmb_profit":  _max_rmb(c_profit),
        "ceiling_fee_rate": round(var_rate, 4),
    }


def _market_warning(result: dict, market_price_high: Optional[float]) -> str:
    if not market_price_high:
        return ""
    mh = market_price_high
    if result["price_traffic"] > mh:
        return "市場天花板低於引流價，進入成本過高，不建議此商品"
    if result["price_core"] > mh:
        return "市場天花板低於毛利款定價，最多只能做引流款"
    if result["price_profit"] > mh:
        return "市場天花板低於主力款定價，最多做到毛利款"
    return ""


@router.post("/calc-cost")
def calc_cost_preview(body: CalcCostRequest):
    """輕量即時計算 endpoint，供前端 preview 使用（支援 standard_1688 / qql_agent）"""
    cfg = _get_settings()

    if body.procurement_mode == "qql_agent":
        # QQL 模式：採購成本 = (成本 + 境內運) × QQL匯率 × (1 + 服務費)
        qql_exr = cfg.get("qql_exchange_rate", 4.5)
        qql_fee = cfg.get("qql_service_fee",   0.03)
        sea_exp = cfg.get("sea_express_rate",   45)
        vol_div = cfg.get("volumetric_divisor", 6000)
        lc, wc, hc = body.length_cm or 0, body.width_cm or 0, body.height_cm or 0
        vol_w     = (lc * wc * hc / vol_div) if (lc and wc and hc) else 0
        billable  = max(body.weight_kg, vol_w)
        proc_cost = (body.cost_rmb + body.head_freight_rmb) * qql_exr * (1 + qql_fee)
        cross_bdr = billable * sea_exp
        # 傳入 calc_full_cost：cost_rmb=0，將採購成本和跨境費合進 cross_border_twd
        result = calc_full_cost(
            0.0, body.selling_price, cfg,
            weight_kg=body.weight_kg,
            packaging_cost=body.packaging_cost,
            return_rate=body.return_rate,
            damage_rate=body.damage_rate,
            coupon_rate=body.coupon_rate,
            cross_border_twd=proc_cost + cross_bdr,
            ccb_plan=body.ccb_plan,
            is_promo_day=body.is_promo_day,
            fulfillment_days=body.fulfillment_days,
        )
        result["market_warning"] = _market_warning(result, body.market_price_high)
        if body.market_price_high:
            result.update(_calc_ceiling(
                body.market_price_high, cfg,
                weight_kg=body.weight_kg, packaging_cost=body.packaging_cost,
                coupon_rate=body.coupon_rate, ccb_plan=body.ccb_plan,
                is_promo_day=body.is_promo_day, fulfillment_days=body.fulfillment_days,
                procurement_mode="qql_agent",
            ))
        return result

    # Standard 1688 模式
    freight_rates = {
        "sea_fast":    cfg.get("sea_fast_per_kg",    45),
        "sea_regular": cfg.get("sea_regular_per_kg", 20),
        "air":         cfg.get("air_freight_per_kg", 115),
    }
    special_sur = cfg.get("special_goods_surcharge", 15) if body.is_special_goods else 0
    freight_per_kg = freight_rates.get(body.freight_type, 45) + special_sur
    cross_bdr = body.weight_kg * freight_per_kg if body.weight_kg > 0 else body.head_freight_rmb * cfg.get("exchange_rate", 4.5)

    result = calc_full_cost(
        body.cost_rmb, body.selling_price, cfg,
        weight_kg=body.weight_kg,
        packaging_cost=body.packaging_cost,
        return_rate=body.return_rate,
        damage_rate=body.damage_rate,
        coupon_rate=body.coupon_rate,
        head_freight_rmb=body.head_freight_rmb,
        cross_border_twd=cross_bdr,
        ccb_plan=body.ccb_plan,
        is_promo_day=body.is_promo_day,
        fulfillment_days=body.fulfillment_days,
    )
    result["market_warning"] = _market_warning(result, body.market_price_high)
    if body.market_price_high:
        result.update(_calc_ceiling(
            body.market_price_high, cfg,
            weight_kg=body.weight_kg, packaging_cost=body.packaging_cost,
            coupon_rate=body.coupon_rate, ccb_plan=body.ccb_plan,
            is_promo_day=body.is_promo_day, fulfillment_days=body.fulfillment_days,
            procurement_mode=body.procurement_mode,
        ))
    return result


class CalcCeilingRequest(BaseModel):
    market_price_high: float
    weight_kg: float = 0
    packaging_cost: float = 0
    coupon_rate: float = 0
    ccb_plan: str = "none"
    is_promo_day: bool = False
    fulfillment_days: int = 1
    procurement_mode: str = "standard_1688"  # standard_1688 | qql_agent


@router.post("/calc-ceiling")
def calc_ceiling_endpoint(body: CalcCeilingRequest):
    """
    Top-Down Sourcing Ceiling Calculator

    給定市場天花板售價，回傳三個角色的最高可承受落地成本與最高 1688 報價。
    不需要已知成本，適合選品評估階段的純反推計算。

    Response fields:
      ceiling_traffic/core/profit  — 各角色最高落地成本（NT$）
      max_rmb_traffic/core/profit  — 粗估最高 1688 報價（¥，已扣末端配送）
      ceiling_fee_rate             — 總費率（不含 FSS）
    """
    cfg = _get_settings()
    return _calc_ceiling(
        body.market_price_high, cfg,
        weight_kg=body.weight_kg,
        packaging_cost=body.packaging_cost,
        coupon_rate=body.coupon_rate,
        ccb_plan=body.ccb_plan,
        is_promo_day=body.is_promo_day,
        fulfillment_days=body.fulfillment_days,
        procurement_mode=body.procurement_mode,
    )


@router.get("/settings")
def get_settings():
    """讀取系統費率設定"""
    with db() as conn:
        rows = conn.execute("SELECT key, value, label, unit FROM fl_settings").fetchall()
        if not rows:
            _get_settings()  # 初始化預設值
            rows = conn.execute("SELECT key, value, label, unit FROM fl_settings").fetchall()
    return [{"key": r["key"], "value": float(r["value"]), "label": r["label"], "unit": r["unit"]} for r in rows]


class SettingsUpdate(BaseModel):
    values: dict  # { "exchange_rate": 4.6, "platform_fee": 0.05, ... }


@router.put("/settings")
def update_settings(body: SettingsUpdate):
    """更新系統費率設定"""
    with db() as conn:
        for k, v in body.values.items():
            if k in _DEFAULT_SETTINGS:
                conn.execute(
                    "INSERT OR REPLACE INTO fl_settings (key, value, label, unit, updated_at) "
                    "VALUES (?, ?, (SELECT label FROM fl_settings WHERE key=?), "
                    "(SELECT unit FROM fl_settings WHERE key=?), CURRENT_TIMESTAMP)",
                    (k, str(v), k, k),
                )
    return {"ok": True, "updated": list(body.values.keys())}


@router.get("/dashboard")
def get_dashboard():
    """電商總覽：月營收、毛利、熱銷 Top3、需補貨清單"""
    with db() as conn:
        summary = conn.execute("""
            SELECT
                SUM(revenue_7d) * 4 as monthly_revenue_est,
                SUM(gross_profit) * 4 as monthly_profit_est,
                COUNT(*) as active_skus,
                AVG(gross_margin) as avg_margin
            FROM fl_performance
            WHERE record_date = (SELECT MAX(record_date) FROM fl_performance)
        """).fetchone()

        top3 = conn.execute("""
            SELECT p.sku, p.name, p.role, f.revenue_7d, f.gross_margin, f.next_action
            FROM fl_performance f JOIN fl_products p ON f.sku = p.sku
            WHERE f.record_date = (SELECT MAX(record_date) FROM fl_performance)
            ORDER BY f.revenue_7d DESC LIMIT 3
        """).fetchall()

        low_stock = conn.execute("""
            SELECT p.sku, p.name, f.current_stock, f.sales_7d
            FROM fl_performance f JOIN fl_products p ON f.sku = p.sku
            WHERE f.record_date = (SELECT MAX(record_date) FROM fl_performance)
              AND f.current_stock < (f.sales_7d / 7.0 * 14)
              AND f.sales_7d > 0
            ORDER BY f.current_stock ASC
        """).fetchall()

    return {
        "summary": dict(summary) if summary else {},
        "top3": [dict(r) for r in top3],
        "low_stock_alert": [dict(r) for r in low_stock],
    }

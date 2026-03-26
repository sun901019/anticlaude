"""
Ecommerce Extra Routes (not in src/ecommerce/router.py)
  POST /api/ecommerce/auto-flag
  GET  /api/ecommerce/performance-history
  GET  /api/ecommerce/alerts
"""
import asyncio as _asyncio
from fastapi import APIRouter
from src.utils.logger import get_logger

router = APIRouter()
log = get_logger("api.ecommerce_extra")


@router.post("/api/ecommerce/auto-flag")
async def auto_flag_products():
    """自動標記滯銷/低毛利商品，更新 next_action 欄位"""
    try:
        from src.db.connection import db
        flagged = []
        with db() as conn:
            rows = conn.execute(
                """SELECT p.sku, p.name,
                          latest.gross_margin as gross_margin_rate,
                          COALESCE(latest.current_stock, inv.total_stock, 0) as stock,
                          latest.record_date as last_record,
                          COALESCE(SUM(f.sales_7d), 0) as recent_sales
                   FROM fl_products p
                   LEFT JOIN (
                       SELECT fp.sku, fp.record_date, fp.current_stock, fp.gross_margin
                       FROM fl_performance fp
                       INNER JOIN (
                           SELECT sku, MAX(record_date) as max_date
                           FROM fl_performance GROUP BY sku
                       ) latest_fp ON fp.sku = latest_fp.sku AND fp.record_date = latest_fp.max_date
                   ) latest ON p.sku = latest.sku
                   LEFT JOIN (
                       SELECT sku, COALESCE(SUM(quantity), 0) as total_stock
                       FROM fl_inventory GROUP BY sku
                   ) inv ON p.sku = inv.sku
                   LEFT JOIN fl_performance f ON p.sku = f.sku
                     AND f.record_date >= date('now', '-14 days')
                   WHERE p.status NOT IN ('stopped', 'archived')
                   GROUP BY p.sku, p.name, latest.gross_margin,
                            latest.current_stock, latest.record_date, inv.total_stock"""
            ).fetchall()
            for r in rows:
                flags = []
                margin = r["gross_margin_rate"]
                sales = r["recent_sales"] or 0
                if margin is not None and margin < 0.10:
                    flags.append("低毛利建議下架")
                if sales == 0 and r["last_record"]:
                    flags.append("14天零銷售建議停售")
                elif sales is not None and sales < 3:
                    flags.append("銷售低迷建議檢視定價")
                if flags:
                    action = "、".join(flags)
                    conn.execute(
                        """UPDATE fl_performance SET next_action=? WHERE sku=?
                           AND record_date=(SELECT MAX(record_date) FROM fl_performance WHERE sku=?)""",
                        (action, r["sku"], r["sku"])
                    )
                    flagged.append({"sku": r["sku"], "name": r["name"], "action": action})
        if flagged:
            try:
                from src.utils.notify import send_line_notify
                msg = "[AntiClaude] 商品自動標記\n" + "\n".join(
                    f"• {f['name']}：{f['action']}" for f in flagged
                )
                loop = _asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(send_line_notify(msg))
            except Exception:
                pass
        return {"flagged": flagged, "count": len(flagged)}
    except Exception as e:
        log.error(f"商品自動標記失敗：{e}")
        return {"flagged": [], "count": 0, "error": str(e)}


@router.get("/api/ecommerce/performance-history")
async def get_performance_history(weeks: int = 8):
    try:
        from src.db.connection import db
        with db() as conn:
            rows = conn.execute(
                """SELECT p.record_date, p.sku, pr.name,
                          p.revenue_7d, p.gross_margin, p.roas, p.sales_7d
                   FROM fl_performance p
                   JOIN fl_products pr ON p.sku = pr.sku
                   WHERE p.record_date >= date('now', ?)
                   ORDER BY p.record_date ASC""",
                (f"-{weeks * 7} days",)
            ).fetchall()
        return {"history": [dict(r) for r in rows]}
    except Exception as e:
        log.error(f"績效歷史查詢失敗：{e}")
        return {"history": []}


@router.get("/api/ecommerce/alerts")
async def get_product_alerts():
    try:
        from src.db.connection import db
        with db() as conn:
            rows = conn.execute(
                """SELECT p.sku, p.name,
                          COALESCE(latest.current_stock, inv.total_stock, 0) as stock,
                          CASE
                              WHEN latest.sales_7d IS NOT NULL AND latest.sales_7d > 0
                              THEN ROUND(COALESCE(latest.current_stock, inv.total_stock, 0)/(latest.sales_7d/7.0),1)
                              ELSE NULL
                          END as days_of_stock,
                          latest.gross_margin as gross_margin_rate
                   FROM fl_products p
                   LEFT JOIN (
                       SELECT fp.sku, fp.current_stock, fp.sales_7d, fp.gross_margin
                       FROM fl_performance fp
                       INNER JOIN (
                           SELECT sku, MAX(record_date) as max_date
                           FROM fl_performance GROUP BY sku
                       ) latest_fp ON fp.sku = latest_fp.sku AND fp.record_date = latest_fp.max_date
                   ) latest ON p.sku = latest.sku
                   LEFT JOIN (
                       SELECT sku, COALESCE(SUM(quantity),0) as total_stock
                       FROM fl_inventory GROUP BY sku
                   ) inv ON p.sku = inv.sku
                   WHERE p.status NOT IN ('stopped','archived')"""
            ).fetchall()
        alerts = []
        for r in rows:
            issues = []
            days = r["days_of_stock"]
            margin = r["gross_margin_rate"]
            if days is not None and days < 7:
                issues.append(f"庫存僅剩 {days} 天")
            if margin is not None and margin < 0.15:
                issues.append(f"毛利率過低 {round(margin * 100, 1)}%")
            if issues:
                alerts.append({"sku": r["sku"], "name": r["name"], "issues": issues})
        if alerts:
            try:
                from src.utils.notify import send_line_notify
                msg = "[AntiClaude] 商品警示\n" + "\n".join(
                    f"• {a['name']}（{a['sku']}）：{'、'.join(a['issues'])}" for a in alerts
                )
                loop = _asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(send_line_notify(msg))
            except Exception:
                pass
        return {"alerts": alerts, "count": len(alerts)}
    except Exception as e:
        log.error(f"商品警示檢查失敗：{e}")
        return {"alerts": [], "count": 0}

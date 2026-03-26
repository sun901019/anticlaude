# Flow Lab QQL Procurement Integration Specification (2026-03-21)

## 1. Purpose

This document integrates the new `QQL Agent Mode` into the existing Flow Lab product-intake and reverse-pricing system.

The goal is not to replace the previous Flow Lab model, but to extend it so the system can support multiple procurement modes.

The correct approach is:

- keep the existing Flow Lab pricing and Shopee 2026 architecture
- add `QQL Agent Mode` as a procurement-specific cost engine path
- preserve the same downstream outputs:
  - landed cost
  - suggested price
  - role fit
  - profitability view

---

## 2. Main Integration Principle

The previous spec assumed a general 1688 + cross-border shipping model.

The new QQL mode adds a more specific two-stage procurement model:

1. procurement cost paid through the agent
2. cross-border consolidation cost paid separately

This does **not** conflict with the earlier logic.

It simply means the system should now support:

- `procurement_mode = standard_1688`
- `procurement_mode = qql_agent`

The rest of the pricing system can stay shared.

---

## 3. Procurement Mode Architecture

Add a procurement mode field:

- `standard_1688`
- `qql_agent`

### 3.1 Standard 1688 mode

This follows the earlier generic model:

- product cost
- domestic shipping
- selected shipping route
- optional special-goods premium

### 3.2 QQL Agent mode

This uses the new two-stage model:

- negotiated product unit price
- domestic shipping allocation
- QQL exchange rate
- QQL service fee
- weight / volumetric logic
- sea-express shipping rate

This mode is more specific and should be modeled as a dedicated engine branch.

---

## 4. New Required Inputs for QQL Mode

## 4.1 User Inputs

These should be available when `procurement_mode = qql_agent`.

- `sku`
- `product_name`
- `cost_rmb`
- `domestic_shipping_rmb`
- `weight_kg`
- `length_cm` (optional)
- `width_cm` (optional)
- `height_cm` (optional)
- `target_role`

### Notes

- dimensions are optional, but when present they enable volumetric-weight pricing
- if dimensions are missing, the system should fall back to actual weight only

---

## 5. Global Environment Variables for QQL Mode

These should live in system settings, not per-product first-entry fields.

### QQL procurement variables

- `ENV_QQL_EXCHANGE_RATE`
- `ENV_QQL_SERVICE_FEE`
- `ENV_SEA_EXPRESS_RATE`
- `ENV_VOLUMETRIC_DIVISOR`

### Shared Shopee 2026 variables

- `ENV_SHOPEE_BASE_FEE`
- `ENV_SHOPEE_TX_FEE`
- `ENV_SHOPEE_FSS_FEE`
- `ENV_ADS_BUDGET`

These should become part of the pricing environment layer.

---

## 6. QQL Cost Engine Logic

## 6.1 Phase 1: Procurement Cost

This is the amount paid to the agent for purchasing the product.

Formula:

`Procurement_Cost_TWD = (cost_rmb + domestic_shipping_rmb) * ENV_QQL_EXCHANGE_RATE * (1 + ENV_QQL_SERVICE_FEE)`

This should be shown explicitly in the UI as:

- `Procurement Cost (Phase 1)`

## 6.2 Phase 2: Cross-Border Shipping Cost

This is the amount paid to the consolidator or logistics route.

### Volumetric weight

`Vol_Weight = (length_cm * width_cm * height_cm) / ENV_VOLUMETRIC_DIVISOR`

### Billable weight

`Billable_Weight = max(weight_kg, Vol_Weight)`

### Shipping cost

`Cross_Border_Cost_TWD = Billable_Weight * ENV_SEA_EXPRESS_RATE`

If dimensions are missing:

- `Billable_Weight = weight_kg`

## 6.3 Total Landed Cost

`Landed_Cost_TWD = Procurement_Cost_TWD + Cross_Border_Cost_TWD`

This should become the shared downstream input for all pricing logic.

---

## 7. Shopee 2026 Pricing Logic Under QQL Mode

After `Landed_Cost_TWD` is computed, the rest of the pipeline should remain shared with the existing Flow Lab pricing model.

### Shared pricing structure

Suggested price should still be derived from:

- landed cost
- Shopee fee environment
- target role
- ad budget assumption

### Shared total fee model

`Total_Shopee_Fee_Rate = ENV_SHOPEE_BASE_FEE + ENV_SHOPEE_TX_FEE + ENV_SHOPEE_FSS_FEE + ENV_ADS_BUDGET`

### Target margin mapping

- `traffic` -> `25%`
- `core` -> `40%`
- `profit` -> `55%`

### Reverse-derivation formula

If all relevant fees are percentage-based:

`Suggested_Price_TWD = Landed_Cost_TWD / (1 - Total_Shopee_Fee_Rate - Target_Margin_Rate)`

If fixed fee components exist in the future, they should be moved into the numerator as previously defined in the Flow Lab pricing spec.

---

## 8. UI / Dashboard Output Requirements

When the operator clicks calculate, the system should not only show a final price.
It should show a trust-building cost breakdown.

Required display order:

1. `Procurement Cost (Phase 1)`
2. `Cross-Border Shipping Cost (Phase 2)`
3. `Total Landed Cost`
4. `Suggested Shopee Price`
5. `Estimated Gross Profit per Unit`
6. `Matched Role`

This is especially important for QQL mode, because the two-stage cost model is the key business change.

---

## 9. Integration With Existing Flow Lab UX

The current Flow Lab intake model should not be discarded.

Instead, add a procurement-mode branch:

### Quick Add

Required first-step fields:

- SKU
- product name
- procurement mode
- cost_rmb
- domestic_shipping_rmb
- target_role

### Show conditional fields

If `procurement_mode = qql_agent`, show:

- weight
- dimensions

If `procurement_mode = standard_1688`, continue using the earlier generic shipping model.

This keeps the UX clean while supporting both procurement logic paths.

---

## 10. Recommended Data Model Additions

Add or standardize the following fields:

- `procurement_mode`
- `cost_rmb`
- `domestic_shipping_rmb`
- `weight_kg`
- `length_cm`
- `width_cm`
- `height_cm`
- `procurement_cost_twd`
- `cross_border_cost_twd`
- `landed_cost_twd`
- `target_role`
- `suggested_price_twd`
- `estimated_profit_twd`

Environment settings:

- `qql_exchange_rate`
- `qql_service_fee`
- `sea_express_rate`
- `volumetric_divisor`

---

## 11. Recommended UX Interpretation

The operator flow should become:

1. Choose sourcing mode.
2. Enter the product's known cost information.
3. Let the system calculate:
   - phase 1 procurement cost
   - phase 2 shipping cost
   - landed total cost
4. Let the system reverse-calculate the suggested Shopee price.
5. Review:
   - estimated profit
   - target role fit
   - market realism

This is a cleaner and more believable sourcing flow.

---

## 12. Recommended Integration Decision

The best integration decision is:

- do not replace the previous Flow Lab spec
- do not force every product into QQL mode
- add QQL as a procurement-specific engine path

This gives the system flexibility and keeps the architecture clean.

---

## 13. Final Conclusion

The new QQL procurement logic is compatible with the existing Flow Lab architecture.

The right way to combine them is:

- shared downstream pricing system
- procurement-mode-specific cost engine
- identical recommendation outputs

In short:

- procurement can vary
- landed cost model can vary
- pricing decision layer should stay unified

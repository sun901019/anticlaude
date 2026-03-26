# Flow Lab Top-Down Sourcing Ceiling Spec (2026-03-22)

## Purpose
This spec adds a new ecommerce decision module to Flow Lab:

- Bottom-Up pricing:
  - start from sourcing cost
  - estimate landed cost
  - derive suggested Shopee selling price

- Top-Down sourcing ceiling:
  - start from market selling price
  - define target role and target margin
  - calculate the maximum sourcing cost that is still acceptable

This turns Flow Lab from a pricing calculator into a stronger product selection decision engine.

## Why This Module Matters
This module supports a second high-value workflow:

### Existing flow: Bottom-Up
- You discover a product on 1688
- You input cost
- The system tells you whether Shopee pricing is viable

### New flow: Top-Down
- You discover a hot-selling Shopee product
- You input the market selling price
- The system tells you the maximum cost ceiling you can accept on 1688 / QQL

This gives you a hard sourcing negotiation threshold.

## Recommended Module Name
- `1688 採購天花板計算器`
- English internal name: `top_down_sourcing_ceiling`

## Core Concept
Instead of asking:
- "I found a product at this cost, what can I sell it for?"

You ask:
- "If I want to sell at this market price and keep my target margin, how much can I afford to pay upstream?"

## User Input Requirements

### Required Inputs

#### 1. `target_market_price_twd`
The target Shopee selling price in TWD.

Definition:
- the price you plan to sell at
- usually based on competitor market price or average hot-selling price

Example:
- `299`

#### 2. `target_role`
The intended product role.

Recommended enum:
- `traffic`
- `core`
- `profit`

Suggested mapping:
- `traffic` -> 25% target margin
- `core` -> 40% target margin
- `profit` -> 55% target margin

#### 3. `estimated_weight_kg`
Estimated unit weight in kg.

Purpose:
- used to reserve cross-border freight cost
- required for a practical sourcing ceiling

Example:
- `0.4`

### Optional Inputs

These are optional but useful when known:

#### 4. `estimated_length_cm`
#### 5. `estimated_width_cm`
#### 6. `estimated_height_cm`

Use case:
- especially important for QQL mode or volumetric freight cases
- if dimensions are present, system should compare actual weight and volumetric weight

#### 7. `procurement_mode`
Enum:
- `standard_1688`
- `qql_agent`

Reason:
- the upstream cost ceiling differs depending on procurement mode

#### 8. `domestic_shipping_rmb`
Optional if the operator already knows likely domestic shipping burden.

Default behavior:
- if unknown, treat as `0` in top-down screening
- operator can later refine with bottom-up calculator

## Hidden System Variables
These should come from existing ecommerce settings, not from user input each time.

### Shopee variables
- `commission_fee`
- `transaction_fee`
- `fss_pct`
- `fss_fixed`
- `fss_threshold`
- `promo_surcharge`
- `fulfillment_penalty`
- `traffic_margin_target`
- `core_margin_target`
- `profit_margin_target`

### Sourcing / logistics variables
- `exchange_rate`
- `qql_exchange_rate`
- `qql_service_fee`
- `sea_express_rate`
- `sea_fast_per_kg`
- `sea_regular_per_kg`
- `air_freight_per_kg`
- `volumetric_divisor`
- `special_goods_surcharge`

### Ads and risk defaults
- `default_ad_budget_rate`
- `default_return_rate`
- `default_damage_rate`

## Top-Down Calculation Logic

## Step 1: Compute maximum landed cost
This is the total cost budget allowed if the product must still preserve the desired margin.

Base idea:

`max_landed_cost = target_market_price * (1 - total_platform_fee_rate - target_margin - ad_budget_rate - risk_rate)`

Where:
- `total_platform_fee_rate` includes Shopee fees
- `target_margin` comes from role
- `ad_budget_rate` depends on strategy
- `risk_rate` may include default return/damage assumptions

### Suggested defaults
- `traffic` -> margin 25%, ads 10%
- `core` -> margin 40%, ads 15%
- `profit` -> margin 55%, ads 5%

If the system wants a simplified quick-screening mode, it may use:
- Shopee total burden rate as a pre-aggregated system value

But the more robust design is to keep the same fee engine family used by the ecommerce pricing backend.

## Step 2: Reserve cross-border freight
Subtract freight budget from landed-cost budget to get the product-cost budget.

### Standard 1688 mode
If `procurement_mode = standard_1688`:

`max_product_cost_twd = max_landed_cost - cross_border_freight_twd`

Where:
- `cross_border_freight_twd = billable_weight * selected_freight_rate`

### QQL mode
If `procurement_mode = qql_agent`:

The sourcing cost should account for QQL exchange and service fee.

If dimensions are present:
- `vol_weight = length * width * height / volumetric_divisor`
- `billable_weight = max(estimated_weight_kg, vol_weight)`

Else:
- `billable_weight = estimated_weight_kg`

Then:
- `cross_border_freight_twd = billable_weight * sea_express_rate`

## Step 3: Convert into sourcing ceiling

### For standard 1688
If the target is the maximum product cost in TWD:

`max_rmb_price = max_product_cost_twd / exchange_rate`

If domestic shipping is known and should be separated:

`max_goods_rmb = max_rmb_price - domestic_shipping_rmb`

### For QQL
If QQL applies:

`max_rmb_price = max_product_cost_twd / (qql_exchange_rate * (1 + qql_service_fee))`

If domestic shipping is known:

`max_goods_rmb = max_rmb_price - domestic_shipping_rmb`

## Output Requirements
The dashboard should not just show one number. It should explain the decision.

### Primary Outputs

#### 1. `target_profit_twd`
How much unit profit the chosen role is targeting.

Example:
- `NT$120`

#### 2. `max_landed_cost_twd`
The total landed cost ceiling.

Meaning:
- if final landed cost exceeds this, the role target fails

#### 3. `reserved_cross_border_freight_twd`
The freight budget deducted from the landed-cost ceiling.

#### 4. `max_product_cost_twd`
The maximum TWD budget that can be allocated to product sourcing before conversion.

#### 5. `max_rmb_price`
The final sourcing ceiling in RMB.

This is the key negotiation number.

### Secondary Outputs

#### 6. `system_judgment`
Short decision sentence.

Example:
- `請尋找單件含境內運費低於 ¥23.6 的供應商，否則無法達到 40% 主力款毛利。`

#### 7. `risk_flag`
Possible values:
- `safe`
- `tight`
- `not_viable`

#### 8. `assumption_summary`
Show the scenario assumptions used:
- role target
- fee environment
- freight mode
- weight or volumetric weight

## UI/UX Recommendations

## Placement Options

### Option A: Separate ecommerce tool
Add a dedicated section:
- `採購天花板`
- or `Top-Down 採購`

Best if you want this to feel like a distinct sourcing workflow.

### Option B: Inside Pricing Simulation
Add a toggle:
- `Bottom-Up`
- `Top-Down`

Best if you want both calculators in the same decision space.

### Option C: Inside product detail as a secondary tool
Useful later, but not ideal as first placement because top-down is often used before product creation.

### Recommended choice
Use **Option B or A**.

Reason:
- top-down is usually used at research / screening time
- not after full product data entry

## Best Input Design
Keep the form minimal:

- target market price
- target role
- estimated weight
- optional dimensions
- procurement mode

Do not require:
- SKU
- full product detail
- market low/high
- notes
- CCB/promo/fulfillment

Those are too heavy for a fast sourcing screen.

## Practical Example

### Input
- target market price: `299`
- role: `core`
- estimated weight: `0.4`
- procurement mode: `qql_agent`

### Example assumptions
- Shopee total burden rate: `17%`
- target margin: `40%`
- QQL sea express: `40 TWD/kg`
- QQL exchange rate: `4.686`
- QQL service fee: `1%`

### Logic
1. `max_landed_cost = 299 * (1 - 0.17 - 0.40) = 128.57`
2. `reserved_cross_border_freight = 0.4 * 40 = 16`
3. `max_product_cost_twd = 128.57 - 16 = 112.57`
4. `max_rmb_price = 112.57 / (4.686 * 1.01) = 23.8`

### Output
- target unit profit: `NT$120`
- landed cost ceiling: `NT$128.6`
- reserved cross-border freight: `NT$16`
- max sourcing ceiling: `¥23.8`
- judgment: `若供應商含境內運費報價高於 ¥23.8，則此商品無法達到 40% 主力款標準。`

## How This Fits Existing Flow Lab Architecture

### Existing tools
- Bottom-Up product intake and pricing spec
- QQL procurement integration
- ecommerce pricing decision workspace

### New tool role
This new module becomes the **pre-sourcing gate**.

Recommended workflow:

1. See hot-selling Shopee product
2. Use top-down sourcing ceiling tool
3. Get max acceptable RMB sourcing ceiling
4. Go to 1688 / QQL and screen suppliers
5. If supplier pricing is viable, continue into normal product intake
6. Use bottom-up calculator for full validation

## Decision Value
This tool answers:
- whether a category is even worth sourcing
- how hard you can negotiate
- whether a supplier quote should be rejected immediately

This prevents wasted time on impossible products.

## Required Questions To Confirm In Product Design

Before implementation, clarify these choices:

### 1. Should ad budget be fixed by role or editable?
Recommended:
- default by role
- optional advanced override

### 2. Should top-down mode include return/damage assumptions?
Recommended:
- yes, using global defaults
- but display them in assumption summary

### 3. Should market price use one number or competitor range?
Recommended:
- quick mode uses one target market price
- advanced mode can optionally accept low/hot/premium range later

### 4. Should domestic shipping be included in top-down screening?
Recommended:
- optional
- default zero if unknown
- allow operator to refine later

### 5. Should this be productless or attached to a candidate product?
Recommended:
- productless first
- allow "Save as candidate" later

## Recommended MVP
For first version, only require:
- target market price
- target role
- estimated weight
- procurement mode

System uses settings for everything else.

Outputs:
- target unit profit
- landed cost ceiling
- freight reserve
- max RMB sourcing ceiling
- decision sentence

This is enough to make the tool immediately valuable.

## Future Extensions

### Extension 1: competitor price structure
Later, this module can incorporate:
- floor price
- hot-selling price band
- premium sellable price band

### Extension 2: supplier comparison
Input multiple supplier quotes and compare them against the sourcing ceiling.

### Extension 3: save to candidate pool
Save successful top-down checks into candidate products.

### Extension 4: role comparison table
Show:
- traffic ceiling
- core ceiling
- profit ceiling

For the same market price.

This helps operators decide which strategy is realistic.

## Final Recommendation
Yes, this should be added to the system.

It is not a duplicate of the current calculator.
It serves a different decision stage:

- Bottom-Up = viability after discovering cost
- Top-Down = viability before sourcing

Together they form a stronger two-way sourcing and pricing system.

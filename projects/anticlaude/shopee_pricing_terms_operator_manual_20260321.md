# Shopee Pricing Terms Operator Manual (2026-03-21)

## Purpose

This is a short operator manual for the key Shopee pricing terms used in the Flow Lab / e-commerce system.

It is designed to be reusable inside:

- help drawer
- tooltip content
- settings page help text
- internal operator manual

---

## 1. CCB

`CCB` means the Shopee cashback program.

In this system, it represents the extra fee you pay when joining a Shopee coin/cashback promotion plan.

### Available modes

- `none`
  - no cashback plan
  - extra fee: `0%`
- `ccb5`
  - 5% cashback plan
  - extra fee: `1.5%`
- `ccb10`
  - 10% cashback plan
  - extra fee: `2.5%`
  - can offset certain promotion-day surcharge scenarios

### Why it matters

CCB directly affects:

- total cost
- suggested selling price
- gross margin
- campaign-day profitability

### Operator guidance

If you do not know which CCB mode to use yet, leave it as the system default and adjust later in product detail or scenario settings.

---

## 2. FSS

`FSS` means the Shopee free-shipping service fee.

In your current 2026 logic, it is effectively unavoidable and should always be included in cost estimation.

### Available modes

- percentage mode
  - example: `6%`
- fixed mode
  - example: `TWD 60`

### Why it matters

FSS changes the recommended selling price significantly.

### Operator guidance

Do not manually calculate FSS every time.
The system should calculate it automatically and show whether percentage mode or fixed mode is cheaper.

---

## 3. Promotion Day

Promotion day means Shopee campaign periods such as big sale days, mid-month events, or themed campaign windows.

### Effect in the system

- extra commission surcharge may apply
- current rule example: `+2%`
- certain CCB plans may reduce or offset this penalty

### Operator guidance

This is an environment condition, not core product identity.
It should be treated as a scenario setting, not a required first-step product field.

---

## 4. Fulfillment Days / Prep Days

This means how long it takes before the order can be shipped.

### Effect in the system

- if prep days are too long, Shopee may apply an extra penalty
- current rule example:
  - more than 2 days -> `+3%`

### Operator guidance

This should usually be handled as:

- a default setting
or
- a per-product scenario override

It should not be one of the main fields that block quick product creation.

---

## 5. Shipping Mode

This is the cross-border logistics route used from China to Taiwan.

### Current modes

- `air`
- `sea_express`
- `sea_freight`

### Why it matters

Shipping mode changes:

- landed cost
- delivery speed
- pricing pressure
- product suitability

### Operator guidance

This is a real sourcing fact and should stay in Quick Add.

---

## 6. Goods Type

This distinguishes between general goods and special goods.

### General goods

- normal products
- no battery
- no liquid
- no magnetic sensitivity

### Special goods

- battery
- magnetic
- liquid
- powder
- other restricted-risk goods

### Why it matters

Special goods usually increase shipping cost.

### Operator guidance

This is a first-entry product fact and should stay in Quick Add.

---

## 7. Suggested Role

The system may calculate a recommended role based on estimated margin.

### Current role logic

- `< 25%`
  - not suitable
- `25% - 40%`
  - traffic
- `40% - 50%`
  - core
- `>= 50%`
  - profit

### Operator guidance

The system should suggest the role first.
Manual role override should happen later in product detail, not during the initial Quick Add flow.

---

## 8. Suggested Selling Price

The system can reverse-calculate a recommended selling price based on:

- landed cost
- Shopee 2026 fee environment
- target role
- ad budget assumptions

### Typical outputs

- break-even price
- traffic price
- core price
- profit price

### Operator guidance

Use suggested price as a decision aid, not as an absolute truth.
If market high/low price is known, compare suggested price against market reality before finalizing.

---

## 9. Recommended Placement Inside the System

This manual can be reused in:

- e-commerce settings page
- product detail help section
- Add Product helper tooltip
- pricing simulation drawer

For the best UX, show short summaries inline and link to a longer help drawer when needed.

---

## 10. Final Principle

The operator should not need to memorize Shopee fee vocabulary.

The system should:

- explain terms simply
- calculate them automatically
- only ask for manual input when truly necessary

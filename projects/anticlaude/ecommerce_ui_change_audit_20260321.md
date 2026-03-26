# E-commerce UI Change Audit (2026-03-21)

## 1. Audit Scope

This audit checks whether the recent e-commerce UI work actually changed the experience, and what still remains unimproved.

Files inspected:

- `dashboard/src/app/ecommerce/page.tsx`
- `dashboard/src/components/Sidebar.tsx`
- `dashboard/src/components/TopNav.tsx`
- `src/ecommerce/router.py`

Validation:

- `npm run build` in `dashboard/` passed successfully

---

## 2. What Has Actually Improved

## 2.1 Add Product has been simplified compared to the earlier version

There is a real change.

Observed improvements:

- The Add Product modal is now explicitly framed as a simpler flow.
- Core identity and sourcing fields are placed earlier:
  - name
  - SKU
  - 1688 product cost
  - domestic shipping
  - shipping mode
- The pricing preview now appears much earlier and is visually more prominent.
- The pricing recommendation cards are now more central to the flow.
- The page has a local commerce accent direction rather than only the older global accent style.

This is a meaningful improvement.

## 2.2 Procurement / Add Inventory has improved

There is visible UX improvement in the procurement flow.

Observed improvements:

- procurement modal has a clearer title and intent
- live preview exists
- projected stock after inbound is shown
- estimated TWD cost is shown
- total batch preview is shown

This is better than the previous minimal inventory form.

## 2.3 E-commerce-specific styling has started

There is a commerce-themed styling layer already appearing in the page:

- local orange/commerce accent usage
- recommendation cards with differentiated colors
- more domain-specific visual emphasis

This means the page is no longer only using the generic system styling.

---

## 3. What Is Still Not Fully Improved

## 3.1 Add Product is simpler, but still not truly minimal

Even after the simplification, Quick Add still contains too much.

Still present in the Add Product flow:

- weight
- special goods toggle
- target price
- market high/low
- packaging cost
- ad budget
- notes
- expandable Shopee scenario controls

This is better than before, but still not a pure "Quick Add".

### Recommendation

Keep Quick Add focused on:

- name
- SKU
- product cost
- domestic shipping
- shipping mode
- goods type
- initial stock

Everything else should move to product detail or advanced configuration.

## 3.2 Shopee scenario controls are still inside Add Product

The following are still nested inside the modal:

- CCB plan
- promo day
- fulfillment days

These remain environment/scenario settings rather than first-entry product facts.

### Recommendation

Move them to:

- product detail
or
- settings defaults

The Add Product flow should not still be the place where the operator simulates campaign conditions.

## 3.3 Manual role logic is improved indirectly, but still not fully clean

The new preview cards are more prominent, but the overall role semantics still need cleanup across the page.

The page still contains mixed language around:

- suggested role
- target role
- viability
- manual role fields elsewhere

### Recommendation

Standardize role logic as:

- system suggests role during Quick Add
- operator overrides role only in detail view

## 3.4 Procurement is improved, but still not yet a full restock workflow

Current procurement modal is better, but still missing some higher-value fields:

- shipping method
- ETA
- landed cost by route
- richer notes and decision support

### Recommendation

Push the procurement modal one step further into a true restock workflow.

## 3.5 Product detail experience is still only partially structured

The drawer now shows grouped information, which is a good step.

But it is still mostly a display surface, not yet the full advanced configuration surface the new UX model needs.

### Recommendation

Turn the product drawer into a real detail workspace with sections for:

- basic
- cost & logistics
- pricing & market
- Shopee scenario
- performance
- AI recommendation

## 3.6 Some text still shows mojibake / garbled characters

This remains visible in several labels and helper texts in the inspected page output.

This reduces perceived quality and trust.

### Recommendation

Run a focused cleanup pass on the e-commerce page strings and nearby shared labels.

---

## 4. Visual Direction Assessment

## 4.1 Positive change

The page is visibly moving toward a more commerce-oriented tone.

That is good.

## 4.2 What still needs improvement

The styling is improved, but it does not yet feel fully unified.

Current issue:

- some areas use commerce styling
- some areas still feel like the older generic dashboard styling

### Recommendation

Create a consistent local token set for the e-commerce page:

- commerce accent
- commerce accent soft
- commerce border
- commerce text
- commerce muted text
- commerce warning/success bands

Then apply it consistently across:

- modal headers
- preview cards
- procurement preview
- detail drawer labels
- CTA buttons

---

## 5. Architecture Fit

The recent changes did **not** require a full rewrite, which is good.

The work so far mostly fits the intended direction:

- improve within the current architecture
- avoid destabilizing the system
- make the main operator flow simpler

This is the correct direction.

---

## 6. Current Overall Verdict

The e-commerce UI has **definitely changed and improved**.

This is not just a documentation-only change.

### What is now clearly better

- Add Product is cleaner than before
- pricing preview is more visible
- procurement preview is better
- commerce accent styling has started

### What is still unfinished

- Quick Add is still not minimal enough
- Shopee scenario settings still live inside Add Product
- product detail is not yet a full advanced workspace
- text cleanup is still needed
- visual consistency is not fully unified yet

---

## 7. Recommended Next Improvements

Priority order:

1. Remove remaining non-essential fields from Quick Add.
2. Move CCB/promo/prep-day controls out of Add Product.
3. Expand product detail into the real advanced settings surface.
4. Upgrade procurement to a fuller restock workflow.
5. Do a focused mojibake/string cleanup pass.
6. Unify commerce-local visual tokens across the page.

---

## 8. Final Conclusion

Yes, there are real improvements.

But the current state is:

- improved
- moving in the right direction
- not yet fully refined

The next step is not another rewrite.

The next step is a tighter refinement pass that finishes the split between:

- Quick Add
- advanced product detail
- procurement workflow
- settings defaults

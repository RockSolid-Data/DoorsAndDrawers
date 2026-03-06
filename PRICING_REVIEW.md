# Doors & Drawers — Pricing Review Document

> **Purpose:** Review how prices are currently calculated so we can identify what needs to change.
> Mark up this document with corrections, and we'll update the system accordingly.

---

## PART 1: DOOR PRICING

### How a Door Price is Currently Calculated

```
Door Price Per Unit = Style Price + (Wood Price × 2)
```

- **Style Price** — Each door style (e.g., ATFP, CTF) has a flat dollar price.
- **Wood Price** — Each wood type (e.g., Cherry, Maple) has TWO prices:
  - **Raised Panel Price** — used when the style's panel type is a raised panel
  - **Flat Panel Price** — used when the style's panel type has "use flat panel price" turned on
- The wood price is **multiplied by 2** and added to the style price.

#### Example

| Component         | Value   |
|-------------------|---------|
| Style (ATFP)      | $15.00  |
| Wood (Cherry) — Raised Panel | $8.50   |
| **Door Price**    | $15.00 + ($8.50 × 2) = **$32.00** |

---

### What DOES Affect Door Price

| Setting                          | Where to Change It         | How It's Used                        |
|----------------------------------|----------------------------|--------------------------------------|
| Style Price                      | Settings → Doors → Styles  | Base price per door                  |
| Wood Stock — Raised Panel Price  | Settings → Doors → Wood Stock | Added when panel type is raised    |
| Wood Stock — Flat Panel Price    | Settings → Doors → Wood Stock | Added when panel type is flat      |
| Panel Type — Use Flat Panel Price | Settings → Doors → Panel Types | Switches between raised/flat wood price |

---

### What DOES NOT Affect Door Price (but is tracked)

| Setting                        | Notes / Questions for Client                     |
|--------------------------------|--------------------------------------------------|
| Door Width & Height            | Should dimensions affect price? (e.g., per sq ft)|
| Panel Type — Surcharge Width   | What should this do?                             |
| Panel Type — Surcharge Height  | What should this do?                             |
| Panel Type — Surcharge Percent | What should this do?                             |
| Panel Type — Minimum Sq Ft     | Should there be a minimum sq ft charge?          |
| Edge Profile selection         | Should this affect price?                        |
| Design selection               | Should this affect price?                        |
| Panel Rise selection           | Should this affect price?                        |

---

### Questions for Client — Doors

1. Should door price be based on **square footage** (width × height) instead of or in addition to flat rates?
2. Should there be a **minimum square footage** charge per door?
3. Should the **panel type surcharges** (width, height, percent) apply to the price? If so, how?
4. Should different **edge profiles** have different prices or surcharges?
5. Should different **designs** have different prices?
6. Should **panel rise** options affect pricing?
7. Is the **"wood price × 2"** multiplier correct, or should it be calculated differently?
8. Any other factors that should affect door pricing?

---

## PART 2: DRAWER PRICING

### How a Drawer Price is Currently Calculated

```
Drawer Price Per Unit = Wood Stock Price + Bottom Price
                        + Undermount Charge (if selected)
                        + Finish Charge (if selected)
```

- **Wood Stock Price** — Each drawer wood type has a flat price.
- **Bottom Price** — Each drawer bottom material has a flat price.
- **Undermount Charge** — A single global charge added when undermount slides are selected.
- **Finish Charge** — A single global charge added when finishing is selected.

#### Example

| Component                | Value   |
|--------------------------|---------|
| Wood Stock (Maple)       | $12.00  |
| Bottom (1/4" Plywood)    | $5.00   |
| Undermount Charge        | $3.50   |
| Finish Charge            | $6.00   |
| **Drawer Price** (both options on) | $12.00 + $5.00 + $3.50 + $6.00 = **$26.50** |

---

### What DOES Affect Drawer Price

| Setting              | Where to Change It               | How It's Used                     |
|----------------------|----------------------------------|-----------------------------------|
| Wood Stock Price     | Settings → Drawers → Wood Stock  | Base material cost                |
| Bottom Price         | Settings → Drawers → Bottom Sizes| Bottom material cost              |
| Undermount Charge    | Settings → Drawers → Default Settings | Added if undermount = Yes    |
| Finish Charge        | Settings → Drawers → Default Settings | Added if finishing = Yes     |

---

### What DOES NOT Affect Drawer Price (but is tracked or configured)

| Setting                       | Notes / Questions for Client                        |
|-------------------------------|-----------------------------------------------------|
| Drawer Width                  | Should width affect price?                          |
| Drawer Height                 | Should height affect price?                         |
| Drawer Depth                  | Should depth affect price?                          |
| Drawer Pricing Table (height-based tiers) | This exists in settings but is not used. Should it be? |
| Surcharge Width               | What should this do?                                |
| Surcharge Depth               | What should this do?                                |
| Surcharge Percent             | What should this do?                                |
| Ends Cutting Adjustment       | What should this do?                                |
| Sides Cutting Adjustment      | What should this do?                                |
| Plywood Size Adjustment       | What should this do?                                |

---

### Questions for Client — Drawers

1. Should drawer price depend on **dimensions** (width, height, depth)?
2. The settings page has a **"Drawer Pricing" table** with price/height tiers — should this be used? How?
3. What are the **surcharge width/depth/percent** fields supposed to do?
   - Example: Add X% if width exceeds a certain size?
4. What are the **cutting adjustments** (ends and sides) for?
   - Are these subtracted from dimensions before cutting?
   - Do they affect pricing or just the cut list?
5. What is the **plywood size adjustment** for?
6. Should undermount/finish charges vary by wood type or size, or stay as a single flat rate?
7. Any other factors that should affect drawer pricing?

---

## PART 3: LINE ITEMS & ORDER TOTALS

### Line Item Total

```
Line Item Total = Price Per Unit × Quantity
```

- Any line item can be switched to **Custom Price** mode, which lets you manually enter a price instead of using the calculated price.

---

### Order Total Calculation

The order total is built up in layers:

```
Step 1:  Item Total  = Sum of all line item totals (doors + drawers + other items)
Step 2:  Discount    = Item Total × discount %   OR   flat dollar amount
Step 3:  Surcharge   = Item Total × surcharge %  OR   flat dollar amount
Step 4:  Shipping    = Item Total × shipping %   OR   flat dollar amount
Step 5:  Subtotal    = Item Total − Discount + Surcharge + Shipping
Step 6:  Total       = Subtotal + Tax
```

- **Discount, Surcharge, and Shipping** are set per customer (under Customer Defaults).
- Each can be either a **percentage** of the item total or a **fixed dollar amount**.
- **Tax** is a dollar amount on the order.

#### Example

| Step          | Calculation              | Result   |
|---------------|--------------------------|----------|
| Item Total    | (sum of all items)       | $500.00  |
| Discount (10%)| $500.00 × 10%           | −$50.00  |
| Surcharge (5%)| $500.00 × 5%            | +$25.00  |
| Shipping (flat)| —                       | +$25.00  |
| Subtotal      | $500 − $50 + $25 + $25  | $500.00  |
| Tax           | —                        | +$0.00   |
| **Order Total** | —                      | **$500.00** |

---

### Questions for Client — Order Totals

1. Is the discount/surcharge/shipping calculation correct?
2. Should discount apply **before** or **after** surcharges?
3. Should shipping be calculated on the subtotal (after discount) instead of the item total?
4. How should tax be determined? Flat rate? Percentage? Based on customer state?
5. Any other order-level charges or adjustments needed?

---

## PART 4: CURRENT SETTINGS VALUES

> **Action needed:** We will pull the current values from the database and fill these in
> before the client meeting, or review them live in the Settings pages.

### Door Settings to Review
- [ ] All **Style** names and prices
- [ ] All **Wood Stock** names, raised panel prices, and flat panel prices
- [ ] All **Panel Type** configurations
- [ ] All **Edge Profile** options
- [ ] All **Design** options

### Drawer Settings to Review
- [ ] All **Drawer Wood Stock** names and prices
- [ ] All **Drawer Bottom** types, thicknesses, and prices
- [ ] **Drawer Pricing** table entries (currently unused)
- [ ] **Default Drawer Settings** (charges and adjustments)

### Customer Defaults to Review
- [ ] Discount type and value per customer
- [ ] Surcharge type and value per customer
- [ ] Shipping type and value per customer

---

## How to Use This Document

1. **Review** each section with the client
2. **Answer** the questions in each section
3. **Mark up** what needs to change:
   - Cross out anything that should be removed
   - Add notes for new pricing rules
   - Correct any values or formulas
4. **Return** this document and we will update:
   - The calculation logic in the code
   - The settings pages to match
   - Any new fields or options needed
   - All current price values in the database

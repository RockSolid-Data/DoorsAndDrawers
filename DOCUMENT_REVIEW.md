# Doors and Drawers - Printable Documents Review

> **Purpose:** This document lists every printable document the software currently generates,
> along with a detailed breakdown of what each one contains. It also lists document types that
> do NOT currently exist but may be needed. Review this with the client, mark up what should
> change, and hand it back so the documents can be rebuilt/updated/created accordingly.
>
> **How to use this document:** For each section below, discuss with the client:
> 1. Is this document needed? (Yes / No / Needs changes)
> 2. What should be added or removed?
> 3. Write notes directly in the "Client Notes" areas.

---

## TABLE OF CONTENTS

1. [Existing Documents](#existing-documents)
   - [Order PDF](#1-order-pdf)
   - [Quote PDF](#2-quote-pdf)
2. [Documents That Do NOT Exist Yet](#documents-that-do-not-exist-yet)
   - [Invoice](#3-invoice-does-not-exist)
   - [Work Order / Shop Ticket](#4-work-order--shop-ticket-does-not-exist)
   - [Packing Slip](#5-packing-slip-does-not-exist)
   - [Customer List Report](#6-customer-list-report-does-not-exist)
   - [Order List / Summary Report](#7-order-list--summary-report-does-not-exist)
   - [Quote List / Summary Report](#8-quote-list--summary-report-does-not-exist)
3. [Available Data Fields Reference](#available-data-fields-reference)

---

## EXISTING DOCUMENTS

---

### 1. Order PDF

**Status:** Exists  
**Triggered from:** "Print Order" button on the Order Detail screen  
**Output:** Downloads as PDF file named `order_<number>.pdf`  
**Page size:** Letter (portrait), 2cm margins  

#### What it currently contains:

**HEADER**
- Company name: "Doors and Drawers" (centered, large text)
- Order number (e.g., "Order #1042")

**ORDER INFORMATION (left column)**
- Order Date
- Created At (timestamp)

**CUSTOMER INFORMATION (right column)**
- Company name
- Contact name (first + last)
- Billing Address (line 1, line 2 if present)

**ORDER NOTES**
- Free-text notes field (only shown if notes exist)

**LINE ITEMS - DOORS TABLE** (only shown if door items exist)
| Column | Description |
|--------|-------------|
| Type | Door type (e.g., "Door") |
| Wood Type | Name of wood stock |
| Edge Profile | Edge profile name |
| Panel Rise | Panel rise name |
| Style | Style name |
| Dimensions (W x H) | Width and height |
| Rails (T x B x L x R x I) | Top, bottom, left, right, and interior rail sizes |
| Sanding | "Edge", "Cross Grain", or "None" |
| Quantity | Number of units |
| Price/Unit | Dollar amount per unit |
| Total | Line total |

**LINE ITEMS - DRAWERS TABLE** (only shown if drawer items exist)
| Column | Description |
|--------|-------------|
| Wood Type | Name of wood stock |
| Bottom Type | Drawer bottom material name |
| Dimensions (W x H x D) | Width, height, and depth |
| Options | "Undermount" and/or "Finished"/"Unfinished" |
| Quantity | Number of units |
| Price/Unit | Dollar amount per unit |
| Total | Line total |

**LINE ITEMS - MISCELLANEOUS TABLE** (only shown if generic items exist)
| Column | Description |
|--------|-------------|
| Type | Item type |
| Name | Item description |
| Quantity | Number of units |
| Price/Unit | Dollar amount per unit |
| Total | Line total |

**ORDER SUMMARY**
| Line | Description |
|------|-------------|
| Items Total | Sum of all line items |
| Discount | Discount amount (shown as negative) |
| Surcharge | Surcharge amount |
| Shipping | Shipping amount |
| Subtotal | After discount/surcharge/shipping |
| Tax | Tax amount |
| **Grand Total** | **Final total** |

**FOOTER**
- "Generated on [date]"

#### What it does NOT currently include:
- Customer phone, fax, or email
- Customer city, state, zip (only billing address lines)
- Payment terms or due date
- PO number / reference number
- Company logo (image)
- Company address, phone, or contact info
- Line item number / row number
- Any subtotals per section (doors subtotal, drawers subtotal, etc.)
- Page numbers

#### Client Notes:
> _Is this document needed?_ Yes / No / Needs changes
>
> _What should be added?_
>
>
> _What should be removed?_
>
>
> _Other notes:_
>
>

---

### 2. Quote PDF

**Status:** Exists  
**Triggered from:** "Print Quote" button on the Quote Detail screen  
**Output:** Downloads as PDF file named `quote_<number>.pdf`  
**Page size:** Letter (portrait), 2cm margins  

#### What it currently contains:

**HEADER**
- Company name: "Doors and Drawers" (centered, large text)
- Quote number (e.g., "Quote #1042")

**QUOTE INFORMATION (left column)**
- Quote Date
- Created At (timestamp)

**CUSTOMER INFORMATION (right column)**
- Company name
- Contact name (first + last)
- Billing Address (line 1, line 2 if present)

**QUOTE NOTES**
- Free-text notes field (only shown if notes exist)

**LINE ITEMS - DOORS TABLE** (identical to Order PDF)
| Column | Description |
|--------|-------------|
| Type | Door type |
| Wood Type | Name of wood stock |
| Edge Profile | Edge profile name |
| Panel Rise | Panel rise name |
| Style | Style name |
| Dimensions (W x H) | Width and height |
| Rails (T x B x L x R x I) | Top, bottom, left, right, and interior rail sizes |
| Sanding | "Edge", "Cross Grain", or "None" |
| Quantity | Number of units |
| Price/Unit | Dollar amount per unit |
| Total | Line total |

**LINE ITEMS - DRAWERS TABLE** (identical to Order PDF)
| Column | Description |
|--------|-------------|
| Wood Type | Name of wood stock |
| Bottom Type | Drawer bottom material name |
| Dimensions (W x H x D) | Width, height, and depth |
| Options | "Undermount" and/or "Finished"/"Unfinished" |
| Quantity | Number of units |
| Price/Unit | Dollar amount per unit |
| Total | Line total |

**LINE ITEMS - MISCELLANEOUS TABLE** (identical to Order PDF)
| Column | Description |
|--------|-------------|
| Type | Item type |
| Name | Item description |
| Quantity | Number of units |
| Price/Unit | Dollar amount per unit |
| Total | Line total |

**QUOTE SUMMARY**
| Line | Description |
|------|-------------|
| Items Total | Sum of all line items |
| Discount | Discount amount (shown as negative) |
| Surcharge | Surcharge amount |
| Shipping | Shipping amount |
| Subtotal | After discount/surcharge/shipping |
| Tax | Tax amount |
| **Grand Total** | **Final total** |

**FOOTER**
- "Generated on [date]"
- "This is a quote only. Not an invoice or confirmation of order."

#### Differences from Order PDF:
- Says "Quote" everywhere instead of "Order"
- Footer includes disclaimer: "This is a quote only. Not an invoice or confirmation of order."
- Otherwise identical in structure and content

#### What it does NOT currently include:
- Quote expiration / valid-until date
- Customer phone, fax, or email
- Customer city, state, zip (only billing address lines)
- Company logo (image)
- Company address, phone, or contact info
- Acceptance / signature line
- Terms and conditions
- Line item number / row number
- Page numbers

#### Client Notes:
> _Is this document needed?_ Yes / No / Needs changes
>
> _What should be added?_
>
>
> _What should be removed?_
>
>
> _Other notes:_
>
>

---

## DOCUMENTS THAT DO NOT EXIST YET

The following document types are common for this kind of business but do not currently exist
in the software. Discuss with the client whether any of these are needed.

---

### 3. Invoice (Does Not Exist)

**Status:** Does not exist  
**Typical purpose:** A billing document sent to the customer requesting payment for a completed order.

#### Typical contents for this type of business:
- Company name, address, phone, logo
- "INVOICE" header with invoice number
- Invoice date and payment due date
- Payment terms (e.g., Net 30, Due on Receipt)
- Bill-To customer info (company, contact, address, city, state, zip, phone)
- Ship-To address (if different)
- Reference/PO number
- Line items with pricing (same as order)
- Order summary (subtotal, discount, surcharge, shipping, tax, total)
- Amount paid / balance due
- Payment instructions or notes

#### Client Notes:
> _Is this document needed?_ Yes / No
>
> _If yes, what should it include?_
>
>
> _How is it different from the Order PDF?_
>
>
> _Other notes:_
>
>

---

### 4. Work Order / Shop Ticket (Does Not Exist)

**Status:** Does not exist  
**Typical purpose:** An internal document for the shop floor that tells workers what to build. Focused on production specs, not pricing.

#### Typical contents for this type of business:
- Order number and date
- Customer name (for reference)
- Line items with FULL production specs but NO pricing:
  - **Doors:** Wood type, edge profile, panel rise, style, width, height, all rail sizes, sanding options, quantity
  - **Drawers:** Wood type, bottom type, width, height, depth, undermount yes/no, finishing yes/no, quantity
  - **Misc items:** Name, description, quantity
- Special instructions / order notes
- Checkboxes or sign-off lines for QC
- Due date or priority

#### Client Notes:
> _Is this document needed?_ Yes / No
>
> _If yes, what should it include?_
>
>
> _Should pricing be shown or hidden?_
>
>
> _Other notes:_
>
>

---

### 5. Packing Slip (Does Not Exist)

**Status:** Does not exist  
**Typical purpose:** A document included with a shipment that lists what is in the box/pallet. No pricing.

#### Typical contents for this type of business:
- Order number
- Ship date
- Ship-To customer name, company, address
- List of items being shipped (description + quantity)
- No pricing information
- Space for notes or shipping instructions

#### Client Notes:
> _Is this document needed?_ Yes / No
>
> _If yes, what should it include?_
>
>
> _Other notes:_
>
>

---

### 6. Customer List Report (Does Not Exist)

**Status:** Does not exist  
**Typical purpose:** A printable list of all customers (or filtered subset) for reference.

#### Typical contents:
- Company name
- Contact name (first + last)
- Phone and fax
- Address (full: line 1, line 2, city, state, zip)
- Taxable status
- Customer notes

#### Client Notes:
> _Is this document needed?_ Yes / No
>
> _If yes, what should it include?_
>
>
> _Should it be filterable/sortable before printing?_
>
>
> _Other notes:_
>
>

---

### 7. Order List / Summary Report (Does Not Exist)

**Status:** Does not exist  
**Typical purpose:** A printable summary of multiple orders (e.g., all orders for a date range, or all orders for a customer).

#### Typical contents:
- Report title and date range
- Table of orders:
  - Order number
  - Customer name
  - Order date
  - Total amount
  - Status
- Grand total of all listed orders
- Count of orders

#### Client Notes:
> _Is this document needed?_ Yes / No
>
> _If yes, what filters should be available?_ (by date range, by customer, etc.)
>
>
> _Other notes:_
>
>

---

### 8. Quote List / Summary Report (Does Not Exist)

**Status:** Does not exist  
**Typical purpose:** A printable summary of multiple quotes.

#### Typical contents:
- Report title and date range
- Table of quotes:
  - Quote number
  - Customer name
  - Quote date
  - Total amount
  - Status (open, converted to order, expired)
- Grand total of all listed quotes
- Count of quotes

#### Client Notes:
> _Is this document needed?_ Yes / No
>
> _If yes, what filters should be available?_
>
>
> _Other notes:_
>
>

---

## AVAILABLE DATA FIELDS REFERENCE

These are all the data fields currently stored in the system that could potentially be
included on any document. This is provided for reference when deciding what to add.

### Customer Fields
| Field | Description |
|-------|-------------|
| company_name | Company name |
| first_name | Contact first name |
| last_name | Contact last name |
| taxable | Whether the customer is taxable (yes/no) |
| address_line1 | Street address line 1 |
| address_line2 | Street address line 2 |
| city | City |
| state | State (2-letter code) |
| zip_code | ZIP code (5 digits) |
| phone | Phone number (10 digits) |
| fax | Fax number (10 digits) |
| notes | Free-text customer notes |
| door_defaults | Customer-specific door default settings (JSON) |
| drawer_defaults | Customer-specific drawer default settings (JSON) |

### Order / Quote Fields
| Field | Description |
|-------|-------------|
| order_number | Auto-generated order/quote number |
| customer | Link to customer record |
| is_quote | Whether this is a quote vs. confirmed order |
| billing_address1 | Billing address line 1 |
| billing_address2 | Billing address line 2 |
| order_date | Date of the order/quote |
| notes | Free-text order/quote notes |
| discount_amount | Discount dollar amount |
| surcharge_amount | Surcharge dollar amount |
| shipping_amount | Shipping dollar amount |
| tax_amount | Tax dollar amount |
| total | Grand total |
| item_total | Calculated sum of all line items |
| subtotal | Calculated subtotal after adjustments |
| created_at | Timestamp when record was created |
| updated_at | Timestamp when record was last modified |

### Door Line Item Fields
| Field | Description |
|-------|-------------|
| type | Item type (always "Door") |
| wood_stock | Wood species/stock (linked record) |
| edge_profile | Edge profile (linked record) |
| panel_rise | Panel rise type (linked record) |
| style | Door style (linked record) |
| width | Door width |
| height | Door height |
| rail_top | Top rail size |
| rail_bottom | Bottom rail size |
| rail_left | Left rail size |
| rail_right | Right rail size |
| interior_rail_size | Interior rail size |
| sand_edge | Sand edge (yes/no) |
| sand_cross_grain | Sand cross grain (yes/no) |
| quantity | Number of units |
| price_per_unit | Calculated or custom price per unit |
| custom_price | Whether price was manually overridden |
| total_price | Quantity x price per unit |

### Drawer Line Item Fields
| Field | Description |
|-------|-------------|
| type | Item type (always "Drawer") |
| wood_stock | Wood species/stock (linked record) |
| bottom | Drawer bottom material (linked record) |
| width | Drawer width |
| height | Drawer height |
| depth | Drawer depth |
| undermount | Undermount option (yes/no) |
| finishing | Finishing option (yes/no) |
| quantity | Number of units |
| price_per_unit | Calculated or custom price per unit |
| custom_price | Whether price was manually overridden |
| total_price | Quantity x price per unit |

### Generic (Miscellaneous) Line Item Fields
| Field | Description |
|-------|-------------|
| type | Item type category |
| name | Item name / description |
| quantity | Number of units |
| price_per_unit | Price per unit |
| custom_price | Whether price was manually overridden |
| total_price | Quantity x price per unit |

---

## SUMMARY

| # | Document | Status | Notes |
|---|----------|--------|-------|
| 1 | Order PDF | EXISTS | Printable from order detail page |
| 2 | Quote PDF | EXISTS | Printable from quote detail page |
| 3 | Invoice | DOES NOT EXIST | |
| 4 | Work Order / Shop Ticket | DOES NOT EXIST | |
| 5 | Packing Slip | DOES NOT EXIST | |
| 6 | Customer List Report | DOES NOT EXIST | |
| 7 | Order List / Summary Report | DOES NOT EXIST | |
| 8 | Quote List / Summary Report | DOES NOT EXIST | |

> **Next steps:** After reviewing with the client, fill in the "Client Notes" sections
> and return this document. Each document will then be built, updated, or removed as specified.

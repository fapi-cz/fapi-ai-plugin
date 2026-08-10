---
name: fapi-upsell-order-bump
description: >-
  Use this skill when the user wants Fapilot to add, update, verify, or remove
  an order bump, miniupsell, checkout add-on, doplňková položka, upsell page, or
  post-order offer on an existing FAPI sales form. Trigger for requests such as
  “přidej order bump”, “miniupsell do formuláře”, “nabídni po objednávce”,
  “one-click upsell”, “upsell stránka”, or “něco navíc v košíku”. Do not use
  for creating a new sales form from scratch, creating a standalone product
  catalog item without assigning it to a form, or building marketing copy only.
---

# Configure a FAPI order bump or upsell

## Purpose

Configure a revenue add-on on an existing FAPI sales form without overwriting unrelated form configuration.

Order bumps and upsells are commercial flow settings, not only text blocks. They depend on resolved products, correct form update semantics, and a verified buyer journey.

## Scope

Use this skill for:

* Adding, replacing, removing, or verifying order bumps on an existing form.
* Adding, replacing, removing, or verifying post-order upsell pages on an existing form.
* Resolving or creating missing bump or upsell products when the user provides enough product data.
* Preserving current form items, triggers, discounts, legal settings, payments, and existing add-ons during updates.

Do not use this skill for:

* Creating the original sales form from scratch; use `fapi-sales-form-create`.
* Creating a product that will not be attached to a form.
* Inventing landing-page URLs, legal content, prices, product IDs, or external automation IDs.
* Running a real checkout or payment test unless the user explicitly asks for it.

## Domain model

### Order bump / miniupsell

An order bump appears inside the order form before the buyer submits the original order. FAPI customer-facing help may call it a miniupsell or a doplňková prodejní položka.

In MCP/API fields:

```text
allow_order_bumps: true
order_bumps: [{ item_template_id, name, description }]
```

The title must include `{price}`. Safe HTML is allowed in the title and description, but the title is usually plain text.

### Upsell page

An upsell appears after the original order is submitted. It requires a real URL of a separate upsell page that contains the FAPI upsell choice controls.

In MCP/API fields:

```text
upsell_pages: [{ upsell_url, upsells: [{ item_template_id }] }]
```

Do not substitute an order bump when the user asks for a post-order offer, and do not invent an upsell URL.

### Product / item template

The add-on offer must reference a FAPI product from the catalog. Resolve every referenced product using `item_templates_list` and `item_templates_show`; create it only when the request contains enough name, price, currency, and product-type information.

## Procedure

### 1. Classify the requested add-on

Determine:

* Target form: name, ID, or enough context to find it.
* Offer type: order bump before checkout submission, upsell after order submission, or both.
* Add-on product: existing product ID/name/code or product details for creation.
* Commercial behavior: one-time, recurring, installment-related, physical shipping, discountable, or fulfillment-specific.
* Copy and URL requirements: bump title/description, upsell page URL, and whether the user supplied final wording.

Ask one focused question only when the workflow is blocked by an indispensable value:

* No identifiable existing form.
* No identifiable add-on product and insufficient product data to create one.
* Missing price or currency for a product that must be created.
* Missing upsell URL for a post-order upsell.
* Ambiguous matched form or product candidates.

Do not ask for optional wording. Draft concise bump copy when the product and price are known, keeping `{price}` in the title.

### 2. Load the current form

1. If the user supplied a form ID, call `forms_show`.
2. Otherwise call `forms_list` with `search`, `show_only_names: true`, and a small `limit`.
3. If there is one clear candidate, inspect it using `forms_show`.
4. If several candidates match, ask which form to modify.

Read `references/update-fields.md` before composing `forms_update`.

Do not update from `forms_list` alone. The existing `items`, `order_bumps`, `upsell_pages`, `triggers`, and other relational lists must be preserved unless the user explicitly wants to change them.

### 3. Resolve add-on products

For each order bump or upsell product:

1. Search with `item_templates_list` by exact name or code when available.
2. Inspect the selected candidate using `item_templates_show`.
3. Verify price, currency, type, VAT, stock, and periodic settings against the form.
4. Create a missing product with `item_templates_create` only when all required commercial values are known.
5. Use the returned or inspected product ID as `item_template_id`.

Do not guess IDs. Do not use a stock-enabled product as a recurring add-on unless existing form behavior and product configuration already make that valid.

### 4. Compose the update

Start from the `forms_show` result and change only the requested add-on lists.

#### Add or update an order bump

Use:

```json
{
  "allow_order_bumps": true,
  "order_bumps": [
    {
      "item_template_id": 200,
      "name": "Ano, přidat pracovní sešit za {price}",
      "description": "<p>Praktická cvičení ke kurzu. Cena: <strong>{price}</strong>.</p>"
    }
  ]
}
```

Rules:

* Preserve existing order bumps unless the user wants them replaced or removed.
* Include `{price}` in `name`; include `{price}` in `description` when price is mentioned.
* Use `{itemName}`, `{priceBeforeDiscount}`, or `{image}` only when it improves the offer.
* Keep HTML to the safe subset: `a`, `br`, `p`, `strong`, `b`, `i`, `em`, `u`, `s`, `strike`, `span`, `ul`, `ol`, `li`.
* Use only `http`, `https`, or `mailto` links in anchors.
* If the main form is recurring, explicitly decide whether the bump should also recur. If it should not recur, report the limitation or use supported recurring replacement logic only with verified requirements.

#### Add or update an upsell page

Use:

```json
{
  "upsell_pages": [
    {
      "upsell_url": "https://example.cz/upsell",
      "upsells": [{ "item_template_id": 300 }]
    }
  ]
}
```

Rules:

* Preserve existing upsell pages unless the user wants them replaced or removed.
* Require a real URL for every upsell page.
* Multiple products may be offered on one page only when the user intends that.
* Multiple sequential offers should usually be separate `upsell_pages` entries in the intended order.
* When installment behavior matters, inspect existing form settings before using `settings.upsell_to_all_repayment_invoices`.
* If one-click or post-payment behavior is requested, verify the relevant current form settings and report anything the MCP cannot configure.

#### Remove add-ons

When removing:

* Remove only the matching bump or upsell entry.
* If no order bumps remain, set `allow_order_bumps: false` and `order_bumps: []`.
* If no upsells remain, set `upsell_pages: []`.
* Preserve unrelated relational lists.

### 5. Update exactly once

Call `forms_update` with the form ID and the smallest payload that changes the intended add-on configuration.

Important update behavior:

* Sending `order_bumps` replaces the stored order-bump list.
* Sending `upsell_pages` replaces the stored upsell-page list.
* Sending `items`, `item_groups`, `triggers`, `discount_codes`, `changeable_items`, or similar relational lists replaces those lists.
* Omit unrelated fields and lists.

### 6. Verify the stored form

Call:

```text
forms_show({ id: form_id, withPaymentMethods: true })
```

Verify:

* The form ID and name match the intended target.
* Existing main products and unrelated settings are still present.
* Order bump IDs, title, description, and `allow_order_bumps` match the intended result.
* Upsell pages contain the intended URLs and product IDs in the intended order.
* Product currencies and recurring/installment assumptions are compatible with the form.
* No requested external effect is claimed without a real test.

Do not consider the task complete from `forms_update` success alone.

## Decision table

| User intent | Interpretation | Action |
| --- | --- | --- |
| “Přidej něco navíc do košíku” | Order bump / miniupsell | Resolve form and product, merge into `order_bumps`, enable `allow_order_bumps`. |
| “Miniupsell ve formuláři” | Order bump | Use `order_bumps`; keep `{price}` in title. |
| “Nabídni po objednávce” | Post-order upsell | Require `upsell_url`, merge into `upsell_pages`. |
| “One-click upsell” | Upsell journey with payment behavior expectations | Configure verified upsell page fields, then report any unverified payment-flow limitation. |
| “Nahraď bump X produktem Y” | Replace one list entry | Preserve other add-ons and update only the matching entry. |
| “Smaž upsell” | Remove post-order offer | Remove matching `upsell_pages` entry and verify empty or remaining list. |
| “Přidej doplněk k novému formuláři” | New-form creation with add-on | Use `fapi-sales-form-create`; this skill may inform the add-on part. |

## Known failure modes

### Existing add-ons disappear

Cause: `forms_update` was sent with a partial `order_bumps` or `upsell_pages` list.

Resolution:

1. Always inspect the current form first.
2. Merge the intended change into the complete existing list.
3. Send the full list only for the list being changed.
4. Verify with `forms_show`.

### Order bump is rejected or rendered incorrectly

Check:

* `allow_order_bumps` is true.
* `item_template_id` belongs to a valid product.
* `name` contains `{price}`.
* HTML uses only the allowed tags and URL schemes.
* Product price exists in the form currency.

### Upsell cannot be configured

Check:

* A real `upsell_url` is known.
* The upsell page exists outside the form and can host FAPI upsell controls.
* `upsells` contains valid product IDs.
* The user is not expecting a checkout-in-form bump while asking for post-order behavior.

### Recurring or installment behavior is unclear

Order bumps on recurring purchases can affect later recurring invoices. Upsells may need explicit installment behavior such as applying to all repayment invoices.

Ask only when the commercial outcome changes materially. Otherwise keep existing form behavior and state the assumption.

## Output

Return in the user's language using only applicable sections:

```markdown
## Upsell/order bump nastaven

**Formulář:** …
**Přidaná nabídka:** …
**Typ:** order bump / upsell

## Ověření

- …

## Zbývá ověřit ručně

- …
```

Do not claim that payment, one-click charging, email delivery, membership access, or external integrations work end to end unless those flows were actually tested.

## Examples

### Add a checkout order bump

**Request**

> Do formuláře „Kurz time managementu” přidej pracovní sešit za 190 Kč jako miniupsell.

**Procedure**

1. Find and inspect the form.
2. Resolve or create the workbook product.
3. Merge an order bump into the existing `order_bumps` list with `{price}` in the title.
4. Call `forms_update`.
5. Verify with `forms_show`.

### Add a post-order upsell

**Request**

> Po objednávce e-booku nabídni videokurz na stránce https://example.cz/upsell-videokurz.

**Procedure**

1. Find and inspect the form.
2. Resolve the video-course product.
3. Merge a new entry into `upsell_pages`.
4. Call `forms_update`.
5. Verify the URL and product ID in `forms_show`.

## Resources

Load resources only when needed:

* `references/update-fields.md` — Read before any `forms_update` call.
* `references/help-sources.md` — Read when terminology, user-facing behavior, or FAPI help provenance matters.

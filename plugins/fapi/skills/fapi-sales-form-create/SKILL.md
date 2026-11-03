---
name: fapi-sales-form-create
description: >-
  Use this skill when the user wants Fapilot to create a new FAPI sales form,
  order form, checkout, objednávkový formulář, or prodejní formulář. Trigger
  for requests to start selling an existing or new product, configure payment
  methods, installments, subscriptions, buyer fields, an order bump, upsell,
  thank-you page, or post-purchase actions as part of a new form. Do not use
  for editing an existing form, issuing a manual invoice, merely embedding a
  form, or troubleshooting an already-created checkout.
---

# Create a FAPI sales form

## Purpose

Create a usable, customer-facing FAPI sales form that matches the user's offer, reuses account defaults, minimizes checkout friction, and is verified after creation.

A sales form is not merely a visual form. It connects products, orders, invoicing, payment, customer data, messages, reminders, fulfillment actions, and the post-order journey.

## Scope

Use this skill for:

* Creating a new one-time, installment, or recurring sales form.
* Reusing an existing product or creating a missing product when the request contains enough product data.
* Configuring products, payments, currencies, billing fields, order bumps, upsells, discounts, thank-you URLs, and supported automations.
* Producing the shortest correct path to a first order while honoring explicit advanced requirements.

Do not use this skill for:

* Updating, deleting, archiving, duplicating, or reactivating an existing form.
* Creating a manual invoice without a sales form.
* Styling with custom CSS, obtaining embed code, or running a live checkout test as the primary task.
* Inventing legal text, consent wording, prices, URLs, or entity IDs.

## Domain model

### Sales form

The form is the checkout configuration. It references reusable products and account-scoped entities such as a project, invoice series, message-template set, reminder set, payment gateway, discount code, and integration connection.

Creation returns `form_id`. Always use that ID to inspect the stored result.

### Product / item template

FAPI stores reusable products as item templates. Resolve a product before assigning it to:

* `items` — main products,
* `item_groups` — grouped choices or add-ons,
* `order_bumps` — an offer inside checkout before submission,
* `upsell_pages` — an offer after the original order is submitted,
* `changeable_items` — a replacement used in later recurring invoices.

A new product requires at least a name and one price containing `type`, `currency_code`, and `price`.

### Installments versus recurring billing

* **Installments** divide one purchase into a fixed number of payments. Use `allow_repayments` and `repayment_counts`.
* **Recurring billing** creates an ongoing schedule. Use `allow_recurring`, `period`, and `end_by`.
* **Automatic recurring card charges** additionally require a compatible gateway and `allow_gopay_recurring_payments`.
* **Installments** and **Recurring billing** can not be combined.

Do not use these concepts interchangeably.

### Order bump versus upsell

* An **order bump** appears inside the form before submission.
* An **upsell** is offered after the original order and requires an upsell page URL.

Order bumps and upsells on a recurring purchase are also included in later recurring invoices unless replacement logic changes it.

### Account defaults

FAPI can supply account defaults for project, invoice series, message templates, reminders, business terms, recurring terms, and GDPR information.

Preserve those defaults unless the user explicitly requests a different known entity, URL, or wording. Never send placeholder legal content.

## Procedure

### 1. Build the offer model

Determine from the request and available account data:

* Main product or products.
* Price, currency, VAT treatment, quantity behavior, and whether the product is physical, digital, a service, or recurring.
* One-time payment, installments, or recurring billing.
* Requested payment methods.
* Necessary buyer and delivery data.
* Optional discount, order bump, upsell, thank-you page, or fulfillment action.

Infer a form name when absent, for example `Objednávka – <product name>`. Do not block creation merely to ask for a name.

Ask one focused question only when creation is impossible without an indispensable value, typically:

* No identifiable product or offer.
* Missing price or currency for a product that must be created.
* A required external URL or undiscoverable integration/entity ID.

Do not ask the user to choose every optional setting. Leave unspecified options at FAPI defaults.

### 2. Prevent duplicates

1. Call `forms_list` with `search` set to the proposed name and a small `limit`.
2. Compare returned names exactly; form search may be broader than an exact match.
3. If an exact match exists, inspect it with `forms_show` and compare its products and purpose.
4. Reuse it only when it already represents the requested result or the user clearly refers to it.
5. Do not silently create a second identical form. A request for “another”, “copy”, “variant”, or a distinct campaign permits a separate, clearly named form.

`forms_create` is non-idempotent. Duplicate prevention must happen before the write.

### 3. Resolve every product

For each main, bump, upsell, grouped, or replacement product:

1. Call `item_templates_list` with an exact `name` or `code` when available.
2. If there is one unambiguous match, inspect it using `item_templates_show`.
3. Verify prices, currencies, VAT, type, periodic settings, stock, and quantity rules.
4. If no match exists and the request contains sufficient data, call `item_templates_create`.
5. If several products match, do not guess. Resolve by exact code or ask one focused question.

When creating a product:

* Use `one_time` for a normal price, including a product later sold through form-level installments.
* Use `repayment` only for an explicitly defined installment price entry.
* Set `periodic: true` and `period` only for a genuinely recurring product.
* Do not infer a VAT rate from the product name. Use `vat: 0` only when known.
* Use vat rate from account settings `vat` key. Is user is non-vat-paying, set `vat: 0`. Alse set `include_vat: false`.
* For `enable_stock: true`, also provide `stock`.
* Never use a stock-enabled product in recurring billing.
* Ensure intended currencies have product prices, or explicitly report reliance on conversion.

### 4. Resolve only required dependencies

Do not enumerate the whole account before creating a simple form.

| Requirement                   | Read tool                                                                         | Rule                                                                                                                |
|-------------------------------|-----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Existing product              | `item_templates_list`, `item_templates_show`                                      | Always resolve before creation.                                                                                     |
| Online payment                | `payment_gateways_list`, `payment_gateways_show`                                  | Require a connected compatible gateway; prefer production mode for a production form.                               |
| Bank transfer or QR readiness | `bank_account_sets_list`                                                          | Verify an account for each currency when payment readiness matters.                                                 |
| Existing discount             | `discount_codes_list`, `discount_codes_show`                                      | Use only a matching verified code ID.                                                                               |
| Custom sales email communication | `message_template_sets_list`, `notification_reference_show` | Omit to inherit defaults unless explicitly requested. Use `fapi-sales-email-communication-create` for custom sales emails. |
| Default message/reminder set | `message_template_sets_list`, `reminder_sets_list`, `notification_reference_show` | Use `fapi-default-notification-templates` when only default notification templates or reminders are needed. |
| Integration action            | `connections_list`, `connections_show`                                            | Filter by application and use only an owned connection.                                                             |
| Currency validation           | `currencies_list`                                                                 | Use when a requested code is uncertain or uncommon.                                                                 |

The current MCP does not provide a general list of projects, invoice series, shipping methods, custom fields, FAPI Member sections, or individual message templates. Use `fapi-sales-email-communication-create` when custom sales email communication is required. Use `fapi-default-notification-templates` when default message or reminder content is required. Use IDs only when the user supplies them or another tool result exposes them. Never fabricate IDs.

### 5. Compose the smallest correct form

Read `references/form-create-fields.md` when translating detailed requirements into fields.

#### Products

* Put ordinary products in `items`.
* Use `item_groups` only for an explicitly grouped set of choices or add-ons.
* In `item_groups`, child items may be required only when `allow_multiple_items: true`.
* When `allow_multiple_items` is false or omitted, require the group instead and leave every child item's `required` false or unset.
* Keep the first product preselected unless the user wants a conscious choice; then set `settings.disable_autofill_product: true`.

#### Buyer fields

Start from the low-friction default: email and country visible and required; name, company, address, phone, and note hidden.

Add fields only for an operational reason:

* Named access or personalization: name.
* Full invoice or B2B sale: relevant name/company and address fields.
* Physical delivery: name, address, usually phone, and optionally a separate shipping address.
* Buyer instructions: note only when useful.

Do not collect data merely because a field exists.

A simplified Czech tax document is appropriate only within the applicable value limit. When the known order may exceed `10,000 CZK`, require the necessary address data and disable simplified-document behavior when appropriate.

#### Payments

When the user does not specify methods, preserve FAPI's baseline rather than inventing a gateway choice.

For an online method:

1. Resolve a compatible connected gateway.
2. Set `allow_gopay: true` and `gopay_connection`.
3. Enable only requested methods actually supported by that connection, such as `allow_gopay_card`, `allow_gopay_wire`, `allow_gopay_gpay`, or `allow_gopay_paypal`.
4. Verify the resolved methods after creation.

Field names containing `gopay` are historical and are also used with other supported providers.

Use cash on delivery only for physical fulfillment. Use cash only when an in-person process exists.

#### Currency

For a typical new form, use `currency_setting: by-country`. FAPI uses the buyer's billing country for the order and invoice. The built-in map uses CZK for Czechia and EUR for Slovakia and every other country. An account-specific currency map takes precedence.

Keep the billing country visible and required. With `by-country`, omit `currency_code` and `allowed_currencies`. A product price quoted in CZK can still use country-based checkout.

* For an explicitly requested fixed currency, use `currency_setting: always` and `currency_code`.
* If the user wants the buyer to choose, use `currency_setting: choice` and `allowed_currencies`.

Use uppercase ISO 4217 codes. Check product prices and requested payment methods in each offered currency. Verify bank-account compatibility when bank transfer or QR payment is needed.

#### Invoicing

Keep `proforma: true` for the normal pay-before-tax-document flow unless the user explicitly wants an immediate regular invoice.

Do not set project, invoice series, message sets, reminder sets, reverse-charge policy, or delayed invoice behavior without a stated requirement and a known entity/value.

#### Legal settings

Normally omit:

* `terms_url`,
* `recurring_terms_url`,
* `purposes`,
* custom GDPR HTML.

This lets account-level settings populate the form. Override only with user-provided, form-specific legal configuration. Do not generate legal wording.

#### Installments

Use:

```text
allow_repayments: true
repayment_counts: [<positive counts>]
```

Use the plural field. `repayment_count` is deprecated.

#### Recurring billing

Use:

```text
allow_recurring: true
period: <DateTime-modify period, e.g. "1 months">
end_by: none | iteration | date
```

Supply `iteration` only with `end_by: iteration`, and `last_date` only with `end_by: date`.

For automatic card charging:

1. Resolve a gateway that supports recurring/on-demand charges.
2. Enable card payment through that gateway.
3. Set `allow_gopay_recurring_payments: true` before the customer's first card payment.
4. Inherit recurring terms unless the user supplies a specific URL.

#### Order bump

Use only for a complementary, low-friction add-on:

* Set `allow_order_bumps: true`.
* Use a verified product ID.
* Include `{price}` in the title.
* Use `{itemName}`, `{priceBeforeDiscount}`, or `{image}` only when useful.
* Prefer `item-paid` fulfillment when delivery depends on the bump being selected and paid.

When the internal thank-you page should contain product-specific instructions, put shared content outside the conditional block and wrap only the optional product content in `{item-<item_code>}...{/item-<item_code>}` inside `thanks_content`. Resolve the product and use its non-empty `code` in both tags, preserving the returned spelling even though matching ignores letter case. If the product has no code, update it with a unique code first. This syntax is for the internal FAPI thank-you page; it does not modify content hosted at a custom `thanks_url`. Do not nest product-conditional blocks.

#### Upsell

An upsell requires a real post-order URL:

```text
upsell_pages: [{ upsell_url, upsells: [{ item_template_id }] }]
```

Do not invent the URL or substitute an order bump for an upsell.

#### Actions

Use payment events for fulfillment that must follow successful payment:

* `paid` for the order,
* `item-paid` for one product,
* `item-paid-with-code` for a product-code family.

Use `ordered` only when fulfillment may occur before payment. Configure an action only when every required ID or URL is verified.

### 6. Create exactly once

Call `forms_create` with:

* the resolved name,
* resolved main product IDs,
* explicit user requirements,
* only optional configuration justified by the request.

Do not create speculatively and then repair the result with updates. Resolve dependencies first and make one coherent create call.

Capture `form_id`.

### 7. Verify the stored form

Call:

```text
forms_show({ id: form_id, withPaymentMethods: true })
```

Verify every applicable requirement:

* Exact name and intended product IDs.
* No item group with `allow_multiple_items: false` or omitted contains a child item with `required: true`.
* Stored currency mode, available product prices, and billing country visibility for `by-country`.
* Requested payment methods are resolved and available.
* Installment or recurring settings are internally consistent.
* Buyer fields collect enough data without unnecessary friction.
* Order bump and upsell IDs are correct.
* Thank-you URL and requested triggers are stored.
* Account defaults remain inherited where no override was requested.

A successful `forms_create` response is not enough by itself.

Configuration verification does not prove a real payment, bank import, email, webhook, membership grant, or shipping flow works end to end. The FAPI preview is functional and can create a real order; distinguish inspection from an actual checkout test.

### 8. Return an operational summary

Respond in the user's language using only applicable sections:

```markdown
## Prodejní formulář vytvořen

**Název:** …  
**ID formuláře:** …

**Nabídka:** …
**Platby:** …
**Fakturace:** …
**Údaje zákazníka:** …
**Automatizace:** …

## Ověření

- …

## Zbývá ověřit ručně

- …
```

Clearly separate completed configuration from external steps the tools cannot execute or verify.

## Decision table

| User intent                                  | Interpretation                                                    | Configuration                                                                |
|----------------------------------------------|-------------------------------------------------------------------|------------------------------------------------------------------------------|
| “Vytvoř jednoduchý formulář pro produkt X”   | Minimal one-time checkout                                         | Resolve X, use `items`, prefer `by-country`, and inherit account defaults.                            |
| “Chci platbu kartou”                         | Online checkout                                                   | Resolve gateway, enable gateway and card, verify resolved methods.           |
| “Na 3 nebo 6 splátek”                        | Fixed installment choices                                         | `allow_repayments: true`, `repayment_counts: [3, 6]`.                        |
| “Měsíční členství bez konce”                 | Indefinite recurring billing                                      | Monthly period, `end_by: none`.                                              |
| “12 měsíčních plateb”                        | Usually a finite recurring schedule, but potentially installments | Resolve the ambiguity only when it changes the commercial model.             |
| “Přidej levný doplněk v košíku”              | Order bump                                                        | Resolve add-on, enable bumps, include `{price}` in title.                    |
| “Nabídni produkt po objednávce”              | Upsell                                                            | Require a real upsell URL and use `upsell_pages`.                            |
| “Potřebuji fakturační adresu”                | Full buyer identification                                         | Show and require the appropriate address/name/company fields.                |
| “Prodávám fyzické zboží”                     | Shipping-capable checkout                                         | Physical product, delivery fields, verified shipping methods when available. |
| “Použij moje běžné e-maily, GDPR a podmínky” | Account inheritance                                               | Omit form-specific overrides.                                                |

## Known failure modes

### Product is missing or ambiguous

1. Search by exact name and code.
2. Inspect the candidate.
3. Create only with sufficient product data.
4. Otherwise ask for the single missing blocking value.

### Online payment does not resolve

Check in order:

1. A connected gateway exists.
2. The intended connection is selected.
3. `allow_gopay` and the specific method flag are enabled.
4. The gateway supports the method and currency.
5. The form contains a payable product.

Then verify with `forms_show(..., withPaymentMethods: true)`.

### Bank transfer or QR readiness is uncertain

Check `bank_account_sets_list` for each currency. Form creation alone does not prove bank payments will be imported and paired.

### Recurring creation fails

Common causes:

* A product has stock tracking enabled.
* Automatic charging has no gateway connection.
* The gateway/API version does not support recurring charges.
* Recurring message configuration is incomplete.
* `end_by` lacks its companion `iteration` or `last_date`.

### Order bump is rejected or incomplete

Check the enable flag, product ownership, `{price}` placeholder, and any product-specific delivery trigger.

### Legal content is missing

Do not invent it. Inherit account defaults or request the user's approved URL/text.

### Shipping or membership automation is blocked

The connection may be discoverable while the required shipping-method or member-section ID is not. Create the safe core form when possible and report the exact unresolved dependency.

### The user assumes the form was fully tested

A configuration check is not a transaction test. A real preview/order/payment test remains necessary for payment, email, fulfillment, and external integration assurance.

## Domain-specific rules and gotchas

* Every referenced entity must belong to the authenticated account.
* Never guess product, discount, gateway, connection, message, reminder, shipping, or custom-field IDs.
* Product search can be exact; form search may be broader, so compare form names exactly.
* Use uppercase three-letter currency codes.
* `max_width`, when changed, must be at least `500`.
* A redirect-style two-step form requires `two_step_redirect_url`.
* Enabling bumps, discounts, shipping methods, or changeable items without valid entries is incomplete.
* In a single-selection item group, require the group rather than an individual child item. `items[].required: true` is valid only when `allow_multiple_items: true`.
* UI terminology “prodejní položka” maps to MCP “item template”.
* `proforma: true` is a normal advance-invoice flow, not test mode.
* Form language also influences the default country shown to the buyer.
* The executable MCP schema is authoritative. UI documentation may expose additional options not supported by the tool.

## Examples

### Simple digital product

**Request**

> Vytvoř mi formulář pro e-book „Produktivita bez chaosu“ za 490 Kč.

**Procedure**

1. Search for the product.
2. If missing, create a one-time CZK digital product.
3. Check for an exact form-name collision.
4. Create a one-product form with `currency_setting: by-country` and inherited account defaults.
5. Verify the form and resolved payment methods.

### Subscription with automatic card charging

**Request**

> Udělej formulář na měsíční členství za 790 Kč, platba kartou se má strhávat automaticky.

**Procedure**

1. Resolve or create the recurring monthly product.
2. Verify stock tracking is disabled.
3. Resolve a compatible connected gateway.
4. Create indefinite monthly billing with card and automatic recurring charging.
5. Verify recurring and payment-method configuration.

### Complementary checkout offer

**Request**

> K hlavnímu kurzu přidej v objednávce pracovní sešit za 190 Kč.

Interpret “v objednávce” as an order bump. Resolve both products, create the course as the main item, add the workbook as a bump with `{price}`, and verify its ID.

## Resources

Load resources only when needed:

* `references/form-create-fields.md` — Read when mapping detailed business requirements to `forms_create` fields or validating combinations.
* `references/scenario-recipes.md` — Read for physical goods, installments, recurring billing, order bumps, upsells, multiple currencies, or two-step forms.
* `references/sources.md` — Read when provenance, capability precedence, or recently changed FAPI behavior matters.

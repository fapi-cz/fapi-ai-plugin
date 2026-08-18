---
name: fapi-account-activation
description: >-
  Use this skill when the user wants Fapilot to activate or onboard a FAPI
  account for first sale, start sales, prepare an empty account, set billing
  information, invoice defaults, VAT/currency basics, bank account readiness,
  payment gateway readiness, first product, first sales form, embed/share the
  form, or run a first test order checklist. Do not use for only creating a
  product, only creating a sales form, only adding an upsell/order bump, or
  troubleshooting an already-running account.
---

# Activate a FAPI account for first sale

## Purpose

Move a FAPI account from initial setup to a verified first sellable checkout with the fewest safe steps.

Activation is an onboarding workflow across account defaults, billing identity, payment readiness, product catalog, sales form, publication, and test order. It should delegate specialized creation tasks to the product and form skills instead of duplicating their full logic.

## Scope

Use this skill for:

* Auditing readiness of a new or inactive account.
* Setting or verifying billing information.
* Verifying account defaults such as VAT mode, currency, due date, proforma behavior, language, and invoice/email behavior.
* Checking bank account and payment-gateway readiness.
* Orchestrating first product creation and first sales-form creation.
* Producing a launch checklist for embedding/sharing the form and testing the first order.

Do not use this skill for:

* Only creating a product; use `fapi-product-create`.
* Only creating a sales form; use `fapi-sales-form-create`.
* Only editing an order bump or upsell; use `fapi-upsell-order-bump`.
* Reconfiguring advanced tax/accounting/legal settings without explicit user-provided values.
* Claiming that payments, bank imports, emails, or integrations work end to end without a real test.

## Domain model

### Activation state

```text
account defaults -> billing identity -> payment readiness -> product -> sales form -> publish -> test order -> real sale
```

Each stage can be complete, incomplete, blocked, or delegated to a more specific skill.

### Billing information

Billing information identifies the seller on invoices. `users_update_billing_information` requires:

```text
name
emails
address.street
address.city
address.zip
address.country_code
```

### Payment readiness

Bank transfer and QR payment require a usable bank account set for the intended currency. Online card and wallet methods require a connected production-ready payment gateway.

The payment gateway MCP tools are read-only. When no gateway is connected, report that the payment gateway must be setup manually instead of pretending to connect one.

### First sellable checkout

A first checkout needs at minimum:

* one usable product (`item_template_id`),
* one sales form (`form_id`),
* at least one viable payment method,
* a way to publish or share the form,
* a test-order plan.

## Procedure

### 1. Determine activation goal

Classify the request:

* Audit only: inspect and report readiness.
* Guided activation: fill missing account details and create missing product/form when data is sufficient.
* First sale launch: finish enough setup for a concrete product and payment path.

Extract known values:

* Seller billing name, email, address, country, company IDs, phone, web.
* Currency, VAT mode, default VAT, due date, language.
* Bank account details and intended currencies.
* Payment methods: bank transfer, QR, card, PayPal, Google Pay, cash, COD.
* First product details: name, price, currency, type.
* Form/publication details: form name, thank-you URL, embed target, test/live requirement.

Ask one combined question only when a write cannot be done safely because indispensable values are missing. Do not ask about optional polish.

### 2. Inspect account state

Use read-only tools first:

1. `settings_list` for `account_summary` and key settings.
2. `users_show` for current user and billing state when available.
3. `bank_account_sets_list` for bank-transfer and QR readiness.
4. `payment_gateways_list` with `only_connected: true` and, for production launch, `production_mode_enabled: true`.
5. `item_templates_list` with a small limit or exact name/code when the first product is known.
6. `forms_list` with `show_only_names: true` and search when a likely form name is known.

Read `references/readiness-checklist.md` before reporting readiness or deciding what to write.

Do not enumerate unrelated account objects when the user asks for a narrow activation path and enough context is already known.

### 3. Complete billing identity when requested and safe

Use `users_update_billing_information` only when the user supplied enough verified seller data.

Required shape:

```json
{
  "name": "FAPI s.r.o.",
  "emails": "billing@example.cz",
  "address": {
    "street": "Hlavni 123",
    "city": "Praha",
    "zip": "12000",
    "country_code": "CZ"
  }
}
```

Rules:

* Prefer `country_code` over `country`.
* Do not invent registration numbers, VAT IDs, phone, web, or file reference.
* Preserve existing billing information unless the user clearly wants to change it.
* After update, verify using the returned user or `users_show`.

### 4. Treat account settings as guarded

Use `settings_update` only for explicit, low-ambiguity user requests or when the activation request cannot work without that setting and the user provided the value.

Guarded settings include:

* `currency`
* `vat_mode`
* `vat`
* `payday`
* `payment_type`
* `language`
* `proforma`
* invoice/email behavior settings

Changing `currency` can affect existing invoices and exchange rates. Do not change it silently.

Read `references/account-fields.md` before updating settings, bank accounts, or payment readiness.

### 5. Ensure payment readiness

For bank transfer or QR:

1. Inspect `bank_account_sets_list`.
2. Check that at least one set has a bank account for the intended currency.
3. If missing and the user provided bank account data, create a set with `bank_account_sets_create`.
4. If updating an existing set, inspect it first and send the complete `bank_accounts` list, preserving existing account IDs.
5. Never create new bank account set, when you have more bank_accounts. Only when you want to create new bank account set is when you're creating new project. Only one back account set is default, other bank account sets MUST be assigned to a project. If bank account set is not default, or it is not assigned to a project, it will not be used for payment. If you want to use bank account set for payment, it must be default or assigned to a project.

For online payments:

1. Call `payment_gateways_list` with `only_connected: true`.
2. For production launch, include or filter by `production_mode_enabled: true`.
3. Use `payment_gateways_show` for the selected gateway.
4. If none is connected, report manual gateway setup as a blocker or launch with bank transfer/QR only when acceptable.

Do not claim a payment gateway was connected; MCP exposes read-only gateway tools.

### 6. Create or resolve the first product

If no suitable product exists and the user supplied enough product details, use `fapi-product-create`.

Minimum product data:

* name,
* price,
* currency or known account default,
* product type or enough context to infer one safely.

Do not continue to form creation with an unknown product ID.

### 7. Create or resolve the first sales form

If no suitable form exists and product/payment requirements are known, use `fapi-sales-form-create`.

Minimum form outcome:

* references the resolved main product,
* uses viable payment methods,
* preserves account defaults for legal texts, messages, reminders, project, and numbering unless explicitly overridden,
* is verified with `forms_show`.

If the product exists but the form is incomplete, let `fapi-sales-form-create` handle creation. If an existing form only needs an add-on, use `fapi-upsell-order-bump`.

### 8. Publish and test

Give the user the next operational steps:

* Share or embed the form.
* Run a test order in the FAPI preview/test flow.
* Verify invoice creation, payment method display, email delivery, thank-you page, and fulfillment.
* Then run the first real low-risk transaction if needed.

Configuration inspection is not a transaction test.

## Decision table

| User intent | Interpretation | Action |
| --- | --- | --- |
| “Rozjeď mi FAPI účet” | Full activation | Inspect settings, billing, payments, products, forms; fill safe gaps and delegate product/form. |
| “Chci první prodej” | First sellable checkout | Resolve product and form; verify payment readiness; return launch checklist. |
| “Jen zkontroluj účet” | Readiness audit | Read-only inspection and gap report. |
| “Doplň fakturační údaje” | Billing identity update | Use `users_update_billing_information` when required seller fields are supplied. |
| “Nastav účet na EUR” | Guarded setting change | Explain currency impact; update only with explicit instruction. |
| “Chci platbu kartou” | Payment gateway readiness | Inspect connected production gateways; report blocker if none exists. |
| “Vytvoř produkt” | Product-only task | Use `fapi-product-create`. |
| “Vytvoř formulář” | Form-only task | Use `fapi-sales-form-create`. |

## Known failure modes

### Activation stalls on billing data

Cause: billing identity requires seller data that cannot be inferred.

Ask for the missing required fields together: seller name, billing email, street, city, ZIP, and country code.

### Bank transfer appears enabled but cannot be paid correctly

Check:

* bank account set exists,
* intended currency has a bank account,
* `bank_account_name` is not too long for QR usage,
* form payment methods include wire/QR where intended.

### Online payment is requested but no gateway is connected

MCP can inspect but not connect gateways. Report the exact blocker and proceed with bank transfer/QR only if the user accepts that launch mode.

### Account settings are over-edited

Cause: broad activation interpreted as permission to change defaults.

Resolution: update only settings that are explicitly supplied and required. Prefer preserving account defaults.

### First form exists but is not verified

Do not rely on `forms_list`. Inspect with `forms_show`, including payment methods when relevant.

## Output

Return in the user's language using only applicable sections:

```markdown
## Aktivace účtu

**Stav:** připraveno / částečně připraveno / blokováno

## Hotovo

- …

## Chybí

- …

## Ověření

- …

## Další krok

- …
```

Clearly separate completed configuration from manual or external setup.

## Examples

### Readiness audit

**Request**

> Zkontroluj, jestli je účet připravený na první prodej.

**Procedure**

1. Inspect settings, user billing, bank accounts, payment gateways, products, and forms.
2. Classify readiness by activation stage.
3. Return blockers and the shortest next step.

### Guided first sale

**Request**

> Rozjeď mi prodej e-booku za 490 Kč, účet je nový.

**Procedure**

1. Inspect account defaults and billing readiness.
2. Ask for missing billing data if needed.
3. Use `fapi-product-create` for the e-book.
4. Use `fapi-sales-form-create` for the checkout.
5. Verify and return publish/test steps.

## Resources

Load resources only when needed:

* `references/readiness-checklist.md` — Read before readiness audits or final activation status.
* `references/account-fields.md` — Read before billing, setting, bank-account, or payment-readiness writes.
* `references/sources.md` — Read when source precedence or related workflow routing matters.

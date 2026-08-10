---
name: fapi-invoice-create
description: >-
  Use this skill when the user wants Fapilot to create, prepare, verify, or
  safely issue a FAPI invoice, manual invoice, proforma invoice, simplified
  invoice, credit note, faktura, zálohová faktura,
  daňový doklad, dobropis, or invoice from an existing client/product. Trigger
  for requests involving invoice customer data, invoice items, VAT, due dates,
  paid status, notification emails, triggers, payment type, or credit-note
  parent invoice. Do not use for recurring/periodic invoice setup, product
  catalog creation only, sales-form checkout creation, or invoice deletion.
---

# Create a FAPI invoice

## Purpose

Create a correct invoice document from verified client, item, tax, payment, and date data, then verify the stored result.

Manual invoice creation is not a sales-form checkout. It writes a financial document directly, so client identity, VAT, dates, paid state, emails, triggers, document type, and parent invoice relationships need explicit care.

## Scope

Use this skill for:

* Creating regular invoices, proformas, simplified invoices, payment confirmations, or credit notes.
* Resolving or creating a client before invoice creation.
* Reusing item templates for invoice items when known.
* Creating invoice items from explicit request data.
* Setting dates, currency, language, payment type, bank details, notification behavior, and paid status when explicitly requested.
* Verifying created invoices with `invoices_show`.

Do not use this skill for:

* Periodic or recurring invoice templates; use a recurring-invoice skill.
* Creating product catalog items unless needed as a separate `fapi-product-create` step.
* Creating a sales form or checkout; use `fapi-sales-form-create`.
* Updating or deleting existing invoices unless the user explicitly asks and a separate update/delete workflow is appropriate.
* Creating credit notes without a verified parent invoice and correction reason when required by the business context.

## Domain model

### Invoice

`invoices_create` requires:

```text
client
items: [{ name, price }]
```

The `client` is a FAPI client ID, not merely a customer email. Resolve or create the client first.

### Client versus customer

* `client` is the stored FAPI client ID required by `invoices_create`.
* `customer` is invoice snapshot data such as email, name, address, VAT IDs, and shipping address.

Use `customer` only for invoice-specific snapshot overrides. Do not assume it creates or selects the client.

### Item template versus invoice item

An `item_template_id` links an invoice item to a reusable product. It is optional; every invoice item still needs at least `name` and `price`.

Use `item_templates_list` and `item_templates_show` when the user references an existing product. Use `fapi-product-create` only when a missing catalog product must be created for future reuse, not for a one-off invoice line.

### Document type

Only one of these should be true for a created document:

```text
proforma
simplified_invoice
credit_note
```

If none is set, FAPI creates the normal default invoice flow according to supplied and account-level values.

## Procedure

### 1. Build the invoice intent

Determine:

* Document type: regular invoice, proforma, simplified invoice or credit note.
* Client identity: existing client ID, email, name/company, address, VAT identifiers.
* Invoice items: names, prices, counts, VAT, price-includes-VAT, type, code, item template IDs.
* Currency, language, payment type, dates, due date, bank details.
* Whether the invoice should be marked paid and with which `paid_on` date.
* Whether to send notifications or execute triggers.
* Whether the invoice is connected to a form, shipping method, parent invoice, or credit-note correction.

Ask one combined question only when creation is blocked by missing required or tax-sensitive data:

* no client ID and no email to resolve/create a client,
* no invoice item,
* missing price,
* unclear document type when the requested flags conflict,
* missing parent invoice for credit note,
* missing currency or VAT treatment when account defaults do not decide safely.

### 2. Inspect account defaults and current data

Use read-only tools first:

1. `settings_list` for currency, VAT mode/default VAT, due date, language, proforma/payment defaults, and email behavior.
2. `clients_list` by exact email, ID, or search to resolve the invoice client.
3. `item_templates_list` / `item_templates_show` when invoice items reference existing products.
4. `invoices_show` when creating a credit note, payment confirmation, or parent-linked invoice.
5. `bank_account_sets_list` only when overriding bank account data or payment readiness matters.

Read `references/invoice-fields.md` before composing `invoices_create`.

### 3. Resolve or create the client

If the user supplies a client ID:

1. Use `clients_list` with `id` when possible or proceed if the client was already verified by context.
2. Do not create another client for the same buyer.

If the user supplies an email:

1. Call `clients_list({ email, limit: 10 })`.
2. Reuse an exact unique match.
3. If several clients match or the existing client conflicts materially, ask.
4. If no client exists and required data is sufficient, call `clients_create`.

Client creation minimum:

```json
{
  "email": "customer@example.test"
}
```

Add name, company, VAT IDs, address, shipping address, and metadata only when known.

### 4. Resolve invoice items

For each item:

* Require `name` and `price`.
* Use `count` when quantity differs from one.
* Use `including_vat` when known; otherwise rely on account/product defaults only when safe.
* Use `vat` when explicit or inherited from verified product/account default.
* Use `item_template_id` only after resolving a product.
* Do not create a catalog product merely to issue a one-off custom line unless the user wants future reuse.

Read `references/scenario-recipes.md` for proformas, simplified invoices, credit notes, paid invoices, and product-backed items.

### 5. Compose the invoice payload

Use snake_case field names exactly as exposed by MCP:

```json
{
  "client": 23,
  "items": [
    {
      "name": "Konzultace",
      "price": 2500,
      "including_vat": true,
      "count": 1,
      "type": "service"
    }
  ],
  "customer": {
    "email": "customer@example.test",
    "address": {
      "country": "CZ"
    }
  },
  "payment_type": "wire",
  "create_date": "2026-05-04",
  "execute_triggers": false
}
```

Rules:

* Do not set `paid: true` unless the user explicitly says it has already been paid or the operation is intentionally recording a paid invoice.
* If `paid: true`, include `paid_on` when known.
* Use `notify` and `execute_triggers` deliberately. Defaults may send emails or execute actions.
* Use exact ISO dates: `YYYY-MM-DD`.
* Set only one document type flag among `proforma`, `simplified_invoice`, and `credit_note`.
* For credit notes, verify the parent invoice and include `parent`.
* Do not override bank account, rounding, tax exemption, reverse charge, language, or currency without a clear requirement.

### 6. Create exactly once

Call `invoices_create` only after the client and item list are resolved.

Capture `invoice_id` and `number` for later verification.

Do not create a speculative invoice and then repair it unless a safe update is explicitly intended.

### 7. Verify the stored invoice

Call:

```text
invoices_show({ id: invoice_id })
```

Verify:

* invoice ID and number,
* document type,
* client/customer identity,
* item names, prices, counts, VAT, currency,
* dates and due date,
* payment type and paid status,
* parent/credit-note relationship when relevant,
* notify/trigger expectations reported accurately.

Configuration verification does not prove email delivery, payment pairing, gateway payment, bank import, or external trigger execution.

## Decision table

| User intent | Interpretation | Action |
| --- | --- | --- |
| “Vystav fakturu klientovi X” | Regular invoice | Resolve client, build items, create invoice, verify. |
| “Pošli zálohovou fakturu” | Proforma | Set `proforma: true`; be deliberate with `notify`. |
| “Už je zaplaceno” | Paid invoice record | Set `paid: true` and `paid_on` if known. |
| “Zjednodušený doklad” | Simplified invoice | Set `simplified_invoice: true` only when legally/commercially intended. |
| “Dobropis k faktuře” | Credit note | Verify parent invoice, set `credit_note: true`, `parent`, and correction reason when known. |
| “Faktura za produkt z katalogu” | Product-backed item | Resolve item template and include `item_template_id` plus item fields. |
| “Opakovaná fakturace” | Recurring setup | Use recurring-invoice workflow, not this skill. |

## Known failure modes

### Client missing

`invoices_create` requires `client`. Search by exact email/ID first. Create a client only when enough buyer data is known and no exact client exists.

### Notification or trigger fired unintentionally

`notify` and `execute_triggers` can send emails or run actions. Set them explicitly when the user cares about side effects; otherwise report the assumed behavior.

### Wrong document type

Only one of `proforma`, `simplified_invoice`, and `credit_note` should be true. Resolve conflicting wording before creating.

### VAT or currency is guessed

Use settings, verified product data, or explicit user input. Ask if the account/defaults do not decide safely.

### Credit note lacks parent context

Always verify the parent invoice before creating a credit note. Do not invent a parent invoice ID.

## Output

Return in the user's language using only applicable sections:

```markdown
## Faktura vytvořena

**Číslo:** …
**ID faktury:** …
**Klient:** …
**Částka:** …

## Ověření

- …

## Zbývá ověřit ručně

- …
```

Separate created document details from unverified side effects such as email delivery or payment.

## Examples

### Regular invoice

**Request**

> Vystav fakturu klientovi petr@example.cz za konzultaci 2500 Kč.

**Procedure**

1. Read settings for defaults.
2. Resolve or create client by email.
3. Create one service item.
4. Call `invoices_create`.
5. Verify with `invoices_show`.

### Credit note

**Request**

> Vystav dobropis k faktuře 123 za vrácený kurz.

**Procedure**

1. Inspect invoice 123.
2. Confirm correction amount/items if not explicit.
3. Create credit note with `parent: 123`.
4. Verify parent relationship and amount.

## Resources

Load resources only when needed:

* `references/invoice-fields.md` — Read before composing `invoices_create`.
* `references/scenario-recipes.md` — Read for proformas, paid invoices, simplified invoices, credit notes, product-backed items, or side effects.
* `references/sources.md` — Read when source precedence, MCP field naming, or related workflow routing matters.

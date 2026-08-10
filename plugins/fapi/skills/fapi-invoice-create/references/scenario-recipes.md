# Invoice creation recipes

These are decision recipes, not copy-paste payloads. Resolve the client first.

## Regular invoice

```json
{
  "client": 23,
  "items": [
    {
      "name": "Konzultace",
      "price": 2500,
      "including_vat": true,
      "type": "service"
    }
  ],
  "payment_type": "wire"
}
```

Use account defaults for currency, due date, VAT, language, and bank account unless explicitly overridden.

## Proforma invoice

```json
{
  "client": 23,
  "items": [{ "name": "Kurz", "price": 1990, "including_vat": true }],
  "proforma": true,
  "payment_type": "wire"
}
```

Use when the user wants an advance invoice before payment.

## Paid invoice record

```json
{
  "client": 23,
  "items": [{ "name": "Konzultace", "price": 2500 }],
  "paid": true,
  "paid_on": "2026-06-17"
}
```

Only use when the user explicitly says the invoice has already been paid or asks to record it paid.

## Simplified invoice

```json
{
  "client": 23,
  "items": [{ "name": "Produkt", "price": 500 }],
  "simplified_invoice": true
}
```

Use only when legally and commercially appropriate. Do not infer it only because the amount is small unless the user asks.

## Credit note

```json
{
  "client": 23,
  "parent": 123,
  "credit_note": true,
  "credit_note_correction_reason": "Vrácení objednávky",
  "items": [
    {
      "name": "Vrácený kurz",
      "price": 1990,
      "including_vat": true
    }
  ]
}
```

Verify the parent invoice with `invoices_show` first. Do not invent the correction amount or reason.

## Product-backed item

```json
{
  "items": [
    {
      "name": "Online kurz",
      "price": 1990,
      "including_vat": true,
      "item_template_id": 456
    }
  ]
}
```

Resolve the item template first. Use product data to fill item name, price, VAT, type, code, and accounting fields when safe.

## Notification-safe draft-like create

When the user does not want customer communication or external actions:

```json
{
  "notify": false,
  "execute_triggers": false
}
```

Use this only when the user asks to avoid emails/triggers or when creating an internal verification invoice.

# Product creation recipes

These are decision recipes, not copy-paste payloads. Resolve account defaults and duplicates first.

## Digital course or download

Use for online courses, recordings, templates, downloads, software access, and most digital content that is not specifically an e-book/publication.

```json
{
  "name": "Online kurz",
  "prices": [{ "type": "one_time", "currency_code": "CZK", "price": 1990 }],
  "including_vat": true,
  "count": 1,
  "allow_change_count": false,
  "type": "electronic-service"
}
```

Use `electronic-publication` for a one-time e-book or electronic publication.

For digital services and e-books, omit `metadata.allow_contract_withdrawal` to preserve the MCP default `true`. Set it to `false` only on an explicit, legally grounded instruction; a digital product name does not establish consent or a legal exclusion.

## Service

Use for consulting, coaching, implementation, audits, or offline services.

```json
{
  "name": "Konzultace",
  "prices": [{ "type": "one_time", "currency_code": "CZK", "price": 2500 }],
  "including_vat": true,
  "count": 1,
  "type": "service"
}
```

## Physical product

Use for shipped goods and printed products.

```json
{
  "name": "Tričko FAPI",
  "prices": [{ "type": "one_time", "currency_code": "CZK", "price": 399 }],
  "including_vat": true,
  "count": 1,
  "allow_change_count": true,
  "type": "good",
  "enable_stock": true,
  "stock": 120,
  "show_stock_information": true
}
```

For foreign shipping, add customs metadata only when known:

```json
{
  "metadata": {
    "weight": 0.25,
    "english_name": "T-shirt",
    "country_of_origin": "CZ",
    "harmonized_system_code": "61091000"
  }
}
```

If the product type is `food`, perishability or short shelf life may be relevant to a legal exception, but set `metadata.allow_contract_withdrawal: false` only on an explicit, legally grounded instruction. Otherwise omit the field to preserve its default.

## Live event

Use for workshops, conferences, seminars, and live in-person or live online events.

```json
{
  "name": "Workshop",
  "prices": [{ "type": "one_time", "currency_code": "CZK", "price": 3500 }],
  "including_vat": true,
  "type": "live-event"
}
```

Use reservation metadata only when the event/reservation setup is known.

## Recurring product

Use product periodicity only when the product itself should be periodic.

```json
{
  "name": "Měsíční členství",
  "prices": [{ "type": "one_time", "currency_code": "CZK", "price": 790 }],
  "including_vat": true,
  "type": "electronic-service",
  "periodic": true,
  "period": "1 months"
}
```

Recurring billing still needs form configuration later.

For recurring electronic publications and similar digital access, also omit `metadata.allow_contract_withdrawal` unless an explicit, legally grounded instruction justifies an exemption.

For non-digital product types, recurring access alone is not enough to disable `metadata.allow_contract_withdrawal`.

## Repayment price

Use when the product itself needs a repayment price entry.

```json
{
  "prices": [
    {
      "type": "repayment",
      "currency_code": "CZK",
      "price": 700,
      "repayment_count": 3
    }
  ]
}
```

For ordinary sales-form installments, prefer a normal `one_time` product and configure installments on the form.

## Multi-currency product

Use one price per intended currency.

An added EUR amount normally supplements the same product's CZK price. For an update, load `item_templates_show`, merge the added price with every existing currency and price kind, and send the complete `prices` value. A partial nonempty list replaces the stored prices. Verify all prices afterward; do not change the account currency or guess a conversion.

```json
{
  "prices": [
    { "type": "one_time", "currency_code": "CZK", "price": 1990 },
    { "type": "one_time", "currency_code": "EUR", "price": 89 }
  ]
}
```

Verify that later sales forms, payment gateways, and bank accounts support each currency.

## Buddy delivery metadata

Use only when the product includes Buddy messages.

```json
{
  "metadata": {
    "buddy_metadata": {
      "messages_count": 100
    }
  }
}
```

## Affiliate commission

Use only for FAPI Rewards or an explicit affiliate setup.

```json
{
  "metadata": {
    "affiliate_commission": 20,
    "affiliate_commission_type": "percentage",
    "affiliate_including_discount": true
  }
}
```

For `affiliate_commission_type: "constant"`, the value is a fixed amount in the account default currency.

## Pohoda accounting

Use only when the account or user request contains Pohoda codes.

```json
{
  "pohoda_accounting": "604000",
  "pohoda_centre": "ONLINE",
  "pohoda_store": "SKLAD",
  "pohoda_stock_item": "SKU-123"
}
```

Do not invent accounting codes.

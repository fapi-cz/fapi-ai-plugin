# FAPI product field guide

Use this reference before `item_templates_create` or `item_templates_update`.

## Required fields for create

```json
{
  "name": "Online kurz",
  "prices": [
    {
      "type": "one_time",
      "currency_code": "CZK",
      "price": 1990
    },
    {
      "type": "special_one_time",
      "currency_code": "CZK",
      "price": 997
    }
  ]
}
```

Rules:

* `name` is required.
* `prices` must contain at least one entry.
* Each price needs `type`, `currency_code`, and `price`.
* Use uppercase ISO 4217 currency codes.
* `type` is `one_time`, `special_one_time`, or `repayment`.
* `repayment_count` is required by intent when `type` is `repayment`.

## Common fields

| Field | Meaning | Rule |
| --- | --- | --- |
| `code` | Product code/SKU | Use when supplied or needed to avoid ambiguity. |
| `description` | Invoice-facing short description | Do not invent legal or fulfillment promises. |
| `public_description` | Order-form-facing description | Use safe HTML only when provided or straightforward. |
| `vat` | VAT rate percentage | Use account defaults or explicit user value. |
| `including_vat` | Whether price includes VAT | Default to true for public consumer prices. |
| `count` | Default quantity | Usually `1`. |
| `allow_change_count` | Buyer can change quantity | Usually true for physical goods, false/omitted for fixed digital offers. |
| `type` | Product type | Choose deliberately from MCP enum. |
| `disable_discount` | Discount codes do not apply | Use only when requested. |
| `metadata.allow_contract_withdrawal` | Whether the customer has the right to withdraw from the contract for the product | Keep true unless a legal exception clearly applies. |

## Product types

* `good`
* `food`
* `service`
* `electronic-publication`
* `electronic-period-publication`
* `electronic-service`
* `live-event`
* `excluding_vat`
* `printed-publication`
* `printed-period-publication`

## Stock

```json
{
  "enable_stock": true,
  "stock": 50,
  "show_stock_information": true
}
```

Rules:

* `stock` is required when `enable_stock` is true.
* Use stock primarily for physical goods and printed publications.
* A stock-enabled item cannot be used in periodic invoicing.

## Recurring product fields

```json
{
  "periodic": true,
  "period": "1 months"
}
```

Rules:

* `period` is required when `periodic` is true.
* Use DateTime-modify-like period text, for example `1 days`, `1 weeks`, `1 months`, or `1 years`.
* Product periodicity is not the same as enabling recurring billing on a sales form.

## Metadata

`metadata` is an object. On update, sending it replaces the whole stored object.

Common typed metadata:

```json
{
  "metadata": {
    "weight": 0.25,
    "english_name": "Printed book",
    "country_of_origin": "CZ",
    "harmonized_system_code": "49019900",
    "affiliate_commission": 20,
    "affiliate_commission_type": "percentage",
    "affiliate_including_discount": true,
    "subscription": {
      "name": "Premium membership",
      "code": "premium"
    },
    "subscription_level": {
      "name": "Gold",
      "code": "gold"
    },
    "buddy_metadata": {
      "messages_count": 100
    },
    "custom_params": {
      "external_id": "course-2026-01"
    }
  }
}
```

Use metadata only when the user requirement or existing account pattern justifies it.

## Contract withdrawal

`metadata.allow_contract_withdrawal` controls whether the product should participate in the contract-withdrawal flow.

Preserve the current MCP default `true` by leaving the field absent on create, including digital products. Set `false` only on an explicit, legally grounded instruction establishing an applicable exclusion and its conditions. Do not infer consent, early performance or required notice from an e-book/course name. If the legal basis is unclear, omit the field or ask only when the user requests an exemption. On update, preserve the stored value or its absence when replacing metadata; do not silently reset it.

* Common exceptions come from § 1837 of the Czech Civil Code, for example fully performed services with prior explicit consent and notice, started digital-content delivery with prior explicit consent and notice, custom-made goods, perishable goods, opened sealed hygiene goods, newspapers or periodicals outside subscriptions, and leisure or accommodation tied to a specific date.

## Update replacement semantics

Before `item_templates_update`, inspect with `item_templates_show`.

Fields with replacement behavior:

* `prices` — send the full list of prices to keep.
* `metadata` — send the full metadata object to keep.
* `triggers` — send the full trigger list to keep.

Omit these fields when they should remain unchanged.

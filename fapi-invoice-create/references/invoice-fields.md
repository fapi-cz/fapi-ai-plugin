# Invoice create fields

Use this before `invoices_create`.

## Required fields

```json
{
  "client": 23,
  "items": [
    {
      "name": "Product",
      "price": 990
    }
  ]
}
```

Rules:

* `client` is a FAPI client ID.
* `items` must contain at least one item.
* Each item needs `name` and `price`.
* MCP input uses snake_case field names.

## Customer snapshot

```json
{
  "customer": {
    "name": "Test Company s.r.o.",
    "email": "customer@example.test",
    "ic": "12345678",
    "dic": "CZ12345678",
    "address": {
      "street": "Main 1",
      "city": "Prague",
      "zip": "11000",
      "country": "CZ"
    },
    "shipping_address": {
      "street": "Delivery 2",
      "city": "Brno",
      "zip": "60200",
      "country": "CZ"
    }
  }
}
```

`customer` is invoice-specific snapshot data. It does not replace the required `client` ID.

## Item fields

```json
{
  "name": "Konzultace",
  "price": 2500,
  "type": "service",
  "vat": 21,
  "including_vat": true,
  "count": 1,
  "code": "CONSULT",
  "description": "Strategická konzultace",
  "item_template_id": 456
}
```

Allowed item types:

* `good`
* `food`
* `service`
* `live-event`
* `discount`
* `electronic-service`
* `electronic-publication`
* `electronic-period-publication`
* `printed-publication`
* `printed-period-publication`

Use `item_template_id` only after resolving an item template.

## Dates and payment

Dates are ISO `YYYY-MM-DD`:

* `create_date`
* `payday_date`
* `vat_date`
* `automatic_charge_date`
* `paid_on`

Payment type examples:

* `wire`
* `credit card`
* `gopay`
* `cash`
* `collect on delivery`
* `paypal`
* `gpay`
* `wire gopay`

Only set `paid: true` when the user explicitly wants to record the invoice as paid.

## Document type flags

Only one of these should be true:

* `proforma`
* `simplified_invoice`
* `credit_note`

Other related flags:

* `create_payment_confirmation`
* `create_simplified_invoice`
* `parent`
* `credit_note_correction_reason`

For credit notes, verify the parent invoice first.

## Side effects

* `notify` may send notification emails.
* `execute_triggers` may execute form triggers/actions.

Set them intentionally when the user cares about side effects. Report assumptions.

## Optional overrides

Do not override without a clear requirement:

* `currency`
* `language`
* `bank_account_name`
* `bank_account`
* `swift`
* `iban`
* `round_function`
* `round_precision`
* `tax_exempt`
* `reverse_charge`
* `form`
* `shipping_method_id`
* `shipping_metadata`

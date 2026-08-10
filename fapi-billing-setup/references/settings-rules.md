# Billing setting rules

Use this before `settings_update` or `settings_create`.

## Prefer update for standard keys

Standard billing keys usually already exist. Use `settings_update`; use `settings_create` only for genuine custom keys.

## Common billing keys

| Key | Value type | Rule |
| --- | --- | --- |
| `currency` | string | Uppercase ISO 4217 code. Guarded because it can affect existing invoices/exchange rates. |
| `vat_mode` | string | One of `vat-payer`, `non-vat-payer`, `identified-person`. Tax-sensitive. |
| `vat` | number | Default VAT rate. Tax-sensitive. |
| `payday` | string | Duration such as `14 days` or `2 weeks`. |
| `payment_type` | string | Default payment type. Use only with explicit desired value. |
| `language` | string | Account language/default customer-facing language. |
| `proforma` | boolean | Advance invoice behavior. |
| `payment_confirmation` | boolean | Payment confirmation behavior. |
| `send_invoice_email_to_client` | boolean | Customer invoice email behavior. |
| `send_invoice_email_to_user` | boolean | Seller invoice email behavior. |
| `print_qr_code_on_invoice` | boolean | QR code display on invoices. Requires bank-account readiness for usefulness. |
| `hide_vat_breakdown_on_final_invoice` | boolean | Invoice VAT breakdown display. |
| `period_periodic` | string | Recurring invoice period such as `1 months`. |
| `vat_recapitulation_algorithm` | string | `default` or `pohoda`. |

## Boolean keys

Send actual JSON booleans:

```json
{ "key": "proforma", "value": true }
```

Do not send string `"1"` or `"0"`.

## Guardrails

* Do not change tax settings from vague wording.
* Do not change currency silently.
* Do not change invoice email behavior without an explicit request.
* Verify every changed setting with `settings_show` or a fresh `settings_list`.

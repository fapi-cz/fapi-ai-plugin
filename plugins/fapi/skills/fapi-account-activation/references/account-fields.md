# Account activation fields

Use this reference before write to billing information, settings, bank accounts, or payment readiness.

## Billing information

Tool: `users_update_billing_information`

```json
{
  "name": "FAPI s.r.o.",
  "emails": "billing@example.cz;office@example.cz",
  "ic": "12345678",
  "dic": "CZ12345678",
  "address": {
    "street": "Hlavni 123",
    "city": "Praha",
    "zip": "12000",
    "country_code": "CZ"
  }
}
```

Rules:

* `name` is required.
* Preserve loaded `emails`; include supplied addresses using semicolon separation. A profile email is needed for basic checklist completion, not a prerequisite for every independent settings write.
* `address.street`, `address.city`, `address.zip`, and `address.country_code` are required.
* Prefer `country_code`.
* Do not invent `ic`, `dic`, `ic_dph`, `uk_vat_id`, `phone`, `web`, or `file_reference`.
* Read and merge the complete current identity/address before updating; omitted fields may be cleared. Save country changes before explicit VAT settings.

## Guarded settings

Tool: `settings_update`

Common keys:

| Key | Meaning | Risk                                                                                                                                                      |
| --- | --- |-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `currency` | Default account currency | Can affect existing invoices and exchange rates. Base currency for account.                                                                               |
| `vat_mode` | VAT mode | Tax-sensitive. Vat mode, vat-payer, identified-person, non-vat-payer                                                                                      |
| `vat` | Default VAT rate | Tax-sensitive. Base vat rate.                                                                                                                             |
| `payday` | Invoice due date | Affects payment expectations. Use like "7 days", "14 days". 7 - 14 days are prefered.                                                                     |
| `payment_type` | Default payment type | Can affect invoice defaults. This is only base payment type. Does not efect almost anythink.                                                              |
| `language` | Account language | Affects generated customer-facing output. Default laguange of the invoices or sales form.                                                                 |
| `proforma` | Advance invoice behavior | Affects invoice flow. Proforma invoice is created and after payment the main invoice is created. This is most common usecase so this should prefered true |
| `payment_confirmation` | Payment confirmation behavior | Affects customer communication. In 95% sould be false.                                                                                                    |

Update only when the user supplied an explicit desired value or the activation would otherwise be blocked and the value is unambiguous.

## Bank account sets

Create:

```json
{
  "name": "Výchozí sada bankovních účtů",
  "bank_accounts": [
    {
      "currency_code": "CZK",
      "bank_account": "123456789/0800",
      "bank_account_name": "Jan Novak",
      "iban": "CZ6508000000192000145399",
      "swift": "GIBACZPX"
    }
  ]
}
```

Rules:

* Prefer `currency_code`.
* `bank_account_name` maximum is 35 characters for QR payments.
* Use the user's existing `default_bank_account_set`; creating a different set does not assign it as default.
* Nonempty `bank_accounts` upserts supplied entries by ID or set/currency. Omitted entries remain, but omitted fields on a supplied entry may be cleared. Merge loaded account details and preserve IDs.
* Do not create fake IBAN/SWIFT values.

## Payment gateways

Tools:

* `payment_gateways_list`
* `payment_gateways_show`

Rules:

* Gateway tools are read-only.
* Use `only_connected: true` to find usable connected gateways.
* Use `production_mode_enabled: true` for live launch readiness.
* Inspect selected gateway before enabling card/wallet methods on a form.
* If no connected gateway exists, report manual setup as a blocker.

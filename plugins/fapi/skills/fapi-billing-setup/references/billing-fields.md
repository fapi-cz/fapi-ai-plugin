# Billing setup fields

Use this before writing seller billing information or bank account sets.

## Seller billing information

Tool: `users_update_billing_information`

```json
{
  "name": "FAPI s.r.o.",
  "emails": "billing@example.cz;office@example.cz",
  "ic": "12345678",
  "dic": "CZ12345678",
  "ic_dph": null,
  "uk_vat_id": null,
  "phone": "+420123456789",
  "web": "https://example.cz",
  "address": {
    "street": "Hlavni 123",
    "city": "Praha",
    "zip": "12000",
    "country_code": "CZ"
  }
}
```

Required:

* `name`
* `address.street`
* `address.city`
* `address.zip`
* `address.country_code`

Read `users_show` and merge the complete current billing/address data with supplied changes, including existing emails. Omitted identity fields may be cleared; do not send a partial name/VAT-ID update. Preserve omitted emails as well. Missing profile email is a checklist gap; it does not block an independent `settings_update`.

Do not invent registration or VAT identifiers.

If country and VAT mode change together, save billing first and the explicitly stated mode second, because country changes can reset defaults. Preserve that stated mode after later country updates.

## Bank account set

Tool: `bank_account_sets_create` / `bank_account_sets_update`

```json
{
  "name": "Výchozí bankovní účty",
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

* Use `currency_code` when possible.
* Each bank account needs `currency_code` or `currency_id`.
* Each bank account needs `bank_account` or `iban`.
* Preserve known IBAN/SWIFT; an IBAN alone is not a reason to require a missing SWIFT.
* `bank_account_name` maximum is 35 characters.
* In onboarding, update the set from `users_show.default_bank_account_set`. Creating another set does not assign it as default.
* Nonempty `bank_accounts` upserts supplied entries by ID or set/currency. Omitted entries remain. A supplied entry's omitted name, local account number, IBAN, or SWIFT can be cleared, so merge the complete loaded entry and keep its `id`.

## Verification

After a billing-information update, verify with returned user data or `users_show`.

After bank-account create/update, verify with `bank_account_sets_show`.

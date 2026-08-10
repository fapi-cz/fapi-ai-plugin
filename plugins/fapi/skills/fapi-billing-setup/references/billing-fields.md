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

`emails` is documented as required in `mcp/TOOLS.md`; include it when available and ask when absent for a billing-information write.

Do not invent registration or VAT identifiers.

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
* `iban` requires `swift`, and `swift` requires `iban`.
* `bank_account_name` maximum is 35 characters.
* Update replaces the complete `bank_accounts` list.
* When updating, keep `id` on existing accounts that should remain.

## Verification

After a billing-information update, verify with returned user data or `users_show`.

After bank-account create/update, verify with `bank_account_sets_show`.

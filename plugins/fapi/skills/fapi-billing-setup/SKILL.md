---
name: fapi-billing-setup
description: >-
  Use this skill when the user wants Fapilot to set up, audit, or update FAPI
  billing and invoicing basics: seller billing information, fakturační údaje,
  VAT mode, VAT rate, currency, invoice due date, proforma/payment-confirmation
  behavior, invoice email defaults, QR invoice setting, or bank account sets.
  Trigger for “nastav fakturaci”, “doplnit fakturační údaje”, “nastavit DPH”,
  “změnit měnu”, “splatnost faktur”, “bankovní účet”, or “QR platby”. Do not
  use for creating products, sales forms, invoices, payment gateway connections,
  or full first-sale activation.
---

# Set up FAPI billing

## Purpose

Configure the account-level billing foundation that invoices and sales forms depend on, while avoiding unsafe changes to tax, currency, and bank-account state.

Billing setup is narrower than account activation. It does not create products or forms; it prepares seller identity, invoice defaults, and bank-account readiness.

## Scope

Use this skill for:

* Auditing current billing and invoicing readiness.
* Updating seller billing information.
* Reading and selectively updating account settings for VAT, currency, due date, proforma, payment confirmation, invoice emails, QR display, and similar invoice defaults.
* Creating or updating bank account sets for bank transfer and QR payment readiness.
* Reporting manual gaps for payment gateway setup without claiming to connect gateways.

Do not use this skill for:

* Creating a product; use `fapi-product-create`.
* Creating a sales form; use `fapi-sales-form-create`.
* Full first-sale orchestration; use `fapi-account-activation`.
* Creating or editing invoices; use an invoice-specific workflow.
* Connecting payment gateways; MCP can inspect gateways but not connect them.
* Guessing legal, tax, registration, or banking data.

## Domain model

### Seller billing information

Seller billing information appears on invoices. `users_update_billing_information` writes the authenticated user's billing identity.

Required:

```text
name
address.street
address.city
address.zip
address.country_code
```

Preserve known `emails` and all other loaded billing fields when updating. A missing profile email is a basic-checklist gap, not a reason to block an independent VAT-mode write.

### Account settings

Account settings are key/value defaults. The most relevant billing keys are:

```text
currency
vat_mode
vat
payday
payment_type
language
proforma
send_invoice_email_to_user
print_qr_code_on_invoice
hide_vat_breakdown_on_final_invoice
period_periodic
vat_recapitulation_algorithm
```

Some settings affect existing invoices or tax behavior. Treat them as guarded writes.

### Bank account set

A bank account set groups bank accounts by currency. It can be used as an account default or assigned to projects/forms indirectly by existing FAPI configuration.

On update, nonempty `bank_accounts` upserts supplied entries by ID or set/currency. Omitted entries remain, but omitted details on a supplied entry may be cleared. Read and merge each existing entry, preserving its ID and fields.

## Procedure

### 1. Classify the billing task

Determine whether the user wants:

* Audit only.
* Seller billing-information update.
* Settings update.
* Bank account set creation/update.
* Payment-readiness check.
* A combination of the above.

Extract known values:

* Billing name, email(s), address, country code, company registration IDs, VAT IDs, phone, web.
* VAT mode, VAT rate, currency, due date, language, proforma/payment-confirmation choices.
* Bank account number, account holder/display name, currency, IBAN, SWIFT.
* Whether the change is for a new account or an already active account.

Ask one combined question only when a write cannot be done safely because required data is missing or ambiguous.

During guided onboarding, explicitly supplied billing, VAT, and bank details are instructions to save them now, without another general confirmation. Complete independent writes while asking only for missing or contradictory data. Audit-only requests remain read-only; unrelated live changes and deletion keep their normal safeguards.

### 2. Inspect current state first

Use read-only tools before any write:

1. `settings_list` for current billing defaults and `account_summary`.
2. `users_show` for current user and billing information when needed.
3. `bank_account_sets_list` for current bank accounts.
4. `bank_account_sets_show` before updating a specific set.
5. `payment_gateways_list` only when the user asks whether online payments are ready.

Read `references/billing-fields.md` before composing write payloads.

### 3. Update seller billing information

Use `users_update_billing_information` only when required fields are known.

Example:

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

* Prefer `country_code`.
* Do not invent `ic`, `dic`, `ic_dph`, `uk_vat_id`, phone, web, or file reference.
* Preserve existing values unless the user clearly replaces them.
* Read `users_show` and merge the complete identity/address payload. Do not send only the new name or VAT ID: omitted fields may be cleared.
* Save a country change before the explicit VAT mode, because country changes can reset tax defaults. Restore an already stated mode after a later address/country update too.
* Verify through the returned user or `users_show`.

### 4. Update settings carefully

Use `settings_update` for existing standard keys. Use `settings_create` only for genuinely new custom keys; standard setup keys normally already exist.

Guarded setting rules:

* `currency`: update only with explicit instruction; it can affect existing invoices and exchange rates.
* `vat_mode` and `vat`: tax-sensitive; do not infer from product names or vague user wording.
* In onboarding, “jsme plátci DPH” directly sets `vat_mode: vat-payer`, “jsem identifikovaná osoba” sets `identified-person`, and explicit non-payer status sets `non-vat-payer`. Specific identified-person wording wins over generic non-payer wording. Save the mode before dependent products; do not wait for a missing VAT ID or bank account when the mode write is independently valid.
* A stated VAT mode does not supply a VAT ID or rate. Preserve the current recap method unless the user gives another one.
* `payday` and `period_periodic`: use duration strings such as `14 days` or `1 months`.
* Boolean keys must be actual booleans, not `"1"` or `"0"`.
* `vat_recapitulation_algorithm` must be `default` or `pohoda`.
* Update only requested settings, then verify each changed key with `settings_show` or `settings_list`.

Read `references/settings-rules.md` when changing settings.

### 5. Create or update bank account sets

For create:

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

* Prefer `currency_code`.
* Provide either `bank_account` or `iban`.
* Preserve a known IBAN/SWIFT; do not require or invent SWIFT merely because an IBAN was supplied.
* `bank_account_name` has a 35-character limit.
* For onboarding, read `users_show.default_bank_account_set`, inspect it, and update that existing set. A new set does not become default merely by being created. If tools cannot assign a missing default, give Nastavení → Způsoby platby as the manual step; reserve new sets for an explicitly requested project/configuration.
* Save a supplied CZK account immediately for CZK. An EUR product price is not a reason to reject or defer it or to speculate that EUR/SEPA payments cannot arrive.
* Offer an additional EUR account afterward if useful; save both when supplied without replacing one with the other or duplicating an existing account.
* For each updated account, merge all loaded details and preserve its ID. Other entries are not deleted by omission; deletion is a separate explicit operation.
* Verify with `bank_account_sets_show`.

### 6. Check payment readiness without overclaiming

For bank transfer/QR readiness:

* Confirm bank-account set coverage for intended currencies.
* Confirm `print_qr_code_on_invoice` only if QR invoice display matters.

For online payment readiness:

* Call `payment_gateways_list({ only_connected: true })`.
* For production launch, check `production_mode_enabled: true`.
* Use `payment_gateways_show` for selected gateway details.
* Report missing gateway setup as a manual blocker; do not claim the gateway was connected.

### 7. Verify and report

After writes, verify:

* Billing identity fields.
* Updated settings and value types.
* Bank account set contents.
* Any payment-readiness checks requested.

Do not claim invoice delivery, payment pairing, QR scanning, bank import, or online payment success without an actual transaction test.

## Decision table

| User intent | Interpretation | Action |
| --- | --- | --- |
| “Nastav fakturační údaje” | Seller billing identity | Read current user, update required billing fields, verify. |
| “Jsem neplátce DPH” | VAT mode | Update `vat_mode: non-vat-payer`, usually `vat: 0` if explicitly part of setup. |
| “Jsme plátci DPH, 21 %” | VAT payer defaults | Update `vat_mode: vat-payer` and `vat: 21` if explicit. |
| “Změň měnu na EUR” | Guarded currency change | Confirm explicit instruction and warn about existing invoices before update. |
| “Splatnost 14 dní” | Due-date default | Update `payday: "14 days"`. |
| “Zapni QR na fakturách” | QR invoice display | Update `print_qr_code_on_invoice: true`; verify bank account currency coverage. |
| “Přidej bankovní účet” | Bank account set setup | Create or update set while preserving existing accounts. |
| “Nastav kartu” | Payment gateway readiness | Inspect gateways; report manual setup if not connected. |
| “Rozjeď první prodej” | Broader activation | Use `fapi-account-activation`. |

## Known failure modes

### Currency changed too broadly

Changing `currency` can affect existing invoices and exchange rates. Do not update it unless the user explicitly requested the change and understands the impact.

### VAT settings are guessed

Tax mode and VAT rate require explicit user data or existing account defaults. Ask instead of guessing.

### Bank account update clears existing details

Cause: a supplied existing bank-account entry omitted loaded fields such as IBAN, SWIFT, or display name.

Resolution:

1. Inspect the set with `bank_account_sets_show`.
2. Merge the new/changed account with its complete loaded record.
3. Preserve `id` for unchanged existing accounts.
4. Update the intended entries and verify the set, including unchanged accounts.

### QR payments are configured incompletely

Check:

* bank account exists for invoice currency,
* `bank_account_name` length is at most 35 characters,
* `print_qr_code_on_invoice` is true when invoice QR display is required.

### Payment gateway readiness is overstated

Payment gateway tools are read-only. A connected gateway can be inspected, but setup and end-to-end payment must be handled manually or by another integration.

## Output

Return in the user's language using only applicable sections:

```markdown
## Fakturace nastavena

**Fakturační údaje:** …
**DPH a měna:** …
**Bankovní účty:** …

## Ověření

- …

## Zbývá

- …
```

Separate completed settings from manual checks and external setup.

## Examples

### Billing identity and VAT setup

**Request**

> Nastav fakturační údaje na FAPI s.r.o., Praha, jsme plátci DPH 21 %.

**Procedure**

1. Inspect current settings and user.
2. Save the explicit VAT mode immediately if address data is not ready; ask only for missing billing fields.
3. Merge and update billing information when required fields are known.
4. Save the explicit mode after a country update as well, and change `vat` only when supplied or already known.
5. Verify.

### Bank account setup

**Request**

> Přidej CZK účet 123456789/0800 pro QR platby.

**Procedure**

1. Inspect bank account sets.
2. In onboarding, update the existing default set; do not create an unused set just to add an account.
3. Preserve existing accounts on update.
4. Verify the set and QR-related setting if requested.

## Resources

Load resources only when needed:

* `references/billing-fields.md` — Read before billing-information or bank-account writes.
* `references/settings-rules.md` — Read before account setting updates.
* `references/sources.md` — Read when source precedence, MCP tool boundaries, or related workflow routing matters.

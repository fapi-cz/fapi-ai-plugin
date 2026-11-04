# Account activation readiness checklist

Use this checklist for activation audits and final status reports.

## Fapilot onboarding checklist and red basic settings

In Fapilot's variant D, show only `checklist_basic_settings`, `checklist_product`, `checklist_form`, and `checklist_form_tested`; count completed flags out of four. Values `1`/`"1"` mean checked, `0`/`"0"` unchecked, and an absent flag is unverified. Gateways and bank import are not extra checklist items. Do not rewrite checklist flags; they may lag behind verified data.

`checklist_basic_settings` is a stored flag, not the reason for a red state. Read `users_show`, `settings_list`, and the user's default bank account set. Its conditions are nonempty `ic` and `name`, at least one profile email, an existing address, a bank account in `default_bank_account_set`, and `vat_mode`. VAT payers and identified persons also need `dic` and `vat_recapitulation_algorithm` (`default` or `pohoda`, not a boolean).

Explain only a missing condition proved by returned data. Logo, signature, sender name, and gateway connection are not conditions of this flag. Use Nastavení → Fakturační údaje for identity/contact/address, Nastavení → Způsoby platby for accounts, and Nastavení → Nastavení fakturace for VAT. Do not invent an E-maily / Odesílatel tab. If data is unavailable or complete despite a red flag, state that exact uncertainty instead of guessing a cause.

Keep the basic flag distinct from overall sale readiness below. Configuration inspection does not prove test payment or delivery.

## Billing identity

Ready when:

* seller billing name is present,
* billing email is present,
* street, city, ZIP, and country code are present,
* country code is an ISO 3166-1 alpha-2 value.

Use `users_update_billing_information` only when missing values are supplied by the user.

## Account defaults

Inspect with `settings_list`.

Check:

* `vat_mode`: `non-vat-payer`, `vat-payer`, or `identified-person`.
* `vat`: default VAT rate, especially for VAT payers.
* `currency`: default account currency.
* `payday`: invoice due date.
* `language`: account/form language baseline.
* `proforma`: whether advance invoices are used.
* `payment_confirmation`: whether payment confirmations are enabled. Usually, this is should be false.
* invoice email behavior, if first-sale communication matters.

Do not change guarded defaults during a readiness audit.

## Bank transfer / QR readiness

Inspect with `bank_account_sets_list`.

Inspect the default or explicitly selected set, not an arbitrary unused set. Save supplied accounts before discussing remaining currency coverage; an EUR price does not block saving CZK details or prove a bank will reject EUR/SEPA payments.

For QR readiness:

* `bank_account_name` should be present when used.
* `bank_account_name` must fit the documented 35-character limit.
* IBAN/SWIFT are useful for international payments but do not invent them.

## Online payment readiness

Inspect with:

```text
payment_gateways_list({ only_connected: true })
```

For production launch, require production-ready gateway data:

```text
payment_gateways_list({ only_connected: true, production_mode_enabled: true })
```

If none exists, the activation can still proceed with bank transfer/QR when acceptable, but card/wallet launch is blocked.

## Product readiness

Ready when a product exists with:

* `item_template_id`,
* name,
* usable price in intended currency,
* VAT/inclusion behavior consistent with account defaults,
* appropriate product type,
* stock/quantity behavior when physical.

Use `fapi-product-create` for creation or completion.

## Sales-form readiness

Ready when a form exists with:

* `form_id`,
* intended main product in `items` or an intended item group,
* viable payment method,
* account defaults preserved unless explicitly overridden,
* relevant buyer fields for the product type,
* verified state from `forms_show`.

Use `fapi-sales-form-create` for creation.

## Launch readiness

Ready when the user has:

* form URL or embed path,
* test-order plan,
* manual verification plan for payment, invoice, email, thank-you page, and fulfillment,
* clear distinction between test mode and real sale.

Configuration verification does not prove a real transaction path.

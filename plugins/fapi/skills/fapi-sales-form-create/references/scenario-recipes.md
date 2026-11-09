# Sales-form creation recipes

These are decision recipes, not copy-paste payloads. Resolve all IDs first and omit options the user did not request.

For every recipe, retain the MCP defaults of `max_width: 650`, `currency_setting: by-country`, and `reverse_charge: foreign-customers-with-valid-dic` unless the user explicitly requests another supported value. Include `settings.redirect_to_order_status_page_if_error: true` in the complete form settings. Never use `error_custom_content` or send `error_content`.

## 1. Minimal one-time digital sale

### Use when

The user sells an e-book, recording, template, consultation, course, or other one-time non-physical offer.

### Resolve

* Existing product by exact name/code; create it only when name, price, and currency are known.
* Fixed versus country-based currency from the request.
* Any explicitly requested payment gateway.

### Form shape

```json
{
  "name": "Objednávka – Název produktu",
  "settings": { "redirect_to_order_status_page_if_error": true },
  "items": [{ "item_template_id": 123, "required": true }]
}
```

Preserve account messages, reminders, terms, GDPR, project, and series. Do not require address or phone without a reason.

If fulfillment is requested and a valid message/file/member-section dependency is available, trigger it on `paid` or `item-paid`, not merely `ordered`.

### Bounded Czech preparation prompt

> Na mém testovacím účtu [název a ID účtu] připrav produkt „E-book – Základy fotografování“ za konečných 490 CZK včetně případné DPH a formulář „Objednávka – E-book Základy fotografování“. Nejdřív ověř identitu účtu přes MCP a také v UI; při neshodě nebo nedostupném přihlášení nic nezapisuj. DPH převezmi z ověřeného nastavení účtu, typ produktu je elektronická publikace, cena jednorázová a množství pevně 1. Nejdřív zkontroluj duplicity. Chci pouze bankovní převod v CZK, bez platební brány, splátek a předplatného. Ostatní nastavení, e-maily a právní texty ponech výchozí; právo na odstoupení nevypínej. Soubor ani způsob doručení zatím nemám připravený: doručování nenastavuj, jen vypiš, co musím dodat. Nevytvářej faktury ani objednávky, neodesílej formulář ani zprávy a nic neplať. Vrať ID produktu a formuláře, ověř uložená data a odděleně napiš, co bylo zkontrolováno v UI a které transakční a negativní testy nebyly provedeny.

Replace the bracketed account identity before use; this is an example, not a tested write prompt. Resolve existing records first. For this explicit bank-transfer-only request, verify the CZK bank account, use `allow_wire: true`, `allow_gopay: false`, and `allow_qr_code_payment: false`; omit unrelated optional fields. A missing required bank dependency is a blocker to payment readiness, not permission to invent details or change account settings. If card payment is requested instead, resolve a compatible connected gateway; provider signup/approval and missing connections remain merchant/provider steps.

Creating the catalog entry and form does not upload or deliver the e-book. Obtain the actual file, agreed hosting/access method and delivery message/integration before configuring delivery on `paid` or `item-paid`. Do not invent a download URL, file ID or template/connection ID. Without those dependencies, return a prepared configuration with delivery explicitly pending. Stored readback and non-submitting UI inspection do not prove successful payment, failed/unpaid-payment handling, or delivery; those need a separately authorized test plan.

## 2. Physical product

### Resolve

* Product type, price, VAT, stock, weight, and quantity behavior.
* Whether the buyer needs a separate shipping address.
* Verified shipping-method IDs, if available.
* Requested carrier integration and phone requirement.
* COD only when operationally supported.

### Form shape

```json
{
  "name": "Objednávka – Fyzický produkt",
  "items": [{ "item_template_id": 123, "required": true }],
  "allow_shipping_address": true,
  "field_settings": {
    "name": { "name": "name", "show": true, "required": true },
    "address": { "name": "address", "show": true, "required": true },
    "country": { "name": "country", "show": true, "required": true },
    "email": { "name": "email", "show": true, "required": true },
    "phone": { "name": "phone", "show": true, "required": true }
  },
  "allow_simplified": false
}
```

Add `allow_shipping_methods` and `shipping_methods` only with verified IDs. Creating a physical checkout without known shipping methods may be acceptable when shipping is free or handled outside FAPI; report that explicitly.

## 3. Fixed installments

### Use when

The buyer purchases one offer but may divide the price into a fixed number of installments.

### Form shape

```json
{
  "items": [{ "item_template_id": 123, "required": true }],
  "allow_repayments": true,
  "repayment_counts": [3, 6]
}
```

Do not also enable recurring billing unless the user's business model genuinely requires both. The account's invoice settings determine the installment period.

## 4. Indefinite subscription

### Resolve

* Recurring product with a period, for example `1 months`.
* No stock tracking.
* Recurring message/reminder behavior, inherited by default.
* Gateway capability if automatic card charges are requested.

### Form shape without automatic charging

```json
{
  "items": [{ "item_template_id": 123, "required": true }],
  "allow_recurring": true,
  "period": "1 months",
  "end_by": "none"
}
```

### Add for automatic card charging

```json
{
  "allow_gopay": true,
  "gopay_connection": 50,
  "allow_gopay_card": true,
  "allow_gopay_recurring_payments": true,
  "require_recurring_terms": true
}
```

Do not send `recurring_terms_url` when the account default should apply. The first payment must be made by card after automatic charging is enabled so FAPI can obtain the required payment token.

## 5. Finite recurring program

### Fixed number of billing cycles

```json
{
  "allow_recurring": true,
  "period": "1 months",
  "end_by": "iteration",
  "iteration": 12
}
```

### End on a date

```json
{
  "allow_recurring": true,
  "period": "1 months",
  "end_by": "date",
  "last_date": "2027-06-30"
}
```

Use exact ISO dates. Do not use a past date.

## 6. Trial that changes into the regular product

Resolve separate trial and regular item templates.

```json
{
  "items": [{ "item_template_id": 400, "required": true }],
  "allow_recurring": true,
  "period": "1 months",
  "end_by": "none",
  "allow_changeable_items": true,
  "changeable_items": [
    {
      "base_item_template_id": 400,
      "target_item_template_id": 401
    }
  ]
}
```

Use `trial_period` only when the desired behavior matches its semantics. Do not substitute an improvised zero-price item without explicit approval.

## 7. Order bump

### Use when

A complementary product should be selected before checkout submission.

```json
{
  "allow_order_bumps": true,
  "order_bumps": [
    {
      "item_template_id": 200,
      "name": "Ano, přidat pracovní sešit za {price}",
      "description": "<p>Procvičte si každý modul na konkrétních úkolech. Cena: <strong>{price}</strong>.</p>"
    }
  ]
}
```

For recurring forms, decide whether the bump should recur. If it should be one-time only, changeable-item or other follow-up logic may be necessary.

## 8. Post-order upsell

### Use when

The next offer should appear only after the original order is submitted.

```json
{
  "upsell_pages": [
    {
      "upsell_url": "https://example.cz/nabidka-po-objednavce",
      "upsells": [{ "item_template_id": 300 }]
    }
  ]
}
```

The URL is indispensable and must not be invented. Physical products are often safer as order bumps because shipping data and cost are already part of the checkout.

## 9. Multiple product variants

### One variant only

```json
{
  "settings": {
    "disable_autofill_product": true,
    "redirect_to_order_status_page_if_error": true
  },
  "item_groups": [
    {
      "title": "Vyberte variantu",
      "required": true,
      "allow_multiple_items": false,
      "items": [
        { "item_template_id": 101 },
        { "item_template_id": 102 },
        { "item_template_id": 103 }
      ]
    }
  ]
}
```

### Multiple selectable add-ons

Use `allow_multiple_items: true`. Keep the group optional unless at least one add-on is mandatory.

## 10. Multiple currencies

### Fixed currency

Use only when the user explicitly requests a fixed currency:

```json
{
  "currency_setting": "always",
  "currency_code": "EUR"
}
```

### Buyer choice

```json
{
  "currency_setting": "choice",
  "allowed_currencies": ["CZK", "EUR"]
}
```

Before creation, check that products, payment gateway, and bank accounts are compatible with every offered currency. Explicit product prices are preferable to unexpected conversion.

## 11. Two-step checkout

### Inline second step

```json
{
  "template_settings": {
    "container_settings": {
      "is_two_step_form": true,
      "two_step_form_type": "inline"
    }
  }
}
```

### Redirected second step

```json
{
  "template_settings": {
    "container_settings": {
      "is_two_step_form": true,
      "two_step_form_type": "redirect",
      "two_step_redirect_url": "https://example.cz/dokonceni-objednavky"
    }
  }
}
```

A two-step form is justified when collecting a lead/order intent before checkout or when the purchase flow genuinely benefits from separation. Do not add it to a simple checkout by default.

## 12. Discount-code checkout

Resolve the existing code before use:

```json
{
  "allow_discount_codes": true,
  "discount_codes": [{ "discount_code_id": 44 }]
}
```

Verify whether each product permits discounts and whether the discount also applies as intended to an order bump.

## 13. Custom thank-you page with attribution

```json
{
  "thanks_url": "https://example.cz/dekujeme",
  "pass_utm_codes_to_thanks_page": true
}
```

Enable email or variable-symbol URL propagation only when the destination requires it and the user accepts placing that data in a URL.

## 14. Existing account defaults explicitly requested

When the user says “use my normal/default project, emails, reminders, GDPR, terms, and invoice numbering,” omit all corresponding override fields. This is an instruction to inherit defaults, not to list and resubmit them.

## Verification recipe for every scenario

After `forms_create`, call:

```text
forms_show({ id: form_id, withPaymentMethods: true })
```

Compare the stored result to the intended scenario:

1. Main and supplemental product IDs.
2. Currency and product-price compatibility.
3. Resolved payment methods.
4. Invoice and recurring/installment settings.
5. Field visibility and requirement.
6. Thank-you and automation configuration.
7. Inherited defaults versus explicit overrides.

Then report which parts are configured and which external behaviors still need a real preview/order/payment test.

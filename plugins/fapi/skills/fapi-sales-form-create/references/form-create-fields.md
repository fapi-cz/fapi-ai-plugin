# `forms_create` field guide

Use this reference to map user intent to the current FAPI MCP schema. Omit fields that are not justified by the request.

## Required input

| Field | Meaning | Rule |
| --- | --- | --- |
| `name` | Internal form name | Non-empty. Infer from the offer if absent. |

A form can technically be created without products, but a usable sales form should contain at least one resolved main product unless the user explicitly requests an empty shell.

## Account-scoped defaults

These fields are optional because FAPI can load account defaults:

| Field | Entity |
| --- | --- |
| `project` | Project ID |
| `series` | Domestic invoice-series ID |
| `foreign_series` | Foreign invoice-series ID |
| `message_template_set` | Standard message-template set |
| `recurring_message_template_set` | Message set for recurring invoices |
| `reminder_set` | Standard reminder set |
| `recurring_reminder_set` | Reminder set for recurring invoices |

Use explicit IDs only when known and requested. The backend verifies ownership.

## Products and offer structure

### Main products

```json
{
  "items": [
    { "item_template_id": 123, "required": false }
  ]
}
```

`required` controls whether the product must be included, only if `allow_multiple_items: true`.

### Product groups

```json
{
  "item_groups": [
    {
      "title": "Vyberte variantu",
      "required": true,
      "allow_multiple_items": false,
      "items": [
        { "item_template_id": 123 },
        { "item_template_id": 124 }
      ]
    }
  ]
}
```

Use groups only when the user describes a conceptual group. `allow_multiple_items: false` models one-of-many selection; `true` models multiple add-ons.

### Order bumps

```json
{
  "allow_order_bumps": true,
  "order_bumps": [
    {
      "item_template_id": 200,
      "name": "Přidat pracovní sešit za {price}",
      "description": "<p>Praktické úkoly ke kurzu za <strong>{price}</strong>.</p>"
    }
  ]
}
```

Supported placeholders include `{itemName}`, `{price}`, `{priceBeforeDiscount}`, and `{image}`. The title must contain `{price}`. Keep HTML to the safe subset accepted by the schema: `a`, `br`, `p`, `strong`, `b`, `i`, `em`, `u`, `s`, `strike`, `span`, `ul`, `ol`, `li`. Anchor URLs must use `http`, `https`, or `mailto`.

### Upsell pages

```json
{
  "upsell_pages": [
    {
      "upsell_url": "https://example.cz/upsell",
      "upsells": [{ "item_template_id": 300 }]
    }
  ]
}
```

A real URL is required. Each page may contain one or more upsell products.

### Changeable items

```json
{
  "allow_changeable_items": true,
  "changeable_items": [
    {
      "base_item_template_id": 400,
      "target_item_template_id": 401
    }
  ]
}
```

Use for replacing an item in later recurring invoices, for example a trial product with the regular subscription product.

## Payment methods

### Offline

| Field | Default | Meaning |
| --- | ---: | --- |
| `allow_wire` | `true` | Classic bank transfer |
| `allow_qr_code_payment` | `true` | QR payment |
| `allow_cash` | `false` | Cash |
| `allow_collect_on_delivery` | `false` | Cash on delivery |

Cash on delivery belongs to physical fulfillment. Check available bank-account currencies when wire or QR readiness matters.

### Payment gateway

| Field | Meaning |
| --- | --- |
| `allow_gopay` | Enables the selected gateway connection |
| `gopay_connection` | Gateway connection ID |
| `allow_gopay_card` | Card payment |
| `allow_gopay_wire` | Express online bank transfer |
| `allow_gopay_paypal` | PayPal through the gateway |
| `allow_gopay_sms` | Mobile/SMS payment |
| `allow_gopay_bitcoin` | Bitcoin |
| `allow_gopay_gpay` | Google Pay |

The names are historical; supported gateway types include GoPay, ThePay, ComGate, Twisto, Pays, Stripe, and GP webpay. Inspect the selected connection instead of inferring method support from the field name.

## Invoice creation

| Field | Default | Meaning |
| --- | ---: | --- |
| `proforma` | `true` | Issue an advance invoice before payment |
| `disable_create_invoice_automatically` | `false` | Delay automatic invoice creation |
| `date_to_create_invoice_automatically` | unset | ISO date for delayed creation; must not be in the past |
| `allow_simplified` | `true` | Permit simplified document behavior |
| `reverse_charge` | `foreign-customers-with-valid-dic` | Reverse-charge policy; preserve this MCP default unless another supported mode is explicitly requested |
| `show_prices_including_vat` | `true` | Price presentation |

Reverse-charge values:

* `disabled`
* `foreign-customers`
* `foreign-customers-with-dic`
* `foreign-customers-with-ic`
* `foreign-customers-with-valid-dic`

Do not override tax behavior without a clear requirement.

## Currency

| Mode | Fields |
| --- | --- |
| Country-based | `currency_setting: by-country` |
| Buyer choice | `currency_setting: choice`, `allowed_currencies: ["CZK", "EUR"]` |
| Fixed | `currency_setting: always`, `currency_code: "CZK"` |

Currency codes must match `^[A-Z]{3}$`. Available payment methods and bank-account routing can differ by currency.

The MCP default is `currency_setting: by-country`. Use a fixed currency or buyer choice only when explicitly requested; a product price in CZK alone does not select `always`.

## Installments

```json
{
  "allow_repayments": true,
  "repayment_counts": [3, 6, 12]
}
```

Every count must be a positive integer. `repayment_count` is deprecated.

## Recurring billing

```json
{
  "allow_recurring": true,
  "period": "1 months",
  "end_by": "none"
}
```

End modes:

| `end_by` | Required companion |
| --- | --- |
| `none` | none |
| `iteration` | positive `iteration` |
| `date` | ISO `last_date` |

Optional recurring fields:

| Field | Meaning |
| --- | --- |
| `trial_period` | Trial duration in days |
| `allow_gopay_recurring_payments` | Automatic card charging |
| `require_recurring_terms` | Require recurring-terms agreement |
| `recurring_terms_url` | Form-specific terms; omit to inherit account default |

Automatic card charging requires a compatible gateway connection and an initial card payment after the setting is enabled.

## Regions

The tool defaults all regions to allowed:

* `allow_region_cz`
* `allow_region_sk`
* `allow_region_eu`
* `allow_region_world`

Restrict only on explicit business, legal, tax, or fulfillment requirements.

## Buyer fields

Use `field_settings` rather than legacy `show_field_*` and `require_field_*` fields.

```json
{
  "field_settings": {
    "name": { "name": "name", "show": true, "required": true },
    "company": { "name": "company", "show": false, "required": false },
    "address": { "name": "address", "show": true, "required": true },
    "country": { "name": "country", "show": true, "required": true },
    "email": { "name": "email", "show": true, "required": true },
    "phone": { "name": "phone", "show": false, "required": false },
    "note": { "name": "note", "show": false, "required": false }
  }
}
```

Default visible required fields are email and country. All other standard fields are hidden and optional.

For physical delivery, consider:

```json
{
  "allow_shipping_address": true
}
```

## Custom fields

```json
{
  "custom_fields": [
    {
      "name": "Velikost trička",
      "custom_field_id": 55,
      "required": true
    }
  ]
}
```

A custom field ID cannot currently be listed through the available MCP tools. Use only a supplied or otherwise verified ID.

## Shipping methods

```json
{
  "allow_shipping_methods": true,
  "shipping_methods": [
    { "shipping_method_id": 10 }
  ]
}
```

Do not enable shipping methods without at least one verified method ID. There is currently no dedicated shipping-method list tool.

## Appearance and layout

```json
{
  "template_settings": {
    "container_settings": {
      "billing": { "layout": { "column": "single" } },
      "shipping": { "layout": { "column": "single" } },
      "payment": {
        "layout": { "variant": "tile", "column": "single" },
        "allow_inline_payment_card": false
      },
      "is_two_step_form": false,
      "two_step_form_type": "inline",
      "two_step_redirect_url": null
    }
  },
  "max_width": 650
}
```

Allowed values:

* Columns: `single`, `multi`
* Payment variant: `tile`, `radio`
* Two-step behavior: `inline`, `redirect`
* Default `max_width`: `650` pixels; explicit `null` removes the width limit.

For a redirect-style second step, provide `two_step_redirect_url`.

## Form behavior settings

Nested under `settings`:

| Field | Meaning |
| --- | --- |
| `redirect_to_order_status_page_if_error` | Always set to `true` to show the order-status page after an error |
| `allow_upsell_summary_page` | Allow upsell summary |
| `upsell_to_all_repayment_invoices` | Apply upsell to all installment invoices |
| `allow_send_repayment_invoices_consecutively` | Send installment invoices consecutively |
| `min_order_value` | Minimum order value |
| `max_order_value` | Maximum order value |
| `try_to_charge_max_count` | Maximum automatic charging attempts |
| `disable_autofill_product` | Do not preselect the first main product |
| `fb_pixel_id` | Facebook Pixel ID |
| `se_webtracking_guid` | SmartEmailing webtracking GUID |
| `disable_default_payment_method` | Do not preselect a payment method |

Include `redirect_to_order_status_page_if_error: true` in `settings` together with any other justified settings. Never select “Vytvořit obsah chybové stránky” (`error_custom_content`) or send `error_content`; the MCP form tools do not accept custom error-page HTML. When updating settings through `forms_update`, read the form first and preserve unrelated settings because the supplied object replaces the stored settings.

## Language

Supported by the current MCP schema:

* `cs`, `sk`, `en`, `es`, `de`, `vi`, `pl`, `ru`, `it`, `pt`, `fr`, `zh`

Set `language` for the form and `invoice_language` for invoices. UI documentation may list additional languages not yet accepted by the MCP schema; the schema wins for tool calls.

## Thank-you journey and tracking

| Field | Meaning |
| --- | --- |
| `thanks_url` | Custom thank-you page URL |
| `thanks_content` | Internal thank-you page HTML; supports `{item-<item_code>}...{/item-<item_code>}` for product-specific content; codes match case-insensitively |
| `allow_variable_symbol_in_custom_url` | Append/allow variable symbol in custom URL |
| `allow_email_in_custom_url` | Append/allow customer email in custom URL |
| `pass_utm_codes_to_thanks_page` | Pass UTM values onward |
| `enable_google_analytics_support` | Enable GA support |
| `google_analytics_tracking_id` | Tracking ID |
| `allow_own_conversion_code` | Enable custom conversion code |
| `own_conversion_code` | Custom conversion code |
| `campaign_code` | Campaign identifier |

Do not enable tracking merely because a field exists. Use only user-provided identifiers/code.

## Discounts

```json
{
  "allow_discount_codes": true,
  "discount_codes": [{ "discount_code_id": 44 }]
}
```

Resolve the code before creation. Products can independently disallow discounts.

## Legal purposes and terms

```json
{
  "allow_terms": true,
  "terms_url": "https://example.cz/obchodni-podminky",
  "allow_privacy_policy": true,
  "purposes": [
    {
      "html": "<p>Approved consent text supplied by the user.</p>",
      "required": false,
      "step": "order"
    }
  ]
}
```

Omit these fields on normal creation to inherit account-level settings. Do not generate placeholder legal text.

`step` accepts:

* `intent` — first step of a two-step form,
* `order` — order step.

Intent-step purposes do not persist on a one-step form.

## Triggers

### Events

* `ordered`
* `paid`
* `cancelled`
* `item-ordered`
* `item-paid`
* `item-cancelled`
* `item-ordered-with-code`
* `item-paid-with-code`
* `item-cancelled-with-code`

### Actions exposed by the current MCP schema

* `url-notification`
* `add-contact-to-smartemailing`
* `remove-contact-from-smartemailing`
* `add-contact-to-anabix`
* `remove-contact-from-anabix`
* `send-email-to-client`
* `send-email-to-user`
* `send-sms-to-client`
* `send-file`
* `fapi-member`

Action-dependent fields include:

* `notification_url`
* `message_template_id`
* `smartemailing_contactlist_id`
* `anabix_contactlist_id`
* `sendinblue_contactlist_id`
* `fapi_member_section_id`
* `fapi_member_days`
* `connection_id`
* `item_template_id`
* `item_foreign_code`

Use only combinations whose IDs and URLs are known. A FAPI Member action requires `connection_id`; its section ID must also be supplied or otherwise verified.

## Tool defaults worth preserving

Normal create behavior includes these conservative defaults unless overridden:

* Payment: wire and QR enabled; online gateway, cash, and COD disabled.
* Invoice: proforma enabled.
* Regions: Czechia, Slovakia, EU, and world allowed.
* Fields: email and country visible/required.
* Layout: one step, single columns, tile payment methods.
* Prices: shown including VAT.
* Form width: `650` px.
* Currency selection: `by-country`.
* Reverse charge: `foreign-customers-with-valid-dic`.
* Error page: explicitly set `settings.redirect_to_order_status_page_if_error: true`.
* Legal URLs/text: inherited when omitted.

Do not serialize every default into the tool call. Send the intended delta plus required name/products.

# Official FAPI documentation

## Core form workflow

* https://napoveda.fapi.cz/article/44-prodejni-formular

Used for the customer-facing model of a form, the six configuration areas, product selection behavior, payments/invoicing, actions, thank-you pages, buyer fields, languages, simplified documents, terms/GDPR, preview behavior, and the distinction between active and archived forms.

## Payments

* https://napoveda.fapi.cz/article/71-platby-ve-fapi
* https://napoveda.fapi.cz/article/310-co-je-to-platebni-brana-a-jak-ji-vyuzit-ve-fapi

Used for the distinction between gateway payment information and bank-import payment information, available online/offline payment families, and the requirement to configure a gateway for online methods.

## Recurring billing and charging

* https://napoveda.fapi.cz/article/67-pravidelna-fakturace
* https://napoveda.fapi.cz/article/73-opakovane-platby
* https://napoveda.fapi.cz/article/232-opakovane-strhavani-z-karty

Used for recurring invoice behavior, changeable products, gateway/card-token prerequisites, and automatic charge behavior.

## Order bump and upsell

* https://napoveda.fapi.cz/article/77-miniupsell-order-bump
* https://napoveda.fapi.cz/article/76-upsell
* https://napoveda.fapi.cz/article/159-one-click-upsell

Used for placement in the buyer journey and recurring-order implications.

## Legal and consent configuration

* https://napoveda.fapi.cz/article/42-gdpr-ve-fapi

Used for central account-level terms/GDPR inheritance and form-specific consent behavior.

## Currency and two-step form

* https://napoveda.fapi.cz/article/20-meny-ve-fapi
* https://napoveda.fapi.cz/article/192-dvoukrokovy-prodejni-formular

Used for payment/bank currency compatibility and the intended two-step checkout model.

# Known documentation/schema differences

* The help article lists Croatian and Hungarian among UI languages, but the current `forms_create` schema does not accept their language codes. Do not send unsupported codes.
* Official help describes more integration actions than the current MCP trigger schema exposes. Configure only actions accepted by the schema.
* The UI can duplicate, archive, preview, style, and provide embed code. This creation skill does not claim those capabilities unless a dedicated tool exposes them.
* The help describes an order-intent event for two-step forms, while the current MCP trigger-event enum does not expose it. Do not invent an event value.

## API behavior and validation

Important confirmed behavior:

* Missing account-scoped fields are completed from account settings/defaults.
* Referenced entities are validated against the authenticated account.
* Related arrays such as products, upsells, triggers, discounts, groups, bumps, purposes, custom fields, and shipping methods are assigned after the base form is created.
* Stock-enabled products cannot be used for recurring invoicing.
* Automatic recurring charging requires a payment-gateway connection that supports it.
* A delayed automatic invoice date cannot be in the past.
* Product IDs are deduplicated.
* Two-step-only intent purposes/triggers do not apply to a one-step form.

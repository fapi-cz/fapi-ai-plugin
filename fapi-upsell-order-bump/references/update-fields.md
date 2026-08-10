# FAPI add-on update fields

Use this reference before changing an existing sales form.

## Required reads

Always inspect the target form with `forms_show` before `forms_update`.

Use `forms_list` only to find candidates. It is not enough for composing an update.

## Order bumps

```json
{
  "allow_order_bumps": true,
  "order_bumps": [
    {
      "item_template_id": 200,
      "name": "Ano, přidat bonus za {price}",
      "description": "<p>Bonus získáte společně s objednávkou. Cena: <strong>{price}</strong>.</p>"
    }
  ]
}
```

Field rules:

* `item_template_id` is a product catalog ID.
* `name` is the miniupsell/order-bump title and must contain `{price}`.
* `description` is optional, but when it includes price text, keep `{price}` dynamic.
* `allow_order_bumps` must be true when order bumps should be active.
* Safe HTML tags are `a`, `br`, `p`, `strong`, `b`, `i`, `em`, `u`, `s`, `strike`, `span`, `ul`, `ol`, `li`.
* Anchor URLs must use `http`, `https`, or `mailto`.

## Upsell pages

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

Field rules:

* `upsell_url` is required and must be supplied by the user or discovered from existing verified configuration.
* `upsells` contains the products offered on that page.
* Keep the page order intentional when there are multiple upsell pages.

## Replacement semantics

These fields are list-like and replace the stored list when sent:

* `items`
* `item_groups`
* `order_bumps`
* `upsell_pages`
* `changeable_items`
* `discount_codes`
* `purposes`
* `triggers`
* `custom_fields`
* `shipping_methods`

Omit unrelated lists. When changing one list, send the complete desired version of that one list after merging the requested edit with the existing state.

## Verification checklist

After `forms_update`, call `forms_show({ id: form_id, withPaymentMethods: true })` and compare:

* Target form name and ID.
* Main `items` and `item_groups` still match the pre-update form unless intentionally changed.
* `allow_order_bumps` and all `order_bumps` entries.
* `upsell_pages` URLs and product IDs.
* Recurring, installment, currency, and product compatibility.
* Requested external behavior clearly marked as untested when no real checkout test was run.

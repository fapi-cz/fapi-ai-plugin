# Sources and workflow routing

Use this reference when source precedence or routing between skills matters.

## Repository sources

* `mcp/TOOLS.md` documents `users_update_billing_information`, `bank_account_sets_*`, `settings_*`, `payment_gateways_*`, product tools, and form tools.
* `mcp/src/tools/users/usersParams.ts` defines billing-information update shape.
* `mcp/src/tools/bankAccountSets/bankAccountSetsFields.ts` defines bank-account set validation.
* `mcp/src/tools/settings/settingsFields.ts` defines settings validation.
* `mcp/src/tools/paymentGateways/paymentGatewaysFields.ts` defines payment gateway filters.

## Related skills

* `fapi-product-create` — create or update catalog products.
* `fapi-sales-form-create` — create first sales form or checkout.
* `fapi-upsell-order-bump` — add order bumps or upsells to an existing form.

## Public help links

Use these when explaining manual next steps:

* Sales form: https://napoveda.fapi.cz/article/318-prodejni-formular
* Embed sales form: https://napoveda.fapi.cz/article/163-vlozeni-prodejniho-formulare-na-web
* Test mode: https://napoveda.fapi.cz/article/66-testovaci-rezim-prodejniho-formulare
* Payment gateways overview/search: https://napoveda.fapi.cz/

## Precedence

Use this order when sources disagree:

1. Current MCP schema and tool descriptions.
2. Current backend/API docs in the repository.
3. Related skills for workflow boundaries.
4. FAPI public help for user-facing explanation and manual steps.
5. Older skill text only as historical context.

# Sources and workflow routing

Use this reference when source precedence or workflow boundaries matter.

## Repository sources

* `mcp/TOOLS.md` documents `users_update_billing_information`, `settings_*`, `bank_account_sets_*`, and `payment_gateways_*`.
* `mcp/src/tools/users/usersParams.ts` defines seller billing-information fields.
* `mcp/src/tools/settings/settingsFields.ts` defines setting validation and account summary extraction.
* `mcp/src/tools/bankAccountSets/bankAccountSetsFields.ts` defines bank-account validation and replacement semantics.
* `mcp/src/tools/paymentGateways/paymentGatewaysFields.ts` defines read-only gateway filters.

## Related skills

* `fapi-account-activation` — full first-sale activation.
* `fapi-product-create` — product catalog creation.
* `fapi-sales-form-create` — sales-form creation using billing defaults.

## Precedence

Use this order when sources disagree:

1. Current MCP schemas and tool descriptions.
2. Current backend/API docs in the repository.
3. Related skills for workflow boundaries.
4. FAPI public help for manual user-facing steps.

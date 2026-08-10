# Sources and workflow routing

Use this reference when source precedence or workflow boundaries matter.

## Repository sources

* `mcp/src/tools/invoices/invoicesFields.ts` defines the MCP snake_case invoice create schema.
* `mcp/src/tools/invoices/invoicesParams.ts` defines internal invoice parameter concepts.
* `mcp/TOOLS.md` documents `invoices_create`, `invoices_show`, `invoices_update`, and `invoices_delete`.
* `mcp/src/tools/clients/clientsFields.ts` defines client lookup/create fields.
* `web/public/api-doc/src/Invoices.js` documents invoice document types and side-effect flags.

## Related skills

* `fapi-product-create` — create reusable product catalog entries before using `item_template_id`.
* `fapi-billing-setup` — configure seller billing, VAT defaults, currency, and bank accounts.
* `fapi-sales-form-create` — create a checkout instead of manual invoice.

## Field naming

Use MCP snake_case in tool calls:

* `including_vat`, not `includingVat`
* `payment_type`, not `paymentType`
* `paid_on`, not `paidOn`
* `item_template_id`, not `itemTemplateId`
* `shipping_address`, not `shippingAddress`

## Precedence

Use this order when sources disagree:

1. Current MCP schema.
2. Current API docs in the repository.
3. Current backend/domain code.
4. Related skills for workflow boundaries.

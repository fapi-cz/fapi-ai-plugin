# Sources and precedence

Use this reference when behavior, terminology, or field support is unclear.

## Repository sources

* `mcp/src/tools/itemTemplates/itemTemplatesParams.ts` defines MCP TypeScript types for product fields.
* `mcp/src/tools/itemTemplates/itemTemplatesFields.ts` defines MCP validation and descriptions.
* `mcp/TOOLS.md` documents `item_templates_create`, `item_templates_update`, `item_templates_show`, and `item_templates_list`.
* `common/src/Fapi/ItemTemplate/ItemTemplateSaver.php` shows backend create/update behavior, including required prices and replacement behavior for prices/triggers.
* `common/src/Fapi/ItemTemplate/ItemTemplate.php` shows stored product fields.
* `common/src/Fapi/ItemTemplate/ItemTemplatePrice/Price.php` shows price fields and default repayment count behavior.

## Related skills

* `fapi-sales-form-create` creates a sales form and may create a missing product as part of that workflow.
* `fapi-upsell-order-bump` attaches an existing or newly created product to an existing form as an add-on.

## Precedence

Use this order when sources disagree:

1. Current MCP schema.
2. Current backend code.
3. Current `mcp/TOOLS.md`.
4. Related skills as workflow context.
5. Older skill text only as historical context.

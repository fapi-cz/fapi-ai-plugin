# Help and repository sources

Use these sources for terminology and user-facing behavior. The executable MCP schema remains authoritative for tool payloads.

## FAPI help

* Order bump / miniupsell: https://napoveda.fapi.cz/article/77-miniupsell-order-bump
* Doplňkové prodejní položky: https://napoveda.fapi.cz/article/68-doplnkove-prodejni-polozky
* Upsell: https://napoveda.fapi.cz/article/76-upsell
* Sales form context: https://napoveda.fapi.cz/article/318-prodejni-formular

Known legacy aliases:

* https://napoveda.fapi.cz/article/1024-miniupsell redirects to the miniupsell/order-bump article.
* https://napoveda.fapi.cz/article/564-doplnkove-prodejni-polozky redirects to article 68.
* https://napoveda.fapi.cz/article/92-upsell redirects to article 76.

## Repository references

* `mcp/src/tools/forms/formsParams.ts` defines `FormOrderBumpParams`, `FormUpsellPageParams`, and `FormUpsellParams`.
* `mcp/src/tools/forms/formsFields.ts` defines the MCP validation and descriptions for `allow_order_bumps`, `order_bumps`, and `upsell_pages`.
* `web/public/api-doc/src/Forms.js` documents placeholders, allowed HTML tags, and update behavior for order bumps and upsells.
* `mcp/TOOLS.md` describes MCP behavior for `forms_update` and relational-list fields.

## Terminology map

| User-facing term | MCP/API field |
| --- | --- |
| Miniupsell | `order_bumps` |
| Doplňková prodejní položka | `order_bumps` |
| Order bump | `order_bumps` |
| Upsell stránka | `upsell_pages` |
| Prodejní položka | `item_template_id` |

## Precedence

Use this order when sources disagree:

1. Current MCP schema.
2. Current API docs in the repository.
3. Current application code.
4. FAPI public help for terminology and business explanation.
5. Older skill text only as historical context.

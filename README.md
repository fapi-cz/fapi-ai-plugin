# FAPI AI plugin

One installable FAPI plugin for Codex and Claude Code. It combines reusable FAPI workflow skills with the production FAPI MCP server at `https://mcp.fapi.cz/mcp`.

Authentication uses OAuth. The repository does not contain API tokens, usernames, client secrets, or custom authentication headers.

## Included skills

- `fapi-account-activation` — prepare an account for its first sale.
- `fapi-billing-setup` — configure billing identity, VAT, currency, invoice defaults, and bank accounts.
- `fapi-default-notification-templates` — work safely with default notification and reminder templates.
- `fapi-invoice-create` — create and verify invoices, proformas, simplified invoices, and credit notes.
- `fapi-page-editor` — create and edit sales pages, reference styling, fonts, media, lines, and page elements.
- `fapi-product-create` — create and update reusable product catalog items.
- `fapi-sales-email-communication-create` — create email communication for a sales flow.
- `fapi-sales-form-create` — create a complete FAPI sales form.
- `fapi-upsell-order-bump` — configure order bumps and upsells on an existing form.

## Install in Codex

```bash
codex plugin marketplace add fapi-cz/fapi-ai-plugin
codex plugin add fapi@fapi
```

Codex requests FAPI OAuth authorization during installation because the marketplace uses `authentication: "ON_INSTALL"`.

To refresh the marketplace and reinstall the current plugin version:

```bash
codex plugin marketplace upgrade fapi
codex plugin remove fapi@fapi
codex plugin add fapi@fapi
```

To remove the plugin and marketplace:

```bash
codex plugin remove fapi@fapi
codex plugin marketplace remove fapi
```

## Install in Claude Code

```bash
claude plugin marketplace add fapi-cz/fapi-ai-plugin
claude plugin install fapi@fapi
```

Claude Code starts the FAPI OAuth flow when it activates the MCP connection.

To refresh the marketplace and update the plugin:

```bash
claude plugin marketplace update fapi
claude plugin update fapi@fapi
```

To remove the plugin and marketplace:

```bash
claude plugin uninstall fapi@fapi
claude plugin marketplace remove fapi
```

## Troubleshooting

### OAuth does not complete

Retry the connection from the host's plugin or MCP settings. Do not add a static token to `.mcp.json`; the FAPI MCP server is designed to authenticate through OAuth.

### FAPI tools are unavailable

Confirm that `https://mcp.fapi.cz/mcp` is reachable and that the OAuth connection is active. Restart the host after installing or updating the plugin so it reloads the cached plugin version.

### An update is not visible

Refresh the marketplace and update or reinstall the plugin with the commands above. Released changes must bump the version in both plugin manifests.

## OpenAI-hosted skills for Fapilot

Maintain Fapilot workflow instructions in `plugins/fapi/skills/`. Validate the skill, publish its bundle through the [OpenAI Skills API](https://developers.openai.com/cookbook/examples/skills_in_api), and verify the returned skill ID, version and content. Then prepare the Fapilot PR that registers that hosted skill ID. Keep credentials out of the bundle and repository. New workflow instructions do not belong in Fapilot's static `fapilot_instructions.md` or a duplicate static prompt.

## Contributor template

`templates/fapi-template-skill/` is an authoring template for new FAPI skills. It is intentionally outside `plugins/fapi/skills/` and is not installed with the plugin.

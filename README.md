# FAPI AI plugin

One installable FAPI plugin for Codex and Claude Code. It combines reusable FAPI workflow skills with the production FAPI MCP server at `https://mcp.fapi.cz/mcp`.

Authentication uses OAuth. The repository does not contain API tokens, usernames, client secrets, or custom authentication headers.

## Included skills

- `fapi-account-activation` — prepare an account for its first sale.
- `fapi-billing-setup` — configure billing identity, VAT, currency, invoice defaults, and bank accounts.
- `fapi-ebook-delivery` — prepare e-book sales and native product-file delivery after payment.
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

Maintain customer-facing workflows in the owning skills in this repository, including any linked references that govern the same decision. A Fapilot prompt change in `fapi-cz/fapi` does not update these skills or OpenAI-hosted skill versions; keep the relevant sources consistent and track their publication separately. Installed plugin caches are not maintained sources. Merging a repository PR alone does not prove that installed or hosted skills have been refreshed.

`templates/fapi-template-skill/` is an authoring template for new FAPI skills. It is intentionally outside `plugins/fapi/skills/` and is not installed with the plugin.

## Synchronize OpenAI skills

Run from a reviewed checkout with Python, a compatible `ansible-core` installation, and `OPENAI_API_KEY` supplied by the existing secret manager/environment. Optional `OPENAI_PROJECT_ID` and `OPENAI_ORGANIZATION_ID` select the project/organization. Never put the key in inventory, source files, or command arguments.

```bash
ansible-playbook -i localhost, ansible/sync-openai-skills.yml --check
ansible-playbook -i localhost, ansible/sync-openai-skills.yml
```

The playbook runs locally, uploads the complete skill directory including references, and compares file contents with the latest hosted ZIP. It skips unchanged bundles, preserves existing IDs, creates immutable versions for changed content, and verifies uploaded content. It does not change `default_version`, delete remote skills, access application servers, or update installed plugin caches. Fapilot uses `latest`, so a successful live version upload becomes available to it without replacing the ID. Run releases serially for the same project.

`ansible/skills.json` lists the IDs already registered by Fapilot; a missing/mismatched ID stops before writes to catch a wrong project. The restored `fapi-ebook-delivery` source corresponds to its existing hosted ID, not a new registration. Its previous hosted version 2 was inspected before restoring the source here.

New skills are created only in a normal, authorized playbook run. The report's `fapi_pr_required` lists skills without a recorded Fapilot registration, including their new IDs after upload. Follow [AGENTS.md](AGENTS.md): create and cross-link a companion FAPI PR updating the loader registry and its test, then record the ID here after that PR is merged. Upload alone does not make a new skill available to Fapilot. Source/version changes and hosted publication are separate review/release steps.

Check mode performs reads only. Uploads are not blindly retried after a connection failure: inspect the remote state and rerun the comparison to reconcile an ambiguous result. A short bounded retry handles the documented post-upload 404 while a new version becomes available.

Verification without publishing:

```bash
python3 -m unittest discover -s tests
ansible-playbook -i localhost, ansible/sync-openai-skills.yml --syntax-check
```

API behavior follows the [official OpenAI Skills guide](https://developers.openai.com/api/docs/guides/tools-skills), [version upload API](https://developers.openai.com/api/reference/resources/skills/subresources/versions/methods/create), and [version content API](https://developers.openai.com/api/reference/resources/skills/subresources/versions/subresources/content/methods/retrieve).

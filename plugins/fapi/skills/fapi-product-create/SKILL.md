---
name: fapi-product-create
description: >-
  Use this skill when the user wants Fapilot to create, update, verify, or
  prepare a FAPI product, product catalog item, item template, prodejní položka,
  main product image upload, nahrání obrázku k produktu,
  electronic product materials, nahrání souborů nebo materiálů k produktu,
  ceníková položka, price, VAT, stock, recurring product, repayment price,
  subscription metadata, Buddy delivery metadata, affiliate commission, Pohoda
  accounting fields, or a product intended for a sales form, invoice, upsell, or
  order bump. Do not use for creating a full sales form, changing an existing
  form, issuing an invoice, or configuring checkout payment methods.
---

# Create a FAPI product

## Purpose

Create or prepare a reusable FAPI product record that can be safely used in sales forms, invoices, order bumps, upsells, and automations.

In FAPI API and MCP tools, a product is an **item template**. A correct product is more than a name and price: it carries tax, currency, quantity, stock, type, recurring, delivery, affiliate, accounting, and public presentation behavior.

## Scope

Use this skill for:

* Creating a new product in the FAPI catalog.
* Updating or completing an existing product when the user explicitly asks for product-level changes.
* Preparing products for later use in `forms_create`, `forms_update`, `invoices_create`, order bumps, or upsells.
* Resolving duplicate or ambiguous catalog products before writing.
* Verifying product fields after creation or update.
* Uploading or replacing the main product image from a local file accessible to the client.
* Uploading one or more electronic product materials from local files in a supported Codex or Claude Code host.

Do not use this skill for:

* Creating a sales form or checkout; use `fapi-sales-form-create`.
* Adding a product to an existing form as an order bump or upsell; use `fapi-upsell-order-bump`.
* Creating a manual invoice without changing the catalog.
* Deleting a product unless the user explicitly requests deletion and confirms the risk.
* Inventing prices, VAT, legal text, stock, integration IDs, or accounting codes.

## Domain model

### Item template

An item template is a reusable product definition. Its ID is passed as `item_template_id` to sales forms, invoices, order bumps, upsells, and changeable items.

Required for creation:

```text
name
prices: [{ type, currency_code, price }]
```

### Price

Use `one_time` for a normal product price, including a product that will later be sold through form-level installments.

Use `repayment` only for an explicitly defined installment price entry, and include `repayment_count`.

Currency codes must be uppercase ISO 4217 values.

### Product type

Choose the product type deliberately:

* `electronic-service` — online courses, downloads, digital access, recordings, software access, memberships.
* `electronic-publication` — one-time e-books or electronic publications.
* `electronic-period-publication` — recurring electronic publications.
* `service` — consulting, coaching, implementation, offline services.
* `live-event` — workshops, events, conferences.
* `good` — physical goods.
* `food` — food products.
* `printed-publication` — printed books or publications.
* `printed-period-publication` — recurring printed publications.
* `excluding_vat` — only when the product must be handled outside normal VAT behavior.

Use the actual name, description, and delivery ahead of a generic onboarding starter. Coaching cards or a deck of cards normally mean physical `good`, even after a Service starter. Explicit PDF/digital delivery takes precedence. Infer the probable type and briefly report it; ask only when the description is genuinely unclear or contradictory.

### Recurring product

Recurring product metadata is product-level. Recurring billing in a sales form is form-level. Do not confuse the two.

Use product fields:

```text
periodic: true
period: "1 months"
```

Only when the product itself is genuinely periodic.

## Procedure

### 1. Build the product model

Determine:

* Product name and optional code.
* Intended use: sales form, invoice, order bump, upsell, recurring sale, physical delivery, accounting, or integration.
* Price amount, currency, price type, and whether price includes VAT.
* VAT rate and VAT-payer context.
* Product type.
* Quantity behavior: default count, whether buyer may change count, minimum/maximum count.
* Stock behavior for physical products.
* Public and invoice descriptions.
* Optional metadata: physical customs, subscription, Buddy, affiliate, Pohoda, custom integration parameters.

Ask one combined question only when creation cannot continue safely, typically:

* Missing price.
* Missing currency and no account default is known.
* Missing VAT rate for a VAT payer when no default rate is known.
* Missing stock amount when `enable_stock` is required.
* Missing recurring period for a recurring product.
* Missing repayment count for a repayment price.
* Ambiguous existing product candidates.

Do not ask for optional fields that can safely stay unset.

When name, price, currency, and other truly required data are clear, create the requested product without another general confirmation. Never turn a missing price into zero. In guided onboarding, continue with the linked form through `fapi-sales-form-create` unless the user explicitly wants only the product.

### 2. Inspect account defaults

Use:

* `settings_list` for currency, VAT mode, default VAT rate, language, invoice/payment defaults, and account summary.
* `settings_show` only when `settings_list` is insufficient and the setting materially affects the product.

Rules:

* Outside guided onboarding, use account default currency when the user omits it and the default is available. In guided onboarding, require a currency supplied or clearly expressed by the user; do not silently assume CZK.
* In guided onboarding, save an explicitly stated VAT status through `fapi-billing-setup` before creating dependent products. Do not merely acknowledge a new status while using the old account mode.
* If the account is a non-VAT payer, use `vat: 0`.
* If the account is a VAT payer and the user omits VAT, use the account default VAT rate when available; otherwise ask.
* Use `including_vat: true` for normal public consumer prices unless the user clearly says the price is without VAT.

Read `references/product-fields.md` before composing create or update payloads.

### 3. Prevent duplicates

1. Search by exact `code` when supplied.
2. Search by exact `name` when no code is supplied.
3. Use `item_templates_list` with `only_names: true` for a quick candidate check.
4. Inspect likely candidates with `item_templates_show`.
5. Reuse or update only when the existing product clearly matches the user's intent.
6. Create a separate product only when a distinct variant or business purpose is intended. Adding another currency price to the same product is an update, not a reason to create a duplicate.

`item_templates_create` is non-idempotent. Do not silently create duplicates.

### 4. Compose the smallest correct product

Use `item_templates_create` with required fields and only justified optional fields.

Minimum usable example:

```json
{
  "name": "Online kurz",
  "prices": [
    {
      "type": "one_time",
      "currency_code": "CZK",
      "price": 1990
    }
  ],
  "including_vat": true,
  "count": 1,
  "type": "electronic-service"
}
```

Rules:

* Include `code` when the user supplies a stable SKU/code or when naming collisions are likely.
* Include `description` for invoice-facing text only when known.
* Include `public_description` for order-form-facing text only when known and safe.
* Use `count: 1` unless the product is naturally sold in another default quantity.
* Use `allow_change_count: true` for physical goods or products where buyers should choose quantity.
* Use `enable_stock: true` only when stock tracking is intended; then `stock` is required.
* Never enable stock for a product already used in periodic invoicing.
* Use `disable_discount: true` only when discounts must not apply.
* Do not add affiliate, Buddy, subscription, Pohoda, or customs metadata without explicit evidence.

### 5. Handle specialized product scenarios

Read `references/scenario-recipes.md` for physical products, recurring products, repayment prices, multi-currency products, Buddy, affiliate, Pohoda, and custom metadata.

Key constraints:

* Physical products shipped abroad may need `metadata.english_name`, `metadata.country_of_origin`, and `metadata.harmonized_system_code`.
* `metadata.affiliate_commission*` belongs only to FAPI Rewards or an explicit affiliate setup.
* `metadata.allow_contract_withdrawal` controls product eligibility for the withdrawal flow. The current MCP default is `true`; omit it unless an explicit, legally grounded instruction justifies changing it. Product type alone is not a legal exemption.
* `metadata.buddy_metadata.messages_count` belongs only to a Buddy delivery requirement.
* `metadata.subscription` and `metadata.subscription_level` require stable names and codes.
* On update, sending `prices` replaces the stored price list. Sending `metadata` replaces the stored metadata object. Sending `triggers` replaces the trigger list.
* When the user adds an EUR amount to an existing CZK offer, add a `one_time` EUR price alongside CZK unless replacement was explicit. Read `item_templates_show`, merge all existing prices and kinds, send the full `prices` list, and verify both amounts and all previous prices. Do not invent an exchange rate or change account currency.

### Electronic material delivery

For e-books and other electronic files, prefer uploading the material directly to the product in Prodej → Produkty → úprava produktu. After payment of a non-cancelled order, FAPI exposes purchased-product downloads on the order overview and through HTML email placeholders: `{items}` / `{itemsList}` may include the links, and `{downloads}` / `{downloadsList}` provide a separate list. Use `notification_reference_show` when composing email content.

Current product MCP tools cannot upload or list attached product files. Create and verify the product/form, then give the manual upload step; do not claim upload or delivery was tested. A missing file does not block product/form creation. Do not require an external delivery URL or add another sending action when the existing paid email already delivers the product material. The seller must upload and verify delivery before starting sales.

### 5a. Decide contract-withdrawal carefully

Use `metadata.allow_contract_withdrawal: false` only when the legal regime clearly excludes withdrawal.

Practical guardrails:

* Leave the field absent on create to preserve the MCP default `true`, including for `electronic-service`, `electronic-publication`, and `electronic-period-publication`.
* Do not infer consent, early performance, required notice, or a legal exclusion from a name such as “online course”, “membership”, “ebook”, or “electronic magazine”.
* Set `false` only on an explicit, legally grounded instruction establishing the applicable exclusion and its conditions; do not generate consent or legal wording.
* On update, omit `metadata` if no metadata change is requested. If changing another metadata key, preserve the existing withdrawal value or its absence in the full replacement object; do not silently reset it.
* Typical cases where withdrawal may be unavailable are the exceptions in § 1837 of the Czech Civil Code, especially fully performed services with prior explicit consent and notice, digital content not delivered on a tangible medium after performance has started with prior explicit consent and notice, custom-made goods, perishable goods, sealed hygiene goods after opening, newspapers or periodicals outside subscriptions, and leisure or accommodation services tied to a specific date.
* From 19 June 2026, if the contract was concluded through an online interface and the customer does have the withdrawal right, the merchant must also support an online withdrawal flow in that interface.

### 6. Create or update

For creation:

1. Call `item_templates_create`.
2. Capture `item_template_id`.

For update:

1. Call `item_templates_show` first.
2. Send only fields that should change.
3. For `prices`, `metadata`, and `triggers`, merge intentionally and send the complete desired value for that field.
4. Never change price, VAT, stock, recurring, affiliate, accounting, or delivery behavior on a live product without explicit user intent.

### 6a. Upload or replace the main product image

Use this path only when the user requests an image change. It preserves price, VAT, code, metadata and all other product settings. Resolve the product with `item_templates_list`/`item_templates_search` and read `item_templates_show` first; retain the original fields for comparison.

This workflow requires `item_templates_upload_image` and a client that can programmatically read a local file and pass its contents as arguments to the connected MCP tool. The helper requires Node.js 20+. A remote MCP server cannot read a client path. If the tool is absent or the client cannot programmatically pass the file contents through its existing MCP connection, report that exact limitation without claiming an upload or requesting another login.

1. Import `imageUploadInput` from `scripts/upload-image.mjs`, resolving the script relative to this skill's installed directory. Call `await imageUploadInput(productId, localImagePath)` in the client's programmatic tool environment. The function returns `{ id, content_base64 }`; it does not upload anything.
2. Pass that returned object directly to `item_templates_upload_image` through the already authenticated MCP connection. Never print or copy base64 into the conversation. Do not put API keys, OAuth credentials, filesystem paths or a data URI into the tool arguments. There is no separate upload authorization or public transfer endpoint.
3. Require a successful response with `image.item_template_id` matching the intended product and a nonempty `image.image_url`. Independently call `item_templates_show`, require the saved `image_url` to match, fetch that URL through the client's HTTPS/file tools, and check a nonempty image response. Compare the saved price, VAT, code and other settings with the original readback.
4. Report success only after this independent verification. Building tool arguments, reading a local file or receiving a placeholder URL is not an uploaded image. After a timeout or uncertain response, read the product before retrying. Invalid, damaged or oversized image content is rejected before replacing the saved image.

The limit is 5 MiB and 12 million pixels. PNG, JPEG and WebP are supported; AVIF also requires server runtime support and otherwise returns a validation error. Images taller than 500 px are resized proportionally. The product image is public presentation content, including order bumps using `{image}`; paid download materials use a separate delivery workflow.

### 6b. Upload one or more product materials

Use this workflow for electronic files delivered with a purchased product. It adds files to the existing native product materials and preserves the product's other settings. Supported formats are PDF, ZIP and MP4/WebM/MOV/OGV/MPEG/MPG/3GP, from 1 byte to 512 MiB per file. The server validates the actual format; an extension alone does not prove valid content.

This workflow supports Codex and Claude Code clients with local file/shell access, Node.js 20+ and outbound HTTPS. It requires `item_templates_prepare_file_upload` and `item_templates_list_files` on the connected server. It does not provide local file access to Fapilot or other remote hosts. If a required capability is unavailable, report the exact limitation. Never send a client filesystem path to remote MCP or print file content or base64 into the conversation. The helper uses the existing authenticated MCP connection only for preparation; its direct transfer uses a narrowly scoped authorization, not an API key or the host's OAuth credentials.

1. Resolve the intended product with `item_templates_list`/`item_templates_search`; call `item_templates_show` and `item_templates_list_files({ id })`. Retain the original product fields and existing material IDs. Ask only when product selection or the requested local files are ambiguous.
2. Resolve `scripts/upload-materials.mjs` relative to this installed skill. Run `node upload-materials.mjs metadata /local/book.pdf /local/exercises.zip /local/lesson.mp4`. It streams the local files and returns `{ "files": [{ "file_name", "size", "sha256" }, ...] }` in the supplied order. No upload has happened yet.
3. For each descriptor, call `item_templates_prepare_file_upload({ id, file_name, size, sha256 })`. Retain each returned `{ upload: { upload_url, upload_token, expires_at } }` paired with its exact local file and descriptor. Preparation checks ownership; the authorization expires after 30 minutes and is bound to the product and exact file bytes. Prepare files shortly before transfer.
4. Pass this JSON plan programmatically through stdin to `node upload-materials.mjs transfer -`. The following describes its structure; use the real descriptor and preparation response, never placeholder values:

```json
{
  "id": 123,
  "files": [
    {
      "path": "/local/book.pdf",
      "metadata": { "file_name": "book.pdf", "size": 1234, "sha256": "computed SHA-256" },
      "upload": { "upload_url": "returned URL", "upload_token": "returned token", "expires_at": "returned expiry" }
    }
  ]
}
```

The helper also accepts `transfer PLAN.json`; keep any temporary plan private with mode `0600`, never commit or print it, and delete it after use. It streams a raw HTTPS POST with backpressure, refuses redirects and unexpected endpoints, and verifies every successful response by independently downloading and hashing the saved bytes. It accepts only the canonical FAPI HTTPS endpoint and the explicit local `https://web.fapi.docker` endpoint. Use the existing trusted CA setup, including `NODE_EXTRA_CA_CERTS` when required; never disable TLS validation.

5. Inspect every ordered result. `verified` means the upload response and downloaded size/SHA-256 match. `failed` means preflight or the server rejected this file. `uploaded_unverified` retains the saved file ID but needs download verification. `unknown` means the transfer outcome is uncertain. Results retain earlier successes and continue with other files; a nonzero CLI exit status does not mean all files failed. Never automatically retry an uncertain upload: list the product materials first and verify matching candidates to avoid duplicates. Reprepare expired authorizations only after checking whether the previous transfer saved a file.
6. Independently call `item_templates_list_files({ id })` after the transfers. Require each returned uploaded file ID to belong to the intended product with `content_exists: true`; preserve every preexisting material ID. Native storage may sanitize the filename. Use the actual saved ID and returned name, not an invented name or URL. Pass fresh list records and the original local descriptors to `node upload-materials.mjs verify -` with this plan shape:

```json
{
  "id": 123,
  "files": [
    {
      "metadata": { "file_name": "book.pdf", "size": 1234, "sha256": "computed SHA-256" },
      "file": { "id": 456, "item_template_id": 123, "name": "book.pdf", "content_exists": true,
        "download_url": "fresh returned URL", "download_token": "fresh returned token", "expires_at": "fresh returned expiry" }
    }
  ]
}
```

7. Require every requested file's independent verification to pass and compare `item_templates_show` with the original product settings before reporting completion. Report actual saved IDs, verified filenames and per-file failures. Preparation, metadata creation and an HTTP success without byte verification are insufficient. Tokens must never appear in the final report.

Download URLs from these operations require owner-scoped download authorization. They are not public delivery links, do not log in a particular buyer and do not prove payment. Preserve the native paid-product delivery and download checks; do not replace them with these owner verification URLs or change notification settings unless separately requested.

### 7. Verify the result

Call:

```text
item_templates_show({ id: item_template_id })
```

Verify:

* Name and code.
* Price type, amount, currency, and repayment count if relevant.
* VAT and `including_vat`.
* Product type.
* Quantity and stock behavior.
* Periodic settings.
* Descriptions.
* Metadata that was intentionally configured.

Do not consider the task complete from `item_templates_create` or `item_templates_update` success alone.

## Decision table

| User intent | Interpretation | Action |
| --- | --- | --- |
| “Vytvoř produkt e-book za 490 Kč” | Digital publication | Use default/account currency if needed, type `electronic-publication`, one-time price. |
| “Online kurz za 1990 Kč” | Digital service/course | Type `electronic-service`, one-time price. |
| “Konzultace na hodinu” | Service | Type `service`, consider `count: 1`, no stock. |
| “Tričko skladem 50 ks” | Physical good | Type `good`, `enable_stock: true`, `stock: 50`, quantity change likely true. |
| “Měsíční členství” | Recurring product intent | Use `periodic: true`, period such as `1 months` only when confirmed. |
| “Cena na 3 splátky” | Repayment price | Use price `type: repayment` with `repayment_count: 3` only if product-level repayment price is intended. |
| “Produkt pro order bump” | Catalog product for later add-on | Create the product normally; use `fapi-upsell-order-bump` to attach it to a form. |
| “Přidej produkt do formuláře” | Form configuration | Use `fapi-sales-form-create` or `fapi-upsell-order-bump`, not only this skill. |

## Known failure modes

### Duplicate product created

Cause: no exact name/code search before create.

Resolution:

1. Search by code and name first.
2. Inspect likely matches.
3. Ask when candidates are ambiguous.
4. Create only when a new product is intended.

### Price or currency is wrong

Check:

* Account default currency from `settings_list`.
* User-provided currency wording.
* `prices[].currency_code` uppercase ISO code.
* `prices[].type` is `one_time` unless explicit repayment price is required.

### VAT is unsafe

Check:

* Account VAT mode.
* Account default VAT rate.
* User's explicit wording about including/excluding VAT.
* Whether product type implies a tax-sensitive category.

Ask instead of guessing when account defaults do not decide the answer.

### Stock-enabled product fails

Check:

* `stock` is supplied when `enable_stock: true`.
* Product is not used in periodic invoicing.
* Quantity rules do not contradict stock tracking.

### Existing metadata disappears

Cause: `item_templates_update` sent a partial `metadata` object.

Resolution: Inspect current product, merge desired metadata, and send the complete intended metadata object, or omit `metadata` entirely.

## Output

Return in the user's language using only applicable sections:

```markdown
## Produkt vytvořen

**Název:** …
**Kód:** …
**Cena:** …
**Typ:** …

## Ověření

- …

## Zbývá ověřit ručně

- …
```

Mention `item_template_id` when the next step needs it for a sales form, invoice, order bump, or upsell.

## Examples

### Simple digital course

**Request**

> Vytvoř produkt Online kurz produktivity za 1990 Kč.

**Procedure**

1. Read account defaults.
2. Search existing products by exact name.
3. Create a one-time CZK `electronic-service` product.
4. Verify with `item_templates_show`.

### Physical product with stock

**Request**

> Přidej tričko FAPI, 399 Kč, máme 120 kusů skladem.

**Procedure**

1. Read account defaults.
2. Search duplicates.
3. Create a `good` with stock tracking and quantity-change behavior.
4. Verify stock and type.

## Resources

Load resources only when needed:

* `references/product-fields.md` — Read before composing `item_templates_create` or `item_templates_update`.
* `references/scenario-recipes.md` — Read for physical goods, recurring products, repayment prices, multi-currency products, Buddy, affiliate, Pohoda, or custom metadata.
* `references/sources.md` — Read when provenance, MCP/API precedence, or recently changed behavior matters.
* `scripts/upload-materials.mjs` — Compute local descriptors, transfer authorized material bytes, and verify fresh material readback on supported local clients.

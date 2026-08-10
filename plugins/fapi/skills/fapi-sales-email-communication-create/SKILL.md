---
name: fapi-sales-email-communication-create
description: >-
    Use this skill when the user wants Fapilot to create, prepare, or customize
    an email communication set for a FAPI sales form, product sale, order flow, or
    post-payment delivery. Trigger for requests such as e-mailova komunikace,
    sada e-mailu, e-maily k prodejnimu formulari, e-maily po objednani,
    e-maily po zaplaceni, or prodejni e-maily.
---

# Create sales email communication

## Purpose

Create a dedicated customer email communication set for a FAPI sales form. The workflow starts from FAPI default message templates, then rewrites the order-created and paid email templates so the buyer gets clear payment, order, and delivery instructions.

Use this skill for:

- Creating a message template set for a sales form.
- Rewriting the email sent after ordering.
- Rewriting the email sent after payment.
- Preparing email content before assigning the message template set to a form.
- Customizing buyer communication for ebooks, memberships, accesses, consultations, services, or mixed offers.

Do not use this skill for:

- Creating the sales form itself; use `fapi-sales-form-create`.
- Creating products; use `fapi-product-create`.
- Setting payment reminders only; use `fapi-default-notification-templates`.
- Sending one-off invoices; use `fapi-invoice-create`.
- Editing a shared/default message template set unless the user explicitly asks and confirms the risk.

## Domain model

### Message template set

A message template set is the group of transactional email and SMS templates that can be assigned to a sales form. A custom sales communication should normally use its own message template set so one form's buyer communication does not change other forms.

### Message template

A message template is one email or SMS inside a set. This skill updates only the templates needed for the sales communication, especially the order-created email and the paid email. Preserve unrelated templates in the same set.

### Default notification templates

Default templates are the safe starting point for events, fields, and supported placeholders. Use `fapi-default-notification-templates` as the supporting workflow for default template rules, reminder rules, and placeholder safety.

## Operating rules

Call `notification_reference_show` before composing or changing any message template body, subject, event, type, or automatic charge event.

Read every returned `placeholder_groups` category before drafting copy. This catalog is the complete source of truth for supported placeholders in message templates and reminders; choose only exact returned syntax and use each description to confirm its meaning.

Create a new dedicated set with `message_template_sets_create` and `createDefaultMessageTemplates: true` when the user asks for sales-form-specific or product-specific email communication.

Do not invent placeholders. Use only placeholders returned in `notification_reference_show.placeholder_groups`, concrete dynamic IDs returned by another FAPI tool for parameterized syntax such as `{file:<id>}` or `{customField:<id>}`, or custom placeholders explicitly supplied by the user for an endpoint that accepts them.

Never hardcode order-specific values in email text. Order totals, due dates, product lists, variable symbols, bank account details, IBAN, SWIFT, and order overview links must use placeholders.

Concrete fulfillment URLs supplied by the seller, such as ebook download pages, membership login pages, or consultation booking links, may be written as literal URLs because they are not order-specific values.

When one email serves a mixed offer and some delivery content belongs only to an optional product, wrap that content in the product-conditional syntax returned by `notification_reference_show`: `{item-<item_code>}...{/item-<item_code>}`. Resolve the product with `item_templates_list` and confirm it with `item_templates_show`. Use its non-empty `code` in both tags; matching ignores letter case, but preserving the returned spelling prevents mistakes. Do not use an item template ID, invoice item ID, form item ID, miniupsell row ID, or guessed code, and do not nest product-conditional blocks. If the product has no code, update it with a unique code before using a conditional block.

## Procedure

### 1. Understand the sale

Determine from the user's request and available tools:

- Sales form or product name.
- What is being sold.
- Whether the offer is an ebook, electronic product, membership, access, consultation, service, physical product, or mixed package.
- Payment methods, especially whether bank transfer is allowed.
- Delivery links, access expectations, or follow-up instructions.
- Seller greeting and signature.

Infer a set name when absent, for example `<product or form name>`. Do not block creation only because the user did not provide a set name.

Ask one focused question only when a required business fact is missing and cannot be safely derived, for example:

- The product or sales form is unclear.
- An ebook or electronic product has no delivery link or attachment instructions.
- A consultation offer has no booking link or clear next step.
- A membership/access product has no clear access flow.
- The seller signature is missing and no account/template source exposes it.

### 2. Retrieve default references

Use `fapi-default-notification-templates` for the default-template workflow.

Call `notification_reference_show` before writing copy. Use:

- `source: "defaults"` to inspect default template examples and placeholder usage.
- `source: "account"` when current account sets are needed to avoid duplicates or reuse explicit user-selected templates.

Inspect existing message template sets with `message_template_sets_list` before creating a new one. Reuse a set only when it clearly belongs to the same form/product and the user intended that set. Otherwise create a new set.

### 3. Create the sales email set

Create a dedicated set:

- Tool: `message_template_sets_create`
- Required fields:
    - `name`: `<product or form name>` or another descriptive user-provided name.
    - `createDefaultMessageTemplates`: `true`

After creation, call `message_template_sets_show` with the new ID. Use the returned templates to identify:

- the order-created email template,
- the paid email template.

Identify templates by event, name, and default reference. Do not guess template IDs.

### 4. Rewrite the order-created email

The order-created email should help the buyer finish payment and find the order summary.

Include:

- Greeting.
- Confirmation that the order was created.
- Link to the order overview page using a valid placeholder.
- Purchased products using valid placeholders.
- Total amount using a valid placeholder.
- Due date using a valid placeholder.
- Seller greeting and signature.

When bank transfer is allowed, include payment instructions with valid placeholders for:

- bank account,
- IBAN,
- SWIFT,
- variable symbol,
- total amount.

When the user says the form should use card-only payment, omit bank account, IBAN, SWIFT, variable-symbol payment instructions, and bank-transfer wording.

### 5. Rewrite the paid email

The paid email should confirm payment and explain what the customer receives next.

Include:

- Thank-you text for payment.
- Purchased products or product summary using valid placeholders where possible.
- Clear delivery or next-step instructions.
- Seller greeting and signature.

For an optional ebook, miniupsell, order bump, or other add-on, wrap only that product's delivery instructions and links in its verified `{item-CODE}...{/item-CODE}` block. Keep shared confirmation text outside the block.

Apply product-specific rules:

| Sale type                    | Required paid-email content                                                                                                 |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Ebook or electronic product  | Include the seller-provided download URL, file placeholder, or delivery instructions.                                       |
| Membership or access product | Explain that access details will arrive in a separate email. Ask the buyer to check the inbox, bulk mail, and spam folders. |
| Consultation                 | Include the seller-provided consultation booking link or next-step instructions.                                            |
| Service                      | Explain the next step agreed by the seller, such as scheduling, onboarding, or contact.                                     |
| Physical product             | Mention delivery or shipping expectations only when the seller provided them or they are available from the form context.   |

If the needed delivery information is missing, ask for it before writing the paid email.

### 6. Update and verify templates

Update only the identified email templates:

- Tool: `message_templates_update`
- Update `subject` and `body` when changing an email template.
- Preserve existing event, type, automatic charge event, set assignment, and files unless the change requires them.

After every update, verify with `message_templates_show` when checking one template is enough, or `message_template_sets_show` when checking the whole set. Before reporting success, call `message_template_sets_show` for the final set.

## Placeholder discipline

Do not write unsupported placeholder names into the email body. If a useful placeholder is not present in `notification_reference_show.placeholder_groups`, do not use it unless the user explicitly supplied a custom placeholder for an endpoint that supports custom key-value substitutions.

Treat product-conditional blocks listed in `notification_reference_show` as supported control syntax. They are not replaced with a value; FAPI either keeps or removes their enclosed content based on the ordered products.

When a required dynamic value has no available placeholder:

1. Do not hardcode the value.
2. Ask the user or report that the value cannot be safely inserted automatically.
3. Keep the email useful with the available supported placeholders.

Examples of values that must remain dynamic:

- order overview URL,
- invoice/order number,
- product list,
- total amount,
- due date,
- variable symbol,
- bank account,
- IBAN,
- SWIFT,
- customer name or email.

## Safety checks

Ask before writing only when:

- Multiple existing sets could plausibly be the intended target.
- The user asks to edit a default or shared set.
- Required delivery or signature information is missing.
- A required placeholder needs a concrete dynamic ID that no tool result exposes.
- The requested communication would contradict the configured payment methods.

Otherwise choose the smallest safe write, verify it, and report the result.

## Output

After the workflow, return:

- Created or reused message template set ID and name.
- Updated order-created email template ID.
- Updated paid email template ID.
- Whether bank-transfer details were included or omitted.
- Any assumptions used.
- Missing delivery items that still need seller input.
- The exact message template set ID to assign to the sales form.

Do not claim that emails were changed unless the update and verification tools succeeded.

## Examples

### Example: ebook with bank transfer and card payment

**Request**

> Vytvor mi e-mailovou komunikaci pro formular Kurz copywritingu. Prodava se ebook, odkaz je https://example.com/ebook.pdf. Platba kartou i prevodem. Podpis Jana Novakova.

**Procedure**

1. Call `notification_reference_show`.
2. Check existing sets with `message_template_sets_list`.
3. Create `E-maily - Kurz copywritingu` with `createDefaultMessageTemplates: true`.
4. Show the set and identify order-created and paid email templates.
5. Update the order-created email with order overview, product list, amount, due date, variable symbol, bank details, and seller signature using valid placeholders.
6. Update the paid email with thanks, product summary, ebook link, and seller signature.
7. Verify the final set.

**Expected result**

The final report includes the message template set ID and both updated template IDs.

### Example: card-only membership

**Request**

> Priprav e-maily k prodeji clenske sekce Akademie. Chci jen platbu kartou. Pristupy chodi automaticky separatnim e-mailem. Podepsat jako tym Akademie.

**Procedure**

1. Create a dedicated default-based message template set.
2. Omit bank account, IBAN, SWIFT, and bank-transfer variable-symbol payment instructions from the order-created email.
3. In the paid email, tell the buyer that access details arrive separately and to check inbox, bulk mail, and spam.
4. Verify the final set.

**Expected result**

The order-created email does not contain bank-transfer instructions, and the paid email prepares the buyer for a separate access email.

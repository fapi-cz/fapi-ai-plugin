---
name: fapi-default-notification-templates
description: >-
    Use this skill when Fapilot needs default FAPI notification templates,
    message template sets, message templates, reminder sets, reminders, valid
    events, valid message fields, placeholder usage, or safe default templates
    before another workflow rewrites them.
---

# Work with default FAPI notification templates

## Purpose

Inspect, create, and adjust default-based FAPI notification templates without breaking shared defaults or inventing unsupported placeholders.

Use this skill for:

- Creating a default-based message template set or reminder set.
- Creating or updating individual message templates or reminders when another skill needs the low-level template workflow.
- Choosing valid message template events, invoice types, automatic charge events, and placeholders.
- Preparing safe default templates before a specialized skill rewrites them.

Do not use this skill for:

- Creating sales email communication for a product or sales form; use `fapi-sales-email-communication-create`.
- Creating the sales form itself; use `fapi-sales-form-create`.
- Creating products; use `fapi-product-create`.
- Sending one-off invoices; use `fapi-invoice-create`.
- Deleting templates or sets unless the user explicitly asks and confirms the risk.

## Operating rules

Call `notification_reference_show` before composing or changing any template body, reminder body, event, type, or automatic charge event. Use `source: "account"` for current account sets and `source: "defaults"` for repo-defined default message templates and reminders.

Treat `notification_reference_show.placeholder_groups` as the complete source of truth for supported message-template and reminder placeholders. Select placeholders by their exact returned `syntax`; use the accompanying description to choose the intended value. Do not infer availability only from the placeholders that happen to occur in fetched default or account templates.

Prefer an individual message template set and reminder set per sales form when the user wants custom communication. In most FAPI setups, each sales form has its own email/reminder setup or inherits a deliberate default.

Do not edit a shared/default set when the user only asks for one form to behave differently. Create a new set from defaults, customize it, and return the new IDs for assignment to the form.

Do not invent placeholders. Use placeholders returned in `placeholder_groups`, concrete dynamic IDs returned by another FAPI tool for parameterized syntax such as `{file:<id>}` or `{customField:<id>}`, or custom placeholders explicitly supplied by the user for an endpoint that accepts them.

Product-conditional email blocks returned by `notification_reference_show` are supported template syntax, not ordinary value placeholders. Use `{item-<item_code>}...{/item-<item_code>}` to keep the enclosed content only when the order contains that product code. Resolve the exact product with `item_templates_list` and `item_templates_show`, use its non-empty `code` in both tags, and preserve the returned spelling even though matching ignores letter case. Never substitute an item template ID, invoice item ID, form item ID, or guessed code, and do not nest product-conditional blocks.

When a specialized skill needs sales-specific customer communication, this skill should supply the default set creation and placeholder/event reference rules. The specialized skill owns the business content and final workflow.

## Procedure

1. Determine whether the request changes message templates, reminders, or both.
2. Call `notification_reference_show`.
3. Read all returned `placeholder_groups` before drafting content and retain the exact syntax of selected placeholders.
4. Inspect existing sets:
    - `message_template_sets_list` for message template sets.
    - `message_template_sets_show` when you need nested message templates.
    - `reminder_sets_list` for reminder sets.
    - `reminder_sets_show` when you need nested reminders.
5. Reuse a matching dedicated set only when the name and intended form/context match clearly.
6. Create a new message template set with `createDefaultMessageTemplates: true` when customizing the normal FAPI customer emails from a safe starting point.
7. Create a new reminder set with `createDefaultReminders: true` when customizing payment reminders from a safe starting point.
8. Update cloned templates/reminders by ID. Preserve unrelated templates inside the same set.
9. Verify every write with the corresponding `show` or `list` tool.
10. Return changed IDs, names, and the exact assignment IDs the caller should use on the sales form.

## Message templates

Use:

- `message_template_sets_create`, `message_template_sets_show`, `message_template_sets_update`.
- `message_templates_create`, `message_templates_show`, `message_templates_update`.

Field rules:

- `event` should be copied from a matching existing template returned by `notification_reference_show` when possible.
- `type` is only for `issued_invoice` and `issued_invoice_sms`.
- `automaticChargeEvent` is only for `automatic_charge` and `automatic_charge_sms`.
- Email templates should include `subject` and `body`.
- SMS templates should use a short `body`; do not rely on email-only formatting.
- Attached file placeholders use `{file:<id>}` with a concrete file ID.
- Product-conditional email content uses `{item-EBOOK}...{/item-EBOOK}`, where `EBOOK` is the verified product code. Both tags must identify the same code; matching is case-insensitive.

## Reminders

Use:

- `reminder_sets_create`, `reminder_sets_show`, `reminder_sets_update`.
- `reminders_create`, `reminders_show`, `reminders_update`.

Field rules:

- `daysOverdue` is relative to due date.
- Negative `daysOverdue` sends before due date.
- `0` sends on the due date.
- Positive `daysOverdue` sends after due date.
- Set at least one of `email`, `sms`, or `support` according to the user's intent.
- Use `supportEmail` only for support notifications.
- Use `subject` when an email notification is enabled.

## Safety checks

Ask one focused question before writing only when:

- Multiple existing sets could plausibly be the intended target.
- The user asks to edit or delete a default/shared set.
- Required content is missing and cannot be derived from the request.
- A placeholder needs a concrete dynamic ID that no tool result exposes.

Otherwise choose the smallest safe write, verify it, and report the result.

# Email templates for client communication

Use this before `message_template_sets_create` or `message_template_sets_update`.

## Rules

1. Every message template set should be named after sales form or product that is selling.
2. Every message template set should have base templates for all events that are relevant to the product or sales form. So the minimum are types: "issued_order", "paid_order".
3. If user tels you to create custom message templates in message template set. Then you create new message template in message template set with type "custom". And this custom message template can be used in sales form automation. But you should not create custom message templates in empty message template set.
4. For custom symbols, use MCP notification_reference_show.placeholder_groups that will provide you with all available placeholders for message templates. Do not invent placeholders. 
5. Do not invent new placeholders. Use placeholders returned in `placeholder_groups`, concrete dynamic IDs returned by another FAPI tool for parameterized syntax such as `{file:<id>}` or `{customField:<id>}`, or custom placeholders explicitly supplied by the user for an endpoint that accepts them.

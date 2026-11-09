# Sales-page design in FAPI

Adapted from Super's site-agent design workflow. The palette data and critique principles originate in tasteskill v2 by Leon Lin and blueemi; see its [MIT notice](LICENSE-tasteskill). This workflow uses FAPI's structured page tools.

## Establish the offer and choose a direction

Use the request, existing page, owned product and form to establish what is sold, to whom, the useful outcome, what the buyer receives, the known price and terms, and the next action. Ask only for a missing fact that blocks the requested result. An unknown price or delivery term stays unknown; a draft must identify an unfinished checkout. Do not turn ordinary expectations about the industry into facts about this seller.

Inventory the details that distinguish this offer: the actual product, a particular teaching method, supplied examples, the author's experience, a place, material, format or constraint. Make one of these carry the composition. Write the idea in a sentence: “On this page, [a real detail of this offer] becomes [the organizing device].” If replacing the seller's name with a competitor's leaves the idea unchanged, find a more specific detail. When the brief is sparse, use a clear factual design rather than inventing a story.

Consider a few different compositions from the table below and choose the one that serves the offer and its available images. Decide its palette, heading/body fonts, first-screen focal point, section rhythm and primary action together. Carry that decision through the offer, FAQ and closing section. Changing only the colors of the starter template is not a complete design.

When the user requests alternatives, make them different in composition as well as palette. Five looks can span two light, two colored and one dark ground, with distinct compositions and palettes; adapt that spread to the user's brand and requested count. Do not create extra persistent pages merely to describe options. If actual page variants are requested, give each a distinct name and preserve the same verified offer and form reference.

## Composition library

These are layout ideas expressed with existing components. Each row describes an FAPI adaptation, including where the original effect is unavailable. Choose for the subject rather than routinely taking the first row.

| Direction | Fits | Composition in FAPI |
| --- | --- | --- |
| Name as a monument | A short, recognizable product or event name | One dominant Heading, compact explanation and action, then quieter sections. Keep the name readable on a phone. |
| Color chapters | A lively course, event or consumer offer | Successive Section backgrounds from one palette's field pairs; give each chapter real substance. |
| Loud flat poster | A launch, music, sport or a direct voice | A saturated field, short large heading and one strong image. Keep images and text in normal flow. |
| The place carries it | A retreat, venue or workshop | Lead with a real supplied place image and concrete practical details; put the title beside or below the image. |
| The page is the object | A menu, ticket, program or physical product | Let the actual object's organization shape the headings, lists and image sequence. Keep checkout recognizable. |
| One motif | An offer with a recognizable material or shape | Repeat a real product detail in supplied images or a purposeful Line treatment. No invented decorative blobs. |
| Quiet instrument | A precise professional or technical offer | One clear reading column, concrete examples and a restrained action. Use scale and complete content to avoid emptiness. |
| Printed annual | Research, expertise or a substantial B2B offer | A strong title, report-like sections and verified facts; use background fields rather than decorative rules. |
| Split stage | A person, craft or considered service | A two-column Section with a portrait/product and its explanation. It stacks on mobile; neither side is sticky. |
| Well-kept board | Several distinct deliverables or related products | Compact two- or three-column Sections with useful text and images. Columns share the section background; there is no card container. |
| Uneven photographs | A visual craft, portfolio or interior | Alternate supported Image widths and column proportions while retaining shared edges and natural aspect ratios. |
| Dark room | A visual premium product | Dark Section fields, explicitly light Heading/Text, one well-lit image at a time. Keep components with fixed dark text on a light field. |
| Type and nothing else | A strong promise with few suitable images | A typographic opening, specific prose, a clear offer and action. Omit decorative stock photography. |
| Pinned poster | A memorable name and strong photographs | Repeat the name as a static visual anchor among image sections. Pinning and scroll effects are unavailable. |
| Sentence as layout | One concrete claim or useful outcome | A short first-screen statement, then Sections pairing a Heading with its evidence or explanation. |
| The object, large | A tangible product or a demonstrable result | One dominant Image with useful detail sections. Keep the headline outside it; no overlaps or invented cropping controls. |
| Specimen catalogue | Several real items or curriculum modules | A consistent sequence of images, names and factual descriptions; use section fields for grouping. |
| Stacked cards | A course, process or distinct offer stages | Successive flat Section bands. They remain in normal document flow rather than sliding over one another. |
| The letter | A personal service or founder-led offer | First-person copy in a calm column with a real signature/name and a direct action, when that voice fits the request. |
| The chronicle | A meaningful timeline or program | Ordered Text lists or successive factual stages, with dates only when supplied. No decorative vertical timeline component. |
| Magazine cover | A visual story or lifestyle offer | One strong image, a clear title and a few useful previews of the content, kept in normal flow. |
| Zigzag | Several concrete benefits supported by images | Alternate two-column image/text Sections. Below 768px they stack in slot order; verify that reading order. |
| Spotlight | A product or experience that needs attention | A sequence of dominant images followed by short explanatory text, with deliberate changes of scale. |

## Write a complete offer

The first screen needs a clear title, a short sentence saying what this is and who it helps, and an action naming the next step. A short title often survives mobile better; preserve exact requested wording and check its actual line breaks instead of imposing a word limit.

Build the rest from what the buyer needs to decide: the problem or desired outcome, what they receive, how it works, a relevant example or genuine proof, price and terms when known, checkout, and useful objections or FAQ. Use only the sections justified by this offer. Do not manufacture testimonials, statistics, discounts, urgency, guarantees or a row of placeholder facts to fill a recipe.

Vary the composition where the content benefits: a split image/text section, a short factual list, a field of color, a single-column explanation, a Faq and the checkout. Avoid repeating the same equal-column layout throughout. Prefer concrete nouns and supplied details over generic promises, small label badges and category slogans. Use the number of items the content actually has.

Use real seller images, an available authorized image tool or accessible verified image URLs. Stock photos may illustrate a subject but cannot stand in for this seller's product, customers or results. Never invent image URLs or leave image-search tokens in a saved complete page. If no suitable image is available, choose a composition that works without one.

Resolve the owned form and verify its offer before embedding FapiForm. Point in-page checkout actions at the actual ID of the Section containing FapiForm, commonly `#objednavka`. Keep repeated actions pointed at that checkout or the intended real destination. Do not change the form's configuration while styling the page.

## Apply the visual system through supported properties

Preserve the user's brand or follow measured reference values. Otherwise consult [the palette library](design-palettes.md) and choose a palette for the subject. Treat colors as roles: ground for most sections, surface for a quiet grouping, ink for text, accent/accent ink for the action, and optional field/ink pairs for whole chapters. Check contrast for each actual foreground/background pairing, including button labels and links; target at least 4.5:1 for ordinary text. Palette membership alone does not prove readability.

Choose at most two typefaces from the current tool enum. The upstream library's font names do not establish FAPI support. These supported pairs are starting choices, not exact substitutes for upstream fonts:

| Character | Heading | Body |
| --- | --- | --- |
| Direct, factual | Inter | Inter |
| Bold, geometric | Montserrat | Open Sans |
| Warm, contemporary | DM Sans | DM Sans |
| Editorial | Playfair Display | Source Sans 3 |
| Substantial, practical | Roboto Slab | Roboto |
| Friendly, clear | Poppins | Lato |

Map decisions to the schema:

- Set whole-block `font_family` on Heading/Text and, where needed, Button. Use a safe `span` with `text_format: "html"` for Heading/Text color or font size; preserve inline formatting and semantic heading levels. There is no root font or root text-color property.
- Use Section `background` for flat fields and its supported padding for space. Explicit padding applies on mobile too; omitted section padding retains the renderer's responsive defaults. There is no section max-width, viewport height, column-gap or breakpoint-specific property.
- Use `columns`, `column_widths`, the existing slots and their padding for composition. A blank column is not a spacer. Keep the meaningful mobile reading order in slot order.
- Keep body text comfortable to read and establish a clear jump to the main heading. Avoid applying enormous fixed rich-text sizes or desktop padding that crowd a phone. Do not add unsupported tracking, line-height, weight or responsive CSS properties.
- Give Button the chosen `background`, `color`, `size` and a deliberate `border_radius` when changing its style. Flat, square or fully round buttons are useful starting choices; an existing requested radius takes precedence.
- Use Image `width` within its supported limits and preserve its natural aspect ratio. Cropping, image overlays, background images, absolute positioning and animation are unavailable as component properties.
- Set Heading/Text ink explicitly on dark or colored fields. Faq has no question-color property; put it and any other fixed-style component on a field where its actual render stays readable. Check the embedded form's own appearance separately.

For an open-ended design, start with flat colors, one clear focal point, shared edges and purposeful images. Avoid defaulting to gradients, resting shadows, glass, decorative hairlines, emoji icons, labels above every heading or identical feature tiles. Replace weak decoration with useful content, scale or a field of color. Preserve decorations the user explicitly requested and do not remove content to make a page look restrained.

Stay within the available component contract. Do not add CustomHtml, arbitrary CSS keys, external font loaders, or code in header/footer settings to reproduce a missing visual effect. Preserve supplied settings and tracking. Explain an unsupported effect and use an honest supported adaptation.

## Review the actual draft

After saving and reading back, inspect the edited page through an available authorized preview/browser tool, at a desktop width and about 390px, with the full page when the whole design changed. A stored document proves content, not appearance. `inspect_page_reference` inspects public reference websites; it does not grant access to a private FAPI draft. Do not publish a page or send private content to a public inspection service to obtain a screenshot. If the current environment cannot inspect the private draft, report visual verification as unavailable.

Judge the rendered page rather than the properties you intended:

1. In five seconds, can a stranger tell what is sold, for whom and what to do next? Is one thing visually dominant?
2. Does the design belong to this actual offer? Does its idea continue beyond the hero?
3. Are edges shared, outer margins balanced, and related content close together? Are there empty half-sections or excessive gaps?
4. Are heading line breaks readable, body text comfortable and ink/button contrast sufficient? Is any text clipped or covered?
5. Do images show something useful without stretching? Are successive sections varied for a reason, with enough concrete content?
6. On the phone, do columns read in the right order without horizontal overflow? Are actions usable and the checkout and FAQ readable?
7. Does every intended CTA target exist, and is the real form still embedded? Are any placeholders or missing facts honestly identified?

Fix the most consequential visible problems first: hierarchy, composition, typography, color, imagery, then detail. Preview again after a visible fix; stop when the requested result is sound rather than polishing indefinitely. A review-only request returns findings without applying fixes. Never claim screenshot verification or a successful purchase that you did not observe.

Report the chosen direction and concrete changes briefly in the user's language, link the editor, identify unfinished facts or unavailable checks, and state the draft/publication state. Follow the parent skill's revision and publication workflow.

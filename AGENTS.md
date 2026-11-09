# Maintained FAPI skills

`plugins/fapi/skills/` is the authoritative source of customer-facing skills. Update the owning skill and any references or related skills that govern the same decision; changing the Fapilot prompt alone does not update hosted skills. Preserve explicit exceptions such as audit-only requests and product-only tasks.

## OpenAI publication

The standard release path is `.github/workflows/publish-openai-skills.yml`: pull requests run offline checks; pushes to `main` and manual runs on `main` publish through the existing synchronizer and verify the hosted content. A merged skill change should reach Fapilot through this GitHub run without another local upload. Repair or configure this pipeline when it is missing or failing; do not substitute a manual release unless the user explicitly requests that exception.

Keep existing skill IDs; `ansible/skills.json` records the IDs already registered in Fapilot. Never delete or recreate a skill just to update its content. Store the release credential only in the GitHub secret `OPENAI_API_KEY`, with optional project/organization selectors in repository variables. Do not put API keys in source, reports, or command arguments.

The workflow serializes releases, checks current `main` before writing, compares before publication, and requires a final comparison without differences. Inspect `fapi_pr_required` in its summary. Keep tests and PR runs offline, without publication credentials. Source edits and PR creation alone do not publish; a successful release run must verify the uploaded bundles. Preserve explicit source-only or no-release requests.

For an explicitly requested local exception, use `ansible/sync-openai-skills.yml` or the FAPI release helper, which share `scripts/sync_openai_skills.py`. Keep its check-before-write and readback verification. Never implement another upload client or blindly retry an ambiguous write.

## Every genuinely new skill needs a Fapilot PR

Adding a new skill is incomplete until a companion PR exists in `fapi-cz/fapi` so Fapilot can load it:

1. Maintain and validate the skill here. Publish it only through an authorized synchronization to obtain its real `skill_*` ID; never invent an ID.
2. Create the companion FAPI PR that adds this ID to `OPENAI_SKILL_IDS` in `agent/src/agent/FapilotAgent.ts` and updates the corresponding hosted-skill registration test in `agent/src/agent/FapilotAgent.test.ts`. Preserve existing entries and access restrictions.
3. Link both PRs and follow the FAPI repository's development rules. Record the verified ID in `ansible/skills.json` only after the FAPI registration PR is merged; until then keep `fapi_pr_required` pending.
4. Keep source publication, OpenAI publication, FAPI PR creation/merge, and actual loading distinct in the handoff. A newly uploaded skill is not automatically registered by Fapilot.

Restoring source for an already-hosted and already-registered skill preserves its existing ID and does not need a duplicate registration. Changes to an existing skill publish a new version under the same ID; Fapilot references `latest`.

## Verification

Validate changed skills and local reference paths, matching versions in both plugin manifests, and `git diff --check`. For the synchronizer run `python3 -m unittest discover -s tests`, Ansible syntax check, and check mode without writes when authorized. Keep changes on a reviewable branch; never publish directly to the default branch or merge/deploy without authorization.

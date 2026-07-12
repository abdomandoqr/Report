---
name: onboard-client
description: Convert the Database Reactivation Workflow from single-client to multi-tenant parameterized (one-time only), and onboard a new client (fashion/gym/dental/coaching) from discovery-call notes (Fireflies) plus intake-form answers, without rebuilding any existing logic.
whenToUse: Use when adding any new client (the first one or the tenth) to the system, or when asked to "onboard a client" or "set up a new client."
arguments:
  - fireflies_transcript_or_summary
  - intake_form_answers
---

# Onboard Client — Database Reactivation Workflow

## Operational Sequence (execute in this exact order)

**Step 0 — mandatory before anything else:**
If `fireflies_transcript_or_summary` and `intake_form_answers` were not provided with the
command, **ask the user for them immediately and stop.** Do not write a plan, do not inspect
code, do not assume anything about the client's identity before receiving them. This is the
first operational step, not a deferred detail.

**Step 1 — idempotency check (is this the first run, or a new client on an existing setup?):**
Check whether a `core/` directory and a `clients/` directory already exist in the repo.
- **If they do not exist (first run)** → execute the full "Architectural Conversion Plan"
  (section below) first, then continue to onboarding the first client in the same session.
- **If they already exist (second client or later)** → **skip the architectural conversion
  plan entirely** and do not propose rebuilding or modifying it. Go directly to the "Onboard
  New Client" section below.

This check is mandatory on every invocation of this skill, even if it feels repetitive.

**Step 2 — mandatory critical fixes (always run, regardless of first run or later client):**
Before any actual client onboarding, inspect `tools/generate_offer.py` and fix the following
three issues if still present (confirmed by direct code inspection at the time this skill was
written):

1. Add `import time` at the top of the file (currently missing, but `time.sleep(2)` is used
   in the rate-limit retry path — without it, a `NameError` will occur and stop any real
   retry).
2. Fix `extype(exc)` to `type(exc).__name__` in the generic `except Exception` handler (a
   typo that crashes the error handler itself and hides the real error).
3. Update the model names to the current, confirmed values from Anthropic's official
   documentation:
   - `MODEL_INFORMATIONAL = "claude-3-haiku-20240307"` → `"claude-haiku-4-5-20251001"`
   - `MODEL_BONUS_DISCOUNT = "claude-3-sonnet-20240229"` → `"claude-sonnet-4-6"`

Then, **scoped-only** audit the remaining files in `tools/` (`send_email.py`,
`send_instagram_dm.py`, `fetch_customers.py`, `log_action.py`) for the same three bug
patterns only — do NOT perform a full code review:
- missing imports for modules actually used in the file (e.g. `time`, `re`, `datetime`)
- typos inside exception handlers (undefined names, wrong function calls)
- hardcoded outdated/deprecated Claude model strings

For each file, report findings before fixing, and apply the same fix pattern used above.
If a file has none of these three patterns, say so explicitly and move on — do not expand
the scope into a general refactor or style review.

Show the resulting diff to the user before applying it in all cases, and do not assume the
rest of any file is exactly as described here — open and verify first (contents may have
changed since this skill was written).

## Your Role
You are an architect for small Python systems, not just a code executor.
When executing the architectural conversion plan (first run only), you must produce a
detailed, precise implementation plan before touching any actual code, and you must not
begin implementation until the user approves the plan in writing.
When onboarding a client on an already-existing setup, this constraint does not apply —
execution is direct, because it is a repeatable, low-risk operation (creating a folder and
an env file only, no changes to `core/`).

## Confirmed Context (from direct code inspection, not assumptions)

- **The single source of truth is the repo root** — it already contains a full agentic
  layer: `planner.py` (`decide_plan`), `guardrail.py` (`validate_offer`), `state.py`
  (state machine), and `main.py`, which unifies demo/production logic in a single
  `_run_campaign()`.
- **`project/` is a stale copy** — do not use it as a reference; it is a candidate for
  deletion later (not a priority right now).
- **`Report/`** is a completely unrelated project (an old AI-readiness report) — ignore it
  entirely.
- **`reactivation-package/`** has not been inspected yet — it does not affect this skill;
  leave it as a later cleanup note.
- `config.py` is already partially parameterized: `BUSINESS_TYPE`, `CAMPAIGN_LANGUAGE`,
  `CHURN_THRESHOLD_INFO/BONUS/DISCOUNT`, `DISCOUNT_PCT`, `GOOGLE_SHEET_ID`,
  `CUSTOMERS_CSV_PATH`.
- Prompt templates: `tools/prompts/base.md` plus industry add-ons `gym.md`, `dental.md`,
  `coaching.md`, `fashion.md`.
- **Confirmed bug (narrow scope):** `main.py` has `choices=["gym", "dental", "coaching"]` —
  `"fashion"` is missing even though `fashion.md` already exists. **Confirmed that
  `tools/generate_offer.py` does NOT have the same problem** — `_load_prompt_template()`
  loads the prompt file dynamically with no closed list, and already supports `fashion`.
  The fix is only needed in `main.py`.
- **Positive finding:** `_mock_offer()` already contains a complete, professionally written
  Egyptian-Arabic copy for fashion offers (discount/bonus/informational) — this part is
  done and needs no extra work.
- Data source = CSV / Google Sheets only. No Shopify or e-commerce platform integration is
  planned or requested — this is a deliberate decision based on the target Egyptian market
  (DTC fashion, COD) relying on Excel/Sheets, not a gap in understanding.
- Production runs via **GitHub Actions daily cron**. The interactive demo on **Modal**
  exists only to show results to a prospective client before purchase — the two serve
  different purposes and do not conflict.

Before writing any plan step, actually open and inspect: `main.py`, `config.py`,
`planner.py`, `guardrail.py`, `state.py`, `tools/generate_offer.py`, and the rest of
`tools/`. If you find any conflict between this context and the actual code, **stop and
ask** before continuing.

## Mandatory Constraints

1. **Time is tight (days, not weeks).** When choosing between a simple fast solution and a
   "perfect" complex one, choose the simple one and state the trade-off explicitly in the
   plan.
2. **No complex multi-tenancy solution is allowed** (database tenant_id, JWT, row-level
   security, Shopify/e-commerce API integration). The system is small; none of this is
   technically justified.
3. **No real client exists yet.** The final test must use a fake/demo client (a fake DTC
   fashion brand with synthetic data), not a real client.
4. **The sale decision is contingent on this test passing.** Before showing the system to
   any real client, you must document an end-to-end test proving:
   - Two clients (at least) can run the same code version at the same time with no data
     interference.
   - The Modal deployment actually respects `--client-dir`, not just locally.

## Target Architecture

```
project/
  core/            ← shared code (planner, guardrail, state, tools) — never changes
  clients/
    _template/     ← empty template (.env.example + empty data/customers.csv with schema)
    {client_name}/
      .env
      data/customers.csv
      .tmp/
  main.py          ← same main.py, takes --client-dir per client
```

### Implementation Details

1. **Add `--client-dir` support to `main.py`.** When passed, the system reads:
   - `.env` from `{client-dir}/` instead of the root.
   - `data/customers.csv` from `{client-dir}/data/customers.csv`.
   - Saves the state file, demo outputs, and logs inside `{client-dir}/.tmp/` instead of
     the root.
   - **If `--client-dir` is not passed**, the system keeps its current exact behavior
     (backward compatible, no breakage to root `.env`/`data/`).

2. **Add a `clients/README.md`** explaining how a new client is created: copy
   `clients/_template/` (containing an empty `.env.example` and an empty
   `data/customers.csv` with the same schema) into `clients/{client_name}/` and edit the
   values.

3. **Fix the `fashion` bug** in `main.py` by adding `"fashion"` to the allowed `choices`
   list.

## Automatic Intake → env Script

The input is **semi-structured text from Fireflies.ai** (transcript + AI summary + action
items), not a fixed-field form. This script combines two sources:

1. **Fireflies export** (full transcript or the call's AI summary, pasted as text or
   exported as a file) — used to extract: business type, approximate data size, the
   primary channel currently in use. Processing remains AI-based extraction from free text
   (not fixed-field parsing), since Fireflies' summary shape varies call to call.
2. **Technical intake-form answers** (`client_intake_template.html`) — used to extract:
   data format (CSV/Sheet/CRM), available channels (email domain/Instagram), language, who
   will run the system, and budget.

Combine both sources, extract the values, and write a fully ready
`clients/{client_name}/.env` — with no manual editing required from the user afterward.

Form-question → `.env`-field mapping:

| Form question | Resulting field |
|---|---|
| Business type | `BUSINESS_TYPE` (gym/dental/coaching/fashion) |
| Message language | `CAMPAIGN_LANGUAGE` |
| Data format | `GOOGLE_SHEET_ID` (empty if CSV) or `CUSTOMERS_CSV_PATH` |
| Available channels | determines which channels are actually enabled (email/instagram) |
| Who runs the system | GitHub Actions cron scheduling, enabled or disabled |
| Budget | max API calls (rate limiting) |

## Final Plan Requirements (first run only — when core/ and clients/ do not exist)

Write the plan in exactly this format, and present it for approval before executing any
step:

1. **Step table** — name, affected files, estimated hours, breakage risk.
2. **Intake → env automation plan** as described above.
3. **Acceptance criteria** — e.g. "Ran main.py with --client-dir for two different clients
   at the same time and got separate, correct results."
4. **Fake-client test plan** — synthetic DTC fashion test data, from filling the form to
   receiving an actual activation message (email first, Instagram optional).
5. **Modal verification plan specifically** — proving multi-client support in practice, not
   just in theory.
6. **Risks and rollback points.**
7. **Priority ordering** if time runs short — what can be deferred without blocking a demo
   to the first client.

Ask any question you need before writing the plan, and if the actual code differs from this
context, stop and ask instead of assuming. After the user approves in writing, proceed
directly to the "Onboard New Client" section below to create the first client folder as
part of the same session.

## Onboard New Client (every invocation, once core/ and clients/ are confirmed to exist)

This is the direct path for every second client and onward — no plan, no additional
approval, because the operation is low-risk (does not touch `core/`):

1. From `fireflies_transcript_or_summary` and `intake_form_answers`, extract the values per
   the mapping table above.
2. Show the user a short summary of the extracted values (client name, BUSINESS_TYPE,
   language, data source) and ask for a quick confirmation only — not a full plan approval.
3. After confirmation: copy `clients/_template/` to `clients/{client_name}/`, write `.env`
   with the extracted values, and set up an empty `data/customers.csv` with the same schema,
   ready to receive the client's real data.
4. Run `python main.py --client-dir clients/{client_name} --demo` to verify there are no
   errors, and show the result to the user.

# CLAUDE.md — Project Context for Claude Code

## Project Overview

This repository contains **two distinct projects**:

1. **Database Reactivation Workflow** (root) — A Python-based automation CLI that identifies dormant customers and sends personalized AI-generated reactivation emails. Designed as a sellable product for SMBs (gyms, dental clinics, coaching businesses) and their marketing agencies.
2. **Link-in-Bio Page Builder** (`link-in-bio-page-builder/`) — A Next.js web application for building customizable link-in-bio pages.

When working on the **Database Reactivation Workflow**, this is the primary context. When working on the **Link-in-Bio Page Builder**, refer to its own `README.md` and `package.json` for conventions.

---

## Tech Stack

### Database Reactivation Workflow (Primary)
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Primary language |
| Anthropic SDK | 0.26.0 | Claude AI for personalized offer generation |
| Resend SDK | 3.0.0 | Email delivery API |
| pandas | 2.2.3 | CSV reading, filtering, datetime handling |
| gspread | 6.1.0 | Google Sheets integration (optional) |
| oauth2client | 4.1.3 | Google OAuth for Sheets API |
| instagrapi | 2.1.0 | Instagram DM fallback (experimental) |
| python-dotenv | 1.0.1 | `.env` file loading |
| GitHub Actions | N/A | Daily scheduled execution (cron at 9 AM UTC) |

### Link-in-Bio Page Builder
| Technology | Purpose |
|---|---|
| Next.js 15 | React framework with App Router |
| TypeScript | Type safety |
| Tailwind CSS 4 | Styling |
| Drizzle ORM | Database (Neon PostgreSQL) |
| Vitest | Unit testing |
| Biome | Linting and formatting |
| Playwright | E2E testing |

---

## Commands

### Database Reactivation Workflow
```bash
# Install dependencies
pip install -r requirements.txt

# Demo mode (no API calls, generates HTML previews)
python main.py --demo

# Production mode (requires --confirm flag)
python main.py --confirm

# Process single customer
python main.py --confirm --customer-id C001

# Override business type or language
python main.py --confirm --business-type dental --language ar

# Run a specific tool standalone
python tools/fetch_customers.py
python tools/generate_offer.py --customer-id C001
python tools/send_email.py        # dry-run test
python tools/send_instagram_dm.py # dry-run test
python tools/log_action.py        # writes test row
```

### Link-in-Bio Page Builder
```bash
cd link-in-bio-page-builder
npm install
npm run dev          # Start dev server
npm run build        # Production build
npm run lint         # Biome check
npm run lint:fix     # Biome check --write
npm run test         # Vitest (watch)
npm run test:run     # Vitest (single run)
npm run test:e2e     # Playwright E2E tests
npm run db:generate  # Drizzle schema migration
npm run db:migrate   # Drizzle apply migrations
npm run db:studio    # Drizzle GUI
```

---

## Project Structure

### Database Reactivation Workflow
```
/
├── main.py                    # Orchestrator: CLI args, demo/prod routing, loop
├── config.py                  # Central config loader (reads .env, provides typed values)
├── .env.example               # Template for all environment variables
├── requirements.txt           # Pinned Python dependencies
├── .github/workflows/
│   └── daily_reactivation.yml # GitHub Actions CI/CD (cron + manual trigger)
├── data/
│   ├── customers.csv          # Sample customer data (or Google Sheets fallback)
│   ├── system_log.csv         # Action audit log
│   └── demo_output/           # .gitkeep placeholder
├── .tmp/demo_emails/          # Demo mode HTML outputs (auto-created, .gitignored)
├── tools/
│   ├── fetch_customers.py     # Data fetcher + filter engine (CSV or Google Sheets)
│   ├── generate_offer.py      # Claude AI prompt assembly + JSON extraction
│   ├── send_email.py          # Resend API integration with HTML generation
│   ├── send_instagram_dm.py   # Instagram DM fallback (instagrapi)
│   ├── log_action.py          # CSV / Google Sheets logging
│   └── prompts/
│       ├── base.md            # Base prompt template (shared structure)
│       ├── gym.md             # Fitness center addendum
│       ├── dental.md          # Dental clinic addendum
│       └── coaching.md        # Coaching business addendum
└── docs/
    └── google_sheets_template.md  # Client onboarding guide
```

### Link-in-Bio Page Builder
```
link-in-bio-page-builder/
├── src/
│   ├── app/                   # Next.js App Router pages
│   ├── components/            # React components (UI + block types)
│   ├── hooks/                 # Custom React hooks
│   ├── lib/                   # Utilities, DB schema, validations
│   ├── types/                 # TypeScript type definitions
│   ├── middleware.ts          # Next.js middleware
│   └── test/                  # Test utilities
├── tests/e2e/                 # Playwright E2E tests
├── drizzle/                   # Migration files
├── public/                    # Static assets
└── .env.local                 # Local environment variables
```

---

## Patterns & Conventions

### Naming
- **Files**: `snake_case.py` for Python modules
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE` (in `config.py`)
- **Classes**: `PascalCase` (rare; only `EmailSender` ABC)

### Import Pattern
Every tool module under `tools/` adds the project root to `sys.path` at the top:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import config
```
This enables running tools standalone without package setup.

### Configuration
- All tunable parameters live in `.env` and are loaded via `config.py`
- `config.is_dry_run()` returns `True` when `ANTHROPIC_API_KEY` or `RESEND_API_KEY` is missing
- CLI overrides (e.g., `--business-type`, `--language`) mutate `config.BUSINESS_TYPE` directly in `main.py`

### Error Handling — Fail-Forward
- One customer failure must never kill the loop
- Log the failure, skip the customer, continue with the next
- Use `try/except` around per-customer operations, print to `sys.stderr`

### Offer Type Logic (Churn Score → Offer Tier)
```python
if score < CHURN_THRESHOLD_BONUS:       # < 0.80
    return "informational"              # Claude Haiku
if score < CHURN_THRESHOLD_DISCOUNT:    # < 0.90
    return "bonus_points"               # Claude Sonnet
return "discount"                        # Claude Sonnet
```

### Prompt Template Assembly
1. Read `tools/prompts/base.md`
2. Append `tools/prompts/{business_type}.md`
3. Format with `str.format()` using customer data + config values
4. Append Arabic instruction if `CAMPAIGN_LANGUAGE == "ar"`

### Email HTML Generation
- RTL support when `language == "ar"` (`dir="rtl"`, `lang="ar"`)
- `List-Unsubscribe` header + physical address footer for compliance
- Responsive CSS via `<style>` block (max-width 600px for email clients)

### Logging
- Every action appends to `data/system_log.csv`
- Headers: `timestamp, customer_id, action_taken, offer_type, status, error_message`
- `log_action.py` creates parent directories and writes headers if file doesn't exist

### Duplicate Prevention (Double-Guard)
1. Check `last_campaign_date` in data source > 30 days ago
2. Check `system_log.csv` for `SENT_WINBACK_OFFER` with same `customer_id` within 30 days
Both must pass for eligibility.

---

## Key Files

| File | Purpose |
|---|---|
| `main.py` | Entry point. Parses CLI args, routes to demo or production mode, loops over customers. |
| `config.py` | Single source of truth for all configuration. Reads `.env`, provides typed defaults, exposes `is_dry_run()`. |
| `tools/fetch_customers.py` | Reads CSV or Google Sheets, applies eligibility filters (churn score, unsubscribe, duplicate guard, 90+ days silence). |
| `tools/generate_offer.py` | Assembles prompt from markdown templates, calls Claude API, extracts JSON, retries once on parse failure. |
| `tools/send_email.py` | Generates HTML email (with RTL support), sends via Resend API, handles quota exceeded (429), uses ABC for pluggable providers. |
| `tools/send_instagram_dm.py` | Sends Instagram DM via instagrapi. Dry-run when credentials missing. |
| `tools/log_action.py` | Appends audit rows to `data/system_log.csv`. |
| `.env.example` | Comprehensive template documenting every environment variable. |
| `.github/workflows/daily_reactivation.yml` | GitHub Actions workflow for daily cron + manual dispatch with dry_run input. |

---

## Safety & Compliance

- **Production requires `--confirm`** — Running without `--demo` or `--confirm` exits with error
- **Dry-run by default** — Missing API keys = no real sends, no crashes
- **CAN-SPAM / Egypt PDPL** — Every email includes `List-Unsubscribe` header, physical address, and sender identification
- **Unsubscribe filtering** — Customers with `unsubscribed = yes` (case-insensitive) are skipped
- **Rate limiting** — 1-second sleep between production sends; 0.5s in demo mode
- **Instagram DM is experimental** — `instagrapi` is an unofficial library; use only as fallback, not a primary selling point

---

## Testing Strategy

### Database Reactivation Workflow
- **No formal test suite** currently exists. Validation is manual:
  - `python main.py --demo` must generate HTML files without API keys
  - `python main.py` without flags must exit with "requires --confirm" error
  - `python main.py --confirm` with missing `.env` must run in dry-run mode
- When adding tests, prefer `pytest` with `unittest.mock` for API calls.

### Link-in-Bio Page Builder
- **Unit tests**: `vitest` with test files in `src/lib/__tests__/` and co-located `*.test.ts`
- **E2E tests**: `playwright` with tests in `tests/e2e/`
- **Lint/Format**: `biome` (replaces ESLint + Prettier)

---

## On-Demand Context References

- `.claude/PRD.md` — Full Product Requirements Document for the Database Reactivation Workflow
- `docs/google_sheets_template.md` — Client onboarding guide for Google Sheets setup
- `README.md` — Setup, usage, troubleshooting, and pricing documentation
- `database_reactivation (1).md` — Original workflow specification
- `link-in-bio-page-builder/README.md` — Separate README for the Next.js app

---

## Notes for Claude

- **Always check `.env` or `config.py` before assuming defaults** — Many values are configurable.
- **Never hardcode API keys or secrets** — All secrets must flow through environment variables.
- **When modifying prompt templates** — Test with `python main.py --demo` to see output before touching production logic.
- **When adding new business types** — Create `tools/prompts/{type}.md` and update `config.py` / CLI arg choices in `main.py`.
- **CSV schema changes** — Update `fetch_customers.py` filter logic and `README.md` schema table together.
- **Link-in-Bio changes** — These are isolated to `link-in-bio-page-builder/`; do not mix with Python workflow logic.

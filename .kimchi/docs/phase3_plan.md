# Phase 3 Plan: Real-World Validation

**Goal:** Test with real API keys on a small batch to confirm deliverability, rendering, and cost per email.  
**Date:** 2026-06-19  
**Status:** Ready for review — _do not execute until user approves_

---

## 1. Pre-Requisites

Before any test email is sent, the following must be in place:

| Item | Owner | How to Verify |
|------|-------|---------------|
| Resend API key (free tier) | Freelancer / dev | `RESEND_API_KEY` in `.env` — key starts with `re_` |
| Anthropic API key | Freelancer / dev | `ANTHROPIC_API_KEY` in `.env` — key starts with `sk-ant-` |
| Sender email for Resend | Freelancer / dev | Use `onboarding@resend.dev` (default Resend sender). **Domain verification is NOT required for this test round.** |
| Test email addresses (4) | Freelancer / dev | Personal Gmail + Outlook accounts. **Never real customers.** |
| Clean `system_log.csv` | Dev | Only pre-validation rows; no SENT_WINBACK_OFFER within last 30 days for test customer IDs |
| Isolated test CSV | Dev | `data/test_customers.csv` with exactly the 4 test rows |

> **Note on domain verification:** For this initial validation round, we use Resend's default `onboarding@resend.dev` sender. Domain verification (custom domain in Resend dashboard → DNS records → Status = Active) becomes **mandatory only before Phase 4** (real client delivery). This lets us validate deliverability, rendering, and cost without the DNS setup overhead.

### 1.1 Test Customer Data

Create `data/test_customers.csv` with **exactly 4 rows** covering all key variations:

| customer_id | name | email | instagram_handle | last_purchase_date | churn_score | preferred_categories | last_campaign_date | total_purchases | days_since_last_contact | unsubscribed | business_type |
|-------------|------|-------|------------------|-------------------|-------------|---------------------|-------------------|----------------|------------------------|--------------|---------------|
| TEST001 | Info Test | your-gmail-info@gmail.com | | 2024-10-01 | 0.71 | Books | | 5 | 100 | no | gym |
| TEST002 | Bonus Test | your-outlook-bonus@outlook.com | | 2024-08-01 | 0.83 | Sports | | 25 | 140 | no | dental |
| DIS001 | Discount Test | your-gmail-discount@gmail.com | | 2024-05-01 | 0.95 | Beauty | | 30 | 190 | no | coaching |
| ARB001 | فاطمة اختبار | your-outlook-arabic@outlook.com | | 2024-09-01 | 0.91 | Home,Garden | | 18 | 130 | no | gym |

**Coverage:**
- 2 Gmail (inbox + spam folder check)
- 2 Outlook (Microsoft rendering engine)
- 1 Arabic / RTL (ARB001)
- 3 offer types: 1 informational (TEST001=0.71), 1 bonus_points (TEST002=0.83), 2 discount (DIS001=0.95, ARB001=0.91)
- 3 business types (gym, dental, coaching)

---

## 2. Execution Protocol

### 2.1 Run 1: Baseline — English, All 4 Test Customers

**Command:**
```bash
python main.py --confirm --business-type gym --language en
```

**Pre-run checklist:**
- [ ] `.env` has real API keys
- [ ] `SENDER_EMAIL=onboarding@resend.dev` set in `.env`
- [ ] `data/customers.csv` is temporarily backed up (`cp data/customers.csv data/customers.csv.bak`)
- [ ] `data/test_customers.csv` is copied to `data/customers.csv`
- [ ] `data/system_log.csv` has no INFO*, BON*, DIS*, ARB* entries within last 30 days
- [ ] Resend dashboard is open in browser to watch real-time delivery

**Post-run checklist (within 5 minutes):**
- [ ] Resend dashboard shows 4 emails with status "Delivered"
- [ ] Console summary shows: sent=4, failed=0, queued=0
- [ ] `data/system_log.csv` has 4 `SENT_WINBACK_OFFER` rows
- [ ] Claude API usage cost is noted (Anthropic console)

### 2.2 Run 2: Arabic RTL Validation — Arabic, Single Arabic Test Customer

**Why separate:** Arabic emails require visual inspection of RTL rendering. Run as a single customer to isolate rendering issues.

**Command:**
```bash
python main.py --confirm --business-type gym --language ar --customer-id ARB001
```

**Pre-run checklist:**
- [ ] `data/system_log.csv` has no ARB001 entry within last 30 days
- [ ] Test email account is ready to receive Arabic text

**Post-run checklist:**
- [ ] Resend dashboard shows 1 email "Delivered"
- [ ] Check Arabic Outlook inbox: confirm `<html dir="rtl" lang="ar">` renders correctly
- [ ] Confirm CTA button is right-aligned, text flows right-to-left
- [ ] Confirm Noto Sans Arabic font stack renders (or falls back gracefully)
- [ ] Confirm footer (List-Unsubscribe + physical address) is present

### 2.3 Run 3: Single-Customer Precision Test

**Command:**
```bash
python main.py --confirm --customer-id DIS001
```

**Goal:** Validate that `--customer-id` filter works in production with a real API call.

**Pre-run checklist:**
- [ ] DIS001 is not in system_log.csv within last 30 days

**Post-run checklist:**
- [ ] Only 1 email sent per Resend dashboard
- [ ] Console shows "Processing single customer: DIS001"
- [ ] Log file has exactly 1 entry

---

## 3. Validation Checklist

### 3.1 Deliverability (Inbox vs Spam)

Check each test address within 10 minutes of send:

| Email Client | Test Address | Inbox? | Spam? | Rendering OK? | Notes |
|--------------|--------------|--------|-------|---------------|-------|
| Gmail | TEST001 | ⬜ | ⬜ | ⬜ | Check Promotions tab too |
| Outlook | TEST002 | ⬜ | ⬜ | ⬜ | Outlook web + desktop app |
| Gmail | DIS001 | ⬜ | ⬜ | ⬜ | Consistency check |
| Outlook Arabic | ARB001 | ⬜ | ⬜ | ⬜ | RTL must be visually correct |

**Pass criteria:**
- ≥ 3/4 emails land in **Inbox** (not Spam)
- 0/4 land in **Junk/Spam** at Gmail or Outlook
- If any land in spam: record which provider, subject line, and possible cause

### 3.2 HTML Rendering

For each delivered email, verify:

- [ ] **Subject line** matches expected offer type (informational / bonus_points / discount)
- [ ] **CTA button** is visible, blue (#007bff), clickable
- [ ] **Email body** has 3–4 paragraphs, personalized with name and days_since_last_contact
- [ ] **Footer** contains:
  - Physical address (from `SENDER_PHYSICAL_ADDRESS`)
  - Unsubscribe mailto link
  - Sender name + email
- [ ] **RTL emails (ARB*)**: Text flows right-to-left, paragraphs right-aligned, Arabic characters render
- [ ] **Mobile rendering**: Check at least 2 emails on mobile (iPhone/Android). Max-width 600px respected.

### 3.3 Resend Dashboard Verification

- [ ] All 10+ emails show status **"Delivered"** (not "Bounced" or "Dropped")
- [ ] Bounce rate = 0%
- [ ] Complaint rate = 0%
- [ ] Open rate recorded (Resend tracks opens automatically if enabled)
- [ ] Delivery time: all sent within 60 seconds of each other (1s rate limit)

### 3.4 Claude API Cost Verification

**Method:** Check Anthropic console at https://console.anthropic.com/ before and after Run 1.

**Expected costs (per PRD estimates):**
| Offer Type | Model | Input Tokens | Output Tokens | Cost / Email |
|------------|-------|-------------|---------------|-------------|
| informational | Haiku | ~600 | ~500 | ~$0.002–$0.003 |
| bonus_points | Sonnet | ~600 | ~600 | ~$0.012–$0.015 |
| discount | Sonnet | ~600 | ~600 | ~$0.012–$0.015 |

**For 4 emails (mix):**
- Estimated total: **$0.02–$0.05**
- Per-email average: **$0.005–$0.012**

**Acceptance:**
- [ ] Total cost for Run 1 ≤ $0.10
- [ ] Per-email cost ≤ $0.03
- [ ] Costs are within 2× of PRD estimate (acceptable variance)

**If cost exceeds $0.10 for 4 emails:**
- Investigate token usage per request in Anthropic console
- Check if output tokens are unexpectedly high (> 1000)
- Possible fix: tighten `max_tokens` or add output-length instructions to prompt

### 3.5 System Log Verification

Check `data/system_log.csv`:

- [ ] Exactly N rows for N customers sent (no duplicates, no missing)
- [ ] `timestamp` column is correct date/time
- [ ] `customer_id` matches test CSV
- [ ] `offer_type` matches expected tier (informational/bonus_points/discount)
- [ ] `status` = "success" for all
- [ ] `error_message` is empty

---

## 4. Risk Mitigation & Rollback Plan

### Risk: Emails Land in Spam

**Detection:** Within 10 minutes of Run 1, check Gmail/Outlook spam folders.
**Mitigation steps:**
1. Do NOT proceed to Run 2 (Arabic) or client delivery until resolved.
2. Check Resend dashboard for bounce/complaint indicators.
3. Review subject lines for spam triggers (ALL CAPS, excessive punctuation, "Free", multiple exclamation marks).
4. Review HTML — ensure text-to-image ratio is high, no suspicious links.
5. **Fix candidate:** Simplify subject line, remove emojis if any, add more plain-text feel to body.
6. Re-test with 2–3 emails before full batch.

### Risk: Resend Quota Exceeded (429)

**Detection:** Console shows "Resend quota exceeded. Stopping."
**Mitigation:**
1. Free tier = 3,000 emails/month (~100/day). 10 emails will NOT trigger this.
2. If it happens, verify API key tier in Resend dashboard.
3. **Fix:** Switch to paid plan or wait for next day.

### Risk: Claude API Rate Limit (429)

**Detection:** Console shows "Rate limit from Anthropic API... retrying."
**Mitigation:**
1. Code already implements retry-once with 2s sleep (FIX-9 from Phase 1 audit).
2. If persistent: add 3s sleep between customers or use batch API.
3. For 10 emails, unlikely to trigger.

### Risk: Accidental Send to Real Customers

**Prevention (mandatory):**
1. Rename `data/customers.csv` → `data/customers.csv.bak`
2. Create `data/test_customers.csv` with ONLY your test email addresses
3. Verify no real customer data exists in the CSV before `--confirm`
4. Use `--customer-id` flag for single-email tests

### Risk: HTML Does Not Render on Mobile

**Detection:** Mobile inbox shows broken layout, CTA button too wide, text unreadable.
**Mitigation:**
1. Add `@media only screen and (max-width: 480px)` CSS fixes
2. Ensure `max-width: 600px` on body container
3. Test on iPhone Mail + Gmail mobile app

---

## 5. Deliverables After Phase 3

### 5.1 Updated `docs/research_findings.md`

Append a new section **"Phase 3: Real-World Validation Results"** with:

```markdown
## Phase 3: Real-World Validation Results

**Date:** [run date]
**Test batch size:** 10 emails
**Domain:** [yourdomain.com]
**Sender:** [sender email]

### Deliverability Results
| Provider | Inbox | Spam | Notes |
|----------|-------|------|-------|
| Gmail | X/3 | Y/3 | |
| Outlook | X/2 | Y/2 | |
| Apple Mail | X/1 | Y/1 | |
| ProtonMail | X/1 | Y/1 | |

**Overall inbox rate:** X%

### HTML Rendering
- CTA button: [Pass / Fail / Notes]
- Mobile responsive: [Pass / Fail / Notes]
- Arabic RTL: [Pass / Fail / Notes]
- Footer (address + unsubscribe): [Pass / Fail / Notes]

### Resend Dashboard
- Bounce rate: X%
- Complaint rate: X%
- Avg delivery time: Xs

### Claude API Costs
- Total cost for 10 emails: $X.XX
- Per-email average: $X.XXX
- Within PRD estimate: Yes / No

### Adjustments Made
- [List any code changes, prompt tweaks, or config changes applied after testing]

### Recommendations for Client Delivery
- [Specific advice based on test results]
```

### 5.2 `.env` Validation Checklist (for client handoff)

Create a new document or append to README: a step-by-step checklist a freelancer can run before handing to a client.

### 5.3 Go/No-Go Decision

| Criterion | Threshold | Decision |
|-----------|-----------|----------|
| Inbox rate | ≥ 80% | GO / NO-GO |
| Bounce rate | = 0% | GO / NO-GO |
| Complaint rate | = 0% | GO / NO-GO |
| Cost per email | ≤ $0.03 | GO / NO-GO |
| Arabic RTL renders | Yes / No | GO / NO-GO |
| Mobile rendering | Yes / No | GO / NO-GO |

**If any criterion is NO-GO:** Do not proceed to Phase 4. Document blocker, apply fix, re-test.

---

## 6. Chunks (for Build Delegation, if user approves)

If the user approves this plan, execution breaks into these chunks:

| Chunk | Files | Description | Complexity |
|-------|-------|-------------|------------|
| A | `data/test_customers.csv` + `.env` | Create test CSV, verify API keys, backup real customer data | simple |
| B | `main.py`, `tools/*.py` | Run 1: English batch (10 emails), capture logs & costs | simple |
| C | Manual | Check inboxes, record deliverability, screenshot rendering | simple |
| D | `main.py`, `tools/*.py` | Run 2: Arabic RTL batch (2 emails), verify rendering | simple |
| E | Manual | Update `docs/research_findings.md` with results | simple |
| F | `README.md` or new doc | Create client handoff checklist, document adjustments | simple |

---

## 7. Questions for User (if any ambiguities)

1. **Do you have real API keys ready?** If not, the first step is acquiring them (Resend free tier + Anthropic).
2. **Do you own a domain to verify in Resend?** (Required for production sends; prevents "via resend.dev" sender.)
3. **Do you have test email addresses across Gmail / Outlook / Apple / Proton?** If not, which providers can you access?

If you approve this plan, say **"execute Phase 3"** and I will start with Chunk A.

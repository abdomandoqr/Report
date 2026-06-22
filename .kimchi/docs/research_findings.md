# Customer Reactivation & Winback Email Automation — Research Findings

**Compiled:** 2026-06-19  
**Context:** Python-based CSV→Resend→Claude workflow for dormant customer re-engagement

---

## 1. Similar Python-Based Customer Reactivation Workflows

### What Exists
No single off-the-shelf open-source project directly matches this workflow (CSV + churn scoring + AI personalization + email sending). However, several GitHub repos cover adjacent pieces:

| Repo | Stars | Relevance | URL |
|------|-------|-----------|-----|
| `BGlifee/BI-Analyst_customer-churn-prediction` | — | Probability-based churn pipeline with threshold tuning & risk segmentation | https://github.com/BGlifee/BI-Analyst_customer-churn-prediction |
| `chrisProj91/...Customer-Churn-Prediction-with-Profit-Optimized-ML-Business-Decision-Framework` | — | Threshold optimization + ROI analysis + segment-level retention strategies | https://github.com/chrisProj91/Customer-Churn-Prediction-with-Profit-Optimized-Machine-Learning-Business-Decision-Framework |
| `riteshkarmakar/bulk-email-sender` | 10 ⭐ | Python bulk email sender with mail merge, SMTP, dynamic placeholders | https://github.com/riteshkarmakar/bulk-email-sender |
| `Ckokoski/martech-portfolio` | 5 ⭐ | Applied marketing tech: campaign automation, AI-powered email optimization, data-driven reporting | https://github.com/Ckokoski/martech-portfolio |
| `mohity667/ecommerce-customer-analytics` | — | RFM segmentation + churn prediction (0.728 AUC) + business recommendations | https://github.com/mohity667/ecommerce-customer-analytics |

### Common Patterns Found
- **Libraries:** `pandas`, `scikit-learn`, `xgboost`, `smtplib`, `email.mime`, `resend` (Python SDK), `anthropic`
- **Architecture:** Most production pipelines are multi-stage: (1) filter eligible users from DB/CSV, (2) score/segment, (3) generate content, (4) send, (5) log results
- **Data storage:** Small-scale projects use CSV/SQLite; mid-scale use PostgreSQL or Google Sheets (`gspread`)
- **No direct competitor:** The combination of churn-score gating + AI-generated personalization + Resend is a relatively specific stack. Most similar GitHub repos either focus on churn *prediction* (ML) or bulk email *sending* (SMTP), not both together.

### Actionable Insight
The current `/workspaces/Report` implementation (fetch_customers → generate_offer → send_email → log_action) matches the industry-standard four-stage pattern. No off-the-shelf replacement needed — it can be extended rather than rebuilt.

---

## 2. Best Practices for AI-Generated Personalized Reactivation Emails

### What Converts vs. Lands in Spam

**Subject line best practices:**
- Personalize with name: open rates increase ~26% when subject line includes recipient's name (source: Campaign Monitor / Mailchimp industry data, widely cited)
- Keep subject lines under 50 characters; urgency + specificity works (e.g., "Ahmed, your 25% welcome-back reward expires Friday")
- Avoid: ALL CAPS, excessive punctuation (!!!), "Free" in subject, excessive emojis — all trigger spam filters

**Email body best practices:**
- **Tone:** Warm, personal, low-pressure. Acknowledge the gap without guilt-tripping ("It's been a while" vs. "You abandoned us")
- **Length:** 3–5 short paragraphs (150–250 words). Mobile-first.
- **Personalization:** Use customer's name, last purchase category, time since last visit, and purchase history count
- **CTA:** Single clear CTA; avoid multiple competing buttons. Use action-oriented text ("Claim Your Reward" not "Click Here")
- **Plain-text feel:** AI-generated emails that sound too polished can feel like mass spam. Including mild imperfection (specific day counts, personalized observations) improves authenticity

### Industry-Specific Best Practices

**Gyms / Fitness:**
- Lead with progress guilt ("It has been 120 days since your last workout") — creates loss aversion
- Offer class variety, new equipment, trainer availability
- Urgency works well in fitness: seasonal challenges, new programs starting
- Recommended offer: free guest pass OR discounted re-activation membership

**Dental Clinics:**
- Fear-based messaging backfires; lead with health benefit instead
- Emphasize preventive care ("Your next cleaning is due") — low-pressure obligation
- Offer new patient referral bonus if referring a friend
- Timing: sends 2 weeks before typical 6-month checkup cycle is ideal

**Coaching Businesses:**
- Lead with transformation/outcome ("Where were you in your journey?")
- Acknowledge their specific goal area (weight loss, career, etc.)
- Offer a free strategy call or discovery session — preferred over discount
- Personal story angle works well (coach's own re-engagement journey)

### AI Prompt Strategy
- Inject customer-specific data (name, days silent, categories) into prompt — the current `PROMPT_TEMPLATE` in `generate_offer.py` does this correctly
- Add explicit "Return ONLY valid JSON" instruction — the current code handles JSON extraction with fallback for markdown fences, which is a good practice
- Consider adding "write as if from a personal email, not a marketing department" to the prompt to reduce over-polished feel

### Spam Triggers to Avoid (AI-Generated Content)
- Multiple exclamation points
- ALL CAPS words
- "Act now", "Limited time", "Last chance" (use sparingly and only for discount-tier offers)
- HTML-heavy formatting that doesn't render well in plain text
- Missing unsubscribe link (legally required, also hurts deliverability)

---

## 3. Churn Scoring Thresholds

### Are 0.7 / 0.8 / 0.9 Industry Standard?

**Short answer:** Not a universal standard, but these cutoffs are commonly used as starting points in subscription and e-commerce contexts. They are *tiered* thresholds (low/medium/high risk) rather than a single-dimension "churned vs. not churned" threshold.

**What the research says:**

| Source | Threshold Approach | Notes |
|--------|-------------------|-------|
| KHUSHI0809/StreamFlix-Customer-Churn-Prediction | 0.3 (optimized) | Streaming platform — aggressive threshold because acquisition cost is low; 94% recall on churners at 0.3 |
| Ajithkumar-ak1/Bank_customer_churn_prediction | Variable, tuned via SMOTE | Bank churn — 88% accuracy, 0.87+ ROC-AUC, threshold tuned per business cost function |
| AnkitHProfile/customer-churn-prediction | Multiple tiers | Explicitly uses risk segmentation with tier-based thresholds (not just one cutoff) |
| ImeMonday/subscription-churn-risk-analytics | Probability-based, segmented | Uses "probability-based scoring instead of hard labels" — risk segmentation based on thresholds |
| chrisProj91/...Profit-Optimized-ML-Business-Decision-Framework | Business ROI–optimized | Threshold chosen based on profit/retention cost, not model accuracy |

**Key finding:** The "right" threshold depends entirely on:
1. **Business cost of false positives** (contacting someone who wasn't actually churning) vs. false negatives (missing someone who was)
2. **Acquisition cost** — low-cost acquisition (streaming) → lower threshold (contact everyone at >0.3); high-cost (B2B SaaS, coaching) → higher threshold (contact only >0.8)
3. **Campaign cost** — if sending costs money (SMS, print), higher threshold needed

### Alternatives to Fixed Thresholds

1. **Percentile-based:** Contact top 10% most likely churners regardless of absolute score
2. **Decile analysis:** Divide customers into 10 deciles by churn score; target deciles 8–10
3. **Business-cost optimization:** Choose threshold that maximizes (recovered revenue - campaign cost)
4. **RFM + score hybrid:** Combine recency/frequency/monetary with ML churn score for better targeting
5. **Domain-specific calibration:** For fitness/gym: 30-day inactivity → 0.6+; 60-day → 0.75+; 90-day → 0.85+

### Recommended Approach for Current Workflow
The current thresholds (0.7/0.8/0.9) are reasonable for e-commerce/retail with moderate acquisition costs. They align with the tiered offer strategy:
- **0.70–0.79 (informational):** Contact but don't over-invest
- **0.80–0.89 (bonus_points):** Moderate offer, good ROI potential
- **0.90–1.00 (discount):** High-value recovery attempt with significant discount

**Caveat:** The workflow should expose these thresholds as config constants (not hardcoded) so they can be tuned based on campaign results.

---

## 4. Email Deliverability Best Practices in Python

### Resend API vs Gmail API vs SMTP Comparison

| Feature | Resend API | Gmail API | SMTP (smtplib) |
|---------|-----------|-----------|----------------|
| **Setup complexity** | Low (API key only) | High (OAuth 2.0 flow) | Low (credentials + server) |
| **Daily sending limit** | 100/day free, paid plans higher | 500 recipients/day (personal), higher with Workspace | Varies by provider; Gmail caps at 500/day |
| **Warm-up required** | No (managed infrastructure) | No, but rate-limited | Yes (IP warm-up required) |
| **DKIM/SPF** | Automatic (managed) | Automatic (Google) | Manual setup required |
| **HTML templates** | Native | Requires mime library | Requires mime library |
| **Bounce handling** | Built-in webhook support | Built-in | Manual |
| **Dedicated IPs** | No (shared pool) | No | Yes (optional) |
| **Open/click tracking** | Yes (dashboard) | No (requires extension) | No |
| **Best for** | Transactional + marketing emails | Personal/outreach (low volume) | High-volume bulk sending |

**Verdict:** For this workflow's scale (likely <500 reactivation emails/day), **Resend API is the best choice**. It combines Gmail API's deliverability with SMTP's simplicity, without OAuth overhead.

### Deliverability Best Practices (Specific to Python/Resend)

**DKIM & SPF:**
- Resend handles this automatically on verified domains. No additional setup needed.
- Ensure sender email domain has DNS properly configured (Resend provides instructions in dashboard)

**Sender Reputation:**
- Start slow: send to ≤50 emails/day for first week, then ramp
- Monitor Resend dashboard for bounce rates (keep <2%)
- Avoid high complaint rates: only email customers who opted in
- The current workflow filters for "90+ days silent" customers — these are lower-risk for spam complaints since they previously engaged

**Unsubscribe Handling:**
- Resend requires unsubscribe headers for marketing emails (RFC 8058 / List-Unsubscribe-Post)
- Add to Resend API calls: `"headers": {"List-Unsubscribe": "<mailto:unsubscribe@yourdomain.com>"}`
- **Current gap:** The `send_email.py` does not include unsubscribe headers — recommend adding this

**Throttling:**
- Current 1-second sleep between sends is appropriate for small batches
- Resend rate limits: free tier ~1 email/second; paid plans support higher throughput
- For batches >100, consider adding exponential backoff

**Python Libraries Recommended:**
```
resend          # Official Resend SDK (current)
anthropic       # Anthropic API client (current)
pandas          # CSV processing (current)
python-dotenv   # Env management (current)
# Optional future:
sendgrid        # Alternative to Resend
gspread         # Google Sheets integration (Phase 2 upgrade)
```

### Recommended Improvements to Current `send_email.py`
1. Add `List-Unsubscribe` header for CAN-SPAM compliance
2. Add `reply_to` header for better deliverability
3. Implement retry logic with `tenacity` or manual exponential backoff
4. Log Resend's message `id` returned — useful for debugging bounce complaints

---

## 5. Existing Open-Source Reactivation Workflow Projects

### Notable GitHub Repositories

1. **riteshkarmakar/bulk-email-sender** (10 ⭐)  
   Python GUI bulk email sender with mail merge, SMTP support, dynamic placeholders, attachment handling. Good reference for templating patterns.  
   https://github.com/riteshkarmakar/bulk-email-sender

2. **Ckokoski/martech-portfolio** (5 ⭐)  
   Applied marketing technology projects including campaign automation and AI-powered marketing tools. Closest to the full reactivation workflow concept.  
   https://github.com/Ckokoski/martech-portfolio

3. **BGlifee/BI-Analyst_customer-churn-prediction**  
   Probability-based churn prediction pipeline with threshold tuning and business-focused evaluation. Explicitly mentions risk segmentation — directly applicable to the tiered offer strategy.  
   https://github.com/BGlifee/BI-Analyst_customer-churn-prediction

4. **chrisProj91/Customer-Churn-Prediction-with-Profit-Optimized-ML-Business-Decision-Framework**  
   Goes beyond churn prediction into decision-making: threshold optimization based on business profit, ROI analysis, lift analysis, and segment-level retention strategies. Most sophisticated of the bunch.  
   https://github.com/chrisProj91/Customer-Churn-Prediction-with-Profit-Optimized-Machine-Learning-Business-Decision-Framework

5. **mohity667/ecommerce-customer-analytics**  
   End-to-end e-commerce analytics: RFM segmentation (Recency/Frequency/Monetary), churn prediction with 0.728 AUC, and cohort retention analysis. Demonstrates combining RFM with ML scoring — good reference for Phase 2 improvements.  
   https://github.com/mohity667/ecommerce-customer-analytics

### Gap Analysis
None of these projects combine all three pillars: (1) ML-based churn scoring, (2) AI-generated personalized content per customer segment, AND (3) automated email delivery. The current `/workspaces/Report` implementation is actually in a relatively unique position. Most projects pick one or two of these elements.

---

## Recommended Approach Based on Findings

### Keep / Improve Current Architecture
The four-stage pipeline (fetch → generate → send → log) is industry-standard and well-implemented. The main improvements needed are:

### High-Priority Improvements
1. **Add unsubscribe headers** to `send_email.py` for CAN-SPAM compliance
2. **Externalize churn thresholds** (0.7/0.8/0.9) to `.env` or a config file for easy tuning
3. **Add RFM scoring** as a supplementary segmentation signal (see mohity667 repo)
4. **Implement batch retry logic** with exponential backoff in `send_email.py`
5. **Add Resend webhook** handling for bounce/complaint tracking

### Mid-Priority Enhancements
6. **Phase 2 (per existing roadmap):** Replace CSV with Google Sheets via `gspread` for real client use
7. **Phase 3:** Add A/B subject line testing via Resend's batch API
8. **Phase 4:** Add SMS via Twilio for multi-channel reactivation
9. **Threshold calibration:** Instrument the workflow to track conversion rates per churn tier so thresholds can be data-tuned (per chrisProj91's ROI-optimized approach)

### Key Risk: Spam Folder
The biggest risk is deliverability (emails landing in spam). Mitigations:
- Verify sender domain in Resend (DNS setup)
- Monitor Resend dashboard for bounce/complaint rates  
- Start with test send to personal email, check spam score
- Never send to purchased/ rented lists — only warm/engaged contacts

---

## Summary Table

| Topic | Finding | Recommendation |
|-------|---------|----------------|
| **Reactivation workflows** | No direct open-source competitor combines ML scoring + AI generation + email sending | Keep current approach, extend with Phase 2/3 upgrades |
| **Email personalization** | Name, recency, category, specific data = highest conversion; warm/low-pressure tone | Add "personal email" tone instruction to Claude prompt; keep 3–4 paragraphs |
| **Churn thresholds** | 0.7/0.8/0.9 are reasonable tiered cutoffs, not universal | Externalize to config; instrument for data-driven tuning |
| **Email deliverability** | Resend API best for this use case (simple, managed DKIM/SPF) | Add unsubscribe headers; add retry logic; start slow |
| **Open-source projects** | 5 relevant repos identified covering churn ML + email automation + analytics | Reference for Phase 2/3 improvements; not replacements |

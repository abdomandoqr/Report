# Database Reactivation Workflow — Clarifying Questions

*After research, before building. 25 questions organized by category.*

## 1. Product & Delivery Model

1. **Deployment model:** Will this be a SaaS you host for each client, a self-hosted Docker image, or a GitHub repo they clone into their own Codespace?
2. **Pricing/packaging:** One-time setup fee, monthly retainer, or per-recovery commission? Does the pricing include AI API and email provider costs?
3. **White-labeling:** Should emails appear exclusively from the client's brand/domain, or can they mention the tool/service provider?
4. **Demo mode appearance:** Should the demo be a Streamlit/Dash web UI, a terminal CLI wizard, or a Python script with `--dry-run` flags?

## 2. Data & Integration

5. **Churn score source:** Is `churn_score` calculated inside the workflow, provided by the client in the sheet, or imported from an external ML model?
6. **Google Sheets auth:** Will clients use a shared service account (`credentials.json`) or OAuth with their own Google account? Who creates the Google Cloud project?
7. **Customer data schema:** Beyond the current columns, do clients need fields like `phone`, `instagram_handle`, `language_preference`, `birth_date`, or `membership_type`?
8. **Segmentation rules:** Should the tool use only `churn_score + days_since_last_contact`, or also RFM (recency, frequency, monetary) analysis?
9. **Data retention:** How long should customer data and campaign logs be retained? Do clients have a "right to be forgotten" mechanism?

## 3. AI & Personalization

10. **Business type handling:** Separate AI prompts for gyms, dental, and coaching, or one adaptive prompt that detects business type from a sheet column?
11. **Email language:** Default to Arabic, English, or auto-detect from customer data? Should bilingual emails be supported?
12. **AI context window:** Should the AI see full purchase history or just summarized fields (last purchase date, total purchases, preferred categories)?
13. **AI failure strategy:** If Claude returns invalid JSON, retry once, fall back to a static template, skip the customer, or alert a human?
14. **A/B testing:** A/B test subject lines or offer types within a campaign, or one-size-fits-all for MVP?

## 4. Email & Channels

15. **Email provider strategy:** Resend only, or support SendGrid/Mailgun as fallback if Resend rate-limits or the client already has an account?
16. **Visual email design:** Plain text (current), simple HTML with brand colors, or full responsive templates with images and CTA buttons?
17. **Template management:** Templates hard-coded in Python, stored in Google Sheets, or managed via a web UI?
18. **Multi-channel priority:** Email primary, or cycle through channels (email → Instagram DM → SMS) based on preferences or response data?
19. **Unsubscribe handling:** Track unsubscribes in the same Google Sheet, a separate suppression list, or via the email provider's native management?
20. **Bounce/complaint handling:** Automatically suppress bounced addresses from future campaigns? Where is the suppression list stored?

## 5. Operations & Scheduling

21. **Schedule precision:** "Daily" at what local time — client's timezone or fixed UTC time?
22. **Recipient volume:** Expected daily volume per client — 50, 500, or 5,000 emails/day? This determines whether Celery/Redis is needed.
23. **Duplicate prevention rule:** No email to the same address within X days, or no email to the same `customer_id` regardless of address changes?
24. **Notification/alerting:** If the workflow fails (Resend outage, Sheets API error), who gets notified — you, the client, or a Slack/Discord webhook?

## 6. Compliance & Legal

25. **Compliance — Egypt/Arab markets:** Does Egypt have a local anti-spam law, or do we follow GDPR-style consent principles? Do clients collect explicit opt-in before adding leads?

---

*Generated after research phase — 2026-06-18*

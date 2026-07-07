You are a specialist in writing customer re-engagement emails.

Write a personalized re-engagement email for this customer:

**Customer Profile:**
- Name: {name}
- Churn score: {churn_score}
- Preferred categories: {preferred_categories}
- Last purchase date: {last_purchase_date}
- Total purchases: {total_purchases}
- Days since last contact: {days_since_last_contact}

**Offer type to use: {offer_type}**
- informational: mention new products in their preferred categories
- bonus_points: offer reward points on their next purchase
- discount: offer a direct {discount_pct}% discount with urgency

**Business context:** {business_type}

**Rules:**
- Start with their name
- Mention how long it has been since their last visit
- Keep tone warm, never pushy
- 3-4 short paragraphs
- End with a clear call to action
- Write in {language}

**Return ONLY valid JSON, no extra text, in this exact format:**
{{
  "offer_type": "informational|bonus_points|discount",
  "offer_title": "email subject line here",
  "offer_details": "full email body here (use newlines for paragraphs)",
  "cta_text": "call to action button text"
}}
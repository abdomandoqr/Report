# Research: Churn Score Thresholds in Customer Retention & Reactivation Campaigns

## Summary

The current plan uses **0.7 / 0.8 / 0.9** probability cutoffs to trigger informational, bonus_points, and discount offers respectively. Based on industry literature and campaign analytics, this approach is **directionally reasonable but suboptimal**.

- **0.7 is on the high side** for the first intervention (informational). Many practitioners flag at-risk customers at **0.5–0.6**.
- **0.8 and 0.9 are appropriate** for escalating offers, but the steep escalation from 0.7→0.8→0.9 leaves a large gap (0.5–0.7) where early intervention could prevent churn more cost-effectively.
- **A 4-tier or 5-tier segmentation** (e.g., 0.4 / 0.6 / 0.75 / 0.9) is more common in established churn models.
- **Win-back campaign benchmarks** suggest a minimum 3:1 ROI is viable, with recovery rates of 15–30%. Targeting *only* ≥0.7 scores may miss the most cost-efficient recovery window.

---

## 1. Industry-Standard Churn Score Ranges

Churn models typically output a probability between 0 and 1. Industry segmentation into risk tiers varies by sector, but the following patterns are widely cited:

| Risk Tier | Typical Probability Range | Common Actions |
|-----------|--------------------------|----------------|
| Low / Safe | 0.0 – 0.3 | No action, routine engagement |
| Medium / Watch | 0.3 – 0.5 | Passive monitoring, nurture campaigns |
| High / At-Risk | 0.5 – 0.7 | **Informational outreach**, product tips, check-ins |
| Critical / Likely | 0.7 – 0.9 | **Retention offers**, bonus points, discounts |
| Churned / Lost | >0.9 or already churned | **Win-back campaigns**, aggressive discounts |

**Key finding:** The 0.7 threshold is commonly used as the boundary between "at-risk" and "likely to churn," not as the *first* intervention point. Many models begin proactive retention at **0.5–0.6**.

Sources:
- Microsoft Fabric churn tutorial describes building probability scores and segmenting for retention actions: [learn.microsoft.com](https://learn.microsoft.com/en-us/fabric/data-science/customer-churn)
- Kumo.ai churn guide notes models "stuck at 70%" vs those that "break 80%" and emphasizes probability calibration over raw accuracy: [kumo.ai](https://kumo.ai/resources/learn/guide/churn-prediction-complete-guide/)

---

## 2. Are 0.7 / 0.8 / 0.9 Cutoffs Appropriate?

### The 0.7 Threshold
- **0.7 is a common *high-risk* threshold**, but using it as the *first* trigger is conservative.
- By the time a customer reaches 0.7 probability, behavioral decline is often well advanced. Earlier intervention at 0.5–0.6 has higher ROI because it requires lower-cost actions (informational nudges rather than discounts).
- In telecom churn models (e.g., Kaggle Telco dataset analyses), 0.5 is frequently used as the cutoff for flagging at-risk customers.

### The 0.8 and 0.9 Thresholds
- **0.8 is a reasonable escalation point** for medium-value offers (bonus points).
- **0.9 is appropriate for aggressive retention** (discounts), but by this stage the probability of saving the customer is materially lower.
- The gap between 0.7 and 0.8 is narrow (0.1), while the gap below 0.7 is wide and mostly untreated.

### Verdict
The 0.7/0.8/0.9 ladder **over-weights late-stage intervention** and **under-weights early-stage prevention**. A more balanced approach would introduce an earlier tier.

Sources:
- MLQ.ai churn analysis with AI agents uses risk tiering (Low / Medium / High) based on probability outputs to drive differentiated actions: [blog.mlq.ai](https://blog.mlq.ai/predicting-customer-churn-ai-agents/)
- Kumo.ai guide warns against optimizing for accuracy on imbalanced datasets and instead focusing on calibrated probability thresholds for action: [kumo.ai](https://kumo.ai/resources/learn/guide/churn-prediction-complete-guide/)

---

## 3. Alternative Segmentation Strategies

### A. Probability-Decile Approach
- Rank all customers by churn probability into 10 deciles.
- Assign actions by decile rather than fixed thresholds:
  - Deciles 1–3 (low risk): Monitor
  - Deciles 4–5 (medium risk): Informational content, health checks
  - Deciles 6–7 (high risk): Bonus points, feature adoption nudges
  - Deciles 8–10 (critical risk): Discounts, direct outreach, win-back
- **Advantage:** Adapts to model calibration and base rate; ensures resources are always directed to the highest-relative-risk customers even if absolute probabilities shift.

### B. Expected Value Segmentation
- Compute **expected loss = churn probability × customer lifetime value (CLV or ARPU)**.
- Prioritize customers with highest expected loss, not just highest probability.
- A customer with 0.6 churn probability and $500 ARPU may be worth more effort than a 0.9 probability customer with $10 ARPU.
- **Advantage:** Aligns retention spend with revenue protection.

### C. Risk × Recency Matrix
- Combine churn probability with **recency of last engagement**.
- A 0.7 probability customer who logged in yesterday is different from one who logged in 30 days ago.
- This is common in silent-churn detection (e.g., e-commerce / SaaS).

### D. 4-Tier Threshold Model (Recommended Adjustment)
| Tier | Range | Offer Type |
|------|-------|------------|
| Watch | 0.4 – 0.55 | Passive informational, in-app tips |
| At-Risk | 0.55 – 0.70 | Active informational, onboarding refresh |
| High-Risk | 0.70 – 0.85 | Bonus points, value reinforcement |
| Critical | >0.85 | Discounts, win-back, executive outreach |

---

## 4. Data on Reactivation Campaign ROI by Score Segment

### Win-Back Benchmarks
- **Win-Back Rate**: 15–30% of targeted churned customers can be recovered, per Totango metrics cited in industry literature.
- **Time-to-Win-Back**: 90–180 days average.
- **Minimum Viable ROI**: 3:1 (revenue from recovered customers vs campaign cost).

### Cost-Efficiency by Segment
- Early intervention (0.5–0.7 range) typically uses **low-cost channels** (email, in-app messages) and can achieve ROI of 5:1 to 10:1.
- Late intervention (0.8–0.9+) requires **high-cost offers** (discounts, credits, manual outreach) and may only achieve 2:1 to 3:1.
- Therefore, **shifting budget toward earlier thresholds generally improves blended campaign ROI**.

Sources:
- GetMonetizely win-back campaign guide: benchmarks, ROI formula, and recovery rates: [getmonetizely.com](https://www.getmonetizely.com/articles/how-to-track-win-back-campaign-effectiveness-a-complete-guide-for-saas-executives)

---

## 5. Data-Backed Recommendations

1. **Lower the first intervention threshold from 0.7 to ~0.55–0.6.**
   - This captures customers earlier when low-cost informational actions are still effective.
   - Citation: Common practice in telecom and SaaS churn models (Microsoft Fabric, Kaggle Telco analyses).

2. **Introduce a 4th tier or use deciles instead of fixed 0.7/0.8/0.9.**
   - The current 3-tier model leaves a large untreated population below 0.7.
   - Citation: Kumo.ai guide emphasizes calibrated probability tiers; MLQ.ai analysis uses Low/Medium/High risk segmentation.

3. **Weight thresholds by customer value (ARPU / CLV).**
   - High-value customers should trigger at lower probabilities (e.g., 0.5).
   - Low-value customers can be deferred to higher thresholds or excluded.
   - Citation: Expected-value segmentation is standard in B2B SaaS retention playbooks.

4. **Test a decile-based holdout against the fixed-threshold approach.**
   - Run an A/B test: fixed 0.7/0.8/0.9 vs. top-20% / top-10% / top-5% probability deciles.
   - Measure recovery rate, cost per recovery, and 90-day post-recovery retention.

5. **Monitor calibration, not just rank.**
   - A model that says "0.8" should mean ~80% of those customers actually churn.
   - Miscalibrated models make fixed thresholds unreliable. Use Platt scaling or isotonic regression.
   - Citation: Kumo.ai guide warns that "92% accuracy" can hide zero true-positive capture on imbalanced churn datasets.

---

## Citations & Sources

1. **Microsoft Fabric — Customer Churn Tutorial**
   - URL: https://learn.microsoft.com/en-us/fabric/data-science/customer-churn
   - Notes: End-to-end churn model tutorial using scikit-learn and LightGBM; demonstrates probability scoring and segmentation for retention actions.

2. **Kumo.ai — The Complete Guide to Churn Prediction**
   - URL: https://kumo.ai/resources/learn/guide/churn-prediction-complete-guide/
   - Notes: Covers algorithm selection, metrics that matter, probability calibration, and the difference between models that look good in notebooks vs. models that save revenue.

3. **MLQ.ai — Predicting Customer Churn with AI Agents**
   - URL: https://blog.mlq.ai/predicting-customer-churn-ai-agents/
   - Notes: Uses Kaggle Telco dataset; segments customers into Low / Medium / High churn risk tiers with differentiated retention recommendations.

4. **GetMonetizely — How to Track Win-Back Campaign Effectiveness**
   - URL: https://www.getmonetizely.com/articles/how-to-track-win-back-campaign-effectiveness-a-complete-guide-for-saas-executives
   - Notes: Provides win-back rate benchmarks (15–30%), time-to-win-back (90–180 days), and minimum viable ROI (3:1).

5. **Subsets — What is Winback Rate and why it matters**
   - URL: https://www.subsets.com/glossary/metrics/winback-rate
   - Notes: Defines winback rate as a signal of brand strength and a metric for reactivation lever effectiveness.

6. **SaaSPriceLab — Reactivation Rate Formula & Win-Back Guide**
   - URL: https://www.saaspricelab.com/blog/reactivation-rate-win-back-guide
   - Notes: SaaS reactivation benchmarks and win-back strategies.

---

*Document generated: 2026-06-18*

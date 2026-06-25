---
name: pd-content-market-intelligence
description: >
  Deep research skill that maps the full competitive landscape for any topic
  across every major platform — YouTube, Reddit, X/Twitter, TikTok, LinkedIn,
  Google, forums, and blogs. Use this skill whenever someone wants to find
  content opportunities, trending topics, audience pain points, supply/demand
  gaps, or the biggest voices in a space. Trigger on phrases like /research,
  /intel, /gaps, find gaps in a niche, what is trending around a subject,
  who are the biggest creators in a space, find ideas for a topic, what is the
  market like for a subject, competitive research on a topic, what should I
  make about a topic, or any time someone pastes a niche and wants to know
  what is happening. ALWAYS use this skill before ideating — run it first,
  think second. Produces a structured intelligence report with real numbers,
  sentiment analysis, gap scoring, and ranked content ideas ready to execute.
---

# Content Market Intelligence

A deep research protocol for mapping any topic across the full internet — before any content gets made.

## What This Skill Does

1. Maps **demand signals** across YouTube, Reddit, X/Twitter, TikTok, Google, LinkedIn, forums, and blogs
2. Identifies **key voices** — who owns the conversation, their size, their angles
3. Calculates **supply/demand gaps** — what audiences want that nobody is making
4. Measures **trend velocity** — is this topic rising, peaking, or dying?
5. Extracts **audience language** — the exact words and phrases real people use
6. Spots **monetization signals** — sponsorship activity, product demand, affiliate opportunities
7. Generates **10-20 ranked content ideas** with differentiation angles

---

## Research Protocol

### Step 0: Topic Decomposition

Before searching anything, break the input topic into 3 layers:

**Core topic** → The main subject  
**Sub-angles** → 4-6 specific lenses (beginner, advanced, tool-specific, fear-based, aspirational, contrarian)  
**Adjacent topics** → 3-4 related spaces that share the same audience

Example input: "LinkedIn lead generation"  
→ Core: LinkedIn lead generation  
→ Sub-angles: automation safety, cold message copy, Sales Navigator, AI personalization, agency use, account bans  
→ Adjacent: cold email, B2B sales, personal branding, outbound tools

Write these out before searching anything. They become your search matrix.

---

### Step 1: YouTube Intelligence (use browser — live data required)

Run **8-10 searches** using the browser. For each, capture view counts, VPH (views per hour), channel subscriber count, and recency. Extract VidIQ data if visible in the search results panel.

**Search patterns to run:**
```
[topic] 2026
[topic] tutorial 2025 2026
[topic] [sub-angle 1]
[topic] [sub-angle 2]
best [tool/method] for [topic]
[topic] for beginners
[topic] case study results
[topic] mistakes avoid
how to [core desired outcome] with [topic]
[topic] vs [competitor topic]
```

For each search page, capture:
- Top 8-10 videos: title, views, channel name, subscriber count, days/weeks since posted
- VPH if shown (views per hour = velocity signal)
- Remix score if shown (outlier signal)

**Calculate for each video:**
- `views_per_day = total_views ÷ days_since_posted`
- `channel_avg_vpd` = estimate from other recent videos (fetch channel /videos page if needed)
- `velocity_score (1-10)` = how fast this video is growing vs. that channel's baseline
- `outlier_score (1-10)` = how anomalous this is for the niche overall

**Velocity Score Table:**
| vs Channel Avg | Score |
|---|---|
| Below average | 1-3 |
| Slightly above (1-2x) | 4-5 |
| Clearly above (3-5x) | 6-7 |
| Strong outlier (6-10x) | 8-9 |
| Extreme (10x+) | 10 |

**Outlier Score Table:**
| Signal | Score |
|---|---|
| Expected for channel size | 3-4 |
| Modestly above niche avg | 5-6 |
| Clearly outperforming | 7-8 |
| Way above normal | 9-10 |

Also pull the **VidIQ panel data** from the bottom of the search page when visible:
- Overall Score
- Volume rating
- Competition level
- Avg views for that keyword
- Top creator for keyword

---

### Step 2: Reddit Intelligence (web search)

Run these Google searches to surface Reddit conversations:

```
site:reddit.com "[topic]" pain frustration 2025
site:reddit.com "[topic]" "best tool" OR "which tool" OR "recommend" 2025
site:reddit.com "[topic]" "what works" OR "actually works" 2025
site:reddit.com "[topic]" "doesn't work" OR "not working" OR "tried everything" 2025
reddit "[topic]" most upvoted 2025 2026
```

For each Reddit thread found, extract:
- **Upvote count** (demand signal — more upvotes = more people feel this)
- **Pain points** — what are people frustrated about?
- **What's working** — what are people saying actually works?
- **Exact language** — pull verbatim phrases people use (gold for titles/hooks)
- **Questions asked repeatedly** — unanswered questions = content gaps
- **Subreddits active** — which communities are having this conversation

---

### Step 3: X/Twitter Intelligence (web search)

```
site:twitter.com OR site:x.com "[topic]" 2025 2026
"[topic]" influencer opinions site:x.com
[topic] "thread" site:twitter.com trending
```

Look for:
- Viral tweets on this topic (high likes/retweets = proven resonance)
- Influencer hot takes or controversial opinions (debate = content opportunity)
- Emerging terminology nobody else is using yet
- "This changed how I think about [topic]" style posts (paradigm shifts)

---

### Step 4: Google Trends + Search Volume Signals

Run web searches to find proxy search volume data:

```
"[topic]" search volume 2025 2026
"[topic]" keyword difficulty SEO
[topic] google trends rising
"[topic]" monthly searches ahrefs semrush
```

Look for:
- Is search volume growing, flat, or declining?
- Related rising queries (breakout terms = early trend signal)
- Seasonal patterns (peaks/valleys)
- Commercial intent signals (are people buying/paying for solutions?)

---

### Step 5: TikTok & Short-Form Intelligence

```
[topic] tiktok viral 2025 2026 views
"[topic]" tiktok trending
[topic] short form video trending creators
```

Look for:
- Are there TikTok creators dominating this space?
- What format is working (talking head, screencast, reaction, trend audio)?
- Is there an audience younger than YouTube's that YouTube content is missing?
- TikTok often shows trends 3-6 months before they hit YouTube

---

### Step 6: LinkedIn + Professional Community Intelligence

```
"[topic]" site:linkedin.com 2025 viral post
"[topic]" linkedin impressions engagement 2025
[topic] linkedin creator most viewed
```

Look for:
- LinkedIn posts with 50K+ impressions on this topic
- Professional angles not covered on YouTube (enterprise, B2B use cases)
- Executives/practitioners sharing real results (social proof angles)

---

### Step 7: Blog + Podcast Intelligence

```
"[topic]" blog most read 2025 2026
"[topic]" podcast episode most downloaded
"[topic]" newsletter popular
best articles "[topic]" 2025
```

Look for:
- Long-form content gaps (topics well covered in text, not video)
- Podcast angles that haven't been turned into YouTube content
- Newsletter audiences that aren't being served on YouTube

---

### Step 8: Competitor & Key Voice Mapping

For every major creator/voice found across platforms:

| Creator | Platform | Followers/Subs | Avg Views | Best Performing Topic | Gap They're Missing |
|---|---|---|---|---|---|
| [Name] | YouTube | [X] | [Y] | [topic] | [what they don't cover] |

Answer these questions:
1. Who are the top 5 voices on YouTube in this space? What do they NOT cover?
2. Who are the top 5 voices on Reddit/X/LinkedIn? Do they have YouTube channels?
3. Is there a creator who dominates text but has no video presence? (First-mover opportunity)
4. Which successful creator has the weakest content quality but still wins? (Low bar to beat)

---

### Step 9: Monetization Signal Check

```
"[topic]" sponsorship deal 2025
"[topic]" affiliate program
"[topic]" tool pricing revenue
brands sponsoring "[topic]" creators
```

Look for:
- Are brands spending money here? (Yes = the audience has $ to spend)
- Which companies are sponsoring content in this space?
- Are there affiliate programs with high commissions?
- Is there a SaaS tool this audience needs? (B2B = higher CPM on ads)

---

### Step 10: Calculate Opportunity Scores

For each sub-angle or content idea:

**Demand Score (1-10):**
- YouTube search volume / view counts
- Reddit upvotes and thread activity
- Google search volume
- Social conversation volume

**Supply Score (1-10):**
- Number of quality videos on this exact angle
- Recency of best existing content (old = gap)
- Quality of existing content (low = easy to beat)

**Trend Velocity (1-10):**
- Is interest growing or declining?
- Recent viral content on this angle (yes = momentum)
- Emerging terminology (new language = early trend)

**Opportunity Score = (Demand Score + Trend Velocity - Supply Score)**

Range: -8 to +18. Anything above +10 is a strong opportunity.

---

## Output Format

Deliver the full intelligence report in this structure:

---

### Topic Overview

**Core topic:** [X]  
**Research date:** [date]  
**Overall market health:** [Growing / Mature / Declining] + 1-sentence why

---

### Platform-by-Platform Signals

**YouTube:**
- Total estimated monthly searches: [X]
- Top performing video: [Title] — [Views] views, [Channel] ([Subs])
- Average views for content in this space: [X]
- Content age of top results: [Old/Fresh — signals opportunity]
- Competition level: [Low / Medium / High]

**Reddit:**
- Most active subreddits: [list]
- Top pain points (verbatim): [direct quotes]
- Top "what works" insights: [direct quotes]
- Most upvoted thread found: [title + upvotes]

**X/Twitter:**
- Dominant voices: [names + followers]
- Viral tweets found: [summary]
- Hot takes/debates: [summary]
- Emerging language/terms: [list]

**Google Trends:**
- Trajectory: [Rising / Flat / Falling]
- Peak search months: [X]
- Related rising queries: [list]

**TikTok:**
- Active creators: [names]
- Dominant format: [talking head / screencast / etc.]
- Early trend signals: [Y/N + what]

**LinkedIn:**
- Top posts found: [summary]
- Professional angles uncovered: [list]
- B2B/Enterprise gap: [Y/N]

---

### Key Voices & Competitive Landscape

**YouTube Leaders:**
1. [Creator] — [Subs] — Best content: [topic] — Gap: [what they miss]
2. [Creator] — [Subs] — Best content: [topic] — Gap: [what they miss]
3. [Creator] — [Subs] — Best content: [topic] — Gap: [what they miss]

**Non-YouTube Leaders (opportunity to be first on video):**
- [Person/Brand] dominates [platform] but has no/weak YouTube presence

**Weakest Dominant Creator:** [Who wins despite poor quality — low bar to beat]

---

### Audience Language Map

These are the exact words and phrases the target audience uses. Use them in titles, hooks, and scripts.

**Pain language:** (what they say when frustrated)
- "[verbatim quote]"
- "[verbatim quote]"

**Aspiration language:** (what they want)
- "[verbatim quote]"
- "[verbatim quote]"

**Question language:** (what they're asking)
- "[verbatim quote]"
- "[verbatim quote]"

---

### Trend Velocity Assessment

**Current state:** [Rising fast / Growing steadily / Mature plateau / Declining]  
**Why:** [1-2 sentence explanation backed by data found]  
**Best window to act:** [Now / 3-6 months / Already late]  
**Adjacent trend to watch:** [What's coming next in this space]

---

### Monetization Signals

**Sponsorship activity:** [High / Medium / Low] — Brands active: [list]  
**Audience buying power:** [High / Medium / Low] — Evidence: [what they spend on]  
**Affiliate potential:** [Products/programs in this space]  
**CPM estimate:** [High (B2B) / Medium / Low (B2C entertainment)]

---

### Gap Analysis — Ranked by Opportunity Score

| # | Content Angle | Demand | Supply | Velocity | Opportunity Score | Why It's a Gap |
|---|---|---|---|---|---|---|
| 1 | [angle] | 8 | 2 | 9 | +15 | [reason] |
| 2 | [angle] | 7 | 3 | 8 | +12 | [reason] |
| 3 | [angle] | 8 | 5 | 7 | +10 | [reason] |

---

### Content Ideas — Ranked by Impact

For each idea (aim for 15-20):

**Idea #N: [Proposed Title]**
- **Opportunity Score:** [X/18]
- **Funnel Position:** TOF / MOF / BOF
- **Angle:** [What makes this different from what exists]
- **Hook direction:** Fear / Curiosity / Transformation / Proof / Contrarian
- **Why it wins:** [Evidence from research — specific data point]
- **Inspired by gap in:** [Platform + what's missing there]
- **Best format:** Long-form / Short / Series / Case study

---

### Top 3 Recommendations

If only 3 pieces of content get made from this research:

1. **[Title]** — [1-sentence reason, referencing specific data]
2. **[Title]** — [1-sentence reason]
3. **[Title]** — [1-sentence reason]

---

### Differentiation Playbook

How to stand out from the existing content in this space:

- **What everyone else does:** [pattern observed]
- **What nobody is doing:** [gap found]
- **The contrarian angle:** [opposing take that could go viral]
- **The underserved audience:** [who existing creators ignore]
- **The format opportunity:** [format that works elsewhere but not here yet]

---

## Research Rules

- **Never rely on memory.** Every claim must come from a live search in this session.
- **Show your math.** All scores must show brief working (e.g., "320K views ÷ 45 days = 7.1K vpd vs channel avg 1.2K vpd = 5.9x → Velocity 8")
- **Quote real people.** Audience language must be verbatim from Reddit/Twitter/YouTube comments, not paraphrased.
- **Flag uncertainty.** If data is estimated or unavailable, mark it *(estimated)* or *(unconfirmed)*.
- **Don't inflate scores.** Low scores are useful data. Only flag genuine opportunities.
- **Prioritize recency.** Posts and videos from the last 90 days carry 2x the signal weight of older content.

---

## Trigger Phrases

Activate this skill with:
- `/research [topic]` — Full intelligence report
- `/intel [topic]` — Same as /research
- `/gaps [topic]` — Focus on gap analysis only
- `/trends [topic]` — Focus on trend velocity and emerging signals
- `/compete [topic]` — Focus on competitor mapping
- `/audience [topic]` — Focus on audience language and pain points
- `/ideas [topic]` — Run full research and jump straight to ranked ideas

When a topic is pasted with no command, assume `/research` and run the full protocol.

---
name: money-map
description: Finds the painful, expensive, Claude-buildable problem worth solving in any industry. Filters by the 5 Boring Problems framework and by recurring-revenue potential, then picks one specific problem to attack. Use this skill after Industry Download and Ride-Along to convert raw industry research into a single buildable opportunity. Trigger phrases include "money map", "find the painful problem in [industry]", "what should I build for [niche]", "rank the problems", or any request to identify the specific problem worth pursuing.
---

# Money Map

Take everything you know about an industry and find the one painful, expensive, Claude-buildable problem worth attacking. One problem. Ranked. Picked. Done.

## What This Skill Does

**Input:** A specific industry, ideally with Industry Download and Ride-Along already run on it. Raw industry research, friction points from a ride-along narrative, or both.

**Output:** A ranked list of 3-5 specific problems, each filtered through the 5 Boring Problems framework, the Claude-buildability test, and the recurring-revenue test — ending with one clear pick and the rationale for why it's the right first target.

This is the decision-making skill. By the end of running it, you know exactly what problem to take into your discovery calls.

## Why This Skill Exists

Most beginners get stuck at "I have a niche but I don't know what to build." They've researched the industry. They've seen the pain. But they can't pull the trigger on a single problem because every option looks like it might be the wrong one.

Money Map kills that paralysis with hard filters. Most "opportunities" fail one of three tests — they're not painful enough, not expensive enough, or not buildable with Claude in a reasonable timeframe. Run them through the filters and only the real opportunities survive.

## The 5 Boring Problems Framework

Every problem Money Map surfaces gets categorized into one of five types. These are the only categories worth pursuing for a Claude-built B2B service:

1. **Manual repetitive work** — Spreadsheets, paper forms, copy-paste, hours wasted on stuff a machine could do
2. **Compliance or revenue-critical workflows** — One mistake costs the business big (fines, lost contracts, legal trouble)
3. **Outdated software they hate** — Tools from 2005, clunky, glitchy, missing features. They already pay for it and resent it.
4. **Disconnected systems duct-taped together** — Multiple tools that don't talk to each other; humans bridging the gap
5. **Previously impossible** — Things that weren't buildable before AI vision/language models

If a problem doesn't fit one of these five, it's the wrong problem. Skip it.

## The Three Hard Filters

Every problem must pass all three filters or it's cut.

### Filter 1: The Pain Filter
Can the business owner quantify what this problem costs them per month in dollars? If they can't put a number on it, it's not painful enough to pay to solve.

✅ Pass: "This costs us about $15,000/month in declined work."
❌ Fail: "It's annoying and time-consuming."

### Filter 2: The Claude Buildability Filter
Can a non-developer realistically build a working version of this with Claude Code in 1-3 weeks?

✅ Pass: A web app with forms, database, AI-generated outputs, and integrations to one or two APIs (Stripe, Twilio, OpenAI, etc.)
❌ Fail: Requires a custom mobile app, heavy machine learning training, real-time computer vision, or deep operational hardware integration

### Filter 3: The Recurring Revenue Filter
Will this problem keep happening? Can you charge **$1,500/month or more** as an ongoing service to manage it?

This is high-ticket B2B service work, not low-margin SaaS. The floor is $1,500/month — there's no ceiling. Many of these opportunities go to $3K, $5K, $10K/month or more, especially for compliance-critical or revenue-recovery problems where you're directly tied to the business owner's bottom line.

✅ Pass: Ongoing customer follow-up, ongoing compliance reporting, ongoing revenue recovery, ongoing inventory management
❌ Fail: One-time setup, one-time data migration, one-time analysis, anything you can't justify charging at least $1,500/month for ongoing

A problem that fails any one of these filters is cut. Don't argue with the filters.

## How to Use This Skill

When activated with an industry:

### Step 1 — Gather raw signal
- If Ride-Along output is available, extract every friction moment and every "dream system" feature
- If Industry Download output is available, extract every pain point ranked by money loss
- If neither is available, do fresh web research: complaint threads, tool reviews, forum discussions about pain points

### Step 2 — Categorize through the 5 Boring Problems
For each candidate problem, identify which of the 5 categories it falls into. Discard anything that doesn't fit.

### Step 3 — Apply the three hard filters
Run each remaining candidate through:
- The Pain Filter (quantifiable monthly dollar cost?)
- The Claude Buildability Filter (1-3 week Claude Code build?)
- The Recurring Revenue Filter ($1,500+/month retainer floor, no ceiling?)

Cut anything that fails any filter. Don't soft-pass borderline cases.

### Step 4 — Rank the survivors
Rank what's left by total opportunity score = pain × buildability ease × revenue potential. The highest-scoring problem is the pick.

### Step 5 — Output the ranked report and the one pick

## Output Structure

### Section 1: The Candidate Problems (Ranked)

A table or ranked list. For each problem:

- **Problem name** (in the industry's actual language)
- **5 Boring Problems category** (which of the 5 it fits into)
- **Monthly cost to the business** (specific dollar range, sourced from the research)
- **Pain Filter:** ✅ pass / ❌ fail (with one-line rationale)
- **Claude Buildability Filter:** ✅ pass / ❌ fail (with one-line rationale)
- **Recurring Revenue Filter:** ✅ pass / ❌ fail (with one-line rationale)
- **Opportunity score:** 1-10

Show all candidates, including failures, so the user sees the reasoning.

### Section 2: Why The Failed Candidates Failed

A short section listing 1-3 problems that almost worked but got cut, with the specific filter that killed them. This builds the user's pattern recognition for next time.

### Section 3: The Top 3 Survivors — Deep Dive

For each of the top 3 survivors:

**The Specific Problem**
- What's actually broken (in plain language)
- The exact moment it hurts the business owner (timestamp from ride-along if available)
- What they currently do about it (and why that fails)

**Why It Bleeds Money**
- The dollar math: how much they lose per month, with the calculation
- Why this is recurring, not one-time

**The Solution Shape**
- A one-paragraph description of what the software would do
- The 5 Boring Problems category it solves
- Why Claude can build this (the specific mechanics that make it tractable)

### Section 4: The Pick

End with one clear paragraph:

> **"If you only attack one of these first, attack [#1]. Here's why."**

Then 3-5 sentences explaining:
- Why this beats the other two on opportunity score
- What makes it the lowest-risk first build
- What the user should do next (run a discovery call to validate)

## Pro Tips for Better Output

- **Don't fight the filters.** If a problem is exciting but fails the Claude Buildability filter, it's still a fail. Discipline now saves weeks of wasted building later.
- **Quantify aggressively.** "Loses money" is useless. "Loses approximately $8,000-$15,000 per month" is gold. Pull real numbers from research.
- **Watch out for one-shot problems disguised as recurring.** "Help them migrate from QuickBooks" is a one-time job. "Reconcile their books every month" is recurring.
- **Favor the unsexy.** If 50 freelancers on Twitter are pitching solutions for this exact problem, the supply side is saturated. Look one layer deeper into the friction.
- **Use Ride-Along's friction moments directly.** If the ride-along narrative had a 3:17 PM scene where the tech said "did anyone ever follow up on that Camry?" — that's a problem candidate. Pull it verbatim.

## When to Use This Skill

✅ After Industry Download and Ride-Along, to convert research into a buildable target
✅ When you have a niche but don't know what to build
✅ When you have multiple opportunity ideas and need to pick one
✅ Before the first discovery call — to know what problem you're testing for

❌ Don't use without raw industry signal — needs at least one of the upstream skills run first
❌ Don't use to find personal app ideas — this is B2B service work only
❌ Don't use the output as a sales pitch — it's for your decision-making, not the prospect's

## Stacking With Other Skills

Money Map is the third skill in the Step 1 sequence:

1. **Industry Download** — what's this industry like? (facts, language, who pays for what)
2. **Ride-Along** — what does their day actually feel like? (friction moments, dream system)
3. **Money Map** — which specific problem do I attack first? (the decision)

By the end of Money Map, you have one clear target problem and you're ready to move to Step 2: Solve It With Claude (Blueprint Builder).

## Remember

Most opportunities aren't real opportunities. They fail at least one of the three filters. Money Map's job is to be ruthless so your time isn't.

You don't need to find every problem in the industry. You just need to find the one worth attacking first.

**Filter the noise. Find the bleed. Pick the target.**

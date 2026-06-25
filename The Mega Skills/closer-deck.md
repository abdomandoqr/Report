---
name: closer-deck
description: Generates a complete HTML sales presentation that closes the client. Takes a discovery call transcript, extracts the prospect's actual numbers and language, and outputs a self-contained HTML file you can open in Chrome and present immediately. Trigger phrases include "build my closer deck", "create the closing presentation", "build the sales deck for this client", "turn this discovery call into a presentation", or any request to generate a sales deck from discovery notes.
---

# Closer Deck

Turn any discovery call into the exact HTML presentation that closes the deal. A real, ready-to-present file using the prospect's own numbers, in the prospect's own language, with the math doing the selling.

## What This Skill Does

**Input:** A discovery call transcript (or detailed notes covering the prospect's business, problem, current solution, and numbers)

**Output:** A complete, self-contained HTML presentation file. Open it in Chrome. Share screen. Present. Close the deal.

The HTML is a real file — not markdown describing slides, not a slide outline, not a screenshot mockup. A working presentation with keyboard navigation, professional styling, and the prospect's numbers populated throughout.

## Why This Skill Exists

Most beginners lose deals between the discovery call and the close because they walk in with:
- Generic pitch decks built in Canva that take 4 hours to make
- Improvised verbal pitches with no visuals
- Markdown summaries that aren't actually presentable

None of that closes deals. What closes deals is a clean, professional 6-slide presentation that uses the prospect's actual numbers, frames the gap between their reality and their potential in dollars, and lands the offer like the obvious next step.

This skill builds that presentation in 30 seconds.

## The 6-Slide Structure

Every Closer Deck has exactly 6 slides. Don't add slides. Don't subtract slides. Don't reorder them. This structure has closed real $2,500/month deals on real sales calls.

### Slide 1: Where You Are Today
The prospect's current state, in their numbers. Direct quotes from their discovery call where useful. Format: a few specific metrics laid out as big visible numbers — operations, volume, revenue per X, close rate.

### Slide 2: What This Problem Is Costing You
Quantify the pain in dollars per month or per year. Use the prospect's own numbers from Slide 1 to do the math. Be conservative — under-promise so the math feels safe.

### Slide 3: What's Possible When You Solve It
Paint the new reality with specific dollar figures. Show recoverable revenue, not vague "growth." Use conservative recovery percentages so the math holds up to scrutiny.

### Slide 4: The Gap
One slide. One visual. One number. The financial gap between current state and possible state. **This is the slide that does most of the closing.**

### Slide 5: Here's What I'll Do For You
Your offer in their language. Bullet points, not paragraphs. Frame as outcomes ("recover declined revenue") not features ("AI-powered SMS engine").

### Slide 6: Investment + Performance Guarantee
Setup fee + monthly retainer. Frame against the gap from Slide 4. Include performance guarantee to remove risk.

## How to Use This Skill

When activated with a discovery call transcript:

### Step 1 — Extract the prospect's actual numbers
Pull every dollar figure, every percentage, every operational metric they mentioned. These are non-negotiable for Slides 1-4. If a number wasn't mentioned in the call, **do not invent one**. Either flag it for the user to fill in, or omit that metric.

### Step 2 — Identify the core problem
What's the one painful, expensive thing they admitted on the call? That's the spine of the entire deck.

### Step 3 — Pull their language
If they said "decline work" not "lost revenue," use "decline work." If they said ARO not "average ticket," use ARO. Match their vocabulary throughout.

### Step 4 — Generate the HTML file
Use the template at `assets/template.html` as the shell. Inject the 6 slides into the `SLIDES_PLACEHOLDER` location. Replace `{{TITLE}}` with the prospect's business name + "Proposal."

### Step 5 — Output the complete HTML file
Save the file with a descriptive name like `closer-deck-{business-name}.html`. The user opens it in Chrome and presents.

### Step 6 — Output a separate delivery script
After the HTML, output a markdown delivery script (the user reads this off a second screen during the call). Cover: what to say between slides, where to pause, when to shut up after Slide 6.

## Slide HTML Patterns

Use these exact HTML patterns for each slide. Don't deviate from the structure.

### Slide 1 Pattern — Where You Are Today

```html
<div class="slide active">
  <div class="eyebrow">Current State — {Business Name}</div>
  <h1 class="headline">Where you are <span class="accent">today</span></h1>
  <div class="metrics">
    <div class="metric">
      <div class="value">{NUMBER}</div>
      <div class="label">{METRIC LABEL}</div>
    </div>
    <div class="metric">
      <div class="value">${AMOUNT}</div>
      <div class="label">{METRIC LABEL}</div>
    </div>
    <div class="metric">
      <div class="value">{PERCENT}%</div>
      <div class="label">{METRIC LABEL}</div>
    </div>
  </div>
</div>
```

### Slide 2 Pattern — What This Is Costing You

```html
<div class="slide">
  <div class="eyebrow">The Problem</div>
  <h1 class="headline">What this is <span class="accent">costing you</span></h1>
  <p class="subhead">{One sentence describing the specific bleeding workflow in their language.}</p>
  <div class="big-number red">${LOST_AMOUNT}<span style="font-size:0.4em;color:#888;font-weight:500"> / month</span></div>
  <div class="big-number-label">{Specific description of what this represents}</div>
</div>
```

### Slide 3 Pattern — What's Possible

```html
<div class="slide">
  <div class="eyebrow">The Opportunity</div>
  <h1 class="headline">What's possible when you<br><span class="accent">solve it</span></h1>
  <p class="subhead">{Conservative recovery percentage rationale, in their language.}</p>
  <div class="big-number green">${RECOVERABLE_AMOUNT}<span style="font-size:0.4em;color:#888;font-weight:500"> / month</span></div>
  <div class="big-number-label">Recoverable Revenue • Conservative Estimate</div>
</div>
```

### Slide 4 Pattern — The Gap (THE money shot)

```html
<div class="slide">
  <div class="eyebrow">The Gap</div>
  <h1 class="headline">The difference between<br>where you are and<br><span class="accent">where you could be</span></h1>
  <div class="compare">
    <div class="compare-card">
      <div class="compare-label">Today</div>
      <div class="compare-value">$0 recovered</div>
      <div class="compare-sub">No follow-up system in place</div>
    </div>
    <div class="compare-card highlight">
      <div class="compare-label">Possible</div>
      <div class="compare-value">${RECOVERABLE_AMOUNT} / mo</div>
      <div class="compare-sub">Same shop, same staff, same customers</div>
    </div>
  </div>
</div>
```

### Slide 5 Pattern — Here's What I'll Do

```html
<div class="slide">
  <div class="eyebrow">The Solution</div>
  <h1 class="headline">Here's what <span class="accent">I'll do</span> for you</h1>
  <ul class="bullets">
    <li><span class="check">✓</span><div>{Outcome-framed bullet 1}</div></li>
    <li><span class="check">✓</span><div>{Outcome-framed bullet 2}</div></li>
    <li><span class="check">✓</span><div>{Outcome-framed bullet 3}</div></li>
    <li><span class="check">✓</span><div>{Outcome-framed bullet 4}</div></li>
    <li><span class="check">✓</span><div>{Outcome-framed bullet 5}</div></li>
  </ul>
</div>
```

### Slide 6 Pattern — Investment

```html
<div class="slide">
  <div class="eyebrow">The Investment</div>
  <h1 class="headline">A <span class="accent">${MONTHLY}/month</span> investment to recover <span class="accent">${RECOVERABLE_AMOUNT}/month</span></h1>
  <div class="investment">
    <div class="invest-card">
      <div class="invest-amount">${SETUP_FEE}</div>
      <div class="invest-period">One-time setup • configuration • data integration</div>
    </div>
    <div class="invest-card">
      <div class="invest-amount">${MONTHLY}<span style="font-size:0.5em;color:#888;font-weight:500"> / mo</span></div>
      <div class="invest-period">Ongoing service • month-to-month</div>
    </div>
  </div>
  <div class="guarantee">
    <strong>Performance guarantee:</strong> If we don't recover at least the setup fee in your first 30 days, we work for free until we do.
  </div>
</div>
```

## Pricing Guidelines

Pricing depends on the dollar gap from Slide 4. Use these anchors:

- **Setup fee:** 1x to 2x the monthly retainer. For most B2B deals: $1,500-$5,000.
- **Monthly retainer floor:** $1,500/month minimum. No ceiling.
- **Rule of thumb:** Monthly retainer should be roughly 10-20% of the conservative recoverable amount on Slide 3. If they recover $20K/month, you can charge $2K-$4K/month.
- **Performance guarantee:** Always include. It removes risk from the prospect's decision and rarely needs to be invoked because a real Closer Deck only goes to prospects with quantifiable problems.

## Companion Output: Delivery Script

After the HTML, output a markdown delivery script the user keeps on a second screen during the call. Format:

```markdown
# Closer Deck Delivery Script — {Business Name}

## Pre-call setup
- Open the HTML file in Chrome before the call starts
- Have your second screen ready with this script
- Share the Chrome window, not the script

## Slide 1: Where You Are Today
**What to say:** "Just to recap the numbers you shared — {pull 1-2 specific numbers}. Does that look right?"
**Goal:** Get verbal confirmation. They nod yes. You're aligned.

## Slide 2: What This Is Costing You
**What to say:** "Based on what you told me, here's what this is actually costing you each month. Conservatively."
**Goal:** Surface the pain. Don't elaborate. Let the number land.

## Slide 3: What's Possible
**What to say:** "Now here's what's possible if we recover even a conservative percentage of that."
**Goal:** Open the door to the upside.

## Slide 4: The Gap
**What to say:** "And this is the gap. Every month you don't have a system, this is what's walking out the door."
**Goal:** This slide does the closing. PAUSE here. Let them sit with it.

## Slide 5: Here's What I'll Do
**What to say:** "Here's what I do for shops like yours."
**Goal:** Read the bullets out loud. Don't oversell.

## Slide 6: Investment
**What to say:** "$X to set up, $Y per month after that. And we guarantee performance in your first 30 days."
**Goal:** Then SHUT UP. Let them respond first.

## Likely objections and reframes
{List 3-5 specific objections from the discovery call with reframes}

## The close
- Don't ask "do you want to move forward?"
- Ask: "What's the best way to get this set up for you this week?"
- Then SHUT UP.
```

## Pro Tips for Better Output

- **Always use the prospect's exact numbers.** If they said $475K, the deck says $475K. Not "around half a million."
- **Always be conservative on the upside.** If 30% is recoverable, model 15%. Under-promise, over-deliver.
- **Never lead with the price.** Slide 6 is the last slide for a reason. The gap from Slide 4 must do the heavy lifting first.
- **One offer, not three tiers.** Three tiers create decision paralysis on a sales call. Pick one offer. Make it the right one.
- **Match their vocabulary.** Use ARO if they said ARO. Use "decline work" if they said decline work. Industry language signals you know the business.
- **The headline of Slide 6 does double duty.** It contains both the offer AND the value frame in one line: "${MONTHLY}/month investment to recover ${RECOVERABLE}/month." That framing is your single biggest closing weapon.

## When to Use This Skill

✅ After a discovery call where the prospect admitted a real, expensive problem
✅ When you have specific dollar figures from the prospect
✅ When you're ready to actually close, not just explore

❌ Don't use without a discovery call first — generic decks don't close
❌ Don't use if the prospect didn't share numbers — go back and get them
❌ Don't use for prospects who haven't acknowledged the problem — close = pain × urgency × trust, you need all three

## Remember

The closing deck doesn't sell the software. The prospect's own numbers sell the software.

Your job is to put their numbers in front of them, frame the gap, and make the offer feel like the obvious next step.

**6 slides. 15 minutes. One yes.**

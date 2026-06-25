---
name: blueprint-builder
description: Turns any discovery call transcript into a complete software build plan ready to drop into Claude Code. Use this skill when the user has a discovery call recording or transcript and needs to convert it into a buildable spec. Trigger phrases include "build me a blueprint", "turn this transcript into a build plan", "blueprint builder", "create the build plan from this call", or any request to convert a client conversation into a software architecture.
---

# Blueprint Builder

Turn a discovery call transcript into a complete software build plan that drops straight into Claude Code. The client tells Claude what to build. You sit there and listen.

## What This Skill Does

**Input:** A discovery call transcript (or detailed notes covering the prospect's business, current workflow, problem, and desired outcome)

**Output:** A complete Claude.MD-style build plan — project overview, target users, core features (MVP only), tech stack recommendation, database structure, and implementation phases.

This is the file you literally drop into Claude Code to build the software.

## Why This Skill Exists

Most beginners overthink the build. They try to architect a Salesforce competitor when the client just needs three screens that talk to a database.

The discovery call already contains the answer. The client has told you what's broken, what they want, and how they describe success. Blueprint Builder extracts that signal from the noise of a 30-minute conversation and shapes it into a build spec.

## The Core Principle

**Build the smallest possible version that solves the one specific problem.**

Not the next Salesforce. Not a SaaS empire. Not a "platform." One painful problem, one small piece of software, one happy client paying you monthly.

## How to Use This Skill

When the user activates this skill with a discovery call transcript:

1. **Extract the actual problem.** Strip away rapport-building chitchat and identify the specific bleeding workflow they admitted to.
2. **Identify the dollar pain.** Pull every number they mentioned — declined work, hours wasted, revenue leaked.
3. **Map their current workflow.** What tools are they using now? Where do those tools fail?
4. **Define the MVP.** The smallest possible piece of software that solves their one specific problem. If you can't build it in a week with Claude Code, it's too big.
5. **Pick a tech stack you can actually build with.** Default to Next.js + Supabase + Stripe unless the problem demands something different.
6. **Output the full blueprint** in the structure below.

## Output Structure

### 1. Project Overview
- **Project name** (suggest a working title)
- **One-sentence pitch** in the client's language
- **Core problem solved** (their words, not yours)
- **Who uses it** (the actual humans in the business who will touch it daily)

### 2. Target User Profile
- **Primary user**: who logs in, what they do all day
- **Secondary users**: anyone else who interacts with the software
- **Their tech literacy level**: assume low for boring-industry clients

### 3. The Problem (Their Words)
- The painful workflow as they described it
- Exact dollar figures they mentioned
- What they currently use to (poorly) solve it
- Why those existing solutions fail

### 4. Core Features (MVP — 3 to 5 maximum)

For each feature:
- **Feature name**
- **What it does** in one sentence
- **The user action** that triggers it
- **The output** the user sees

Be ruthless. Anything that isn't strictly required to deliver the outcome on Day 1 goes into "Phase 2" instead.

### 5. Phase 2 Features (Out of Scope for MVP)
- Things the client mentioned that are nice-to-have
- Stuff you'll upsell later as a v2 build
- Don't promise these — note them for the proposal

### 6. Tech Stack Recommendation
- **Frontend** (default: Next.js 14 with App Router)
- **Backend** (default: Next.js API routes or Supabase Edge Functions)
- **Database** (default: Supabase / Postgres)
- **Auth** (default: Supabase Auth or Clerk)
- **Payments if needed** (default: Stripe)
- **Hosting** (default: Vercel)
- **External integrations** (Twilio, OpenAI, etc.) only if required by the spec

### 7. Database Schema
A simple table-by-table breakdown:
- **Table name**
- **Key columns and types**
- **Relationships to other tables**

Keep it minimal. 3-7 tables is usually right for an MVP.

### 8. Implementation Phases (For Claude Code)
Break the build into 4-6 sequential phases that Claude Code can execute one at a time:

- **Phase 1: Foundation** (project setup, auth, database schema)
- **Phase 2: Core feature 1**
- **Phase 3: Core feature 2**
- **Phase 4: Integrations** (any external APIs)
- **Phase 5: Polish** (UI cleanup, error states, loading states)
- **Phase 6: Deploy**

Each phase should be a self-contained prompt the user can paste into Claude Code.

### 9. The Claude Code Kickoff Prompt
End with a single, ready-to-paste prompt the user can drop into Claude Code to start the build. Format it clearly so they can copy and run it immediately.

## Pro Tips for Better Output

- **Don't invent features the client didn't ask for.** If they didn't mention reporting, don't build reporting. Add it later.
- **Default to boring tech.** Next.js + Supabase + Stripe handles 90% of these builds. Don't reach for exotic frameworks.
- **Skip the admin panel on Day 1.** You can manage data via the database directly until v2. This saves days of build time.
- **Build the workflow, not the app.** If the client's workflow is "intake form → AI analysis → email result," that's three screens — not a 50-screen platform.
- **Include the client's real numbers in the build plan.** If they said they have 50 customers a month, build for 50, not 50,000.

## When to Use This Skill

✅ After a discovery call where the client described their workflow and pain
✅ When you have specific numbers and current-tool details from the prospect
✅ Before writing a proposal — the blueprint anchors the scope and pricing

❌ Don't use without a real discovery call — generic blueprints are useless
❌ Don't use to build personal apps — this is for B2B service work
❌ Don't use if the client hasn't admitted a real, expensive problem

## Remember

You're not building software. You're delivering an outcome. The blueprint is just the path.

**The client tells Claude what to build. You just sit there and listen.**

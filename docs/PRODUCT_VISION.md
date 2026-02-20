# Savdhaan AI — Product Vision

> Last updated: 2026-02-20

---

## One-Line Vision

**Savdhaan AI is an AI risk copilot that helps people make safer decisions — starting with scam detection, expanding to any risky decision.**

---

## The Insight

People don't just need scam detection. They need a second brain for risky situations.

Every day, hundreds of millions of people face moments of doubt:

- "Is this message a scam?"
- "Is this job offer real?"
- "Is this rental lease normal?"
- "Is this investment pitch too good to be true?"
- "Is this contract clause fair?"
- "Is this online deal legitimate?"

Today, they either:
1. Ask a friend (who may not know better)
2. Google it (and get generic results)
3. Ignore the doubt (and sometimes get burned)
4. Overthink it (and miss legitimate opportunities)

**Savdhaan AI gives them an instant, evidence-based risk assessment for any of these situations.**

---

## Strategy: Hook → Habit → Platform

```
Phase 1: HOOK                Phase 2: HABIT              Phase 3: PLATFORM
━━━━━━━━━━━━━━━━            ━━━━━━━━━━━━━━━━            ━━━━━━━━━━━━━━━━━
Scam detection              + Decision risk              Full risk copilot

"Is this a scam?"           "Is this a good deal?"      "Should I do this?"

Emotional, viral            Valuable, retentive         Essential, daily-use
Free tier                   Premium tier                B2B + Consumer
India-first                 + USA/Global                Multi-market
WhatsApp sharing            Web + Mobile                API + Integrations
Scam cards                  Risk reports                Advisory platform

Acquisition engine          Monetization engine         Platform moat
```

### Why This Sequence

| Phase | Why it comes first |
|-------|--------------------|
| **Scam detection** | Most emotional, most shareable, lowest barrier. A scared person forwards a scam card to 50 people. That's free, organic, viral growth. |
| **Decision risk** | Once users trust Savdhaan for scams, they naturally ask "can it check this job offer too?" Expansion is pull-based, not push-based. |
| **Platform** | With millions of risk assessments, you have the data moat. B2B (banks, fintech, telecom embed your API), consumer premium, and community intelligence. |

---

## Product Categories

### Category 1: Scam Detection (MVP 1)

**The hook. The viral engine. The trust builder.**

| Input | What user sends |
|-------|----------------|
| Suspicious SMS | "Your SBI account will be blocked. Update KYC: http://..." |
| WhatsApp forward | Screenshot of a "you've won" message |
| Email | "Your Netflix payment failed, update billing here" |
| Social DM | "I'm a recruiter from Google, send your resume to..." |
| UPI request | Screenshot of unexpected collect request |

| Output | What user gets back |
|--------|-------------------|
| Risk score | 0-100 with clear level (critical/high/medium/low) |
| Scam type | Phishing, UPI fraud, job scam, investment scam, etc. |
| Evidence | Why we think this — grounded in threat intel + pattern analysis |
| Actions | What to do right now — block, report, do not click, etc. |
| Scam card | Shareable card to forward and warn others |

**Key insight**: The scam card is the growth loop. One person checks → shares card → 50 people see it → some of them check their own messages → cycle repeats.

**Market**: India (UPI fraud, SMS scams, WhatsApp forwards), USA (phishing, tech support scams), UK/Canada/Australia.

**Threat intel**: PhishTank, Google Safe Browsing, URLhaus, Spamhaus, WHOIS.

**Revenue**: Free (ad-supported or freemium). This is for reach, not revenue.

---

### Category 2: Job & Offer Review (MVP 2-3)

**"Is this job offer real? Are the terms normal?"**

| Input | What user sends |
|-------|----------------|
| Job offer email | Full offer letter or key terms |
| Recruiter DM | LinkedIn/email outreach from unknown recruiter |
| Freelance gig | Upwork/Fiverr message with unusual terms |
| Internship offer | "Congratulations! Pay Rs 5000 registration fee to confirm." |

| Output | What user gets back |
|--------|-------------------|
| Legitimacy score | How real does this look? |
| Red flags | Upfront payment requests, vague company details, unrealistic salary |
| Company check | Domain age, LinkedIn presence, Glassdoor reviews (if available) |
| Comparison | "This salary is [above/below/within] range for this role and location" |
| Actions | Verify on company website, check LinkedIn, never pay to get a job |

**Why it monetizes**: Job seekers are anxious and willing to pay for confidence. A $5/month "job offer checker" for active job seekers is an easy sell.

---

### Category 3: Rental & Lease Review (MVP 3+)

**"Is this lease clause normal? What should I negotiate?"**

| Input | What user sends |
|-------|----------------|
| Lease snippet | Photo or text of specific clauses |
| Rental listing | Screenshot of suspiciously good deal |
| Landlord message | "Pay deposit via Zelle before viewing" |
| Broker terms | Commission structure, lock-in period |

| Output | What user gets back |
|--------|-------------------|
| Risk flags | Unusual clauses, missing tenant protections, hidden fees |
| Clause-by-clause | What each clause means in plain language |
| Market comparison | "This deposit is [normal/high/unusual] for this area" |
| Negotiation tips | "You can ask to remove this clause — here's how" |
| Actions | What to verify, what to negotiate, when to walk away |

**Why it monetizes**: Rental decisions involve thousands of dollars. $10 to review a lease before signing is trivial compared to the risk.

---

### Category 4: Investment & Financial Review (MVP 3+)

**"Is this investment pitch realistic?"**

| Input | What user sends |
|-------|----------------|
| Investment pitch | WhatsApp group message, social media ad, email |
| Crypto offer | "10x returns guaranteed" messages |
| Insurance policy | Terms screenshot or document |
| Loan offer | "Instant loan, no documents needed" |

| Output | What user gets back |
|--------|-------------------|
| Reality check | "Returns of 50% monthly are not realistic in any legitimate investment" |
| Red flags | Guaranteed returns, pressure tactics, unregistered entities |
| Regulatory check | Is this entity registered with SEBI/SEC/FCA? (future integration) |
| Historical patterns | "This matches patterns seen in [Ponzi/pyramid/pump-and-dump] schemes" |
| Actions | Verify with regulator, never share OTP/password, report if suspicious |

---

### Category 5: Contract & Terms Review (Future)

**"What am I actually agreeing to?"**

| Input | What user sends |
|-------|----------------|
| Terms of service | Screenshot of app/service terms |
| Contract clause | Specific section of any agreement |
| Purchase agreement | Car, electronics, services |
| Subscription terms | "Free trial" fine print |

| Output | What user gets back |
|--------|-------------------|
| Plain language | What this actually means, no legal jargon |
| Risk flags | Auto-renewal, cancellation penalties, data sharing, liability waivers |
| Comparison | "This is [standard/unusual] for this type of service" |
| Hidden costs | Fees, charges, or obligations buried in the text |
| Actions | What to ask about, what to negotiate, what to watch for |

---

## Unified UX Across All Categories

The user experience is identical regardless of category:

```
1. PASTE / UPLOAD
   Text, screenshot, document snippet, forwarded message

2. SELECT CATEGORY (or auto-detect)
   "What are you checking?"
   → Suspicious message (scam check)
   → Job offer
   → Rental / lease
   → Investment / financial
   → Contract / terms
   → Something else

3. GET INSTANT ASSESSMENT (< 5 seconds)
   → Risk score + level
   → Red flags with evidence
   → Plain language explanation
   → What to do next

4. SHARE (if risky)
   → Shareable card for messaging apps
   → "Savdhaan checked this — here's what it found"
```

---

## Technical Architecture — Category Extensibility

The scan pipeline is already category-agnostic:

```
Input → [OCR if image] → Entity Extraction → Analysis → Risk Score → Evidence → Actions
```

What changes per category:

| Pipeline step | Scam detection | Job offer review | Lease review |
|--------------|---------------|-----------------|-------------|
| Entity extraction | URLs, phones, emails, UPI, crypto | Company names, salary figures, job titles | Amounts, dates, clause types |
| External checks | PhishTank, Safe Browsing, WHOIS | Company domain age, LinkedIn (future) | Market rent data (future) |
| LLM analysis | Scam taxonomy + threat signals | Legitimacy patterns + offer norms | Clause risk patterns + tenant rights |
| Action engine | Block, report, don't click | Verify, negotiate, ask questions | Negotiate, verify, walk away |

**Implementation**: Each category has its own:
- LLM system prompt (classification framework)
- Entity extraction schema (what to look for)
- Risk framework (what constitutes high/low risk)
- Action templates (what to recommend)

The pipeline, infrastructure, API, database, and UX are shared.

Adding a new category = new config + new prompts. No code changes to the core pipeline.

### API Extension

```json
POST /api/v1/scan
{
  "content": "...",
  "content_type": "text",
  "category": "scam_check",      // NEW FIELD
  "channel": "whatsapp",
  "locale": "en"
}
```

`category` values:
- `scam_check` (default, MVP 1)
- `job_offer` (MVP 2-3)
- `rental_lease` (MVP 3+)
- `investment` (MVP 3+)
- `contract` (future)
- `auto` (auto-detect category from content)

---

## Market Sizing

### Scam Detection (Phase 1)

| Market | Size | Savdhaan opportunity |
|--------|------|---------------------|
| India | 1.2B mobile users, 500M+ WhatsApp users, Rs 10K+ crore lost to fraud annually | Massive. Underserved. WhatsApp-native distribution. |
| USA | 330M population, $10B+ lost to scams annually (FTC 2024) | Large. Competition exists but fragmented. |
| UK/Canada/Australia | 100M+ combined, growing scam problem | Medium. English-speaking, high digital adoption. |

### Decision Risk Copilot (Phase 2-3)

| Category | Addressable users | Willingness to pay |
|----------|------------------|--------------------|
| Job seekers | 200M+ globally active at any time | High — career decisions are high-stakes |
| Renters | 100M+ in India + USA alone | High — thousands of dollars at stake |
| Retail investors | 150M+ demat accounts in India, 60M+ in USA | High — money directly at risk |
| Contract signers | Everyone, eventually | Medium — depends on contract value |

**TAM progression**:
- Phase 1 (scam only): ~$500M (security/anti-fraud tools)
- Phase 2-3 (risk copilot): ~$5B+ (decision support + financial advisory tools)

---

## Competitive Landscape

### Scam Detection Competitors

| Competitor | What they do | Our advantage |
|-----------|-------------|---------------|
| **Truecaller** | Caller ID + spam | Phone calls only. No message content analysis. No sharing. |
| **Google Messages** | Built-in SMS spam filter | SMS only. No explanation. No cross-channel. |
| **Norton Genie** | AI scam detection (discontinued 2024) | Dead product. Was text-only, no threat intel, no sharing. |
| **ScamAdviser** | Website reputation | URLs only. No message context. No mobile. |

### Decision Risk — No Direct Competitor

Nobody offers a **unified risk copilot** across scams, jobs, leases, investments, and contracts. Individual categories have tools, but no one connects them under a single trust brand.

This is the strategic moat: **Savdhaan becomes the brand people trust for "is this safe?"** across any domain.

---

## Revenue Model

| Phase | Model | Pricing |
|-------|-------|---------|
| **Phase 1** | Freemium | Free: 10 scam checks/hour. Enough for most users. |
| **Phase 2** | Premium consumer | $5-10/month: Unlimited scans, all categories, scan history, priority processing |
| **Phase 3** | B2B API | $0.01-0.05/scan: Banks, fintech, telecom, marketplaces embed Savdhaan |
| **Phase 3** | Enterprise | Custom pricing: White-label risk assessment for financial institutions |

**Unit economics target**:
- Free user: $0 revenue, ~$0.02/scan cost (LLM API). Justified by viral growth.
- Premium user: $7/month average, ~$0.50/month cost. Strong margin.
- B2B: Volume-based, high margin after fixed costs.

---

## Brand

**"Savdhaan"** (सावधान) = "Be alert. Be cautious. Be aware."

It's not scam-specific. It's a universal warning. It works for:
- सावधान — this is a scam
- सावधान — this job offer has red flags
- सावधान — this lease clause is unusual
- सावधान — this investment pitch is unrealistic

The brand scales with the product.

**Tagline options**:
- "Check before you click. Check before you sign. Check before you send."
- "Your AI risk copilot."
- "Doubt it? Check it."
- "Think before you trust. Savdhaan before you act."

---

## Success Metrics (North Stars)

| Metric | Phase 1 target | Phase 2 target | Phase 3 target |
|--------|---------------|---------------|---------------|
| **Monthly active users** | 100K | 1M | 10M |
| **Scans per day** | 10K | 100K | 1M |
| **Scam cards shared per day** | 2K | 20K | 200K |
| **Premium conversion** | — | 3-5% | 5-8% |
| **B2B API customers** | — | — | 50+ |
| **Revenue (MRR)** | $0 (pre-revenue) | $50K | $500K |
| **NPS** | > 50 | > 60 | > 65 |

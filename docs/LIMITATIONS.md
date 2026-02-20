# Savdhaan AI — Limitations & Adversarial Resilience

> Last updated: 2026-02-20

---

## Philosophy

Savdhaan AI is a **scam detection assistant, not a guarantee of safety**. We must be
radically honest with users about what we can and cannot do. Overpromising erodes trust
faster than any false negative.

Our product messaging must always communicate:
1. We significantly reduce risk — we don't eliminate it
2. We explain what we checked and what we couldn't
3. Human judgement is always the final layer
4. When in doubt, verify through a known channel (call your bank directly, not the number in the message)

---

## What We Can Detect Well

| Scenario | Why we're effective | Confidence |
|----------|-------------------|------------|
| **Mass phishing** — "Update your KYC", "Verify your account" with malicious links | URLs hit threat intel databases, domains are new, templates match known patterns | High |
| **Known scam campaigns** — lottery, prize, advance fee scams | Well-documented patterns, urgency + money request signals are clear | High |
| **Malware links** — URLs distributing malware or trojans | URLhaus, Safe Browsing, VirusTotal databases catch most known URLs | High |
| **Brand impersonation** — fake bank, fake Amazon, fake government messages | Domain similarity detection, known phishing domains, pattern matching | High |
| **UPI/payment fraud** — fake collect requests, QR code scams with suspicious UPI IDs | Pattern analysis, known fraud UPI patterns, urgency signals | Medium-High |
| **Job scams** — fake offers requiring upfront fees or personal info | Pattern matching, known scam templates, red flag combinations | Medium-High |
| **Investment scams** — unrealistic returns, pressure to join groups | Pattern analysis, known Ponzi/pyramid language patterns | Medium |

---

## What We Cannot Detect (or Detect Poorly)

### Hard Limitations — Fundamentally Difficult

| Scenario | Why it's hard | What we tell the user |
|----------|--------------|----------------------|
| **Personal social engineering** — "Hey, this is your boss. Transfer money urgently" | No technical indicators. No URLs, no links. Just manipulation. We don't know who your boss is. | "No scam indicators detected. However, we cannot verify the sender's identity. If this involves money or sensitive info, verify by calling them on a known number." |
| **Compromised real accounts** — Message from your friend's hacked WhatsApp | The sender IS your friend's real account. No spoofing to detect. | "This message comes from a real account, but accounts can be compromised. If the request is unusual, verify through another channel." |
| **Context-dependent scams** — "Your order #4823 is delayed, pay customs fee" | We don't know if you actually have an order. The message might be legitimate. | "We cannot verify whether this relates to a real transaction. Check your order status directly on the retailer's official app or website." |
| **Brand-new scam types** — Novel approaches never seen before | No patterns in our database, no matching threat intel, LLM hasn't seen this pattern in training | "No known scam patterns matched. This doesn't guarantee safety. If something feels off, trust your instincts." |
| **Legitimate-but-suspicious** — Aggressive but real marketing, real debt collectors, real government notices | These genuinely look like scams but aren't. Tone and urgency overlap with scam patterns. | "This message shows some warning signs common in scams, but may be legitimate. Verify by contacting the organization directly through their official website." |
| **Image-only scams with no text** — QR codes that lead to malicious sites, images with embedded phone numbers in decorative fonts | OCR may miss stylized text, QR code destinations aren't checked (yet) | "We could not extract enough information from this image for a reliable assessment." |
| **Voice/video references** — "Call this number" (the scam happens on the call, not in the text) | We analyze text, not what happens when you call | "This message directs you to a phone call. We cannot assess what happens on the call. Be cautious about sharing personal or financial information." |

### Soft Limitations — Detectable But Not Reliably

| Scenario | Current accuracy | Improvement path |
|----------|-----------------|-----------------|
| **Regional scams in local languages** | Medium — Claude handles Hindi/Tamil/Telugu but misses cultural context | Community reports + region-specific training data |
| **Slowly evolving scams** | Medium — LLM catches some, misses subtle shifts | Feedback loop + scam card analytics to spot new trends |
| **Multi-step scams** | Low — first message may be harmless ("Hi, how are you?") | Future: conversation context analysis (with user consent) |
| **Deepfake references** | Low — "Watch this video of [celebrity] recommending..." we can't analyze the video | Future: media analysis integration |

---

## Honest User Messaging Framework

### Every Scan Result Must Include

1. **What we checked** — "We verified URLs against 5 threat databases, checked domain age, and analyzed message patterns"
2. **What we couldn't check** — "We cannot verify sender identity or confirm whether this relates to a real transaction you made"
3. **Confidence qualifier** — Never absolute language

### Language Guidelines

| Never say | Instead say |
|-----------|-------------|
| "This message is safe" | "No scam indicators detected in our checks" |
| "This is definitely a scam" | "This message shows strong scam indicators" (even at 95+ score) |
| "You're protected" | "Here's what we found — use this to make an informed decision" |
| "100% accurate" | "Our detection covers known scam patterns and databases" |
| "Trust our results" | "Our analysis is one input — combine it with your own judgement" |

### Risk Level Messaging

| Level | Score | User-facing message |
|-------|-------|-------------------|
| **Critical** | 80-100 | "Strong scam indicators detected. We strongly recommend you do not engage with this message. [evidence]" |
| **High** | 60-79 | "Multiple warning signs detected. Exercise extreme caution. [evidence]" |
| **Medium** | 40-59 | "Some suspicious elements found. Proceed with caution and verify independently. [evidence]" |
| **Low** | 20-39 | "Minor concerns noted, but likely legitimate. Stay alert. [details]" |
| **No indicators** | 0-19 | "No scam indicators detected in our checks. However, no automated system is perfect. If something feels wrong, trust your instincts and verify directly." |
| **Insufficient data** | N/A | "We don't have enough information to assess this reliably. When in doubt, verify through official channels." |

---

## Adversarial Abuse — Scammers Using Savdhaan AI

### The Threat

Scammers can create accounts and use Savdhaan AI to:
1. **Test their messages** — iterate until they bypass detection
2. **Understand our detection** — learn which signals trigger alerts
3. **Reverse-engineer our prompts** — understand how the LLM classifies content
4. **Automate evasion** — build tools that auto-modify scam messages until they pass

This is not hypothetical. It happens to every security product.

### Anti-Abuse Strategy — Defense in Depth

We cannot prevent all abuse, but we can make it **expensive, slow, and detectable**.

#### Layer 1: Information Asymmetry

**Don't give scammers a free debugging tool.**

```
Normal user response:
{
  "risk_score": 87,
  "risk_level": "critical",
  "scam_type": "phishing",
  "explanation": "This message contains a link to a domain registered 2 days ago
                  that is flagged in phishing databases...",
  "evidence": [
    { "source": "phishtank", "detail": "URL matches known phishing page" },
    { "source": "whois", "detail": "Domain registered 2 days ago" }
  ]
}

Suspected tester response (after abuse score triggers):
{
  "risk_score": 87,
  "risk_level": "critical",
  "scam_type": "phishing",
  "explanation": "This message shows strong indicators of a phishing scam.",
  "evidence": []   // Sources not disclosed
}
```

The user still gets the verdict. But the scammer doesn't get a roadmap for evasion.

#### Layer 2: Behavioral Detection

Track patterns that distinguish normal users from testers:

| Signal | Normal user | Scammer testing |
|--------|------------|----------------|
| **Scan frequency** | 1-3 per week | 10+ per hour |
| **Content variation** | Different messages each time | Same message with small tweaks |
| **Flagged rate** | Mix of safe and risky | Mostly flagged content |
| **Time pattern** | Random, during waking hours | Systematic, possibly automated |
| **Entity overlap** | Different URLs/phones each scan | Same entities appearing repeatedly |
| **Account age vs volume** | Gradual ramp-up | High volume immediately |

Each signal contributes to an **abuse score** (0-100) per API key:

```python
abuse_signals = {
    "high_frequency":       scans_last_hour > 8,           # near rate limit
    "iterative_testing":    similar_content_ratio > 0.7,    # >70% scans are variants
    "high_flag_rate":       flagged_ratio > 0.8,            # >80% of scans are flagged
    "entity_reuse":         unique_entities_ratio < 0.3,    # same URLs/phones recycled
    "rapid_account":        account_age_hours < 1 and scans > 5,
    "burst_pattern":        scans_last_10_min > 5,
}

abuse_score = weighted_sum(abuse_signals)
```

#### Layer 3: Progressive Response Degradation

As abuse score increases, reduce information disclosure:

| Abuse Score | Response |
|-------------|----------|
| 0-30 | Full response with all evidence and sources |
| 31-60 | Full verdict, simplified evidence (no source names) |
| 61-80 | Verdict only, no evidence details, CAPTCHA on next scan |
| 81-100 | Rate limited to 1 scan/hour, minimal response, account flagged for review |

This is **never communicated to the user**. From their perspective, the API just
returns less detail. They don't know they've been flagged.

#### Layer 4: Semantic Fingerprinting

Hash the **semantic structure** of scam messages, not the exact text:

```
Original:  "You won Rs 10 lakh! Click here: bit.ly/abc"
Variant 1: "You won Rs 25 lakh! Click here: bit.ly/xyz"
Variant 2: "You won $50,000! Claim now: t.co/def"

All three share the same semantic fingerprint:
  [prize_claim] + [urgency] + [shortened_url] + [monetary_value]
```

When we detect iterative testing of the same semantic pattern across any account,
that pattern gets **boosted in our detection** — making it harder for all scammers,
not just the one testing.

#### Layer 5: Intelligence Harvesting

Scammers testing on our platform are **giving us free threat intelligence**:

- New phishing URLs we haven't seen → add to our database
- New scam templates → improve LLM classification
- New phone numbers / UPI IDs / crypto addresses → flag across all future scans
- Testing patterns → understand scammer workflows

Every test they run makes our system better for everyone else.

#### Layer 6: External Signals

Cross-reference with external abuse indicators:

- **IP reputation** — known VPN/proxy/datacenter IPs (common for automated testing)
- **Payment fraud signals** — if premium account, check payment legitimacy
- **Device fingerprinting** — multiple accounts from same device (web/mobile)
- **Email reputation** — disposable email domains for signup

---

## Accuracy Goals and Metrics

### What We Track

| Metric | Definition | MVP 1 Target | Long-term Target |
|--------|-----------|-------------|-----------------|
| **True Positive Rate** (Recall) | % of actual scams correctly flagged | > 85% | > 95% |
| **False Positive Rate** | % of legitimate messages incorrectly flagged | < 10% | < 3% |
| **True Negative Rate** | % of legitimate messages correctly cleared | > 90% | > 97% |
| **False Negative Rate** | % of actual scams missed | < 15% | < 5% |
| **Median confidence** | Average risk score confidence on flagged scams | > 75 | > 85 |

### How We Improve

```
User scans message
        │
        ▼
   Savdhaan AI returns result
        │
        ▼
   User provides feedback ───────────────┐
   ("confirm scam" / "false positive")   │
        │                                │
        ▼                                ▼
   Feedback stored              LLM prompts refined
        │                       Detection patterns updated
        ▼                       Threat intel enriched
   Weekly accuracy review
   by scam type + channel
```

The feedback loop is the most important long-term accuracy driver. Every user report
teaches the system. Community wisdom > any single AI model.

---

## What Competitors Do (and What We Can Learn)

| Product | Approach | Weakness we avoid |
|---------|----------|-------------------|
| **Truecaller** | Caller ID + spam detection | Phone calls only, no message content analysis |
| **Google Messages** | Built-in spam detection for SMS | Limited to SMS, no explanation, no sharing |
| **ScamAdviser** | Website reputation checker | URLs only, no message context analysis |
| **Norton Genie** | AI scam detection (discontinued) | Was text-only, no threat intel integration, no sharing |

Our differentiation:
1. **Multi-source evidence** — not just AI vibes, but grounded in threat databases
2. **Shareable scam cards** — network effect, one check protects many
3. **Honest about limits** — we tell you what we can't check, others don't
4. **Cross-channel** — works for SMS, email, WhatsApp, social DMs, any text/image

---

## User Education — Built Into the Product

Every scan result is a teaching moment. Beyond the verdict:

| Feature | What it teaches |
|---------|----------------|
| **Evidence breakdown** | Users learn to spot red flags themselves (new domains, urgency, etc.) |
| **"Why this is suspicious"** | Pattern education — next time they might catch it without us |
| **Action recommendations** | Teaches proper response (report to 7726, contact bank directly) |
| **Scam type label** | Gives vocabulary — "this is smishing" — empowers users to discuss and warn |
| **"What we couldn't check"** | Teaches that no tool is perfect, builds healthy scepticism |

Long-term goal: **Users who use Savdhaan AI regularly become better at spotting scams
on their own.** The best outcome is a user who no longer needs us for obvious scams.

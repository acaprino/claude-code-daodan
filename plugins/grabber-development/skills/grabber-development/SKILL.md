---
name: grabber-development
description: >
  Comprehensive Python web scraping knowledge base covering stealth browser automation (Patchright, Camoufox, Nodriver),
  TLS/HTTP fingerprint impersonation (curl_cffi, primp), anti-bot bypass (Cloudflare, DataDome, PerimeterX),
  CAPTCHA solving, proxy architecture, AI-assisted extraction (Crawl4AI, Firecrawl, ScrapeGraphAI),
  framework selection (Scrapy, Crawlee), rate limiting, and production observability.
  TRIGGER WHEN: building, implementing, writing, coding, creating, optimizing, or debugging Python web scrapers.
  DO NOT TRIGGER WHEN: the task is outside the specific scope of this component.
---

# Python Web Scraping

Knowledge base for building production-grade Python web scraping systems. Covers the full stack from target assessment through production observability.

## When to Use

- Assessing a target site's protection level and choosing the right tools
- Discovering API endpoints via network traffic interception (Playwright/Patchright)
- Extracting data from rendered pages when no API is available
- Bypassing anti-bot systems (Cloudflare, DataDome, PerimeterX)
- Configuring TLS/HTTP fingerprint impersonation (curl_cffi, primp)
- Setting up stealth browser automation (Patchright, Camoufox, Nodriver)
- Designing proxy architecture with tiered escalation
- Solving CAPTCHAs programmatically (CapSolver, 2Captcha, playwright-captcha)
- Building production scraping pipelines (Scrapy, Crawlee)
- Adding rate limiting and observability to scraping systems

## Discovery Gate (READ BEFORE WRITING ANY CODE)

**Phase 1 (Target Assessment) and Phase 2 (Data Discovery) are blocking gates, not optional steps.** You MUST execute them yourself and have their concrete outputs in hand before scaffolding any project file (`pyproject.toml`, modules, models, CLI). No exceptions.

**You execute the discovery, not the user.** When the target is reachable from your environment, drive the browser yourself via `playwright-skill` (writes scripts to `/tmp`, runs them with a visible browser, returns DOM + network traffic to you in-loop). Patchright code embedded below is fine too. The point is the same: Claude opens the browser, Claude observes the traffic, Claude records the real URLs and field names.

A user-runnable discovery script (`scripts/discover.py` style) is allowed ONLY when:
- The user must type credentials / 2FA / OTP that you cannot enter automatically, OR
- The target is firewalled / VPN-only / requires the user's machine identity, OR
- The user explicitly asks for a handoff script.

In every other case, "I wrote a discovery script for you to run" is a workflow failure. Open the browser instead.

**Discovery outputs you MUST collect before scaffolding** (treat as a checklist; if any item is still a guess, you have not finished discovery):
- Real URL of every page that holds target data (not assumed paths, not `/#/...` guesses)
- Real XHR/fetch endpoint URLs, methods, status codes, request headers, cookies
- Real field names and shapes from at least one captured JSON response (paste a redacted sample into the design notes)
- Anti-bot fingerprint (`cf_clearance`, `__cf_bm`, `datadome`, `_px3`, `ak_bmsc`, `incap_ses` -- present or absent)
- SPA framework / DOM structure of any page where API discovery fails and a DOM fallback is needed

If any of those is still a guess, you have not finished discovery; do not proceed to scaffolding.

### Anti-Patterns (do not do these)

- Scaffolding `pyproject.toml` and module skeleton before observing one real network request from the target
- Inferring endpoint URLs from "common patterns" (e.g. `/api/invoices`, `/#/fatture-ricevute`) without observation
- Building a regex / filter list of "common field names" (e.g. `(fatture|invoice|received|ricevute|passive)`) as a substitute for the real endpoint name
- Writing a Pydantic model with `Field(alias=...)` tuples of "Italian + English likely names" instead of the names actually returned by the API
- Handing the user a `discover.py` script as the *first* discovery step when you could open the browser yourself
- Marking Phase 1 / Phase 2 as "skipped, will refine later" and proceeding to write code anyway

## Core Workflow

For every scraping task, follow this sequence (the Discovery Gate above governs steps 1 and 2):

### 1. Target Assessment (YOU execute this)
- Load the target URL in a stealth browser (via `playwright-skill` or inline Patchright)
- Identify: static HTML vs JS-rendered, anti-bot service (check for cf_clearance, DataDome cookies, px cookies), data volume needed, update frequency
- Capture: real landing URL after any redirects, SPA framework if any, presence/absence of anti-bot cookies

### 2. Data Discovery (API-first, YOU execute this)
- Navigate the site with Playwright/Patchright **yourself**
- Intercept all network traffic via `page.on("request")` and `page.on("response")`
- Filter for XHR/fetch requests returning JSON, GraphQL, or structured data
- Classify: REST endpoints, WebSocket streams, GraphQL queries, SSE feeds
- Record (do not guess): URLs, methods, headers, cookies, response shapes, real field names
- If structured API found: generate curl_cffi replay code (skip browser entirely)
- If the page is gated by credentials you have and 2FA you can prompt for, log in via the browser session and continue discovery in the authenticated area

### 3. DOM Fallback (only if no API)
- If data exists only in rendered HTML: extract via CSS/XPath selectors
- Check for JSON-LD, microdata, or inline `<script>` JSON before parsing DOM
- For unstable DOM: use LLM-based extraction (Crawl4AI, ScrapeGraphAI) as final fallback
- Hybrid pattern: CSS selectors for stable fields ($0/extraction) + LLM for unstable fields (~$0.01/repair)

### 4. Stealth & Evasion (layer minimally)
- No protection: plain curl_cffi with `impersonate="chrome"` -- done
- Basic Cloudflare: Patchright persistent context + real Chrome channel
- Heavy Cloudflare/Turnstile: stealth browser + CAPTCHA solver + residential proxy
- DataDome: Camoufox + ghost-cursor behavioral simulation + residential proxy
- PerimeterX: organic navigation pattern + session warming + residential proxy

### 5. Production Hardening
- Rate limiting: pyrate-limiter v4 with Redis backend for distributed scraping
- Proxy rotation: tiered escalation (datacenter -> ISP -> residential -> mobile)
- Observability: structlog + Prometheus + Grafana
- Error handling: retry with backoff, proxy failover, session rotation

## Tool Selection Quick Reference

| Target Profile | HTTP Client | Browser | Framework |
|---------------|-------------|---------|-----------|
| No JS, no protection | curl_cffi | none | Scrapy / httpx |
| JS-rendered, no protection | none | Playwright | Crawlee |
| Basic Cloudflare | curl_cffi + cf_clearance | Patchright (for cookie) | Scrapy |
| Heavy Cloudflare | none | Patchright persistent | Crawlee |
| DataDome | none | Camoufox + ghost-cursor | custom |
| PerimeterX | none | Nodriver / Patchright | custom |
| AI extraction needed | none | Crawl4AI / Firecrawl | standalone |

## Proxy Tier Quick Reference

| Tier | Type | Price Range | Use When |
|------|------|-------------|----------|
| 0 | No proxy | free | Unprotected targets, development |
| 1 | Datacenter | $0.10-0.50/GB | Light protection, high volume |
| 2 | ISP (static residential) | $0.53-1.47/IP | Account management, login flows |
| 3 | Residential | $0.49-8.00/GB | Anti-bot bypass, geo-targeting |
| 4 | Mobile | $4-13/GB | Highest trust, last resort |

## Reference Materials

- `field-guide.md` -- full 2025-2026 Python web scraping field guide covering browser stealth, TLS fingerprinting, behavioral biometrics, anti-bot bypass, CAPTCHA solving, proxy landscape, frameworks, AI-assisted scraping, GraphQL reverse engineering, rate limiting, and observability

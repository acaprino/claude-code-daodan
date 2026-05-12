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

## Core Workflow

For every scraping task, follow this sequence:

### 1. Target Assessment
- Load the target URL in a stealth browser
- Identify: static HTML vs JS-rendered, anti-bot service (check for cf_clearance, DataDome cookies, px cookies), data volume needed, update frequency

### 2. Data Discovery (API-first)
- Navigate the site with Playwright/Patchright
- Intercept all network traffic via `page.on("request")` and `page.on("response")`
- Filter for XHR/fetch requests returning JSON, GraphQL, or structured data
- Classify: REST endpoints, WebSocket streams, GraphQL queries, SSE feeds
- If structured API found: generate curl_cffi replay code (skip browser entirely)

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

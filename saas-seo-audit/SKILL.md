---
name: saas-seo-audit
description: Quick SEO health check on any page — scan title tags, meta, headings, content quality, technical tags, and competitor gaps. Outputs a Pass/Fail/Warning table with prioritized fixes. Use before launching a page or as a weekly health check.
---

# SaaS SEO Audit

Runs a structured SEO health check on any page. Fetches the page, inspects on-page elements (title, meta, headings, content, technical tags), and outputs a scannable Pass/Fail/Warning table with prioritized action items: Fix Now, Fix This Week, and Nice to Have.

## When to Use This Skill

- Before launching a new landing page or blog post
- Weekly SEO health check on your top 5 pages
- Auditing a competitor's page to find their SEO weaknesses
- After a CMS migration or redesign
- When organic traffic drops and you need a fast diagnostic

## What This Skill Does

1. **On-page basics**: title tag length and keyword placement, meta description quality, H1 count and structure, heading hierarchy
2. **Content quality**: word count check, keyword density in first 100 words and H2s, internal/external link count
3. **Technical tags**: canonical tag (self-referencing?), Open Graph completeness, schema markup presence
4. **Performance estimates**: page size ballpark, third-party script detection
5. **Competitor gap check**: identifies the primary keyword and suggests 3 "People Also Ask" long-tail variants

## How to Use

### Basic Usage

```
/audit-seo [PAGE_URL]
```

### Advanced Usage

```
Audit the SEO health of [PAGE_URL]. I'm targeting the keyword "[KEYWORD]". 
Also check for any schema markup opportunities and suggest 5 long-tail keyword variants.
```

## Example

**User**: "/audit-seo https://my-saas.com/pricing"

**Output**:
```
## SEO Audit: https://my-saas.com/pricing

| Check | Status | Fix |
|-------|--------|-----|
| Title tag (52 chars) | Pass | — |
| Meta description | Fail | Missing entirely |
| H1 (2 found) | Warning | Should have exactly one H1 |
| Word count (180) | Fail | Thin content — aim for 300+ |
| Canonical tag | Pass | Self-referencing |
| OG tags | Pass | og:title + og:description present |
| Schema markup | Fail | None detected — add FAQ or Product schema |
| Keyword in first 100 words | Pass | "pricing" appears twice |

### Fix Now
1. Add meta description (120-155 chars, include "pricing" + value prop)
2. Consolidate to a single H1
3. Expand page content to 300+ words

### Fix This Week
1. Add FAQ schema markup ("How much does X cost?", "Is there a free trial?")
2. Add 3 internal links to feature pages

### Nice to Have
1. Add Product schema markup with price range
2. Target "affordable [category] pricing" as a long-tail variant
```

## Tips

- Combine with `/research-competitor` for a full competitive page analysis
- Run before and after any landing page redesign
- The "Competitor Gap Check" section surfaces content ideas from "People Also Ask" patterns
- If the page returns a JS-rendered SPA, note it — the audit will be partial
- For ecommerce pages, pay extra attention to Product schema and image alt text

## Common Use Cases

- Solo founders doing their own SEO before hiring an agency
- Content marketers auditing blog posts before publishing
- Developers checking SEO basics after deploying a new page
- Weekly founder routine: audit one page per week
- Pre-launch checklist item before shipping a new landing page

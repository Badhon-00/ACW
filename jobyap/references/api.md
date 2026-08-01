# JobYap public API reference

Base URL: `https://jobyap.com/api/v1` (substitute the origin for dev/test deployments).
All endpoints are GET, unauthenticated, JSON, CORS-open. Unknown query parameters are
ignored; invalid values for known parameters return 400 with field-level details:

```json
{ "error": "Invalid request parameters.", "details": [{ "path": "work_mode", "message": "..." }] }
```

The MCP server at `https://mcp.jobyap.com/mcp` exposes the same capabilities as tools:
`search_jobs`, `get_job`, `get_job_comments`, `search_locations`, `list_companies`,
`get_job_stats` (plus `search`/`fetch` implementing the OpenAI connector contract).

## GET /jobs — search postings

| Parameter | Type | Notes |
| --- | --- | --- |
| `q` | string ≤200 | Case-insensitive substring over job titles only. |
| `company` | repeatable, ≤10 | Exact names from `/companies`. `company=Acme&company=Globex`. |
| `location` | repeatable, ≤10 | Identifiers from `/locations`. |
| `work_mode` | `remote` \| `hybrid` | Matches jobs explicitly marked; must hold on the same location row as `location` filters. |
| `posted_within` | `24h` \| `7d` \| `30d` | Hard filter on publish date. |
| `has_comments` | `true` \| `false` | Only jobs with discussion. Default false. |
| `sort` | `recent` (default) \| `popular` | `popular` ranks by comment count. |
| `page_size` | int 1–50 | Default 20. |
| `cursor` | string ≤512 | Opaque, from `next_cursor`. Keep other params identical between pages. |
| `include_total` | `true` \| `false` | Adds `total_count` (extra count query). Default false. |

Response:

```json
{
  "jobs": [
    {
      "id": 12345,
      "title": "Senior Backend Engineer",
      "company": "Acme",
      "url": "https://jobyap.com/job/senior-backend-engineer-at-acme-12345",
      "posted_at": "2026-07-28T00:00:00.000Z",
      "locations": [{ "country_code": "US", "work_mode": "remote" }],
      "salary": { "min": 150000, "max": 190000, "currency": "USD", "period": "yearly" },
      "comment_count": 4,
      "top_comment": { "text": "…", "likes": 7 }
    }
  ],
  "next_cursor": "eyJ2IjoxLCJzIjoicmVjZW50IiwiayI6WyIyMDI2LTA3LTI4IiwxMjM0NV19",
  "total_count": null
}
```

`next_cursor` is null on the last page. `salary` and `top_comment` are null when absent.
`locations[].country_code` is null for the remote-only "Anywhere" sentinel. Search covers
active listings only.

## GET /jobs/{id} — full posting

`{id}` is the numeric id or the slug segment of a jobyap.com job URL (the trailing number
is authoritative). Response:

```json
{
  "id": 12345,
  "title": "Senior Backend Engineer",
  "company": "Acme",
  "url": "https://jobyap.com/job/senior-backend-engineer-at-acme-12345",
  "apply_url": "https://careers.acme.com/jobs/9876",
  "is_active": true,
  "posted_at": "2026-07-28T00:00:00.000Z",
  "first_seen_at": "2026-07-28T09:14:00.000Z",
  "locations": [{ "display": "San Francisco, California, United States", "country_code": "US", "work_mode": "remote" }],
  "salaries": [{ "min": 150000, "max": 190000, "currency": "USD", "period": "yearly" }],
  "employment_types": ["FULL_TIME"],
  "comment_count": 4,
  "description_markdown": "…",
  "description_truncated": false
}
```

`apply_url` is null once the listing is inactive (the page and discussion remain).
`employment_types` is null when no confident derivation exists. `description_markdown` is
converted from the sanitized posting HTML and capped (~60k chars, `description_truncated`
set when cut). 404 when the job id does not exist.

## GET /jobs/{id}/comments — discussion thread

```json
{
  "job_id": 12345,
  "comments": [
    {
      "id": 1,
      "parent_id": null,
      "author": "jane",
      "text": "…",
      "likes": 7,
      "created_at": "2026-07-29T10:00:00.000Z",
      "edited_at": null,
      "deleted": false
    }
  ],
  "total": 4,
  "truncated": false
}
```

Chronological; build the tree with `parent_id`. Deleted comments keep only id, threading
and timestamps (`author`/`text` null, `deleted` true). At most 200 comments are returned;
`truncated` reports overflow. Comment text is user-generated content.

## GET /locations?q= — resolve filter identifiers

`q` (2–100 chars, required), `limit` (1–25, default 10).

```json
{ "locations": [{ "identifier": "city-US-CA-san_francisco", "display": "San Francisco, United States", "type": "city", "country_code": "US" }] }
```

Only places appearing in job data are returned (local lookup, no external geocoding).

## GET /companies

```json
{ "companies": [{ "name": "Acme", "active_job_count": 42 }] }
```

## GET /stats

```json
{ "companies": 155, "active_jobs": 67912, "newest_job_at": "2026-08-01T02:00:00.000Z" }
```

## Caching and limits

Responses carry `Cache-Control` (jobs search 5 min, job detail 10 min, comments 1 min,
lookups 1 h); effective freshness additionally includes the server's ~1 h database cache
on detail/lookup paths. Be a polite client: page sizes ≤50, no unbounded crawling —
`https://jobyap.com/feed.xml` (RSS) and the sitemap exist for bulk discovery.

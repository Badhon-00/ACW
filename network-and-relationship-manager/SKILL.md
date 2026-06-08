---
name: network-and-relationship-manager
description: >
  Never forget a person again — search your entire professional network, recall exactly
  what you discussed, and always know who you know at any company. Powered by Rarefriend
  personal CRM. Use when the user wants to: search contacts, find who they know at a company,
  add meeting notes or call summaries, tag and organise contacts, schedule or check calendar
  events, import LinkedIn connections, bulk import contacts, connect Google Contacts or
  Microsoft Outlook, track relationship context, log an interaction, or do anything related
  to contacts, networking, or relationship management. Triggers on: contact, contacts, CRM,
  notes, my network, schedule, calendar, LinkedIn, Google Contacts, Outlook, bulk import,
  who do I know, who do I know at, relationship, networking, person, people, meeting notes,
  who should I reach out to, warm intro, remind me about, what do I know about.
license: MIT-0
user-invocable: true
argument-hint: '[setup|contacts|notes|tags|calendar|import|integrations]'
metadata:
  openclaw:
    requires:
      env:
        - RAREFRIEND_CLIENT_ID
        - RAREFRIEND_CLIENT_SECRET
      primaryEnv: RAREFRIEND_CLIENT_ID
    install:
      - kind: node
        package: '@rarefriend-ai/mcp'
    envVars:
      - name: RAREFRIEND_CLIENT_ID
        required: true
        description: OAuth client ID — rarefriend.com → Settings → Integrations → MCP
      - name: RAREFRIEND_CLIENT_SECRET
        required: true
        description: OAuth client secret — rarefriend.com → Settings → Integrations → MCP
  author: Rarefriend
  homepage: https://rarefriend.com
  repository: https://github.com/Whitefield-Labs/rarefriend-skills
---

## About Rarefriend

Rarefriend remembers your professional network so you don't have to — contacts from Google, LinkedIn, Microsoft, and your phone in one place, with notes, tags, and full relationship history always at your fingertips.

Access it from your AI assistant, the web app at [rarefriend.com](https://rarefriend.com), or Hops — Rarefriend's AI on WhatsApp.

**LinkedIn sync** requires the Rarefriend Chrome extension — set it up at rarefriend.com → Settings → Integrations → LinkedIn.

---

## Setup Detection Protocol

**ALWAYS run this before any CRM action.**

1. Call `list_connected_integrations` with no arguments.
   - **If the tool is not available → MCP is not connected.** Present these steps inline to the user:
     1. Sign in at [rarefriend.com](https://rarefriend.com) → **Settings → Integrations → MCP** → copy the Client ID and Client Secret
     2. **Claude Code:** run `claude mcp add rarefriend -e RAREFRIEND_CLIENT_ID=your_id -e RAREFRIEND_CLIENT_SECRET=your_secret -- npx -y @rarefriend-ai/mcp`
     3. **Cursor:** add to `~/.cursor/mcp.json` under `mcpServers.rarefriend` with `command: npx`, `args: ["-y", "@rarefriend-ai/mcp"]`, and the two env vars
     4. **Claude Desktop:** add the same block to `claude_desktop_config.json`
     5. Restart the client, then try again
   - If it returns an empty list → MCP is connected but no integrations synced. Proceed and offer to connect Google or Microsoft when relevant.
   - If integrations are present → proceed directly to the user's request.

2. Never assume whether an integration is connected — always call the tool to check.

---

## Core Workflows

### 1 — Search and retrieve contacts

```
search_contacts(query, searchMode?, tag?, source?, limit?, offset?)
  searchMode: 'all' | 'name' | 'company' | 'role' | 'email' | 'exact'
  tag:    filter to contacts with this exact tag (e.g. "investor")
  source: filter by origin — 'google_contacts' | 'microsoft_contacts' |
          'linkedin' | 'linkedin_csv' | 'manual' | 'mcp' | 'gmail' |
          'google_calendar' | 'microsoft_calendar' | 'microsoft_email' | 'phone_contacts'
  Use offset + limit for pagination when hasMore=true in the response.

get_contact(contactId)
  Returns full profile — emails, phones, notes count, tags.
```

**Pattern:** Always search first. Only call `get_contact` for a specific person the user asks about — do not fetch every result from a list.

**Source attribution:** Each contact in the response includes a `sourceLabel` field (e.g. "Google Contacts", "LinkedIn (extension)", "Added manually"). Always mention this when presenting a contact — e.g. _"Found Alice Wang in Google Contacts"_ or _"Sarthak Sharma — LinkedIn (extension), Product Manager at Acme"_.

### 2 — Create and update contacts

```
create_contact(displayName, firstName?, lastName?, emails?, phones?,
               company?, role?, location?, bio?)

update_contact(contactId, ...same optional fields...)
```

**Pattern:** For updates, call `get_contact` first so the user sees the current state, then apply the change.

### 3 — Notes

```
create_note(contactId, content, isPinned?)
update_note(noteId, content?, isPinned?)
delete_note(noteId)
list_notes(contactId, limit?, offset?)
get_note(noteId)
pin_note(noteId, pinned)
search_notes(query, limit?)          — full-text across all contacts
get_recent_notes(limit?)             — most recent notes, all contacts
```

**Pattern:** After any meeting or call, create a note immediately. Use `search_notes` when the user asks "what did I last discuss with…" or "what do I know about…". Pin notes for critical context.

### 4 — Tags

```
list_tags()
add_tag(contactId, tag)
remove_tag(contactId, tag)
rename_tag(oldTag, newTag)           — renames across all contacts
```

**Pattern:** Normalise tags to lowercase kebab-case. When bulk-tagging ("tag everyone at Sequoia"), search contacts first then loop `add_tag`.

### 5 — Google Calendar

```
create_google_calendar_event(title, startTime, endTime, description?,
                              attendees?, location?, transparency?)
  transparency: 'opaque' (busy) | 'transparent' (free)

search_google_calendar_events(query, timeMin?, timeMax?)
get_upcoming_google_events(limit?, days?)
reschedule_google_event(eventId, startTime, endTime)
cancel_google_event(eventId)
find_available_google_time(durationMinutes, preferredDays?,
                            preferredTimeRange?, attendeeEmails?)
```

**Pattern:** Pass times in ISO 8601 with timezone. Use `find_available_google_time` before scheduling. Use `search_contacts` to resolve attendee emails by name before creating events.

### 6 — Microsoft Outlook

```
search_microsoft_contacts(query, limit?)
get_microsoft_contact(contactId)
create_microsoft_calendar_event(title, startTime, endTime, description?,
                                 attendees?, location?)
search_microsoft_calendar_events(query, timeMin?, timeMax?)
get_upcoming_microsoft_events(limit?, days?)
reschedule_microsoft_event(eventId, startTime, endTime)
cancel_microsoft_event(eventId)
find_available_microsoft_time(durationMinutes, preferredDays?,
                               preferredTimeRange?, attendeeEmails?)
```

Microsoft contacts are readable from Outlook — edits go through `update_contact` in Rarefriend.

### 7 — Bulk import

```
bulk_create_contacts(contacts[])
  Each: { displayName*, firstName?, lastName?, emails?, phones?,
          company?, role?, location?, bio? }
  Max 50 contacts per call.
```

**Pattern:** Parse any list the user provides (text, CSV, spreadsheet rows) into the contacts array. If the batch exceeds 50, split and make sequential calls. If the response contains `quota_exceeded`, inform the user their plan limit has been reached and direct them to rarefriend.com to upgrade.

### 8 — Integration management

```
list_connected_integrations()
connect_integration(integration)
  integration: 'gmail' | 'google_calendar' | 'google_contacts'
             | 'microsoft_calendar' | 'microsoft_contacts' | 'microsoft_email'
get_integration_sync_status(integration)
```

**Pattern for connecting:** Call `connect_integration`, present the `connectUrl` as a clickable link, say: _"Open this link in your browser to connect [integration]. It expires in 15 minutes."_ Never ask the user to paste credentials.

**Pattern after connecting:** Call `get_integration_sync_status` to confirm when sync completes (typically a couple of minutes after connecting).

---

## Quick Reference

| Category     | Tool                              | Key params                                       |
| ------------ | --------------------------------- | ------------------------------------------------ |
| Contacts     | `search_contacts`                 | `query`, `searchMode`, `tags`, `limit`, `offset` |
|              | `get_contact`                     | `contactId`                                      |
|              | `create_contact`                  | `displayName` (required), others optional        |
|              | `update_contact`                  | `contactId` + fields to change                   |
|              | `delete_contact`                  | `contactId`                                      |
| Notes        | `create_note`                     | `contactId`, `content`                           |
|              | `search_notes`                    | `query`                                          |
|              | `get_recent_notes`                | `limit`                                          |
|              | `pin_note`                        | `noteId`, `pinned`                               |
| Tags         | `add_tag`                         | `contactId`, `tag`                               |
|              | `rename_tag`                      | `oldTag`, `newTag`                               |
| Google Cal   | `find_available_google_time`      | `durationMinutes`                                |
|              | `create_google_calendar_event`    | `title`, `startTime`, `endTime`                  |
| Microsoft    | `find_available_microsoft_time`   | `durationMinutes`                                |
|              | `create_microsoft_calendar_event` | `title`, `startTime`, `endTime`                  |
| Bulk         | `bulk_create_contacts`            | `contacts[]` (max 50 per call)                   |
| Integrations | `connect_integration`             | `integration` (enum)                             |

---

## Error Handling

| Response field      | Meaning                       | What to do                                   |
| ------------------- | ----------------------------- | -------------------------------------------- |
| `quota_exceeded`    | Plan contact limit reached    | Tell user to upgrade at rarefriend.com       |
| `bulk_rate_limited` | Too many bulk calls this hour | Wait or use `create_contact` for individuals |
| `rate_limited`      | General rate limit hit        | Wait a moment and retry                      |
| `hasMore: true`     | More results available        | Call again with `offset + limit`             |

---

## References

- [MCP setup — Claude Code, Cursor, Claude Desktop](references/SETUP.md)
- [Full tool parameter reference](references/TOOLS.md)

## Other capabilities (outside this MCP)

- **LinkedIn sync** — requires the Rarefriend Chrome extension. Go to rarefriend.com → Settings → Integrations → LinkedIn to install and connect. Once synced, contacts appear here searchable with `source="linkedin"`.
- **Hops on WhatsApp** — Rarefriend's AI assistant available on WhatsApp. Same contacts, notes, and network — ask Hops anything about your network by message.
- **Reminders** — set follow-up reminders on contacts via the web app at rarefriend.com.
- **Phone contacts sync** — sync your phone contacts via the web app.

## Focused skills

Users who want a narrower skill for a specific use case can install these instead of (or alongside) this one:

- `npx skills add google-contacts` — contacts, notes, tags, Google Contacts sync
- `npx skills add google-calendar` — Google Calendar scheduling
- `npx skills add microsoft-contact-calendar-management` — Microsoft Outlook contacts and calendar
- `npx skills add linkedin-connection-management` — manage and search LinkedIn-synced connections

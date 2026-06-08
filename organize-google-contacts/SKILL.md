---
name: organize-google-contacts
description: >
  Your Google Contacts — supercharged with notes, tags, and relationship memory via
  Rarefriend. Find anyone instantly, remember every conversation, and never lose context
  on a person again. Use when the user wants to: search people they know, find someone's
  email or phone, create or update a contact, add meeting notes or call summaries, tag
  contacts, bulk import a list of people, connect Google Contacts, or check what they
  know about someone. Triggers on: contact, contacts, Google Contacts, who do I know,
  find someone, person, people, notes about, meeting notes, tag, import contacts, network,
  what do I know about, who is, remember this about, add a note.
license: MIT-0
user-invocable: true
argument-hint: '[setup|search|create|notes|tags|import|connect]'
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

Rarefriend layers notes, tags, and relationship history on top of your Google Contacts — so every person you know comes with full context, not just a name and email.

Access it from your AI assistant, the web app at [rarefriend.com](https://rarefriend.com), or Hops — Rarefriend's AI on WhatsApp.

---

## Setup Detection Protocol

1. Call `list_connected_integrations`.
   - **Tool not available → MCP not connected.** Present these steps inline to the user:
     1. Sign in at [rarefriend.com](https://rarefriend.com) → **Settings → Integrations → MCP** → copy the Client ID and Client Secret
     2. **Claude Code:** run `claude mcp add rarefriend -e RAREFRIEND_CLIENT_ID=your_id -e RAREFRIEND_CLIENT_SECRET=your_secret -- npx -y @rarefriend-ai/mcp`
     3. **Cursor:** add to `~/.cursor/mcp.json` under `mcpServers.rarefriend` with `command: npx`, `args: ["-y", "@rarefriend-ai/mcp"]`, and the two env vars
     4. **Claude Desktop:** add the same block to `claude_desktop_config.json`
     5. Restart the client, then try again
   - Empty list → connected, no Google sync yet. Proceed; offer `connect_integration("google_contacts")` at the end.
   - `google_contacts` present → proceed directly.

---

## Core Workflows

### Search contacts

```
search_contacts(query, searchMode?, tag?, source?, limit?, offset?)
  searchMode: 'all' | 'name' | 'company' | 'role' | 'email' | 'exact'
  tag:        filter to contacts with this exact tag (e.g. "investor")
  source:     filter by origin — 'google_contacts' | 'manual' | 'mcp' | 'linkedin_csv' | ...
```

- "Who do I know at Stripe?" → `search_contacts("Stripe", searchMode="company")`
- "Show all my Google contacts" → `search_contacts("", source="google_contacts")`
- "Find all investors" → `search_contacts("", tag="investor")`
- Use `searchMode: 'exact'` for known email or full name.
- Pass `offset + limit` from the previous response when `hasMore` is true.

**Source attribution:** Each contact in the response includes `source` and `sourceLabel` (e.g. "Google Contacts", "LinkedIn (extension)", "Added manually"). Always mention this when presenting results — e.g. _"Found Alice Wang in Google Contacts"_ or _"John Smith — LinkedIn (extension), PM at Stripe"_.

```
get_contact(contactId)   — full profile; call only when user needs details on one person
```

### Create and update contacts

```
create_contact(displayName*, firstName?, lastName?, emails?, phones?,
               company?, role?, location?, bio?)

update_contact(contactId, ...same optional fields...)
```

Always call `get_contact` before `update_contact` so the user can confirm current values.

### Notes

Notes are the core of relationship memory. Create one after every meeting, call, or interaction.

```
create_note(contactId, content, isPinned?)
update_note(noteId, content?, isPinned?)
delete_note(noteId)
list_notes(contactId, limit?, offset?)
get_note(noteId)
pin_note(noteId, pinned)
search_notes(query, limit?)     — full-text across ALL contacts
get_recent_notes(limit?)        — most recent notes, any contact
```

- `search_notes` → "what did I discuss with..." / "what do I know about..." / meeting prep
- `get_recent_notes` → "what have I been up to" / relationship activity summary
- `pin_note` → mark critical context (intro given, hot deal, key meeting)

### Tags

```
list_tags()
add_tag(contactId, tag)         — lowercase kebab-case
remove_tag(contactId, tag)
rename_tag(oldTag, newTag)      — renames across all contacts
```

**Bulk tagging:** "tag everyone at Sequoia as investor"

1. `search_contacts("Sequoia", searchMode="company")`
2. Loop `add_tag(contactId, "investor")` for each result

### Bulk import

```
bulk_create_contacts(contacts[])
  Each: { displayName*, firstName?, lastName?, emails?, phones?,
          company?, role?, location?, bio? }
  Max 50 per call — split larger lists and call sequentially.
```

If the response includes `quota_exceeded`, direct the user to rarefriend.com to upgrade.

### Connect Google Contacts

```
connect_integration("google_contacts")
```

Returns a `connectUrl`. Present as a clickable link:

> _"Open this link in your browser to connect Google Contacts. It expires in 15 minutes."_

After OAuth completes:

```
get_integration_sync_status("google_contacts")
```

Wait until sync completes (usually a couple of minutes) before searching synced contacts.

---

## Quick Reference

| Tool                          | When to use                                            |
| ----------------------------- | ------------------------------------------------------ |
| `list_connected_integrations` | Always check first — detects MCP and integration state |
| `search_contacts`             | Find by name, company, email, role, tag, or source     |
| `get_contact`                 | Full profile for one person                            |
| `create_contact`              | Add a new person                                       |
| `update_contact`              | Edit an existing contact                               |
| `delete_contact`              | Remove a contact                                       |
| `bulk_create_contacts`        | Import a list of people                                |
| `create_note`                 | Log a meeting, call, or interaction                    |
| `update_note`                 | Edit a note                                            |
| `delete_note`                 | Remove a note                                          |
| `list_notes`                  | All notes for one contact                              |
| `get_note`                    | Full note content                                      |
| `pin_note`                    | Mark as critical context                               |
| `search_notes`                | Find notes by keyword across all contacts              |
| `get_recent_notes`            | Latest activity across the network                     |
| `list_tags`                   | See all tags in use                                    |
| `add_tag` / `remove_tag`      | Categorise contacts                                    |
| `rename_tag`                  | Rename a tag everywhere                                |
| `connect_integration`         | Connect Google Contacts                                |
| `get_integration_sync_status` | Check when sync completes                              |

---

## References

- [MCP setup — Claude Code, Cursor, Claude Desktop](references/SETUP.md)

## Other capabilities (outside this skill)

- **Google Calendar** — schedule meetings, find free time, create events. Install `schedule-with-google-calendar`.
- **Microsoft Outlook** — Outlook contacts and calendar. Install `schedule-with-outlook`.
- **LinkedIn sync** — requires the Rarefriend Chrome extension. Direct user to rarefriend.com → Settings → Integrations → LinkedIn. Once synced, LinkedIn contacts appear here with `source="linkedin"`.
- **Hops on WhatsApp** — same contacts and notes accessible via Rarefriend's WhatsApp AI assistant.
- **Reminders and phone contacts** — available in the web app at rarefriend.com.
- **Full feature set in one skill** — install `network-and-relationship-manager`.

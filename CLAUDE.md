# CGS Contact Manager — Project State for Claude

## What This Is
A personal CRM / contact intelligence tool for Mark Henry Saft (markhenrysaft@gmail.com).
11,495 LinkedIn contacts with notes, tags, sector classification, and project organisation.
Single-page app deployed on Cloudflare Pages. No backend — data lives in static JS files
and localStorage.

---

## Live URLs
- **Production:** https://cgs-contact-manager.pages.dev
- **GitHub:** https://github.com/Marcus-Henri/cgs-contact-manager
- **PIN to unlock app:** `8487`

---

## Deploy Commands
```bash
# Deploy to Cloudflare Pages
wrangler pages deploy "C:\CGS" --project-name cgs-contact-manager --commit-dirty=true

# Push to GitHub
git -C /c/CGS add -A && git -C /c/CGS commit -m "message" && git -C /c/CGS push origin main
```
Wrangler is authenticated as markhenrysaft@gmail.com, Account ID: 9719f18bf9de08b2926a9f2bd227accb.
Do NOT use Vercel — this project uses Cloudflare Pages only.

---

## File Structure
```
C:\CGS\
  index.html   — HTML shell + all <style> blocks (386 lines)
  app.js       — All JavaScript logic (1110 lines)
  data.js      — Sets window.INITIAL_DATA (13.8 MB, 11,495 contacts, READ-ONLY)
  CLAUDE.md    — This file
  split.py     — Script used to split CGS_FINAL_V8.html into 3 files (keep for reference)
  patch.py     — Legacy patch script (keep, do not run)
```
Source of truth (unsplit): `C:\Marcus-Henri\CGS Contact Manager\CGS_FINAL_V8.html`

---

## Architecture

### Script Loading (index.html lines 147-148)
```html
<script src="data.js"></script>   <!-- synchronous, sets window.INITIAL_DATA -->
<script src="app.js"></script>    <!-- synchronous, runs after data.js -->
```
Both are synchronous (no defer/async). This is intentional — app.js uses
`window.INITIAL_DATA` immediately at the top level. The original V8 was one
inline script; this mirrors that behaviour.

### Data Flow
```
data.js → window.INITIAL_DATA (array of 11,495 contact objects)
app.js  → const contacts = window.INITIAL_DATA.map(...)  [maps to internal schema]
        → let currentData = contacts                       [filtered view]
        → renderList()                                     [paints sidebar]
```

### Contact Schema (from INITIAL_DATA)
Fields: id, first_name, last_name, full_name, company, position, linkedin_url,
email, email2, email3, phone, whatsapp, telegram, signal, wechat, twitter,
website1, website2, website3, birthday, connected_on, sector_tags[], custom_tags[],
seniority, relevance_score, priority, has_email, status, notes[], projects[], about

Internal mapped schema (contacts array): id, person, entity, position, linkedin,
email, email2, email3, phone, whatsapp, telegram, signal, wechat, twitter,
website1, website2, website3, birthday, connected_on, sector_tags, custom_tags,
seniority, relevance_score, priority, status, about, notes[]

### localStorage Keys
- `cgs_anthropic_key`  — user's Anthropic API key (entered once in the API key bar)
- `cgs_projects`       — JSON array of project objects (see Projects section)
- `cgs_new_contacts`   — JSON array of contacts added via modal (delta persistence)
- `cgs_auth`           — session flag set to "1" after PIN entry (sessionStorage)

---

## Features — Current State

### Working
- **Contact list** — sidebar shows all 11,495 contacts, paginated 100 at a time with "Load more"
- **Search** — filters by name, company, position, sector tags, email, notes
- **Contact detail** — click any contact to see full profile in right panel
- **PIN gate** — PIN `8487` stored in inline script in index.html (sessionStorage-based)
- **Add Contact modal** — 3 tabs:
  1. "Paste JSON from Claude" — paste Claude output, click Import
  2. "Manual Entry" — fill form fields directly
  3. "AI Extract (API)" — URL or screenshot → Claude API → pre-fills form
- **AI extraction (URL path)** — paste LinkedIn URL, Claude infers name from slug
- **AI extraction (screenshot path)** — drop/upload PNG or JPEG, Claude vision reads all visible fields
- **Projects** — create projects, add/remove contacts, persist via localStorage
- **New contact persistence** — contacts added via modal saved to `cgs_new_contacts`
  in localStorage, merged into contacts array on every page load (device-specific)
- **Export JSON** — downloads full dataset + projects as JSON
- **API key bar** — hidden bar (toggle in header), saves key to localStorage

### Known Gaps / Next Steps
1. **AI Extract end-to-end test** — fixed 3 bugs (wrong CORS header, undefined
   ANTHROPIC_API_KEY, hardcoded image/jpeg MIME type) but hasn't been confirmed
   live with a real API key.

3. **gstack upgrade available** — v0.13.4 → v0.15.9 (non-blocking).

---

## Bugs Fixed This Session (in order)
1. Contacts not displaying — scripts placed before `</main>`, no IIFE, worked fine
   ACTUAL CAUSE: `defer` attribute on app.js caused timing issues → removed defer
2. All JS functions undefined globally — no console error visible
   ACTUAL CAUSE: SyntaxError on line 732: unescaped apostrophe in `'Claude's'`
   inside single-quoted string. Fixed by changing to double quotes.
3. AI extraction never worked — silent API failure
   ACTUAL CAUSE: `buildHeaders()` used `anthropic-dangerous-allow-browser` (wrong)
   instead of `anthropic-dangerous-direct-browser-access` (correct)
4. `ncExtract()` would throw ReferenceError
   ACTUAL CAUSE: referenced undefined global `ANTHROPIC_API_KEY` instead of `getApiKey()`
5. Screenshot vision would fail for PNG files
   ACTUAL CAUSE: `media_type` hardcoded to `image/jpeg` — fixed to detect from `file.type`
6. `clearAddForm` infinite recursion — stack overflow when opening Add Contact modal
   ACTUAL CAUSE: two `function clearAddForm()` declarations in classic script; both hoisted,
   second wins globally, so `_origClear` captured the override itself. Calling it caused
   infinite recursion. Fixed by merging override's resets into original, deleting override.
7. `ncSave()` ReferenceError — new contact couldn't be saved from Manual tab
   ACTUAL CAUSE: referenced undefined `DB` variable and `save()` function (legacy code).
   Fixed to use `contacts` array and `persistNewContact()`.

---

## Key Code Locations in app.js

| Feature | Line range |
|---|---|
| INITIAL_DATA guard | 3–10 |
| Contact mapping | 12–42 |
| localStorage delta helpers (loadNewContacts, persistNewContact, deletePersistedContact) | ~44–65 |
| Delta merge on load | ~65 |
| Projects data layer | ~67–120 |
| Projects UI (panel, detail, picker) | ~121–340 |
| Add Contact modal state | ~360–395 |
| Image drop/upload handler | ~400–420 |
| API key helpers (getApiKey, saveApiKey, buildHeaders) | ~430–460 |
| extractFromScreenshot() | ~462–530 |
| extractFromUrl() | ~535–615 |
| populateForm() | ~618–680 |
| saveNewContact() | ~682–760 |
| renderList() | ~820–865 |
| view(id) — contact detail | ~870–960 |
| showAddContactModal() | ~1000–1070 |
| ncExtract() / ncSave() | ~1070–1110 |

---

## index.html Key Locations

| Element | Line |
|---|---|
| `<style>` block | 7–92 |
| Favicon (base64 SVG) | 93 |
| PIN gate + inline script | 96 |
| Header (logo, stats, buttons) | 97–120 |
| API key bar | 122–135 |
| Mode tabs (JSON/Manual/AI) | 158–175 |
| AI tab: drop zone + URL input | 230–260 |
| Add Contact form fields | 270–360 |
| Script tags (data.js, app.js) | 147–148 |
| Projects button in header | 118 |

---

## Development Notes
- **Do not touch data.js** — it is 13.8MB, read-only, sets `window.INITIAL_DATA`
- **Test syntax before deploy:** `node --input-type=module < /c/CGS/app.js 2>&1 | grep -i syntaxerror`
  (will report false positives for function redeclaration in module mode — only care about SyntaxError lines)
- **Browse tool path:** `B="/c/Users/Mark Henry Saft/.claude/skills/gstack/browse/dist/browse"`
- **Bypass PIN in browse tests:** `sessionStorage.setItem('cgs_auth','1'); document.getElementById('cgs-pin-gate').style.display='none';`
- The `stats` span in index.html has hardcoded text "11,495 contacts" — this was
  a red herring during debugging. JS overwrites it on load via `contacts.length`.
- Function redeclaration (`clearAddForm` defined twice) is valid in classic scripts,
  not in ES modules — ignore that node error.

---

## Git History
```
bece6f0  Fix clearAddForm infinite recursion — delete stale override, merge resets into original
         (also includes: localStorage delta persistence for new contacts, ncSave fix)
3e3e4b9  Add Projects feature: create, manage, add contacts, persist via localStorage
6fd6535  Fix AI extraction: header name, undefined API key, media type
cbf5332  Fix syntax error: escape apostrophe in Claude's string literal
3d29127  Fix: remove defer from app.js, add INITIAL_DATA guard
5e380c9  Deploy split app: index.html + app.js + data.js
083b364  Deploy full V8 patched CGS (original single-file deploy, remote only)
```

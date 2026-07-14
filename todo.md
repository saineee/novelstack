# novelstack TODO

## Phase 3 (frozen — no additions)
- [x] Nav in `base.html` — auth-conditional (always / authenticated / anonymous), username display, logout as POST form
- [x] User registration — `CustomUserCreationForm`, `register` view, `users/urls.py`, redirect to login
- [x] Search form on `book_list` — labels, repopulation, `selected`, `{% empty %}`
- [x] Library search — 4 filters (title, genre, publication status, reading status), `book__` traversal, exact vs icontains, two uncrossed dropdowns
- [x] pytest coverage across books, library, users — **9 tests** (see below; note `books/tests.py` still empty — tracked in 3.5)
  - Setup: `pytest` + `pytest-django`, `pytest.ini` with `DJANGO_SETTINGS_MODULE`, DB user granted `CREATEDB`
  - `conftest.py` fixture `library_data` (2 users, 2 books, 4 userbooks, spread statuses)
  - Library: reading-status filter, user-scoping, title, publication status, combined/AND — all with count + identity assertions
  - Profile aggregation: total_books, total_chapters (Sum), avg_rating (Avg, via `pytest.approx`), books_by_status (dict-flatten for order-independence), fav_genre (tie handled with `in`)
  - UserBook uniqueness: `pytest.raises(IntegrityError)` on duplicate (user, book)
  - CreateUserForm: duplicate email rejected, asserts `'email' in form.errors`

## Phase 3.5 — CLOSED ✅ (fully hardened, tested, access-controlled)

### Done this session
- [x] Password reset templates — full auth flow branded (reset x5, change x2, logout), plaintext email, `{% if validlink %}` guard on confirm, block-nav override kills nav on auth pages
- [x] Decide: `profile` in `library` or `users`? → **moved to `users`** (view + url + template + test relocated; `UserBook` imported cross-app from `library.models`)
- [x] Auth page chrome — **resolved via `{% block nav %}` default in `base.html`**; auth pages override empty. `base_auth.html` eliminated (no more doctype dup)
- [x] `from . import views` over `from .views import a, b, c` in urlconfs (books, library, users all converted; `manage.py check` clean)
- [x] **Data integrity constraints:**
  - `date_ended` after `date_started` — single-table `CheckConstraint` in Meta (`Q(date_ended__gte=F('date_started'))`); SQL null-comparison handles blanks (nulls pass). DB-enforced, unbypassable — verified rejects raw SQL violation.
  - `date_started` after book's `release_date` — cross-table, form-level `clean()` on `UserBookForm`; explicit null guards on both dates; strict `<` boundary; `add_error('date_started', ...)`.
- [x] Revisit whether `release_date` should be required on `Book` → **made nullable** (`null=True, blank=True`); webnovels with unknown release dates now addable
- [x] Rename reading-status empty option "Any status" → "Any reading status" (cosmetic)
- [x] **Catalog access model (SECURITY)** — established public/auth/staff tiers, enforced at BOTH view and template layers (template hides, view enforces — verified by hitting URLs directly):
  - **Public** (anyone, incl. anonymous): `book_list`, `book_details` — view only
  - **Logged-in** (`@login_required` + `{% if user.is_authenticated %}`): `add_to_library`. Add-to-library button hidden from anonymous.
  - **Staff** (`@staff_member_required` + `{% if user.is_staff %}`): `book_create`, `book_update`, `book_delete`. Catalog CRUD buttons + "Add Book" link hidden from non-staff. `book_create` route existed but was unlinked — now surfaced as staff-only link.
  - **Bug fixed along the way:** making `book_details` public exposed an `AnonymousUser` crash — `already_exists = UserBook.objects.filter(user=request.user)` blew up on anonymous users (FK expected an id, got AnonymousUser). Guarded with `if not request.user.is_authenticated: already_exists = False` else run the query.

### Remaining
**NONE — Phase 3.5 is CLOSED.** All items below completed this session.

- [x] **`books/tests.py`** — DONE. Empty → fully covered:
  1. **`book_list` search filters** — title/genre/status + combined, atomic one-behavior-per-function tests, set-equality assertions (`query_results == expected`, catches wrong count AND wrong identity AND extra leakage). `book_data` fixture (5 books, engineered overlaps) in root conftest.
  2. **Access-model tests** — `book_details` anonymous regression (200 + `already_exists` False — guards the AnonymousUser crash fix). Staff-gate: create/update/delete reject non-staff (302) and allow staff (GET 200). `add_to_library` rejects anonymous (302). `user_data` fixture (staff + reg, role-keyed) in root conftest.
  3. **Behavior tests** — `test_book_create_staff_post` (staff POSTs → assert Book exists), `test_book_delete_staff_post` (staff POSTs delete → assert gone). Proves the action *works*, not just that the form renders.
  - **LEFTOVER NIT (optional, low priority):** `test_book_{create,update,delete}_anon` are misnamed — they force_login the reg user, so they test logged-in-non-staff, not anonymous. Rename to `_reg`/`_non_staff` when convenient. Not urgent; tests are correct, only the names mislead.
- [x] `Book.description` nullable (`null=True, blank=True`) — migrated. Same reasoning as release_date.
- [x] Comments/docstrings pass — DONE. Why-not-what comments added: access decorators (who/why), `book_details` anonymous guard (prevents AnonymousUser crash), library `book__status` traversal vs direct `status`, exact-vs-icontains choice, `UserBookForm.clean()` cross-table rationale (Django CheckConstraint can't span tables), profile `values().annotate()` GROUP BY behavior + fav_genre tie edge case.


## Phase 4
- [ ] AniList integration — **SCOPE PIVOTED: Feature A (cover-only) → Feature B (FULL BOOK IMPORT) 🔨**
  - **THE PIVOT (decided this session):** Originally building "fetch cover art for an existing Book" (Feature A). Pivoted to **Feature B — import full books from AniList**: an AniList search result *becomes a new Book record* in the catalog (title, cover, format, + whatever else AniList has), not just a cover on an existing book. Cover art is now just ONE field that rides along with the import.
    - A and B are NOT mutually exclusive and the data layer (`fetch_candidates`/`extract_candidates`) serves BOTH. Mature end-state = B for adding new books (import w/ cover), A for backfilling covers on books that already exist or can't be imported (CN webnovels). But building B FIRST.
  - **B's DESIGN — pre-populated form (human-in-the-loop):** import does NOT create the Book directly. It **pre-fills a form** with AniList data → human reviews/completes/corrects it → save creates a *finished* Book. This collapses "import partial → enrich later" into one step and makes the human the safety net for imperfect field mapping. Missing fields render blank for the human to fill.
  - **B's REAL WORK = FIELD MAPPING.** Go field-by-field through `Book`; sort each into ONE bucket, because each is handled differently in the pre-fill logic. **Started with 4 buckets — the data forced a 5th.**
  - **B's BUILD ORDER (revised — supersedes the old cover-only steps 5–8):**
    1. [x] `Book.anilist_id` (CharField(255), null/blank, not in any form) — migrated. (renamed from wln_series_id.)
    2. [x] `Book.anilist_cover_url` (URLField(500), null/blank, not in any form) — migrated (0006). URLField for readability only (validator never fires — not in a form).
    3. [x] `fetch_candidates(title)` in `books/anilist.py` — POSTs GraphQL `Page(perPage:10){media(...)}`, returns raw dict. `variables` built FRESH inside (shared-mutable-state bug avoided). Logs debug breadcrumb. GOTCHA: capital `Media`=singular, lowercase `media` inside `Page`=list.
    4. [x] `extract_candidates(response)` — PURE (dict in, list out), `cleaned_data=[]` FRESH inside. Returns `{id, anilist_cover_url, format, title}` per candidate. Null guards: title=`english if english else romaji`; cover via `.get('coverImage',{}).get('large')`. No Pydantic (below complexity bar). Tested in shell: 2 clean candidates for "Lord of the Mysteries".
    5. [x] **FIELD-MAPPING TABLE — DONE ✅ (10/10). A 5TH BUCKET WAS DISCOVERED.**

       **Bucket definitions (final — 5, not 4):**
       1. **Clean match** — has it, same vocab, same shape. Copy across.
       2. **Vocab mismatch** — has it, same shape, *different words* → mapping dict.
       3. **Shape mismatch** — right concept, *wrong container/type* → transform.
       4. **Missing** — AniList **structurally does not have the concept**. Form blank, human fills.
       5. **Derived (NEW — invented this session)** — no *single* field maps; value is **computed from 2+ fields**. Buckets 1–4 all silently assume 1:1. This one is N:1.

       | `Book` field | Bucket | AniList source | Note |
       |---|---|---|---|
       | `title` | 3 | `title` → `MediaTitle{romaji,english,native,userPreferred}` | Object, not String. Already flattened in `extract_candidates`. **Solved ≠ clean** — still a 3. |
       | `author` | 3 | `staff` → `StaffConnection{edges,nodes,pageInfo}` | **No `author` field exists.** Author is *staff*, behind a connection. Traverse `edges[].node.name.full`, filter on `edges[].role`. |
       | `description` | 1 | `description: String` | Straight across. **Arrives with raw HTML (`<br>`, `<i>`) + `(Source: ...)` credit lines.** |
       | `chapters` | 1 | `chapters: Int` | `Int`→`IntegerField`, same shape. Null-on-RELEASING is a **guard**, not a mapping problem. |
       | `release_date` | 3 | `startDate` → `FuzzyDate{year,month,day}` | Three **separately nullable** `Int`s, not a date. |
       | `classification` | **5** | `format` **+** `countryOfOrigin` | `MANGA`+`KR`→manhwa, `+CN`→manhua, `+JP`→manga. **This field is why bucket 5 exists.** |
       | `genre` | 3 | `genres: [String]` | List → single `CharField`. Blocked on the schema decision below. |
       | `status` | 2 | `status: MediaStatus` | String→string, different words. Mapping dict. **2 orphans.** |
       | `anilist_id` | 1 | `id: Int!` | Populated by code, never by a human/form. |
       | `anilist_cover_url` | 3 | `coverImage` → `MediaCoverImage{extraLarge,large,medium,color}` | Object, not String. Already flattened. Same story as `title`. |

       **`status` mapping — 3 land, 2 orphan:**
```
       FINISHED         → completed
       RELEASING        → ongoing
       HIATUS           → hiatus
       CANCELLED        → ???  no home in STATUS_CHOICES
       NOT_YET_RELEASED → ???  no home in STATUS_CHOICES
```
       A mapping dict needs a target for every key. Decision owed (see OPEN DECISIONS).

    5b. [x] **PYDANTIC — DECIDED ✅. Option A: schema layer SEPARATE from `anilist.py`.**
       - **Trigger cleared.** Old TODO said "decide when the live response shape is in hand; trigger is *response complexity*." Old query = one clean `coverImage` → parse-and-guard was right. New query is 4 levels deep (`staff.edges[].node.name.full`) → hand-written `.get('x',{}).get('y')` chains are where typos hide. **Pydantic buys: parse the whole tree once, fail LOUD at the boundary if AniList's shape changed.** That's the buy — not "safety" in the abstract.
       - Pydantic **coerces types** (`"201"`→`int`) and **can transform via validators**. It is technically capable of doing the whole mapping.
       - **Rejected for mapping anyway.** Line drawn: **type coercion = yes, business logic = no.**
       - **WHY (the actual argument):** if the model emits `manhwa` and a real `date`, then `books/anilist.py` hardcodes *novelstack's vocabulary* and stops being a dumb AniList client. **A second source will have a different combination for "manhwa"** → bake the rule into the client and you rewrite it per source instead of writing it once against your own domain. WLN dying is exactly why this matters: the client must be swappable.
       - **Architecture:**
         - `anilist.py` = **dumb client.** AniList in → AniList shapes out. `startDate` stays `{year,month,day}`. `format`/`countryOfOrigin` stay separate. Testable with a raw dict, no Django.
         - **Separate mapping layer** owns buckets 2/3/5: FuzzyDate→`date`, `MANGA`+`KR`→`manhwa`, role→author, `[genres]`→CharField.
       - Pydantic solves **parsing**. It does **not** solve **mapping**. Two problems, one tool.

    6. [ ] **Expand the GraphQL query** — current query pulls only `id/title/coverImage/format`. Per the mapping table, B needs: `genres`, `status`, `description`, `startDate{year month day}`, `chapters`, `countryOfOrigin`, `staff{edges{role node{name{full}}}}`. Update query + extractor to pull them.
    7. [ ] **Import view** — AniList search → candidate cards → user picks → pre-filled Book form (mapped values) → human completes → save.
    8. [ ] Template(s) — candidate cards (pick) + the pre-filled review form.
    9. [ ] Error handling + caching — try/except (`RequestException`) + `logger.exception(...)` in except; GraphQL errors return `{'errors':[...],'data':None}` HTTP 400, check for `errors` key don't assume `data`.
  - **OPEN DECISIONS I still owe (mine to make):**
    - **Access:** who can import? Staff-only (matches 3.5 access model — catalog creation is `@staff_member_required`) or open to users? If import creates catalog books and catalog creation is staff-only, import is staff-only unless I change the model.
    - **Dedup:** importing a book already in the catalog — check if `anilist_id` already exists BEFORE creating, to avoid duplicate Books.
    - **`genre` field:** keep as single CharField (join AniList's list) or change to support multiple genres? (schema decision) **Blocks the bucket-3 transform.**
    - **`status` orphans:** `CANCELLED` + `NOT_YET_RELEASED` — extend `STATUS_CHOICES`, map them to something, or let them fall through blank for the human?
    - **`author` roles — which `role` strings count?** `role` is **FREE TEXT, not an enum.** Live evidence:
      - Mushoku Tensei: `"Story"`, `"Illustration"`
      - Solo Leveling: `"Art"`, `"Story (chs 1-92)"`, `"Original Story"`, `"Story (chs 93-201)"`, `"Lettering (English)"`, `"Translator (Polish)"`
      - **`role == "Story"` matches Mushoku and MISSES Solo Leveling entirely.** There is a Polish translator sitting in the author field's source data. Exact-match won't work; needs a rule.
    - **`chapters` nullable?** Currently `IntegerField()` — required, no default. Every RELEASING import pre-fills `None`. Nullable / default 0 / leave blank for the human to fill in the review form? (The human-in-the-loop design exists for exactly this — use it.)
    - **`description` HTML:** arrives with `<br>`, `<i>`, `(Source: ...)`. Strip, escape, or render as-is?
    - **Search fuzziness:** `search: "Mushoku Tensei"` returned **`Mushoku Tensei: Dasoku-hen`** — a side-story spinoff. `Media` singular returns one fuzzy match. This is the matching problem, live and confirmed.
  - **Nullable fields for B:** don't blanket-null everything. Field-by-field: `release_date`/`description` already nullable (3.5). Some fields (title) stay required. Nullability handles *missing* fields; it does NOT handle *differently-shaped* fields — that's the mapping problem.
  - **WLN Updates — DEAD, ruled out.** Site + API throwing errors on every page since Feb 2025 (~17 months). Structural: it was a scrape-based feed aggregator, anti-scraping broke its pipeline; solo maintainer non-committal, no fix in sight. Contract still documented on GitHub but server no longer honors it. Lesson: documented ≠ alive.
  - **AniList shape/gotchas:**
    - GraphQL: one endpoint, POST a query describing the fields you want, get exactly that shape back. Different from REST (URL=resource) and WLN's RPC (`mode` key). From Python, plain `requests.post` with the query in the JSON body works — no `gql` lib needed for one query.
    - **Novels live under `type: MANGA` + `format: NOVEL`** (there is no `NOVEL` type). But AniList's novel coverage is Japanese-light-novel / adaptation-driven — **it has 0 CN webnovels as text entries.**
    - `MediaFormat` enum (verified via introspection): `TV, TV_SHORT, MOVIE, SPECIAL, OVA, ONA, MUSIC, MANGA, NOVEL, ONE_SHOT`. **No `MANHWA`/`MANHUA`** — hence bucket 5 for `classification`.
    - `MediaStatus` enum (verified): `FINISHED, RELEASING, NOT_YET_RELEASED, CANCELLED, HIATUS`.
    - `FuzzyDate` (verified): `year`, `month`, `day` — all `Int`, all individually nullable. `{year: 2018, month: null, day: null}` is legal. **A `DateField` cannot hold that.**
    - `MediaCoverImage` (verified): `extraLarge`, `large`, `medium`, `color` — all String.
    - `MediaTitle` (verified): `romaji`, `english`, `native`, `userPreferred` — all String.
    - Stable per-type numeric IDs (ID lives in the anilist.co URL). Fits match-once/store-the-ID.
    - No auth for public reads; OAuth only for acting on a user's own list (not needed here).
  - **CN webnovel handling:** the *webnovel* isn't in AniList, but its *manhua adaptation* often is (e.g. Lord of the Mysteries) → match to the manhua, pull its cover. **Product tradeoff accepted:** showing a manhua's cover on a webnovel entry is fine; *a* relevant cover beats a placeholder. Pure text-only WN with no adaptation → placeholder.
  - **Matching is the real work, NOT the HTTP call.** Your DB has a book under one title string; AniList may return several hits (manhua + anime + language variants). Logic must **pick the right entry from N candidates** (format-disambiguate), not "take the first result." Confirmed live: "Mushoku Tensei" → a spinoff. Match once at add-time, store the ID, never re-match.
  - **`Book.wln_series_id` → renamed to `anilist_id`.** Kept `CharField` (not IntegerField) in case a future source uses non-numeric IDs. **Not** in any form — populated by code after the match, never typed by a user.
  - **Caching non-optional** — rate limit (~90/min) + match-once design both point to storing the resolved cover/ID, not re-fetching. Fetch once, persist.
  - ~~Pydantic vs DRF serializer vs just-parse~~ — **RESOLVED, see 5b.** Pydantic, mirroring AniList's shape, in a layer separate from `anilist.py`.
  - **Future spike (low priority, may dead-end):** a WN-focused cover source for text-only CN webnovels. WLN was supposed to be it and it's dead; CN sources (Qidian etc.) are scrape-hostile / English-metadata-poor. Acceptable outcome: "no good source, placeholders are permanent." Do NOT let this become an open wound — covers are polish, not load-bearing.
- [x] Logging — **DONE ✅** (committed: `feat(logging): add project-level LOGGING config with console handler`). `LOGGING` dictConfig in `settings.py`: one `"novelstack"` logger, console-only (`StreamHandler`), DEBUG level, `{`-style formatter (`{asctime} {levelname} {name} {message}`). Console-only chosen deliberately for ECS Fargate: container stdout → CloudWatch automatically; a log *file* dies with the ephemeral container. Tested live in `manage.py shell` across debug/warning/critical. Key facts: config builds at Django *startup* via dictConfig (name-ref typos fail LOUD there, not at runtime); levels *filter* (raise threshold to quiet, don't delete lines); child loggers by dotted name (`novelstack.covers`) inherit parent config for free. In code: `logger = logging.getLogger("novelstack")` then `logger.debug("... %s", val)` (%-substitution over f-strings — only builds string if it emits); `logger.exception(...)` inside except blocks for auto-traceback. NOTE: standalone scripts run outside Django don't load this config — use print for pure spikes, logger once it runs inside Django.
- [ ] Tailwind + WTR-Lab visual target
  - Book detail: stat grid, "Continue Reading X/Y" progress button
    - **Aggregate community rating** — avg of `UserBook.rating` filtered by book (`UserBook.objects.filter(book=X).aggregate(Avg('rating'))`), displayed as a book-page stat. Data already exists (every UserBook has rating + book_id). Same `Avg` pattern as profile aggregation, grouped by book instead of user. **Null case:** book with no ratings → `Avg` returns None → show "No ratings yet", not 0 or a crash. Consider also showing rating count (how many users rated).
  - Library: cover grid, progress bars, tab filters
  - Search: "Novel Finder" — pill status filters, genre checkboxes w/ AND/OR, chapter range, min rating, order-by
  - ~~**Native date pickers**~~ — **DONE ✅** (committed: `feat(forms): use native date picker for date fields`). `forms.DateInput(attrs={'type': 'date'})` on `UserBookForm` date fields AND `BookForm.release_date`. Swaps widget's `type="text"` → `type="date"` → browser native calendar, forces `YYYY-MM-DD` on the wire (kills the American-format rejection bug). Layer note: model=storage, form field=validation, widget=HTML — overrode the widget, model untouched. Client-side validation = UX only; server/DB still enforce (widget guides, server validates). Nullable `release_date` handles empty fine → `None`.
- [ ] Profile pictures — ImageField + S3 + django-storages
- [ ] Docker + ECR + ECS Fargate + RDS
  - **PROD SETTINGS PREP (do before/with containerizing — the real work is getting secrets + env-specific config OUT of the code and into environment variables so one `settings.py` behaves differently per env via `os.environ`):**
    - `DEBUG = False` — **non-negotiable security requirement.** DEBUG=True leaks tracebacks/settings/internals to anyone triggering an error.
    - `ALLOWED_HOSTS` — MUST be set once DEBUG=False (Django forces it; empty → every request 400s). Set to actual host/domain.
    - `SECRET_KEY` — pull from env var, NOT hardcoded. A committed secret key is a real vuln. (Biggest one people forget.)
    - **DB credentials** — RDS Postgres host/name/user/password from env vars / secrets, not hardcoded. Local settings point at local Postgres; prod points at RDS.
    - **Static files** — DEBUG=False stops Django serving static itself. Need `collectstatic` + a server (WhiteNoise = simple containerized-Django answer). Works in dev, silently breaks in prod — classic gotcha.
    - `EMAIL_BACKEND` — currently console backend (prints emails to terminal, fine for building password reset). Prod → real backend (AWS SES likely, since already in AWS) IF email needs to work live. **Decide first whether password-reset-by-email even needs to function in a portfolio demo** — don't wire SES if nothing depends on it. Only email-sending feature is password reset.
  - Container/infra: Dockerfile, push to ECR, ECS Fargate task/service, RDS Postgres. (Own dedicated session — secrets-management done right matters for the DevOps track.)
- [ ] try/except on external calls only
  - AniList fetch: `requests.exceptions.RequestException`
  - S3 uploads for profile pictures
  - The catch isn't the point — decide what happens next. Fetch fails: retry? placeholder? render coverless?
  - Nothing in Phases 1–3 needs it. All internal DB/form logic.

## Notes
- Anything new goes on 3.5 (or Phase 4 if it's a feature/polish, not a fix). Phase 3 is closed.
- The web fails silently: DTL renders nothing, labels associate with nothing, a form without `method="post"` submits to the wrong place. Check what rendered / what got sent, not just whether it errored.
- **When logic is provably correct but silently doesn't run, check scope/indentation first** (the `clean`-inside-`Meta` bug — cost 20 min chasing None values that were fine). Recurring failure mode.
- **Guard preconditions before logic that assumes them.** Same pattern hit three times: null dates in constraints/clean(), and AnonymousUser in book_details. Check the value exists (is_authenticated, is not None) BEFORE running the query/comparison that needs it.
- **Security: template hides, view enforces.** Hiding a button never protects an action — the URL is still reachable. Every access rule needs both layers; if only one, do the view.
- **API = a published contract** (endpoint + accepted requests + promised responses), not the server and not the act of sending. Server = the machine honoring it; request = you using it (read OR write, per what the contract permits); response = what comes back in the promised shape. Three request shapes seen so far: REST (URL = resource, GET, server picks response), RPC (one endpoint, POST, a `mode` key picks the op — WLN), GraphQL (one endpoint, POST, a *query* defines the response shape — AniList). For novelstack you are the **client**, not the provider — you *call*, you don't *build* an endpoint (that's the FastAPI capstone's job).
- **Documented ≠ alive.** A contract only has value if the server still honors it. WLN's docs are fully readable on GitHub but every request errors — 17 months. A spike must confirm the thing is *up*, not just *documented*.
- **Rendered ≠ schema.** *(Sibling of "documented ≠ alive.")* The anilist.co website is a **client** of the API, same as novelstack will be — it renders what it feels like. Blue Lock's page showed no chapter count → concluded `chapters` didn't exist. It does (`Int`, "the amount of chapters the manga has **when complete**"). The row was hidden because the series is RELEASING → null. **Absence in a UI is not absence in a contract.** Read the schema, not the page.
- **Null ≠ missing (bucket 4).** Bucket 4 = the concept structurally doesn't exist in the source. A null value on one row is a **guard** problem, not a mapping problem. Tagging from one observed row generalizes a symptom into a contract. (Hit this on `chapters` *and* `author` in the same pass.)
- **GraphQL introspection — the schema is queryable at runtime.** AniList's static reference docs 404 in places (their own repo warns they're manually updated and may lag). Don't read docs, **ask the server**:
```bash
  curl -s -X POST https://graphql.anilist.co -H 'Content-Type: application/json' \
    -d '{"query":"{ __type(name: \"MediaStatus\") { enumValues { name } } }"}' | python3 -m json.tool
  curl -s -X POST https://graphql.anilist.co -H 'Content-Type: application/json' \
    -d '{"query":"{ __type(name: \"FuzzyDate\") { fields { name type { name kind } } } }"}' | python3 -m json.tool
```
  **`enumValues` for enums, `fields` for objects.** Using `fields` on an enum returns `"fields": null` — a silent wrong-template bug, not an answer. (Same family as the paren-nesting pattern: right idea, wrong slot.)
- **What introspection does and doesn't buy.** It cannot go *stale* — the answer comes **from the server**, so there's no gap between description and reality. That gap is exactly what killed WLN: docs describing a contract the server no longer honored. But introspection does **not** make the server immortal — AniList can die like WLN did. **Staleness impossible; death still possible.**
- **Connections (`edges`/`nodes`) are a graph shape.** `node` = the thing itself. `edge` = the *link* to it, carrying data about the **relationship** (`role`). `nodes` = shortcut, no relationship info. Need the relationship → use `edges`. `author` needs `edges` because "which of these people is the author?" lives on the edge, not the person.
- **Free text is not an enum.** `staff.edges[].role` looks enum-ish (`"Story"`, `"Art"`) until it isn't (`"Story (chs 93-201)"`, `"Translator (Polish)"`). Verify with **two** live samples before writing a match rule. One sample makes free text look like a vocabulary.
- **A mapping table can need a bucket you didn't design.** Buckets 1–4 all silently assumed 1:1 (one source field → one of mine). `classification` needs `format` **+** `countryOfOrigin` — N:1. Bucket 5 = **derived**. The table was wrong until the data proved it wrong. Build the taxonomy against real responses, not in the abstract.
- **Pydantic solves parsing, not mapping.** Coercion/validation of *shape* = Pydantic's job. Domain rules (`MANGA`+`KR`→`manhwa`, FuzzyDate→`date`, role→author) = a separate layer. Pydantic is *capable* of both via validators; keeping it to one is what keeps the API client swappable.
- **Keep the thing you don't control behind a boundary you own.** Don't let a vendor's vocabulary leak into your code. `anilist.py` speaks AniList; the mapping layer speaks novelstack. Same principle scales all the way up — it's why Anthropic runs Claude across AWS Trainium, Google TPUs, and NVIDIA GPUs instead of welding itself to one. A Dockerfile is portable; an ECS task definition isn't. **Relevant to the Docker/ECR/Fargate phase.**
- **For values whose format you don't own (external IDs), don't encode assumptions you can't enforce.** Tight `max_length` on a third-party ID is you asserting a length you can't know. `varchar(15)` vs `varchar(255)` are stored identically in Postgres — a tight limit costs future migrations and buys nothing. Left `anilist_id` at 255.
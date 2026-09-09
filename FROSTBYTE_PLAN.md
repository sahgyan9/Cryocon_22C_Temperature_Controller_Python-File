# Frostbyte — Lab Platform Build Plan

**Project**: Unify the SRM AP Physics transport-measurement lab into one online platform.
**Owner**: Gyan Kumar Sah
**Status**: Specification. Nothing built yet.
**Audience**: AI coding agents (Antigravity, Claude Sonnet, Claude Code) and human contributors.

---

## 0. How to use this document

This is the single source of truth for the build. An agent picking up work should:

1. Read sections 1 through 6 in full. They define vocabulary, architecture, and hard limits.
2. Find the phase it has been assigned in section 7. Build only that phase.
3. Check its work against that phase's **Done when** list before reporting completion.
4. Read Appendix E (agent conduct) before writing any user-facing string.

Do not skip ahead. Later phases assume earlier ones exist. If a phase is blocked, say so
explicitly and finish everything in the phase that is not blocked.

---

## 1. The name

**Frostbyte.**

Cryogenics plus data, in one word, and it survives being said out loud in a corridor. The lab
runs an LN2 cryostat; the platform turns what that cryostat does into bytes that follow you
home. It is short, spells cleanly as a package name (`frostbyte`), and gives sensible child
names without effort.

| Component | Name | What it is |
|---|---|---|
| Lab PC daemon | `frostbyte-agent` | Python service on each bench PC. Runs programs, streams data. |
| Web app | `frostbyte-web` | React dashboard. Launch, monitor, browse, plot. |
| Database and backend | `frostbyte-db` | Supabase project. Postgres, Realtime, Storage, Edge Functions. |
| Python analysis library | `fbplot` | Publication-grade matplotlib figures from platform data. |
| A bench PC | **rig** | e.g. `bench-1` |
| One measurement | **run** | Has an id, params, status, telemetry, and files. |
| A registered measurement program | **program** | A VI or Python script the platform can launch. |

Vocabulary is fixed. Use `run`, `rig`, `program`, `dataset` in code, database columns, and UI
copy. Do not introduce synonyms like "experiment", "job", "session", or "machine".

---

## 2. What we are building

### 2.1 The outcome

One web address. You sign in from any device. You see:

- Every measurement program in the lab, listed and launchable — Cryocon ramps, Keithley IV
  sweeps, DC2200 LED drives, MFLI time response, Wayne Kerr impedance.
- What is running right now, live, with a chart that updates while you watch from a phone.
- A notification when a run finishes, fails, or loses contact, with the browser closed.
- Every dataset the lab has ever produced, searchable, with its columns indexed.
- A plot builder where you pick several runs, pick an X column and any number of Y columns
  across those files, and get a chart. Then export it as a publication figure.

### 2.2 Explicit non-goals

Out of scope. Each of these has sunk labs before.

- **Do not port LabVIEW VIs to the web.** The VIs stay native and stay on the bench PC.
  Frostbyte launches them and reads their output. Rewriting instrument control in JavaScript
  would take a year and would be worse than what already works.
- **Do not replace `cryocon_gui.py`.** It is validated against real hardware and encodes
  hard-won anti-surge ordering. It gets a publisher hook, nothing more.
- **Do not build a cloud control loop.** All PID and ramp logic stays on the bench PC. The
  network is never in a control path. Ever.
- **Do not self-host anything on the bench PC that needs an inbound port.** University IT will
  not give you one, and you should not want one.
- **Do not pay for anything.** Every component below has a free tier that fits this lab.

### 2.3 The constraint that decides the architecture

Instruments are on USB, serial, and GPIB. They cannot move. The bench PC sits behind
university NAT with no inbound access. Therefore:

> Every connection is outbound from the bench PC. The cloud never initiates anything.
> The agent polls or subscribes; it is never a server.

---

## 3. Architecture

```
BENCH PC (outbound only)              SUPABASE (free)             GROUP DEVICES
+---------------------------+
| frostbyte-agent (service) |
|                           |
|  program launcher  -------|--------> runs, commands
|  csv/tdms tailer   -------|--------> telemetry (0.2 Hz history)
|  broadcast pump    -------|--------> Realtime channel (1 Hz live, ephemeral)
|  storage uploader  -------|--------> Storage: raw/*.csv.gz
|  spool (SQLite)           |            |
|  safety interlocks        |            |
+---------------------------+            |
   ^        |                            +--> Realtime --> frostbyte-web
   |        |                            |                 (Cloudflare Pages)
   |    launches                         |
   |        v                            +--> DB webhook --> Edge Function
   |  cryocon_gui.py                     |                   dispatch-push
   |  staged_ramp_test.py                |                        |
   |  CryoCon_RampControl.vi             |                        v
   |  Keithley / DC2200 / MFLI VIs       |                   Web Push (VAPID)
   |        |                            |                        |
   +--------+ writes CSV/TDMS            +--> pg_cron watchdog     v
              to the run directory           (link-lost alarm)   phones, laptops
```

### 3.1 Data tiers

Three tiers, because the free database is 500 MB and 10 Hz telemetry fills it in 36 hours if
you are careless.

| Tier | Rate | Where | Retention | Purpose |
|---|---|---|---|---|
| Full rate | 10 Hz | Local CSV on bench PC, then gzipped to Storage | Forever | Record of truth. Analysis. |
| History | 0.2 Hz (1 per 5 s) | Postgres `telemetry` | Rolling 48 h | Scrollback on the dashboard. |
| Live | 1 Hz | Realtime Broadcast, not persisted | None | The moving line on your phone. |

The arithmetic, so nobody re-derives it:

- A Cryocon row is 16 columns, about 150 bytes as CSV, about 400 bytes as a Postgres row with
  a jsonb payload and index overhead.
- At 10 Hz that is 345 MB/day against a 500 MB database. It dies overnight.
- At 0.2 Hz it is 6.9 MB/day, so a 48-hour window holds about 14 MB. Comfortable.
- Storage is 1 GB. Raw CSV at 10 Hz is 5.4 MB/hour, so 1 GB is 185 hours. Gzipped, CSV of this
  shape compresses about 9x, giving roughly 1,600 hours. **Gzip is mandatory, not optional.**
- Realtime allows about 2 M messages/month. Broadcasting 1 Hz continuously is 2.6 M/month and
  would exceed it. Therefore **broadcast only while at least one viewer is subscribed**, gated
  on Realtime Presence. An unwatched run costs zero messages.

When Storage approaches 1 GB, move runs older than one year to Google Drive (15 GB free) with
`rclone` and update the `datasets` row to point at the new location. Do not delete.

### 3.2 Why Supabase rather than the alternatives

Postgres, Realtime, Auth, Storage, Edge Functions, and cron in one free project, all reachable
over outbound HTTPS and WSS. One backend means one set of credentials, one authorization model,
and one place to look when something breaks. Firebase would also work but its query model
fights tabular scientific data. Self-hosting reintroduces the inbound-port problem.

---

## 4. Hard constraints

### 4.1 Instrument safety, non-negotiable

From `OVERSHOOT_TUNING_LOG.md` and `FINAL_REPORT.md` in the existing Cryocon repo. These are
measured, not assumed. The agent enforces them in Python. The web UI also enforces them, but
the web UI is not trusted — the agent is the authority.

| Limit | Value | Reason |
|---|---|---|
| Max setpoint | **450 K** | Over-temperature disconnect trips at 470 K. It is set on the front panel and is NOT remotely readable or settable; every SCPI variant returns NAK. |
| Max P gain | **50** | P-only stability limit is P around 82. P = 25 gives about 62 degrees of phase margin. |
| I (integral time) | **900 s** | A time in seconds, not a gain. Lowering it makes windup worse. Do not go below 600 without review. |
| Max power | **70 %** | 35 W of the HI range 50 W full scale. |
| Max ramp rate | **2.0 K/min** | Above 300 K there is no active cooling. Passive return is 0.25 K/min. |
| Command order | Park setpoint at current T in PID mode, engage CONTROL, set TYPE RAMPP, **then** write the target | Reversing this presents the full error the instant control engages. Observed on hardware: heater pinned at 70 % for 35 s, integrator wound to 60 % when 7 % was needed. |
| On exit | Always send `STOP` | Including on crash, on abort, and on agent shutdown. |

Above 300 K an overshoot cannot be undone. A run that overshoots strands the cryostat for
hours. Treat the ceiling as physical, not advisory.

Also note: `Loop_CONTROL.vi` engages **both** control loops. Before first use confirm Loop 2 is
off or harmless, or a second heater is armed silently.

### 4.2 Remote control policy

Remote **monitoring** is open to every group member. Remote **control** is gated:

- `runs.control_origin` is `local` or `remote`.
- A rig holds a single-writer lock (`rigs.locked_by`, `rigs.locked_until`) renewed by the
  heartbeat. Two people cannot drive one rig.
- **Dead-man timer**: if a run has `control_origin = 'remote'` and the agent has had no
  successful cloud contact for 120 s, the agent sends `STOP` and marks the run `aborted`.
  A run with `control_origin = 'local'` is never killed by a network fault, because a human is
  standing next to it.
- Only profiles with role `operator` or `admin` may insert a `launch` or `set_param` command.

### 4.3 Free-tier ceilings

Verify current figures on the Supabase pricing page before committing. These were accurate at
time of writing and are the basis for the sizing above.

| Resource | Free allowance | Expected use |
|---|---|---|
| Postgres | 500 MB | ~15 MB rolling telemetry plus metadata |
| Storage | 1 GB | Gzipped raw data, ~1,600 run-hours |
| Realtime | ~200 concurrent, ~2 M msg/month | Presence-gated, well under |
| Edge Functions | ~500 K invocations/month | A few hundred notifications |
| Auth | 50,000 MAU | Six |
| Cloudflare Pages | Unlimited static requests | Dashboard |
| Tailscale | 100 devices | Six people, three rigs |

**The one trap**: a free Supabase project **pauses after about 7 days of inactivity**. Over a
semester break notifications would silently stop. Phase 1 includes a GitHub Actions cron that
pings the REST API daily. Do not skip it, and do not discover it in January.

---

## 5. Repository layout

One new monorepo, separate from the existing Cryocon repo.

```
frostbyte/
  README.md
  FROSTBYTE_PLAN.md            <- this file, moved here in Phase 0
  AI_STYLE_GUIDE.md            <- copied from overleaf-copy, applies verbatim
  .env.example

  db/
    migrations/
      0001_core.sql
      0002_notifications.sql
      0003_rls.sql
      0004_cron.sql
    seed/seed_dev.sql
    README.md                  <- how to apply migrations

  agent/                       <- frostbyte-agent, Python 3.11+
    pyproject.toml
    frostbyte_agent/
      __init__.py
      config.py                <- reads frostbyte.toml plus env
      client.py                <- Supabase wrapper, retries, backoff
      spool.py                 <- SQLite offline queue
      heartbeat.py
      registry.py              <- loads program manifests
      launcher.py              <- subprocess plus LabVIEW adapter
      tailer.py                <- CSV/TDMS incremental reader
      publisher.py             <- decimation, broadcast, telemetry insert
      uploader.py              <- gzip, Storage upload, dataset indexing
      safety.py                <- interlocks, dead-man, single-writer lock
      commands.py              <- polls the commands table
      cli.py                   <- frostbyte-agent run | register | doctor
    programs/                  <- program manifests live here
      cryocon_ramp.toml
      cryocon_gui.toml
    tests/
    install/
      install_service.ps1      <- NSSM or Task Scheduler registration
      frostbyte.example.toml

  web/                         <- frostbyte-web, Vite + React + TS + Tailwind
    src/
      lib/supabase.ts
      lib/realtime.ts
      lib/push.ts
      components/
      pages/
        Dashboard.tsx
        Programs.tsx
        RunLive.tsx
        RunDetail.tsx
        Explorer.tsx
        PlotBuilder.tsx
        Settings.tsx
      styles/tokens.css
    public/
      manifest.webmanifest
      sw.js                    <- service worker for Web Push
    index.html

  functions/                   <- Supabase Edge Functions (Deno)
    dispatch-push/index.ts
    index-dataset/index.ts

  pylib/                       <- fbplot, pip-installable
    pyproject.toml
    fbplot/
      __init__.py
      client.py                <- fetch runs and datasets from Supabase
      style.py                 <- matplotlib rcParams, the house style
      figures.py
      cli.py
    styles/frostbyte.mplstyle

  .github/workflows/
    keepalive.yml              <- daily REST ping, prevents project pause
    web-deploy.yml
```

### 5.1 Stack decisions, already made

Do not re-litigate these. They are chosen for consistency with the existing Oberleaf codebase
so the same contributors and agents are already fluent.

- Web: **Vite + React 18 + TypeScript + Tailwind**. Server state via React Query. No Next.js.
- Charts: **uPlot** for live and large series (100k points at 60 fps). **Plotly.js** only in the
  Explorer, where interactive zoom and hover matter more than raw speed.
- Agent: **Python 3.11+**, stdlib `sqlite3`, `supabase-py`, `pyserial`, `watchdog`.
- Icons: **Lucide**. No emojis anywhere in the UI. See Appendix E.
- Edge Functions: Deno with `npm:` specifiers.

### 5.2 Design tokens

Reuse the Oberleaf token structure from `overleaf-copy/brand_assets/BRAND_GUIDELINES.md`: warm
neutral surfaces, no cold blue-black dashboard look. Frostbyte adds a temperature-semantic
accent pair, because here colour carries meaning.

```css
/* Light — "Frost" */
--bg-canvas:#FBFBFA; --bg-panel:#FFFFFF; --bg-subtle:#F2F4F5;
--border-subtle:#E3E6E8; --text-main:#1C1917; --text-sub:#57534E;
--accent-cold:#0F6B7B;   /* glacier teal: temperature, setpoint, nominal */
--accent-ember:#C2410C;  /* heater output, power, anything above ambient */
--state-warn:#B45309; --state-critical:#B42318; --state-ok:#1B5E20;

/* Dark — "Nocturne" */
--bg-canvas:#141416; --bg-panel:#1C1C1F; --bg-subtle:#26262B;
--border-subtle:#2E2E35; --text-main:#F5F5F4; --text-sub:#A8A29E;
--accent-cold:#4FA8BD; --accent-ember:#E8703A;
--state-warn:#D9822B; --state-critical:#E5534B; --state-ok:#2EA043;
```

Rule: cold accent for temperature and setpoint traces, ember for heater and power traces. Keep
it identical across web charts and `fbplot`, so a figure in a paper looks like the dashboard it
came from.

---

## 6. Core concepts an agent must understand before coding

### 6.1 A run is a directory

When the agent launches a program it creates:

```
%LOCALAPPDATA%/Frostbyte/runs/<run_id>/
  params.json      <- written by agent before launch; the program reads it
  RUN              <- sentinel file; exists while the run should continue
  data.csv         <- written by the program, appended, flushed per row
  status.json      <- optional, written by the program: {state, message, progress}
  stdout.log
  stderr.log
  DONE             <- written by the program on clean exit
```

This filesystem contract is the entire integration surface between Frostbyte and a measurement
program. It works identically for Python and LabVIEW, needs no TCP, no DLLs, and no NI
libraries on the cloud side. A physicist can implement it in a VI in an afternoon.

### 6.2 Data flows one way

The program writes `data.csv`. The agent tails it. The agent never writes to `data.csv` and the
program never talks to Supabase. This keeps instrument code free of network dependencies and
means a program still works with the platform switched off.

### 6.3 Nothing on the network path may block the control loop

`publisher.enqueue()` writes to a SQLite spool and returns in microseconds. A separate uploader
thread drains the spool. If the WiFi drops for an hour, the spool grows and the run continues
untouched; when the link returns, the backlog uploads. Any code path where a Supabase call can
block a measurement thread is a bug, and a serious one.

---

## 7. Phases

Each phase names its deliverable files, its acceptance test, and the specific mistakes to avoid.
Phases 0 through 5 are the spine. Phase 6 is the one that gives you "upload my LabVIEW program
and Python GUI". Phase 8 is the multi-file plotting.

---

### Phase 0 — Foundations

**Goal**: accounts, network, repo. No application code.

**Tasks**

1. Install **Tailscale** on the bench PC and on every group member's laptop and phone. Free
   plan, up to 100 devices. Sign in with the same identity provider for all.
2. On the bench PC enable Remote Desktop and confirm it is reachable over the Tailscale IP from
   another device. This alone solves "a group member is not present and has no control" for all
   six instruments today, including the LabVIEW ones, with zero code.
3. Create the Supabase project. Region closest to Amaravati (Singapore or Mumbai). Record the
   project ref, URL, anon key, and service role key.
4. Create the GitHub repo `frostbyte`, private. Push the layout skeleton from section 5 and
   move this file into it.
5. Copy `overleaf-copy/AI_STYLE_GUIDE.md` into the repo root unchanged.
6. Generate the VAPID keypair now, before it is needed:
   `npx web-push generate-vapid-keys`. Store both halves in a password manager.

**Done when**: you can RDP into the bench PC from your phone over Tailscale, and
`curl https://<ref>.supabase.co/rest/v1/ -H "apikey: <anon>"` returns from a laptop.

**Do not**: open any router port, request a static IP, or involve university IT. Tailscale
exists precisely so you do not have to.

---

### Phase 1 — Data spine

**Goal**: the database exists, is secured, and stays awake.

**Deliverables**: `db/migrations/0001_core.sql` through `0004_cron.sql`, `db/seed/seed_dev.sql`,
`.github/workflows/keepalive.yml`, `.env.example`.

**Tasks**

1. Apply the schema in Appendix A, one migration file per section. Use the Supabase SQL editor
   or the CLI; either is fine, but the `.sql` files must be committed so the schema is
   reproducible.
2. Create Storage buckets: `raw` (private), `figures` (private), `previews` (private).
3. Apply the RLS policies in Appendix A.5. The lab is six trusted people, so the model is
   deliberately simple: any authenticated user reads everything; only `operator` and `admin`
   write commands; the agent uses the service role key and bypasses RLS.
4. Enable `pg_cron` and `pg_net` extensions.
5. Add `keepalive.yml`: a daily GitHub Action that GETs one row from `rigs` with the anon key.
   This is what stops the project pausing after 7 idle days.
6. Seed one rig (`bench-1`) and one instrument (`cryocon22c`).

**Done when**: `select * from rigs;` returns the seed row; an anonymous request without a JWT
is rejected; the keepalive workflow has run green once.

**Do not**: put the service role key anywhere near the web app or a GitHub Actions log. It
bypasses all row-level security. It belongs only in the agent config on the bench PC and in
Edge Function secrets.

---

### Phase 2 — Agent skeleton

**Goal**: a Windows service that connects, heartbeats, survives network loss, and does nothing
else yet.

**Deliverables**: the whole `agent/` tree from section 5, minus `launcher.py` and `tailer.py`.

**Tasks**

1. `config.py` reads `frostbyte.toml` from `%PROGRAMDATA%/Frostbyte/` with env overrides.
   Fields: `supabase_url`, `service_role_key`, `rig_id`, `programs_dir`, `runs_dir`,
   `heartbeat_interval` (default 15 s), `spool_path`.
2. `spool.py`: SQLite table `queue(id INTEGER PK, kind TEXT, payload TEXT, created_at TEXT,
   attempts INT DEFAULT 0, next_try_at TEXT)`. API is `enqueue(kind, payload)` and
   `drain(batch_size)`. Enqueue must never block or raise on a full disk; log and drop with a
   counter instead of taking the process down.
3. `client.py`: Supabase wrapper with exponential backoff (1, 2, 4, 8, up to 60 s), jitter, and
   a `connected: bool` the rest of the agent can read.
4. `heartbeat.py`: every 15 s, update `rigs.last_seen_at`, `agent_version`, `status`. Renew the
   single-writer lock if held.
5. `cli.py`: `frostbyte-agent doctor` prints Python version, config path, Supabase reachability,
   COM ports found, spool depth, and clock skew against the server. Make this genuinely useful;
   it is the first thing anyone runs when something breaks.
6. `install/install_service.ps1`: register as a Windows service via NSSM, or as a Task Scheduler
   task at logon with highest privileges if NSSM is unavailable. Auto-restart on failure.

**Done when**: unplug the bench PC ethernet for 10 minutes with the agent running; the process
stays alive, the spool grows, `doctor` reports disconnected, and on reconnect `rigs.last_seen_at`
resumes updating with no restart and no lost spool rows.

**Do not**: use `time.sleep()` in the main loop in a way that delays shutdown. Use
`threading.Event().wait(timeout)` so the service stops promptly when Windows asks it to.

---

### Phase 3 — Instrument the existing Cryocon GUI

**Goal**: prove the spine end to end against real hardware, with the smallest possible diff to
validated code.

**Deliverables**: changes to `cryocon_gui.py` in the existing repo; `agent/frostbyte_agent/publisher.py`.

**Tasks**

1. Add `frostbyte_agent.publisher` as an optional import. If it fails to import, or if no config
   is present, the GUI must behave exactly as it does today. Frostbyte must never be a
   prerequisite for running the instrument.
2. In `_toggle_logging` (`cryocon_gui.py:950`), when logging starts: create a run via the
   publisher, capture `run_id`, set `control_origin = 'local'`.
3. In `_log_telemetry_row` (`cryocon_gui.py:1028`), immediately after the existing
   `self.log_writer.writerow([...])`, add one call:
   `self.fb.push(run_id, row_dict)`. The publisher handles decimation to 0.2 Hz for the database
   and 1 Hz for broadcast. The GUI does not know or care about rates.
4. In `_toggle_logging` when logging stops, and in `_on_close` (`cryocon_gui.py:1190`): mark the
   run `done`, gzip the CSV, upload it, insert the `datasets` row, insert a `run_complete`
   notification.
5. Add a small connection indicator to the status area: `Frostbyte: online` / `offline (N queued)`.
   Text only, no emoji, no coloured dot that pulses.

**Done when**: start a ramp on the real Cryocon; a `runs` row appears within 2 s; `telemetry`
grows at about 0.2 Hz; stopping the log produces a `.csv.gz` in the `raw` bucket and a
`datasets` row whose `row_count` matches the local CSV line count minus one.

**Do not**: touch `_polling_worker` (`cryocon_gui.py:621`), the ramp sequencer
(`_execute_anti_surge_ramp_thread`, `cryocon_gui.py:766`), or any PID or command-ordering logic.
Those are validated. The diff for this phase should be under 80 lines.

---

### Phase 4 — Web dashboard, read-only

**Goal**: see the lab from a phone. No control yet.

**Deliverables**: `web/` with Dashboard, RunLive, RunDetail pages; deployed to Cloudflare Pages.

**Tasks**

1. Supabase Auth, email magic link. Invite the six group members. Create their `profiles` rows
   with role `member`, and yours as `admin`.
2. `Dashboard.tsx`: rig cards with online status and current run; a list of recent runs with
   status, program, duration, and who started them.
3. `RunLive.tsx`: subscribe to the Realtime Broadcast channel `run:<run_id>`; render with uPlot.
   Join Presence on subscribe — this is what tells the agent a viewer is watching and that it
   should broadcast at all.
4. `RunDetail.tsx`: query `telemetry` for history, list `datasets` with signed download URLs.
5. Theme tokens from section 5.2, light and dark, following the viewer's system preference.
6. Deploy to Cloudflare Pages. Environment variables: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.

**Done when**: on a phone on mobile data, not on lab WiFi, you can watch a live Cryocon ramp
update once per second, and the chart stays smooth over a 30-minute run.

**Do not**: ship the service role key to the browser. Only the anon key, and it is safe there
precisely because RLS is in force.

---

### Phase 5 — Notifications

**Goal**: your phone buzzes when a run finishes, with the browser closed.

**Deliverables**: `functions/dispatch-push/index.ts`, `web/public/sw.js`,
`web/public/manifest.webmanifest`, `web/src/lib/push.ts`, `db/migrations/0002_notifications.sql`,
`0004_cron.sql`.

**Design**: three layers.

- **In-app**: the dashboard subscribes to `notifications` via Realtime and shows a toast and an
  unread badge. Covers the second-monitor case. About 20 lines.
- **Web Push**: an insert into `notifications` fires a Database Webhook to the
  `dispatch-push` Edge Function, which signs a VAPID payload and pushes to every row in
  `push_subscriptions`. This is the layer that works with the app closed.
- **Server-side watchdog**: `pg_cron` inserts `link_lost` when an active run stops reporting.

**Tasks**

1. Create the tables from Appendix A.4.
2. Write `dispatch-push` using `npm:web-push@3.6.7`. Full implementation in Appendix C.
   Delete subscriptions that return HTTP 404 or 410; they are expired and will never recover.
3. Register a Database Webhook: on `INSERT` to `public.notifications` call `dispatch-push`.
4. `sw.js`: handle `push` (show notification) and `notificationclick` (focus or open
   `/run/<run_id>`). Use `tag: run-<run_id>` so repeated events on one run collapse into a
   single entry instead of stacking.
5. `push.ts`: subscribe with the VAPID public key, upsert into `push_subscriptions` keyed on
   endpoint. Add a Settings toggle so people can turn it off.
6. `manifest.webmanifest` plus icons, so the app is installable.
7. `pg_cron` watchdog from Appendix A.6: every minute, insert a `critical` `link_lost`
   notification for any run that is `running` but whose `last_seen_at` is older than 90 s.
8. The agent's only notification code is an `INSERT` into `notifications`. No push SDK, no
   vendor library, no secrets on the bench PC beyond the Supabase key it already has.

**Notification catalogue** — implement exactly these `kind` values:

| kind | severity | Fires when |
|---|---|---|
| `run_complete` | info | Program exited cleanly. Body carries final value, duration, row count. |
| `run_failed` | critical | Non-zero exit or the program wrote an error to `status.json`. |
| `link_lost` | critical | pg_cron watchdog. No telemetry for 90 s during an active run. |
| `limit_trip` | critical | A safety interlock in `safety.py` fired. |
| `setpoint_reached` | info | Optional, opt-in per run. Temperature within tolerance for 60 s. |

**Done when**: with the dashboard installed to your iPhone home screen and Safari fully closed,
finishing a run produces a lock-screen notification, and tapping it opens that run's page.

**Two caveats to communicate to the group, not to work around**:

- **iOS requires Add to Home Screen.** Web Push works on iPhone only when the app is installed
  as a PWA from Safari (16.4+). Android and desktop work in a normal tab. This is a one-time
  15-second step per person, but somebody has to walk the group through it or they will report
  that push is broken.
- Clearing browser data destroys the subscription. The Settings page must show current
  subscription status and offer a re-subscribe button.

---

### Phase 6 — Program registry and launcher

**Goal**: this is the phase where "all the measurement programs are there and I open it to run
it" becomes true. Register a program once; it becomes launchable from any device.

**Deliverables**: `agent/frostbyte_agent/registry.py`, `launcher.py`, `commands.py`, `tailer.py`;
`web/src/pages/Programs.tsx`; manifests in `agent/programs/`.

**Tasks**

1. Implement the manifest format in Appendix B. `registry.py` loads every `.toml` in
   `programs_dir` at startup and on SIGHUP, validates it, and upserts into the `programs` table
   with `param_schema` as jsonb.
2. `Programs.tsx` renders a form from `param_schema`. Types: `float`, `int`, `bool`, `enum`,
   `string`, each with label, unit, default, min, max, step, options, help text. Validate in the
   browser for a good experience; the agent revalidates because the browser is not trusted.
3. Launching inserts a `commands` row with `verb = 'launch'`. `commands.py` polls every 2 s for
   `status = 'pending'` rows for this rig, claims one atomically
   (`update ... set status='claimed' where id=? and status='pending'`), and executes it.
4. `launcher.py` creates the run directory from section 6.1, writes `params.json`, writes the
   `RUN` sentinel, starts the process, and records the PID.
5. `tailer.py` polls `data.csv` every 250 ms from the last byte offset, parses new complete lines
   (never a partial trailing line), and hands rows to the publisher. Poll rather than use
   filesystem events; Windows file notifications are unreliable for a file being appended to by
   another process.
6. Stop: delete the `RUN` sentinel, wait `stop_grace` seconds from the manifest, then terminate.
   Abort: terminate immediately, then run the manifest's `on_abort` command, which for the
   Cryocon is a direct serial `STOP`.
7. Wire `safety.py`: validate every parameter against Appendix A limits before launch. Reject
   with a clear message naming the limit and the value. Enforce the single-writer lock. Start
   the dead-man timer for `control_origin = 'remote'`.

**Done when**: from your laptop at home, over Tailscale off, purely through the web app, you can
launch a Cryocon ramp to 350 K at 1 K/min, watch it live, and stop it. And attempting to launch
at 470 K is refused by the agent with the message
`Rejected: target 470.0 K exceeds the 450 K ceiling (over-temperature disconnect trips at 470 K).`

**Do not**: let the web app write instrument values directly. Everything goes through `commands`,
so there is one audit trail and one enforcement point.

---

### Phase 7 — LabVIEW integration

**Goal**: the five LabVIEW instruments join the platform without rewriting their VIs.

**Deliverables**: `agent/programs/*.toml` for each VI, a reusable LabVIEW sub-VI
`Frostbyte_RunHarness.vi`, and a folder-watcher path for VIs that cannot be modified.

There are two integration levels. Use the lowest one that meets the need.

**Level 1 — folder watch (zero VI changes).** The VI already writes a CSV or TDMS somewhere.
Point a manifest at that folder with `mode = "watch_folder"`. The agent detects new files,
uploads them, indexes their columns, and posts a notification. You lose live streaming and
remote launch, but you gain data sync and notifications for the cost of one config file. Start
every instrument here.

**Level 2 — full harness (about 6 blocks added to the VI).** Add `Frostbyte_RunHarness.vi` to
the VI's block diagram:

1. **At start**: read `params.json` from the directory in the `FROSTBYTE_RUN_DIR` environment
   variable. Unbundle into the VI's existing controls. If the variable is absent, use front-panel
   values, so the VI still runs standalone by hand.
2. **In the acquisition loop**: append one CSV row per sample to `data.csv`. Open with
   Open/Create/Replace in read/write mode, set file position to end, write, and **flush every
   row**. Without the flush, LabVIEW buffers and the agent sees nothing for minutes.
3. **In the loop**: check whether the `RUN` sentinel still exists. If it is gone, exit the loop
   cleanly through the normal shutdown path, which for the Cryocon means `Loop_STOP.vi`.
4. **Optionally**: write `status.json` every few seconds with `{state, message, progress}`.
5. **On exit**: write `DONE`. The agent treats a vanished process without `DONE` as a failure.

For `CryoCon_RampControl.vi` specifically, follow `labview/CRYOCON_LABVIEW_BUILD_SPEC.md` in the
existing repo. The command ordering there is safety-critical and already verified against
hardware. The harness wraps it; it does not modify it.

Launch a VI headlessly with:
`LabVIEW.exe /r "C:\path\CryoCon_RampControl.vi"` with `FROSTBYTE_RUN_DIR` set in the
subprocess environment. Better, build it to an executable so LabVIEW's IDE is not in the loop.

**Done when**: a Keithley IV sweep launched from the web produces a live chart, and its TDMS file
lands in Storage with its columns indexed and searchable.

**Do not**: try to call LabVIEW over VISA from Python while a VI holds the instrument. Two
processes on one serial port produce interleaved garbage that looks like a hardware fault and
costs a day to diagnose. The manifest declares which instrument a program owns; the agent
enforces exclusivity.

---

### Phase 8 — Explorer and multi-file plotting

**Goal**: pick columns across many files and plot them. The feature you asked for by name.

**Deliverables**: `functions/index-dataset/index.ts` or agent-side indexing;
`web/src/pages/Explorer.tsx`, `PlotBuilder.tsx`; `pylib/fbplot`.

**Tasks**

1. **Index on ingest.** When `uploader.py` uploads a dataset it also parses the header and
   computes per-column statistics, then inserts `dataset_columns` rows: name, position, dtype,
   unit, min, max, null count. This is what makes the column picker instant. Never make the
   browser download a 200 MB CSV to discover its column names.
2. **Unit inference**: parse the trailing token of a column name. `Temp_A_K` gives unit `K`,
   `Heater_Pct` gives `%`, `Ramp_Rate_K_min` gives `K/min`. Store the cleaned label separately
   from the raw column name.
3. **`Explorer.tsx`**: filter runs by program, instrument, sample, tag, date range, and
   free-text title. Multi-select runs into a selection tray that persists across filter changes.
4. **`PlotBuilder.tsx`**, the core interaction:
   - Selection tray holds N datasets.
   - X axis picker lists columns present in **all** selected datasets, from `dataset_columns`.
   - Y axis picker allows any number of series; each series is (dataset, column) with an
     editable legend label, defaulting to `<run title> — <column>`.
   - Per-series options: colour, line style, marker, axis assignment (left or right), and an
     offset or scale factor for stacked comparisons.
   - Axis controls: log or linear, limits, label overrides.
   - Normalisation options that transport measurement actually needs: subtract first point,
     normalise to maximum, divide by a chosen column.
   - Save the whole thing as a `plots` row with a `spec` jsonb. Saved plots are shareable by URL.
5. **Data fetching**: for series under 50k points fetch from `telemetry`. Above that, download
   the gzipped CSV from Storage, parse in a Web Worker, and decimate for display using
   largest-triangle-three-buckets so peaks survive downsampling. Never block the main thread.
6. **`fbplot`**: a pip-installable package so the same plot renders as a publication figure.

   ```python
   import fbplot
   fig = fbplot.plot_spec("<plot_id>")        # by saved spec
   fig.savefig("fig3.pdf")

   runs = fbplot.find(program="cryocon_ramp", sample="MoS2-04")
   fbplot.compare(runs, x="Elapsed_Sec", y="Temp_A_K")
   ```

   `style.py` sets the house rcParams: serif text matching the paper, 300 dpi, minor ticks in,
   1.2 pt spines, colours from section 5.2. Every group member gets identical figures because
   they all import the same style. Promote the existing `make_final_figures.py` into this module
   rather than starting over.
7. **"Copy Python" button** in PlotBuilder emits the exact `fbplot` snippet that reproduces the
   on-screen chart locally. This is the bridge between exploring in the browser and rendering
   for a paper, and it costs almost nothing to build.

**Done when**: you can select six Cryocon runs from different days, plot `Temp_A_K` against
`Elapsed_Sec` for all six on one chart with a legend, add `Heater_Pct` on a right-hand axis,
save it, open the saved URL on another device, and reproduce it byte-for-byte in matplotlib
with the copied snippet.

**Do not**: render publication figures server-side. Deno Edge Functions cannot run matplotlib,
and adding a Python cloud host breaks the free-tier constraint. Interactive plots live in the
browser; publication figures render locally through `fbplot`. If you later want one-click PDF
export, add a `figure_requests` table that any group member's machine can service with
`fbplot watch`.

---

### Phase 9 — Hardening

**Goal**: make it something you trust with an overnight run.

**Tasks**

1. **Retention job**: `pg_cron` deletes `telemetry` older than 48 h. Verify it runs; an unpruned
   telemetry table is the single most likely way to hit the 500 MB limit.
2. **Storage budget alarm**: weekly cron sums `datasets.bytes`; above 800 MB, insert a `warn`
   notification.
3. **Backups**: weekly GitHub Action dumps metadata tables (everything except `telemetry`) to a
   private repo. The free plan has no point-in-time recovery.
4. **RLS audit**: attempt every table read and write with a `member` JWT and confirm the
   expected result. Write it as a test, not a checklist.
5. **Agent supervision**: confirm the service restarts after a forced kill and after a reboot,
   and that it recovers a run that was in progress, marking it `failed` rather than leaving it
   `running` forever.
6. **Clock discipline**: enable NTP on the bench PC. `frostbyte-agent doctor` should warn above
   2 s of skew. Skewed timestamps make multi-instrument correlation useless and the cause is
   invisible until you try to align two datasets.
7. **Runbook**: `docs/RUNBOOK.md` covering agent will not start, run stuck in `running`, push
   notifications silent, database near quota, and how to recover raw data if Supabase is down
   (answer: it is already on the bench PC, that is why local CSV is the record of truth).

---

## Appendix A — Database schema

### A.1 Extensions and identity

```sql
create extension if not exists pgcrypto;
create extension if not exists pg_cron;
create extension if not exists pg_net;

create table profiles (
  id         uuid primary key references auth.users(id) on delete cascade,
  full_name  text,
  role       text not null default 'member' check (role in ('member','operator','admin')),
  created_at timestamptz not null default now()
);
```

### A.2 Hardware and programs

```sql
create table rigs (
  id            text primary key,               -- 'bench-1'
  label         text not null,
  os            text,
  agent_version text,
  status        text not null default 'offline'
                check (status in ('online','offline','busy')),
  last_seen_at  timestamptz,
  locked_by     uuid references auth.users(id),
  locked_until  timestamptz,
  created_at    timestamptz not null default now()
);

create table instruments (
  id         text primary key,                  -- 'cryocon22c'
  rig_id     text references rigs(id) on delete set null,
  label      text not null,
  vendor     text,
  model      text,
  interface  text,                              -- 'serial:COM5@57600'
  created_at timestamptz not null default now()
);

create table programs (
  id            text primary key,               -- 'cryocon_ramp'
  rig_id        text not null references rigs(id) on delete cascade,
  instrument_id text references instruments(id) on delete set null,
  name          text not null,
  kind          text not null check (kind in ('python','labview','executable')),
  description   text,
  param_schema  jsonb not null default '[]',
  manifest      jsonb not null default '{}',
  enabled       boolean not null default true,
  updated_at    timestamptz not null default now()
);
```

### A.3 Runs, telemetry, commands, datasets

```sql
create table runs (
  id             uuid primary key default gen_random_uuid(),
  program_id     text references programs(id) on delete set null,
  rig_id         text references rigs(id) on delete set null,
  instrument_id  text references instruments(id) on delete set null,
  started_by     uuid references auth.users(id),
  control_origin text not null default 'local' check (control_origin in ('local','remote')),
  title          text,
  sample         text,
  tags           text[] not null default '{}',
  params         jsonb  not null default '{}',
  status         text   not null default 'queued'
                 check (status in ('queued','starting','running','completing',
                                   'done','failed','aborted')),
  started_at     timestamptz,
  ended_at       timestamptz,
  last_seen_at   timestamptz,
  row_count      bigint not null default 0,
  error          text,
  created_at     timestamptz not null default now()
);
create index runs_status_seen_idx on runs (status, last_seen_at);
create index runs_created_idx     on runs (created_at desc);
create index runs_sample_idx      on runs (sample);

-- decimated history only; full rate lives in Storage
create table telemetry (
  run_id uuid        not null references runs(id) on delete cascade,
  t      timestamptz not null,
  data   jsonb       not null,
  primary key (run_id, t)
);

create table commands (
  id           uuid primary key default gen_random_uuid(),
  rig_id       text not null references rigs(id) on delete cascade,
  run_id       uuid references runs(id) on delete cascade,
  issued_by    uuid references auth.users(id),
  verb         text not null check (verb in ('launch','stop','abort','set_param','ping')),
  args         jsonb not null default '{}',
  status       text  not null default 'pending'
               check (status in ('pending','claimed','done','failed','expired')),
  claimed_at   timestamptz,
  completed_at timestamptz,
  result       jsonb,
  error        text,
  created_at   timestamptz not null default now(),
  expires_at   timestamptz not null default now() + interval '2 minutes'
);
create index commands_poll_idx on commands (rig_id, status, created_at);

create table datasets (
  id           uuid primary key default gen_random_uuid(),
  run_id       uuid references runs(id) on delete cascade,
  storage_path text not null unique,
  filename     text not null,
  kind         text not null default 'csv'
               check (kind in ('csv','tdms','json','image','other')),
  bytes        bigint,
  sha256       text,
  row_count    bigint,
  t_start      timestamptz,
  t_end        timestamptz,
  created_at   timestamptz not null default now()
);

-- the column index that makes the plot builder instant
create table dataset_columns (
  dataset_id uuid not null references datasets(id) on delete cascade,
  name       text not null,
  position   int  not null,
  dtype      text not null check (dtype in ('float','int','text','datetime','bool')),
  unit       text,
  label      text,
  v_min      double precision,
  v_max      double precision,
  n_null     bigint,
  primary key (dataset_id, name)
);
create index dataset_columns_name_idx on dataset_columns (name);

create table plots (
  id         uuid primary key default gen_random_uuid(),
  owner      uuid references auth.users(id) on delete set null,
  title      text not null,
  spec       jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### A.4 Notifications

```sql
create table notifications (
  id         bigint generated always as identity primary key,
  run_id     uuid references runs(id) on delete cascade,
  rig_id     text references rigs(id) on delete set null,
  instrument text,
  kind       text not null check (kind in
               ('run_complete','run_failed','link_lost','limit_trip','setpoint_reached')),
  severity   text not null default 'info' check (severity in ('info','warn','critical')),
  title      text not null,
  body       text,
  payload    jsonb not null default '{}',
  created_at timestamptz not null default now()
);
create index notifications_created_idx on notifications (created_at desc);

create table push_subscriptions (
  id         bigint generated always as identity primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  endpoint   text not null unique,
  p256dh     text not null,
  auth       text not null,
  user_agent text,
  created_at timestamptz not null default now()
);

create table notification_reads (
  notification_id bigint references notifications(id) on delete cascade,
  user_id         uuid   references auth.users(id)    on delete cascade,
  read_at         timestamptz not null default now(),
  primary key (notification_id, user_id)
);

alter publication supabase_realtime add table notifications;
alter publication supabase_realtime add table runs;
alter publication supabase_realtime add table rigs;
```

### A.5 Row-level security

Deliberately simple. Six trusted people; the complexity budget belongs in the instrument safety
layer, not in per-row ownership rules.

```sql
alter table profiles            enable row level security;
alter table rigs                enable row level security;
alter table instruments         enable row level security;
alter table programs            enable row level security;
alter table runs                enable row level security;
alter table telemetry           enable row level security;
alter table commands            enable row level security;
alter table datasets            enable row level security;
alter table dataset_columns     enable row level security;
alter table plots               enable row level security;
alter table notifications       enable row level security;
alter table push_subscriptions  enable row level security;

-- any signed-in lab member reads everything
create policy read_all on runs            for select to authenticated using (true);
create policy read_all on telemetry       for select to authenticated using (true);
create policy read_all on rigs            for select to authenticated using (true);
create policy read_all on instruments     for select to authenticated using (true);
create policy read_all on programs        for select to authenticated using (true);
create policy read_all on datasets        for select to authenticated using (true);
create policy read_all on dataset_columns for select to authenticated using (true);
create policy read_all on notifications   for select to authenticated using (true);
create policy read_all on profiles        for select to authenticated using (true);

-- only operators and admins may command hardware
create policy write_commands on commands for insert to authenticated
  with check (
    exists (select 1 from profiles p
            where p.id = auth.uid() and p.role in ('operator','admin'))
  );
create policy read_commands on commands for select to authenticated using (true);

-- people manage their own plots and their own push subscriptions
create policy own_plots on plots for all to authenticated
  using (owner = auth.uid()) with check (owner = auth.uid());
create policy read_plots on plots for select to authenticated using (true);
create policy own_push on push_subscriptions for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
```

The agent connects with the service role key and bypasses RLS entirely. That key never leaves
the bench PC and Edge Function secrets.

### A.6 Scheduled jobs

```sql
-- link-lost watchdog: the notification the agent cannot send, because the agent is what died
select cron.schedule('fb_watchdog', '* * * * *', $job$
  insert into notifications (run_id, rig_id, instrument, kind, severity, title, body)
  select r.id, r.rig_id, r.instrument_id, 'link_lost', 'critical',
         'Lost contact with ' || coalesce(r.instrument_id, r.rig_id),
         'No telemetry for over 90 s during an active run.'
  from runs r
  where r.status = 'running'
    and r.last_seen_at < now() - interval '90 seconds'
    and not exists (select 1 from notifications n
                    where n.run_id = r.id and n.kind = 'link_lost');
$job$);

-- telemetry retention: without this the 500 MB limit arrives without warning
select cron.schedule('fb_prune_telemetry', '17 * * * *', $job$
  delete from telemetry where t < now() - interval '48 hours';
$job$);

-- expire stale commands so a dead agent does not leave them pending forever
select cron.schedule('fb_expire_commands', '*/5 * * * *', $job$
  update commands set status = 'expired'
  where status = 'pending' and expires_at < now();
$job$);
```

---

## Appendix B — Program manifest specification

One TOML file per program in `agent/programs/`. The agent validates and upserts these into the
`programs` table on startup.

```toml
id          = "cryocon_ramp"
name        = "Cryocon 22C — Anti-Surge Ramp"
description = "Ramps to a target with validated tuning. Zero overshoot, verified 352 K and 357 K."
kind        = "python"                # python | labview | executable
instrument  = "cryocon22c"            # exclusive lock is taken on this instrument
rig         = "bench-1"

[exec]
command  = ["python", "staged_ramp_test.py"]
cwd      = "C:/Users/sahgy/Downloads/Cryocon_22C_Temperature_Controller_Python-File"
env      = { PYTHONUNBUFFERED = "1" }
mode     = "run_dir"                  # run_dir | watch_folder
stop     = "sentinel"                 # sentinel | ctrl_c | terminate
stop_grace_s = 20
on_abort = ["python", "-c", "import cryocon_controller as c; c.Cryocon22C().disable_control()"]

[output]
file          = "data.csv"
format        = "csv"
timestamp_col = "Timestamp"
elapsed_col   = "Elapsed_Sec"
live_cols     = ["Temp_A_K", "Heater_Pct", "Ramp_SP_K"]   # broadcast subset
poll_ms       = 250

[[params]]
key = "target_k"
label = "Target temperature"
type = "float"
unit = "K"
default = 350.0
min = 77.0
max = 450.0                # hard ceiling; see section 4.1
step = 0.5
help = "Over-temperature disconnect trips at 470 K and cannot be reset remotely."

[[params]]
key = "rate_k_min"
label = "Ramp rate"
type = "float"
unit = "K/min"
default = 1.0
min = 0.1
max = 2.0

[[params]]
key = "p_gain"
label = "P gain"
type = "float"
default = 25.0
min = 1.0
max = 50.0                 # stability limit is about 82; keep margin
advanced = true

[[params]]
key = "i_time_s"
label = "Integral time"
type = "float"
unit = "s"
default = 900.0
min = 600.0
max = 3600.0
advanced = true
help = "Seconds, not a gain. Lower values increase windup."

[[params]]
key = "heater_range"
label = "Heater range"
type = "enum"
options = ["LOW", "MID", "HI"]
default = "HI"
advanced = true

[[params]]
key = "sample"
label = "Sample ID"
type = "string"
default = ""
help = "Recorded on the run for later filtering."
```

For a LabVIEW program that cannot be modified, use the minimal watch-folder form:

```toml
id         = "keithley_iv"
name       = "Keithley 2636B — IV Sweep"
kind       = "labview"
instrument = "keithley2636b"
rig        = "bench-1"

[exec]
mode = "watch_folder"
watch = "D:/LabVIEW Data/Keithley"
glob  = "*.tdms"
settle_ms = 2000            # wait for the file to stop growing before uploading

[output]
format = "tdms"
```

Rules for the agent implementing this:

- Unknown keys are an error, not a warning. Fail loudly at load time with the file and line.
- `max` on a parameter is advisory to the UI and **enforced** by `safety.py`. A manifest may
  narrow a limit but never widen one past section 4.1.
- `instrument` grants an exclusive lock. Two programs naming the same instrument cannot run at
  once. This is what stops LabVIEW and Python fighting over COM5.

---

## Appendix C — Edge Function: dispatch-push

```ts
// functions/dispatch-push/index.ts
import webpush from "npm:web-push@3.6.7";
import { createClient } from "npm:@supabase/supabase-js@2";

webpush.setVapidDetails(
  "mailto:lab@srmap.edu.in",
  Deno.env.get("VAPID_PUBLIC_KEY")!,
  Deno.env.get("VAPID_PRIVATE_KEY")!,
);

const db = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

Deno.serve(async (req) => {
  const { record } = await req.json();          // the inserted notifications row
  const { data: subs } = await db.from("push_subscriptions").select("*");

  const body = JSON.stringify({
    title: record.title,
    body: record.body ?? "",
    tag: `run-${record.run_id}`,                // collapses repeat buzzes for one run
    requireInteraction: record.severity === "critical",
    data: { url: `/run/${record.run_id}`, kind: record.kind, severity: record.severity },
  });

  await Promise.allSettled((subs ?? []).map(async (s) => {
    try {
      await webpush.sendNotification(
        { endpoint: s.endpoint, keys: { p256dh: s.p256dh, auth: s.auth } },
        body,
      );
    } catch (e) {
      // 404 and 410 mean the subscription is permanently gone
      if (e.statusCode === 404 || e.statusCode === 410) {
        await db.from("push_subscriptions").delete().eq("id", s.id);
      }
    }
  }));

  return new Response("ok", { status: 200 });
});
```

Secrets to set: `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`. `SUPABASE_URL` and
`SUPABASE_SERVICE_ROLE_KEY` are injected automatically.

---

## Appendix D — Environment variables

```
# agent — %PROGRAMDATA%/Frostbyte/frostbyte.toml, or env
FROSTBYTE_SUPABASE_URL=https://<ref>.supabase.co
FROSTBYTE_SERVICE_ROLE_KEY=<service role key>     # bench PC only, never in git
FROSTBYTE_RIG_ID=bench-1
FROSTBYTE_PROGRAMS_DIR=C:/ProgramData/Frostbyte/programs
FROSTBYTE_RUNS_DIR=C:/Users/<you>/AppData/Local/Frostbyte/runs
FROSTBYTE_HEARTBEAT_S=15

# web — Cloudflare Pages environment
VITE_SUPABASE_URL=https://<ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon key>                 # safe in the browser, RLS enforces access
VITE_VAPID_PUBLIC_KEY=<vapid public>

# edge function secrets
VAPID_PUBLIC_KEY=<vapid public>
VAPID_PRIVATE_KEY=<vapid private>

# fbplot — each member's own machine
FROSTBYTE_URL=https://<ref>.supabase.co
FROSTBYTE_ANON_KEY=<anon key>
```

`.env` is gitignored. `.env.example` is committed with every key present and every value blank.

---

## Appendix E — Agent conduct

`AI_STYLE_GUIDE.md` in the repo root applies to all code and all copy in this project. The
points that matter most here:

**No emojis anywhere in the product.** Not in buttons, toasts, notification titles, status
badges, commit messages, or log output. Use Lucide icons in the UI and plain text elsewhere.

**Write like a staff engineer talking to a peer.** State the fact, the diagnosis, the change.
No cheerleading, no exclamation points, no "Great question", no "Let me dive in".

**Banned vocabulary**: delve, tapestry, landscape, testament, seamless, game-changer, robust,
plethora, leverage, multifaceted, navigating. Banned structures: "Not just X, but Y" and "It is
worth noting that".

**Notification and UI copy is informative, not decorative.**

- Write `Ramp complete. 350.02 K after 47 min, 28,400 points.`
- Not `Success! Your ramp finished!`
- Write `Rejected: target 470.0 K exceeds the 450 K ceiling.`
- Not `Oops, that temperature is too high!`

**Explain root causes, not symptoms.** If a run fails with six errors from one dropped serial
connection, report the dropped connection as the root cause and label the rest as downstream
effects. This is the same discipline as the TeX cascade handling in the Oberleaf codebase.

**Symmetry of effort.** Diagnose and deliver one correct solution. Do not present four
speculative options and ask the user to choose when the evidence already picks one.

---

## Appendix F — Phase dependency order

```
0 Foundations
  |
  +--> 1 Data spine
         |
         +--> 2 Agent skeleton
                |
                +--> 3 Cryocon publisher hook  ---+
                |                                 |
                +--> 4 Web dashboard (read-only) -+--> 5 Notifications
                                                  |
                                                  +--> 6 Program registry & launcher
                                                         |
                                                         +--> 7 LabVIEW integration
                                                         |
                                                         +--> 8 Explorer & plotting
                                                                |
                                                                +--> 9 Hardening
```

Phases 3 and 4 can proceed in parallel once Phase 2 is done. Phases 7 and 8 can proceed in
parallel once Phase 6 is done.

**Suggested effort**, for a competent agent with hardware access when needed:

| Phase | Effort | Blocking on hardware |
|---|---|---|
| 0 Foundations | 2 h | No |
| 1 Data spine | 4 h | No |
| 2 Agent skeleton | 1 day | No |
| 3 Cryocon hook | 3 h | Yes, for the acceptance test |
| 4 Web dashboard | 2 days | No |
| 5 Notifications | 1 day | No |
| 6 Registry and launcher | 2 days | Yes |
| 7 LabVIEW integration | 2 days per instrument | Yes |
| 8 Explorer and plotting | 3 days | No |
| 9 Hardening | 1 day | Partly |

Phase 0 alone, done in an afternoon, already fixes the largest complaint: a group member who is
not physically present currently has no visibility and no control. Tailscale plus Remote Desktop
solves that for all six instruments before a line of Frostbyte code exists. Do it first.

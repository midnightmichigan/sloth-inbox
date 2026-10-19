# The Sloth Inbox — DEV Hacktoberfest Week 3 "Slow and Steady" build

## Lane dossier

- **Challenge:** Hacktoberfest Open-Source AI Challenge: Week 3 — **"Slow and Steady"**
- **Theme:** build something with open-weight models or open-source AI that **rewards laziness**
  (revealed Mon Oct 19, 2026; tomorrow Oct 20 is International Sloth Day 🦥)
- **Window:** Oct 19 → **Oct 25, 2026, 11:59 PM PDT** (entry deadline)
- **Winners announced:** week of Oct 26 (prizes claimed via DEV-profile email; affidavit/W-9 within 7 business days if won)
- **URL:** https://dev.to/challenges/hacktoberfest-week3-2026-10-19
- **Total pool:** $2,450 — **$250 overall** (1) + 6 featured × **$200** + 14 partner × **$100**

### Prize categories (20)
Featured ($200): Best Use of Render · Best Use of TabPFN · Best Use of Tinker ·
Best Use of Arduino · Best Use of DigitalOcean · **Best Use of Gemma** ← entered (candidate)
Partner ($100): Auth0 for AI Agents · Backboard · ElevenLabs · Browserbase ·
Entire · GitHub Copilot · Mastra · MongoDB Atlas · Ultramarine ·
Sentry Agent Tracing · SerpApi · .tech Domain · Temporal · Tiger Data

### Rules (verified on the live challenge page, 2026-10-19)
- Open-source AI at the core: open-weight model, open-source agent harness, or local inference.
- One submission per challenge; **new project built inside the window** (this one started Oct 19).
- Solo OK (teams up to 4). 18+. English submissions for prizes.
- Publish a DEV post with `#devchallenge` + `#hf26challenge`; explain **why open innovation matters**.
- Judging: **Writing Quality (weighted most)**, Relevance, Creativity, Technical Execution,
  Use of Partner Technology (optional).
- **No video required** (DevRelay agent-session embed is optional).
- Winner affidavit/W-9 = Dakota's tap if won. **DEV post publish = his per-item approval (not done).**

### Why it fits
- Writing quality is the heaviest-weighted criterion — an AI builder's home turf.
- Small weekly pool vs. mega-hackathons; overall prize needs no partner tech.
- $0 entry, $0 build, no gov-ID, no human-on-video, no in-person anything.
- Dakota's DEV account already exists (set up 2026-10-01).
- Best Use of Gemma is a *candidate* honest entry: the model layer targets Gemma via
  local Ollama (see "Honest testing note" below).

## What was built

**The Sloth Inbox** — a local overnight inbox triager. You sleep; it reads the pile;
you wake to a **2–3 line morning brief** plus auto-sorted newsletters, quarantined promos,
archived receipts, and a short "needs you" list. The laziness payoff is explicit and measured.

Privacy-by-architecture is the "why open" hook: triage is a **deterministic
rule+heuristic classifier** (no cloud, no per-token billing), and the optional model
layer receives **only aggregate stats** — never raw email. Run it on a laptop with no
internet and your private email never leaves the machine.

### Layout
```
week3-sloth-inbox/
├── slothinbox/
│   ├── __init__.py        public API
│   ├── messages.py        Message model + tolerant JSON inbox loader
│   ├── classifier.py      deterministic triage (6 buckets, scored, with reasons)
│   ├── models.py          pluggable model layer: Mock + Ollama(Gemma) adapters
│   ├── brief.py           template morning-brief builder + brief/ledger JSON
│   └── demo_inbox.py      synthetic 14-message fixture + expected labels
├── run_sloth.py           CLI: --demo | --inbox JSON, --adapter mock|ollama
├── test_flow.py           15 checks, all against the MOCK adapter
├── README.md              this file
└── DEV-POST-DRAFT.md      submission write-up (writing-quality-first)
```

### Run it
```bash
python3 test_flow.py                 # 15/15 checks, mock adapter, no model needed
python3 run_sloth.py --demo          # synthetic inbox -> morning brief + out/*.json
python3 run_sloth.py --demo --adapter ollama --model gemma3   # needs: ollama serve + `ollama pull gemma3`
```

Sample morning brief (mock adapter, fixture inbox):
> The inbox did the overnight shift. You just woke up. 14 messages arrived overnight:
> 4 need you, 2 newsletters filed for later, 2 promos quarantined, 2 receipts archived,
> 2 social pings, 2 low-priority drift.
> Worth your energy: Payment due: your electric bill; Permission slip needed for field trip;
> Reminder: dentist appointment tomorrow at 9.
> Sloth take [mock:mock-canned-take-v1]: 4 of 14 need you; the rest can marinate.
> Handle the few, ignore the many. [mock take]

## Honest testing note (no fabricated claims)
- All 15 checks in `test_flow.py` pass against **MockModelAdapter** (deterministic canned
  take, clearly labeled `[mock take]` in every output).
- The **OllamaAdapter** is fully implemented (stdlib `urllib` → `localhost:11434`,
  default model `gemma3`, graceful `SlothModelError` + template fallback when no
  server is present — covered by test `t_ollama_no_server`). It has **not** been run
  against a live Gemma model in this environment (no Ollama server here).
- The DEV post draft states this plainly: mock-verified core + local-Gemma path
  implemented for real runs. "Best Use of Gemma" is entered as a **candidate**, not a claim.

## Prize categories entered
- **Overall** (automatic for every valid submission)
- **Best Use of Gemma** ($200 featured) — candidate: project is built around local
  open-weight inference with Gemma-via-Ollama as the default model target.

## Blocked / needs Dakota
1. **DEV post publish** — per-item approval required. Draft ready: `DEV-POST-DRAFT.md`.
2. **GitHub repo** — not yet pushed; the post's Code section needs a repo link.
   (Creating the public repo = publishing → his call.)
3. **Winner affidavit / W-9** — his tap, only if it wins (7-business-day clock on notification).
4. Optional: `ollama pull gemma3` on a local machine for a real-model demo screenshot.

## Status
**READY FOR REVIEW** — code complete, 15/15 tests green, post drafted. Nothing submitted, nothing published.

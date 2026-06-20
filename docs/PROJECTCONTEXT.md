# SATURDAYS — Project Context (single source of truth)

> Read this first. It contains everything a fresh working session needs to run the operation end-to-end. Last updated from the founding strategy session.

---

## 0. What this is
**Saturdays** — a parent's countdown of the time they have left with their kids, made beautiful and visible, designed to change how present you are *today*. It started life as a generic "life countdown / death clock," then we deliberately narrowed it to one tribe and one emotion.

- **Name:** Saturdays (locked). From the gut-punch: *"You get ~940 Saturdays with your kid before they're grown — you've spent 312."*
- **One-liner:** *The childhood you can't get back, made visible.*
- **Tagline candidates:** "Be present for the time you can't get back." · "Make the Saturdays count."

---

## 1. The strategic spine (why it exists this way)
- **The trap we're avoiding:** there are dozens of death-clock apps; they're novelties with no retention (see your number once, never return). "Be the best death clock" is a losing frame.
- **The goal:** ~**10,000 obsessed users** — a "be loved by one specific tribe" number, not a mass-market number. That makes this an *audience + distribution* problem, not a feature problem.
- **Beachhead tribe:** **parents of young kids.** Chosen because the founder is a parent (founder-community fit) and it scores best on reach, recurrence, shareability, positive tone, and "least death-clock-like."
- **Differentiation (not copyable):**
  1. **Frame** — childhood, not death (positive, cherishing).
  2. **Signature mechanic** — *overlapping family timelines* (your life next to your kids' childhoods next to your aging parents): *"When your youngest turns 18, you'll be 54 and your mom will be 81."*
  3. **Distribution artifact** — a literal **kitchen clock** + a shareable **reveal image**.
- **Other tribes are SEQUENCED, not abandoned:** the same engine re-skins for the **Stoic/"life in weeks"** crowd and **distance-separated families** later (config knobs: *who the clock is about · what it counts toward · what "good days" buy back*). Build for parents only; don't build the multi-tribe abstraction until tribe #2 forces it.

---

## 2. Product pillars
1. **Reframed clock** — per-kid countdown to age 18 / "leaving home," shown as **Saturdays / summers / bedtimes left**.
2. **Overlapping family timelines** (signature view).
3. **Presence ritual** — daily check-in reframed from "health" to *presence* (phone-down, fully-there); good days bank time and build a compounding streak.
4. **Ambient / Display Mode** — fullscreen glanceable clock for a spare tablet or Raspberry Pi (the home clock).
5. **The reveal** — one-tap shareable image ("312 Saturdays left") = the growth engine.

---

## 3. Current built state (what already exists)
All static, single-file, no build step, `localStorage` only, no backend, no tracking.

- **`index.html`** — the working app (currently still the *self/health* version, light "health-app" theme). Features already built:
  - Live ticking countdown to a conservative estimated date.
  - Baseline from sex + 8 lifestyle factors; **health conditions** (overlap-dampened); a floor so the clock never starts already-expired.
  - **Daily check-in** with compounding streak, 30-day history, "buy-back" projection.
  - **"Where you'll gain the most"** insights → one-tap into the **what-if simulator**.
  - **"Time with the people you love"** (visits-left estimator) + a **reflection nudge**.
  - **Design:** light health theme (white cards, soft shadows, green→teal gradient), animated **ECG heartbeat hero**, breathing countdown card with live dot + per-second beat, onboarding first-run screen, softer coral for conditions, honors `prefers-reduced-motion`.
- **`ambient-clock.html`** — standalone calm always-on display for the DIY home clock (config block at top; dark screen-friendly face; rotating kids' Saturdays/summers/bedtimes + presence nudges; night auto-dim).
- **`18-SUMMERS-BUILD-PLAN.md`** — the full 6-month roadmap (parallel swimlanes → Jan 1 2027).
- **`DIY-CLOCK-GUIDE.md`** — build the home clock (tablet test → Raspberry Pi) + the 7-day self-experiment.

> Note: the app is currently branded "Life Clock" and is about the *user's own* life. **Rebranding to "Saturdays" + reframing around kids is the v1 job** (see §6).

---

## 4. Where it lives / infra
- **Repo:** `ktxd3130-ops/LifeClock` (private). *(Optional cleanup: rename repo → `saturdays`; GitHub redirects and Vercel follows.)*
- **Hosting:** its **own Vercel project**, separate from the founder's AI course. **Auto-deploys on push to the default branch.**
- **IMPORTANT — the AI course is separate:** the old `ai-launchpad` repo/site is unrelated; the clock was fully removed from it. Do not touch `ai-launchpad`.
- **Data/privacy:** everything local in the browser. Keep it that way until accounts are genuinely needed (cross-device sync, home-clock mirroring, or comparing timelines with *other* users). Privacy is a selling point to parents — say it loudly, never sell data, minimize PII (kids' data is sensitive).

---

## 5. Why we're moving sessions
The session this context was written in was scoped to the unrelated `ai-launchpad` repo, so it could **not push to `LifeClock`** (confirmed: git proxy returns "repository not authorized"; repo creation blocked; no add-repo tool). Every change had to be hand-delivered as files. **The fix: a working session scoped to the app repo**, where push + Vercel auto-deploy work directly. That's this new session.

---

## 6. v1 (MVP) scope — the first build for the new session
Ship in ~4 weeks. Refuse anything not here.
- **Rebrand** Life Clock → **Saturdays** (name, copy, tone shifts from "your death" to "your kids' childhood").
- **Onboarding:** add kids (name + birthdate); set independence age (default 18). Optional: partner, the user's own parents.
- **Hero clocks:** per kid — *Saturdays / summers / bedtimes left* + live countdown.
- **Overlapping family timelines** — single screen, all local (no accounts yet).
- **Presence check-in** — daily phone-down/quality-time toggles → compounding streak (reuse existing engine).
- **The reveal** — one-tap shareable image ("312 Saturdays left").
- **Ambient Mode** — fullscreen glanceable route (fold in `ambient-clock.html`), for tablet/Pi.
- Keep the light health UI + animated hero already built.
- **Deliberately NOT in v1:** accounts, cloud sync, comparing with *other people*, payments, hardware product. Those are built *ahead in parallel* once v1 ships (see build plan).

---

## 7. Roadmap headline (full detail in build plan)
Four parallel swimlanes → **Jan 1, 2027 New Year's resolution launch**:
- **A · Live App** (ship v1, iterate weekly)
- **B · Next Phase, built ahead** (accounts/sync, Ambient Mode polish, "compare with others," Premium)
- **C · Hardware** (DIY now → kit → maybe a finished device, validated by pre-orders)
- **D · Growth/Commercial** (reveal + creators + waitlist → resolution campaign)
- **Business model:** freemium (free reveal drives growth; Premium = family timelines + Ambient Mode + memory logging) + a "Clock + 1yr Premium" holiday/resolution gift bundle + a print-on-demand keepsake poster.

---

## 8. Parked / backlog
- **Naming sub-tasks:** product = Saturdays ✅; still open: final tagline, repo rename, logo/wordmark.
- Travel "life is short, take the trip" angle — keep as the *non-commerce* reflection nudge for now; affiliate only much later if sticky.
- E-ink "calm" home-clock variant (great for the Stoic tribe later; can't tick seconds).
- Founder's **7-day self-experiment** with the DIY clock — the most important near-term data point ("freak out or change my life?"). Fold the finding into the product.

---

## 9. Immediate next actions for the new session
1. Confirm you can **push to this repo and that it auto-deploys** (a tiny test commit is fine).
2. Commit the existing artifacts into the repo if not already there (`index.html`, `ambient-clock.html`, the plan + guide, this file).
3. (Optional) Rename repo → `saturdays`.
4. Start **v1** per §6: rebrand + kid clocks + overlapping timelines + presence + reveal + Ambient Mode. Then deploy and share the URL.

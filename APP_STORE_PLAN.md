# Saturdays — App Store Deployment Plan

> **Status:** Pre-submission planning. The app is a shipping web product; this document is the bridge from "live website" to "App Store listing."
> **Last updated:** 2026-06-20
> **Owner:** Kendall (ktxd3130-ops)

---

## 0. TL;DR / Recommendation

**Wrap the existing `index.html` in [Capacitor](https://capacitorjs.com/), don't rewrite.** The app is a single, polished, self-contained HTML file with canvas rendering, `localStorage`, and `navigator.share` — it is *already* the entire UI. A React Native rewrite throws all of that away for no user-visible gain. A pure PWA can't get a real App Store listing. Capacitor lets us ship the exact same code as a native iOS binary, then bolt on the four things Apple actually cares about: **local notifications, a home-screen widget, native share, and (optionally) HealthKit.**

Those native features aren't just nice-to-haves — they are how we survive **App Review Guideline 4.2** (Apple rejects apps that are "just a repackaged website"). The native layer is the difference between approval and rejection, so it's scoped as **required**, not optional.

**Critical technical blocker to internalize now:** `localStorage` inside a `WKWebView` is **not durable** — iOS can evict it under storage pressure. All user state (`saturdays_v2`) must migrate to `@capacitor/preferences` (and shared into an **App Group** so the widget can read it) before launch. This is the single most important code change.

**Headline risks:** (1) Apple Developer account + signing setup (~1 week of admin, $99/yr); (2) mortality/death content sensitivity review; (3) widget requires native Swift/WidgetKit code (can't stay pure-web); (4) HealthKit triggers extra review scrutiny — defer to v1.1.

**Realistic timeline:** ~4–6 weeks of part-time work to first TestFlight build, ~6–8 weeks to App Store submission.

---

## 1. Current State

### Git
- **Branch:** `main`, clean, up to date with `origin/main`.
- **Commits:**
  - `2d167a6` — *Saturdays v2 — mortality-first rebuild* (current `index.html`)
  - `1f6745d` — *Saturdays v1 — childhood presence clock*
- **Untracked:** `.claude/` only (tooling; gitignore it or leave it).
- **Repo:** `ktxd3130-ops/LifeClock` (private). Consider renaming to `saturdays` later — GitHub redirects and Vercel follows.

### Codebase
- **`index.html`** — 879 lines, the *entire* app: HTML + inline CSS + inline JS. No build step, no dependencies, no backend.
  - **Onboarding:** birthday + sex → SSA period-life-table estimate.
  - **Clock:** hero "Saturdays left" number, life-in-weeks dot grid (canvas), % lived, remaining years/months/weeks.
  - **Health:** 8 lifestyle toggles (`+4` exercise … `-10` smoker) that recompute the number live.
  - **People I love:** shared-Saturdays / visits-left per loved one.
  - **Presence:** weekly "was this Saturday intentional?" check-in + streak + 52-week strip.
  - **The reveal:** 1080×1920 Instagram-story canvas, `navigator.share` + download.
  - **Ambient mode:** fullscreen glanceable clock.
  - **Storage:** `localStorage` key `saturdays_v2`. Nothing leaves the device.
- **`docs/`** — project context, README, DIY clock guide, ambient clock. (Note: `docs/PROJECTCONTEXT.md` describes the older "18 Summers / kids" framing; the live app is the mortality-first self version. Reconcile the docs separately — not a blocker for App Store.)

### Deployment
- **Live:** https://saturdays-vert.vercel.app (confirmed serving the mortality-first v2).
- **Vercel project:** `saturdays` (`prj_U2vErO4SD4VizGsYcEwF83XIE3Vi`), auto-deploys on push to `main`.
- **Footer/share URL** baked into the reveal image: `saturdays-vert.vercel.app`.

**Implication:** Keep the Vercel web app alive permanently. It's the **viral landing page** for shared reveal images and the no-install entry point. The App Store binary and the web app are two faces of one codebase.

---

## 2. App Store Readiness Assessment

### 2.1 The wrapper decision

| Approach | Effort | Reuses current code | App Store eligible | Native features (push, widget, Health) | Verdict |
|---|---|---|---|---|---|
| **PWA only** | Trivial | 100% | ❌ Not a real listing (Apple doesn't list PWAs; "Add to Home Screen" only) | ❌ No widget/HealthKit, limited notifications | **No** |
| **Capacitor** | Low–Medium | ~95% (bundle `index.html` as-is) | ✅ Yes | ✅ Via plugins + small native extensions | ✅ **Recommended** |
| **React Native rewrite** | High | ~0% (re-implement canvas grid, share, all UI) | ✅ Yes | ✅ Native | ❌ Wasteful — no user-visible benefit |

**Decision: Capacitor.** Ship `index.html` essentially unchanged inside a native shell, add native capabilities as Capacitor plugins + two small Swift extensions (widget + share-data writer).

> **PWABuilder note:** PWABuilder can generate an iOS package, but it produces a Capacitor/WKWebView wrapper under the hood — same approach, less control. Use Capacitor directly so we own the Xcode project for the widget extension and HealthKit entitlement.

### 2.2 Guideline 4.2 ("minimum functionality") — the real gate

Apple **rejects thin website wrappers**. To clear 4.2, the binary must demonstrate genuine native value. Our four native features each map to a 4.2 justification:

- **Local notifications** → "reminds you each Saturday morning" (can't do reliably from a website).
- **Home-screen widget** → "your Saturday count, always visible" (impossible on web).
- **Native share sheet** → reliable image export to Messages/Instagram (Web Share files are flaky in WKWebView).
- **HealthKit (v1.1)** → auto-fills your profile from Apple Health.

Ship at least notifications **and** the widget for v1.0. Two solid native features is the safe threshold.

### 2.3 Storage durability (must-fix)

`WKWebView` `localStorage` is evictable by iOS. Migrate `saturdays_v2` to:
- **`@capacitor/preferences`** for the canonical store (durable, native UserDefaults/SQLite-backed).
- Mirror the computed **Saturdays-left integer + birthday + adjustment** into a shared **App Group** (`group.app.saturdays.shared`) so the WidgetKit extension can read it without launching the app.

Keep a thin compatibility shim so the same `index.html` still works on the web (falls back to `localStorage` when Capacitor isn't present).

---

## 3. Native Feature Plan (feature by feature)

### 3.1 Push / reminder notifications — *use LOCAL, not remote*

The Saturday check-in is a **weekly, content-free reminder**. That's a textbook **local notification** — no server, no APNs certificate, no backend. This preserves the "nothing leaves your device" promise (a core selling point).

- **Plugin:** `@capacitor/local-notifications`.
- **Schedule:** a repeating notification every **Saturday ~9:00am local** — *"It's Saturday. Were you present this week?"* deep-linking to the Presence screen.
- **Permission:** request on first visit to the Presence screen (contextual, not at launch — better opt-in rates and avoids a cold permission prompt).
- **Remote push (APNs):** **defer.** Only needed for server-driven campaigns (milestones, win-back). Adds a backend + privacy-label complexity that contradicts the local-only ethos. Revisit post-launch if retention data justifies it.

### 3.2 iOS widget — *requires native Swift (WidgetKit)*

A widget showing the live Saturday count is the strongest retention + 4.2 feature, but **WKWebView can't render widgets** — this is a genuine native code chunk.

- **Build:** a **WidgetKit extension** in the Xcode project (Swift + SwiftUI).
- **Data flow:** the web app writes `{ saturdaysLeft, birthday, adjustmentYears, asOf }` into the shared **App Group** UserDefaults on every recompute. The widget's `TimelineProvider` reads that and, for freshness between app opens, **recomputes the count itself** from `birthday + adjustmentYears` (the math in `compute()` is trivial to port to ~30 lines of Swift). Schedule a daily timeline refresh.
- **Sizes:** small (just the number + "Saturdays left") and medium (number + a compact dot strip).
- **Effort:** ~2–3 days including the Swift port of the date math. This is the most "native" part of the project — budget accordingly.

### 3.3 Share sheet — *native plugin, replace flaky Web Share*

`navigator.share({files})` is unreliable in WKWebView (file sharing support is partial). Replace with native:

- **Plugins:** `@capacitor/filesystem` (write the canvas PNG to a temp file) + `@capacitor/share` (open the native share sheet with the file URL + caption).
- **Flow:** `canvas.toBlob()` → base64 → `Filesystem.writeFile` → `Share.share({ files:[uri], text })`.
- **Keep the web path** as a fallback (same `index.html` runs on Vercel). Feature-detect `Capacitor.isNativePlatform()`.
- The reveal image already renders at 1080×1920 — no changes needed to the canvas itself.

### 3.4 Apple Health (HealthKit) — *defer to v1.1, optional, scrutiny-heavy*

HealthKit can auto-fill onboarding and inform the health toggles, but it raises the review bar and the privacy stakes. **Not in v1.0.**

- **What it could read:** date of birth (`HKCharacteristicType dateOfBirth`), biological sex, and *optionally* activity/resting-HR/sleep to pre-toggle "Exercise regularly" / "Sleep 7–8 hours."
- **Requirements (when we do it):** HealthKit entitlement, `NSHealthShareUsageDescription`, a privacy policy section describing health-data use, and review notes explaining *why* a "memento mori" app reads Health data.
- **Hard constraints:** HealthKit data **may not be used for advertising or marketing**, must not be sold, and the app **must not present medical claims or predictions**. Life-expectancy estimates must stay framed as motivational/population-level, never personal medical prediction.
- **Recommendation:** ship v1.0 with manual entry (already built). Add HealthKit as a v1.1 "Connect Apple Health to auto-fill" convenience, clearly optional, with a skip path. Keep the existing manual flow as the default forever.

---

## 4. Sensitivity & App Review Strategy (mortality/death content)

Death-clock apps **are approved** — precedents include *WeCroak* ("you're going to die," rated 12+), *Memento Mori*, and various "life in weeks" apps. The category is allowed; the framing and disclaimers determine the outcome.

### Likely review flags & mitigations

| Risk | Guideline | Mitigation |
|---|---|---|
| Reads as **medical advice / prediction** | 1.4.1 (medical), 1.1.6 (false info) | Keep the existing "*a mirror, not a prophecy*" / "*not medical advice*" framing prominent. Add a one-line methodology note ("U.S. SSA period life tables, population-level"). Never say "you will die on [date]." |
| **Distressing content / self-harm proximity** | 1.1 (objectionable content) | The framing is *presence and intention*, not doom — lean into that in copy and screenshots. Consider a discreet footer link to a crisis resource (e.g. 988 in the US) on the clock screen. Low cost, strong signal of care to reviewers. |
| **Age appropriateness** | Age rating questionnaire | Expect **12+** (infrequent/mild mature themes), matching WeCroak. Answer the questionnaire honestly; don't target it at kids. |
| **Health-data misuse** (if HealthKit added) | 5.1.3 | Covered in §3.4 — defer, then strict compliance. |

### Submission hygiene
- **App Review notes:** proactively state — *"Saturdays is a reflective 'memento mori' app inspired by Stoic philosophy. Estimates use public U.S. actuarial life tables and are explicitly framed as motivational, not medical or predictive. All data stays on-device."* Pre-empting the concern reduces rejections.
- **Screenshots & description:** emphasize *presence, intention, time with loved ones* — the positive frame. Avoid morbid imagery.
- **Tone:** the app already nails this ("Be present for the time you can't get back"). Carry it into the listing verbatim.

---

## 5. App Store Assets & Connect Checklist

### Accounts & identifiers
- [ ] **Apple Developer Program** enrollment ($99/yr) — *gating item, start first.*
- [ ] Bundle ID, e.g. `app.saturdays.ios` (registered in Developer portal).
- [ ] App Group: `group.app.saturdays.shared` (for the widget).
- [ ] App Store Connect app record created.
- [ ] Signing: Distribution certificate + provisioning profiles (let Xcode "Automatically manage signing").

### Visual assets
- [ ] **App icon** — 1024×1024 PNG, no alpha/transparency. (The amber-on-near-black "Satur**days**" mark translates directly.)
- [ ] **Screenshots** — required: **6.9" iPhone** set (Apple scales down for smaller devices). Add **13" iPad** set only if shipping universal. 3–6 shots: the clock/grid, health toggles, people-I-love, presence streak, the reveal image.
- [ ] **App preview video** (optional) — a 15–30s screen recording of the count animating + grid sweep is high-impact for this app.

### Listing copy (ASO)
- [ ] **Name:** `Saturdays` (check availability; fallback `Saturdays: Memento Mori`).
- [ ] **Subtitle (30 chars):** e.g. *"How many do you have left?"*
- [ ] **Keywords (100 chars):** memento mori, life calendar, weeks, mortality, presence, stoic, life clock, countdown.
- [ ] **Description, promotional text, support URL, marketing URL** (point support/marketing at the Vercel site).
- [ ] **Privacy Policy URL** — **mandatory.** Host at `saturdays-vert.vercel.app/privacy`. Easy win: "we collect nothing, everything is on-device."

### Privacy & compliance
- [ ] **Privacy Nutrition Label:** "**Data Not Collected**" — a genuine competitive advantage; state it loudly.
- [ ] Age rating questionnaire (expect 12+).
- [ ] Export compliance (standard HTTPS only → "uses exempt encryption").

### Build & release
- [ ] TestFlight internal build → external testers.
- [ ] Set release type (manual release recommended for v1.0).

---

## 6. Technical Architecture & Migration Steps

**Principle: one codebase, two targets.** `index.html` stays the source of truth and keeps deploying to Vercel. Capacitor bundles a copy as the native web layer.

### Project structure (proposed)
```
LifeClock/
├─ index.html              # source of truth (web + bundled into app)
├─ www/                    # Capacitor web root (build step copies index.html here)
├─ capacitor.config.ts     # appId: app.saturdays.ios, webDir: www
├─ ios/                    # generated Xcode project (committed)
│  └─ App/
│     ├─ App/              # main app target
│     └─ SaturdaysWidget/  # WidgetKit extension (Swift) + App Group
└─ package.json            # capacitor CLI + plugins
```

### Migration steps
1. **Storage shim** — wrap all `localStorage.getItem/setItem('saturdays_v2', …)` behind a small async-capable `Store` adapter: uses `@capacitor/preferences` on native, `localStorage` on web. *(Highest priority — durability fix.)*
2. **Scaffold Capacitor** — `npm init` → `@capacitor/core @capacitor/cli @capacitor/ios`, copy `index.html` into `www/`, `npx cap add ios`.
3. **Add plugins** — `@capacitor/local-notifications`, `@capacitor/share`, `@capacitor/filesystem`, `@capacitor/preferences`, `@capacitor/status-bar`.
4. **Wire native share** — feature-detect `Capacitor.isNativePlatform()`; native path uses Filesystem+Share, web path keeps `navigator.share`.
5. **Wire local notification** — schedule the weekly Saturday reminder on Presence-screen permission grant.
6. **App Group + widget** — create the App Group, write `{saturdaysLeft, birthday, adjustmentYears}` to it on each `compute()`, build the WidgetKit extension (port date math to Swift).
7. **Splash/icon/status bar** — generate with `@capacitor/assets` from the 1024 icon; dark status bar to match `--bg #0a0a0b`.
8. **Test on device**, then archive → TestFlight.

> Build step is just "copy `index.html` → `www/`" — no bundler needed. A one-line npm script keeps web and app byte-identical.

---

## 7. Phased Roadmap

| Phase | Scope | Est. effort |
|---|---|---|
| **0 — Admin** | Apple Developer enrollment, bundle ID, App Group, Connect record, privacy policy page | ~1 wk (mostly waiting on Apple) |
| **1 — Capacitor MVP** | Scaffold, storage shim, native share, local Saturday notification, icon/splash. Runs on a real device. | ~1 wk |
| **2 — Widget** | WidgetKit extension, App Group data flow, Swift date-math port, small + medium sizes | ~3 days |
| **3 — Assets & listing** | Icon, screenshots, (optional) preview video, copy, ASO, privacy label | ~3 days |
| **4 — TestFlight** | Internal + external testing, fix WKWebView quirks (safe areas, fonts, share) | ~1 wk |
| **5 — Submit v1.0** | Review notes, submit, respond to any rejection | ~1–2 wks incl. review |
| **v1.1 (later)** | HealthKit auto-fill, remote push campaigns (if retention warrants), Android via same Capacitor project | post-launch |

**First TestFlight: ~4 weeks. App Store live: ~6–8 weeks** (part-time, accounting for Apple's review cycle).

---

## 8. Blockers & Risks (prioritized)

| # | Item | Severity | Why it matters | Mitigation |
|---|---|---|---|---|
| 1 | **`localStorage` not durable in WKWebView** | 🔴 High | Users could silently lose their entire history (the emotional core of the app) | Migrate to `@capacitor/preferences` before *any* TestFlight build (§6 step 1) |
| 2 | **Guideline 4.2 "just a website" rejection** | 🔴 High | Thin wrappers get rejected | Ship local notifications **and** the widget; cite both in review notes |
| 3 | **Apple Developer account / signing** | 🟠 Med | Gates everything; enrollment can take days | Start Phase 0 immediately, in parallel with code |
| 4 | **Widget requires native Swift** | 🟠 Med | Only true "can't-do-in-web" piece; needs Xcode + WidgetKit | Budget 3 days; port the ~30-line date math to Swift |
| 5 | **Mortality content sensitivity** | 🟠 Med | Could draw extra reviewer scrutiny | Positive presence framing, disclaimers, crisis-resource link, proactive review notes (§4). Precedent (WeCroak) is favorable |
| 6 | **HealthKit review scrutiny** | 🟡 Low (deferred) | Entitlement + privacy + no-medical-claims rules | Defer to v1.1; ship manual entry first |
| 7 | **Web/app code divergence** | 🟡 Low | Two copies drift apart | Single `index.html` source + copy-to-`www` build step; feature-detect native APIs |
| 8 | **App name collision** | 🟡 Low | "Saturdays" may be taken on the Store | Have fallback `Saturdays: Memento Mori` ready |

---

## 9. Cost Summary

| Item | Cost |
|---|---|
| Apple Developer Program | **$99/year** (required) |
| Vercel hosting | $0 (current free tier is fine) |
| Backend / push infra | $0 (local notifications, on-device data) |
| Capacitor + plugins | $0 (open source) |
| **Total to launch** | **~$99/yr** + your time |

No backend, no recurring infra cost — the local-only architecture keeps this near-free to operate, which is also the privacy story that sells.

---

## Appendix A — Decision log
- **Capacitor over RN/PWA:** reuse the finished single-file app; PWA can't list; RN is a pointless rewrite.
- **Local notifications over APNs:** weekly reminder needs no server; preserves on-device privacy.
- **HealthKit deferred:** review scrutiny + privacy bar outweigh v1.0 value; manual entry already works.
- **Keep Vercel web app forever:** it's the viral landing page for shared reveals and the no-install funnel into the App Store.

## Appendix B — Open questions for Kendall
1. iPhone-only or universal (iPad) for v1.0? (Universal = one extra screenshot set + light layout testing.)
2. Bundle ID / app name preference (`app.saturdays.ios`? "Saturdays" vs "Saturdays: Memento Mori")?
3. Include the 988 crisis-resource footer link? (Recommended — cheap, signals care to reviewers and users.)
4. Android now (same Capacitor project) or iOS-first? (Recommend iOS-first, Android as a fast follow.)

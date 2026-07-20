# Saturdays Left — Roadmap

_Last updated: 2026-07-19, immediately after uploading 1.1.0 (build 3)._

---

## Where we are

**1.1.0 is uploaded and awaiting review.** It is a total rebrand — light-first
Clinical default, four themes, the 7-point shooting-star mark, Futura display
type, the official "Saturdays Left" name — plus two real bug fixes (the
black-and-amber fallback trap, and a timezone bug that filed evening logs under
the wrong day) and an accessibility pass that took contrast failures from 289 to 35.

The web app at `saturdays-vert.vercel.app` is already live with all of it.

---

## The one thing this product is fighting

Every other app in this category is a **novelty**: you see your number once, feel
something for ten seconds, and never open it again. That is the entire risk. The
number itself does not change fast enough to pull anyone back.

So every roadmap decision gets judged against one question:

> **Does this give someone a reason to return, or is it another way to see the number?**

Three mechanics answer "return," and they are the spine of this roadmap:

1. **Ambient presence** — the number visible without opening the app (widget).
2. **Agency** — habits that visibly move the number (built; needs deepening).
3. **Trajectory over time** — seeing your own curve bend across months (not built;
   this is the real long-term hook and, I'd argue, the actual paid product).

---

## Horizons

### H1 · Retention — the widget (next release, 1.2.0)
The single highest-leverage thing left. An always-visible number on the home or
lock screen is the direct antidote to the see-it-once failure mode.

Status: the widget is **written but not wired**. `ios/SaturdaysWidget` exists on
disk, but the Xcode project has exactly **one target** — the widget is not in the
build. Remaining work is integration, not authorship: add the target, register an
App Group in the developer portal, sign entitlements on both targets, and verify
on a real device.

### H2 · Measurement — see the funnel without breaking the promise
"Data Not Collected" is brand equity, and we are not giving it up. But we are
currently blind on whether any of this works.

The unlock: **we don't need an SDK.**
- **App Store Connect Analytics** gives impressions, product page views,
  conversion rate, downloads, crashes, and **retention curves** — free, no code,
  no tracking, no privacy-label impact.
- **Vercel edge/server logs** on the shared URL give reveal-image → visit volume
  in aggregate, no client-side tracking, no PII.

That is a real funnel: share → visit → install → retain. Enough to make decisions.

### H3 · Trajectory & monetization (2.0)
The stated plan is wearables auto-populating the habit inputs, behind a
subscription. **I want to flag a concern before we build it** (see Open
Questions): auto-filling toggles saves a user ~20 seconds a day, which is thin
justification for a recurring charge. The far stronger paid story is
**forecast history** — your life expectancy re-forecast monthly, charted, so you
watch your own trajectory bend. Wearables then become the *input* that makes that
chart effortless, rather than the product itself.

Technical path of least resistance: **HealthKit**, which already aggregates Apple
Watch and most rings/bands — one integration instead of N device partnerships.
Critically, HealthKit data read **on-device and never transmitted** preserves the
"Data Not Collected" label.

### H4 · Platform surface (later)
Apple Watch complication, iPad layout polish, and the physical/DIY kitchen-clock
artifact referenced in the older strategy docs.

---

## Next 4 weeks

### Week 1 — Ship the widget (1.2.0)
**Goal: the number lives on the home screen.**
- Babysit 1.1.0 through review; if rejected, fix and resubmit same day (top priority).
- Add the widget target to the Xcode project; App Group registered and signed on
  both targets; verify the bridge writes and the widget reads live data on a
  **real device**, not just simulator.
- Clear the leftover debt while we're in there: 35 accent-contrast flags, dead
  `dawn`/`minimal` CSS blocks, and rewrite/delete `BRAND_AND_UI_HANDOFF_2026.md`
  (it currently documents the abandoned dark direction and will mislead anyone
  who reads it).
- **Done when:** 1.2.0 is uploaded with a working widget.

### Week 2 — Turn the lights on
**Goal: stop flying blind, and make the share loop measurable.**
- Read the first real 1.1.0 numbers in App Store Connect: did the rebrand move
  conversion rate? What does day-1/day-7 retention look like?
- Aggregate reveal-image → visit counting on Vercel (no client tracking).
- Rework the share card against what the data says; it is the acquisition engine
  and it has never been measured.
- ASO pass on the live listing using real impression/conversion data.
- **Done when:** we can state install→retain numbers and have a baseline to beat.

### Week 3 — Build the hook worth charging for
**Goal: forecast history, the thing that makes this a returning product.**
- Data model for monthly life-expectancy snapshots (on-device).
- The trajectory chart: your forecast over time, bending with your habits.
- HealthKit read integration (steps, sleep, workouts) to auto-populate inputs —
  strictly on-device, privacy label unchanged.
- **Done when:** a user with two months of data sees their own curve.

### Week 4 — Monetization scaffolding
**Goal: a paywall that's defensible.**
- StoreKit 2 (or RevenueCat) wiring, restore purchases, sandbox testing.
- Decide the free/paid line — my recommendation: the core number, habits and
  widget stay **free forever** (they're the retention engine and the share loop);
  forecast history + HealthKit auto-sync are the paid tier.
- Price test framing: $1.99/mo reads impulse; $4.99/mo needs the trajectory chart
  to carry it. Ship at the lower price with an annual option.
- **Done when:** purchase flow works end-to-end in sandbox.

---

## Open questions worth deciding deliberately

1. **Is auto-tracking actually the paid product?** I don't think it is on its own.
   Forecast history is. Wearables make it effortless — that's a feature of the
   paid tier, not the reason to pay.
2. **Positioning was never resolved.** The original strategy chose a narrow,
   differentiated beachhead (parents / "the childhood you can't get back") and it
   was abandoned same-day for the broader mortality framing, with no decision
   record. The narrow framing is stronger psychology and more shareable. It has
   never been market-tested. Worth revisiting before spending on acquisition.
3. **Subtitle.** Listing now says "Life Time Tracker" for ASO. Confirm that's the
   permanent call vs. something closer to the brand voice.
4. **Does the privacy label change with HealthKit?** If data is read on-device and
   never transmitted, no. This must stay true — it's a core differentiator.

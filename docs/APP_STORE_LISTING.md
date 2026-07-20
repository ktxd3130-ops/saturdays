# Saturdays — App Store Listing (draft)

Copy-ready fields for App Store Connect. Character limits noted; counts are approximate — verify in Connect.

---

## Identity
- **Name** (≤30): `Saturdays Left`  *(14)*
- **Subtitle** (≤30): `Life Time Tracker`  *(18)*
- **Bundle ID:** `com.kendalldale.saturdays`
- **Primary category:** Lifestyle
- **Secondary category:** Productivity  *(avoid "Health & Fitness" — invites medical-app scrutiny; this app makes no medical claims)*
- **Age rating:** expect **12+** (infrequent/mild mature themes — mortality). Matches WeCroak.

## URLs
- **Support URL:** `https://saturdays-vert.vercel.app`
- **Marketing URL:** `https://saturdays-vert.vercel.app`
- **Privacy Policy URL:** `https://saturdays-vert.vercel.app/privacy`  *(live — see privacy.html)*

## Keywords (≤100, comma-separated, no spaces after commas)
```
life tracker,life calendar,weeks,countdown,presence,habits,life clock,4000 weeks,memento mori
```
*(93 chars — verified under the 100 limit. Don't repeat the app name in keywords; it's already indexed from the title.)*

## Promotional text (≤170, editable anytime without review)
```
A life is about four thousand Saturdays. See how many you have left — then spend this one like it counts.
```

## Description (≤4000)
```
You get about four thousand Saturdays in a life. Most people never count them.

Saturdays turns that number into something you can actually see. Enter your birthday, and watch your life laid out as a grid of weeks — the ones you've lived, and the ones you have left. It's a memento mori for the modern age: not morbid, but clarifying. The point isn't death. The point is paying attention to the time you still have.

WHAT YOU CAN DO

• See your number — how many Saturdays you likely have left, with your whole life drawn as a grid of weeks.
• Bend the curve — toggle real habits (exercise, sleep, smoking, stress) and watch your Saturdays shift, so you can feel what your choices are worth.
• Hold your people close — add the ones you love and see how many Saturdays you realistically share. The visits-left number changes how you treat the next one.
• Keep a weekly ritual — one question every Saturday: were you present? A quiet streak that rewards attention, not productivity.
• Make it impossible to ignore — generate a shareable image of your count and ask someone what they're doing with theirs.

PRIVATE BY DESIGN

Everything stays on your device. No account. No servers. No analytics. No tracking. We never see your data — because it never leaves your phone.

A NOTE ON THE NUMBERS

The estimate uses public U.S. actuarial (SSA period) life tables and is calculated entirely on your device. It's a population-level mirror for reflection — not a medical prediction, diagnosis, or advice. A mirror, not a prophecy.

If you're struggling, you're not alone. In the U.S. you can call or text 988 anytime.

Spend this Saturday like it counts.
```

## What's New (v1.1.0)
```
A whole new look.

Saturdays Left has been redesigned from the ground up — a clean, light interface built around one clear number, with a new seven-point star mark and four themes to choose from: Clinical, Cardstock, Slate and Graphite. Pick the one that fits how you think.

Also in this release:
• An optional daily reminder to log your day, at a time you choose.
• Fixed a timezone issue that could file an evening entry under the wrong date.
• Sharper contrast and legibility across every screen.

Everything still stays on your device. Always will.
```

---

## App Review notes (paste into "Notes for Reviewer")
```
Saturdays is a reflective "memento mori" app inspired by Stoic philosophy and the "life in weeks" idea. It visualizes how many weeks ("Saturdays") a person may have left.

- The life-expectancy figure uses public U.S. SSA period life tables and is computed on-device. It is explicitly framed throughout the app as motivational/reflective, NOT medical, predictive, or diagnostic ("a mirror, not a prophecy").
- The app does not access Apple Health/HealthKit and makes no medical claims.
- All data is stored locally on the device. No accounts, no servers, no analytics, no third-party SDKs. Privacy nutrition label is "Data Not Collected."
- A discreet 988 crisis-line link is included on the main screen as a duty-of-care measure.
- Native features beyond the web content: local notifications (a weekly presence reminder and an optional daily logging reminder) and native share-sheet image export.

No login required to review all functionality.
```

## Privacy Nutrition Label answers
- **Data Not Collected** — select this. The app collects no data of any kind.
- Encryption / export compliance: uses only standard HTTPS → **exempt** ("uses exempt encryption").

## Screenshots needed (6.9" iPhone required; 13" iPad since Universal)
1. The clock — hero number + life-in-weeks grid (the hook).
2. Bend the curve — health toggles shifting the count.
3. People I love — shared-Saturdays card.
4. Presence — the weekly check-in + streak.
5. The reveal — the shareable image.

> Tip: an App Preview video of the count animating + grid sweep is high-impact for this app.

## Pre-submission checklist
- [ ] Apple Developer enrollment complete
- [ ] Privacy Policy URL live (done: /privacy)
- [ ] Icon 1024×1024, no alpha
- [ ] Screenshots (6.9" iPhone + 13" iPad)
- [ ] Age rating questionnaire (→ 12+)
- [ ] Privacy label = Data Not Collected
- [ ] Review notes pasted (above)
- [ ] TestFlight build uploaded
```

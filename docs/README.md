# Life Clock

A personal life **countdown** driven by how you live. It estimates your remaining time from a conservative baseline life expectancy plus lifestyle factors, health conditions, and a daily good/bad-habit streak that compounds — then renders a live ticking clock to the estimated date.

Standalone, single-file, **no build step**. All data is stored in the browser's `localStorage` only — nothing is ever sent to a server.

## What's here
- `index.html` — the entire app (HTML + CSS + JS inline). Open it directly or deploy as a static site.

## Features
- Live countdown (years → seconds) to a conservative estimated date.
- Baseline from sex + 8 lifestyle factors (smoking, alcohol, activity, diet, weight, sleep, stress, social connection).
- **Health conditions** (diabetes, heart failure, stroke, COPD, cancer, major surgery, fractures, etc.), with overlapping conditions dampened rather than naively summed.
- **Daily check-in** — good days bank time and grow a streak whose bonus compounds; slips burn time and reset it. 30-day history grid.
- **"Where you'll gain the most"** — factors ranked by upside, one-tap into the simulator.
- **What-if simulator** — change any factor to see the effect, without touching your real baseline.
- **Time with the people you love** — add people by age + visits/year to see estimated visits remaining.

> ⚠️ Not medical advice. Conservative, population-level estimates for motivation only — not a prediction or diagnosis.

## Deploy
Any static host works. On Vercel: import this repo as a new project and deploy — the root serves `index.html`. No framework, no build command.

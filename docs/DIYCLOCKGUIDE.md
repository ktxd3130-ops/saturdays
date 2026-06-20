# DIY Ambient Life Clock — Build Guide

Goal: get a screen on your counter that shows your time (and your kids' childhood) **ticking down, 24/7** — so you can run the real experiment: *will I freak out, or will I actually change how I live?*

You'll do this in two stages on purpose:
- **Stage 1 (tonight, $0):** prove the *feeling* on a tablet/old phone before spending a cent.
- **Stage 2 (a weekend, ~$120–180):** the real always-on Raspberry Pi clock.

The display software is the included **`ambient-clock.html`**. Edit the CONFIG block at the top (your birthdate, sex, kids), save, open full-screen. That's the whole clock.

---

## Stage 1 — The $0 test (do this first)

1. Open `ambient-clock.html` and edit the **CONFIG** block: your `birthdate`, `sex`, and your `kids` (name + birthdate). Save.
2. Get the file onto a tablet or old phone. Easiest options:
   - AirDrop / email the file to yourself and open it in a browser, **or**
   - host it (it can live at a URL on your existing site, e.g. `/ambient`), then just open that link.
3. Make it full-screen and keep-awake:
   - **iPad/iPhone:** open in Safari → Share → *Add to Home Screen* → launch it (runs full-screen, no browser bars). Settings → Display → **Auto-Lock → Never**. For a true lock-down, turn on **Guided Access** (Settings → Accessibility) and triple-click to start.
   - **Android:** Chrome → menu → *Add to Home screen*. Settings → Display → **Screen timeout → longest / Stay awake**. Or a free "kiosk browser" app.
4. Prop it where you'll actually see it — kitchen counter, desk, by the coffee.
5. **Live with it for 7 days.** (See "The Experiment" at the bottom.)

If after a week it's changed even one decision, Stage 2 is worth it.

---

## Stage 2 — The Raspberry Pi always-on clock

### Shopping list (~$120–180)
| Part | Notes | Rough $ |
|---|---|---|
| **Raspberry Pi 5 (4GB)** | The brain. Pi 4 is fine; Pi Zero 2 W works but is slower. | $60–80 |
| **Official Raspberry Pi 7" Touch Display 2** | Clean, kitchen-sized. *Or* any small HDMI monitor you have. | $60–100 |
| **microSD card (32GB)** | The "hard drive." | ~$10 |
| **USB-C power supply (official 27W)** | Don't cheap out here. | ~$12 |
| **Case / stand** | A display stand makes it counter-worthy. | $15–25 |

> **Display choice:** use an **LCD/touchscreen** — it shows the smooth, *ticking* clock. (E-ink looks beautiful but refreshes too slowly to tick seconds — save e-ink for a future calm "weeks left" version.)

### Software setup (~30–45 min)
1. **Flash the OS.** Install **Raspberry Pi Imager** on your computer → choose **Raspberry Pi OS (64-bit)** → your SD card. In the Imager's settings (gear icon) pre-set: hostname, **Wi-Fi**, and **enable SSH** so you can work headless.
2. **Boot the Pi** with the SD card + display + power. Let it finish first-time setup, then update:
   `sudo apt update && sudo apt full-upgrade -y`
3. **Put the clock on the Pi.** Two options:
   - **Simplest:** host `ambient-clock.html` at a URL (e.g. on your site at `/ambient`) and just point the Pi at that link. Updates are then instant — change the file, the clock updates.
   - **Fully offline:** copy `ambient-clock.html` onto the Pi (e.g. `/home/pi/ambient-clock.html`) and point the browser at `file:///home/pi/ambient-clock.html`.
4. **Kiosk mode** (boot straight into the full-screen clock). Follow the official guide — it's the canonical, current method for Raspberry Pi OS:
   **https://www.raspberrypi.com/tutorials/how-to-use-a-raspberry-pi-in-kiosk-mode/**
   The core is auto-launching Chromium with these flags pointed at your clock URL/file:
   ```
   chromium-browser --kiosk --noerrdialogs --disable-infobars \
     --incognito --no-first-run "http://your-clock-url"   # or file:///home/pi/ambient-clock.html
   ```
5. **Stop the screen from blanking** (so it stays on). Disable screen blanking via `sudo raspi-config` → *Display Options → Screen Blanking → Off* (and/or `xset s off -dpms` in your kiosk start script).
6. **Reboot.** It should boot directly into the ticking clock. Lean it on the counter. Done.

### Nice touches (optional)
- The clock **auto-dims at night** (configurable in the CONFIG `nightDim` block) so it's not blasting white at 2am.
- Add a small physical frame/stand so it reads as an object, not a gadget — that's also your first piece of marketing content (film the reveal!).

---

## The Experiment (this is the real point)

Treat the first week as a study with one subject: you.

- **Day 1:** Write down your gut reaction the first time you really *see* the seconds fall. Dread? Calm? Nothing?
- **Daily:** Note any moment you chose differently *because* of the clock — closed the laptop, called your mom, said yes to one more story at bedtime. Even once counts.
- **Day 7:** Did it fade into wallpaper (you stopped seeing it), or did it change a decision? Be honest.

That answer tells us whether this is a novelty or a life-changer — and that's the single most important data point for the whole venture. If it moved *you*, it'll move other parents.

> ⚠️ It's a conservative, for-motivation estimate — not a prediction. If watching it ever feels heavy rather than clarifying, turn it off. The goal is to live *more*, not to dread.

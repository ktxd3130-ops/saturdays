# Saturdays — WidgetKit widget setup

A home-screen widget that shows your live **Saturdays-left** count. The Swift,
asset catalog, Info.plist, and JS bridge are all written and committed — these
steps wire the target into Xcode and connect the shared data. **Requires full
Xcode** (not just Command Line Tools) and an **Apple Developer account** (for
App Groups + device/TestFlight).

> Don't have full Xcode yet? Everything in `ios/SaturdaysWidget/` is ready to
> add the moment you do. No code needs to change.

## What's in the repo

```
ios/SaturdaysWidget/
  SaturdaysWidget.swift         # views (small + medium), provider, config
  SaturdaysWidgetBundle.swift   # @main bundle entry point
  SaturdayCalculator.swift      # Saturday math, ported 1:1 from index.html
  Info.plist                    # widgetkit-extension NSExtension
  Assets.xcassets/              # WidgetBackground (#0a0a0b) + AccentColor (#f0a04b)
widget-bridge.js                # reference data-bridge helper (see step 5)
```

The widget reads a JSON snapshot the app mirrors into the shared App Group on
every save/boot, then **recomputes** the count itself so it stays fresh between
app opens.

- **Widget name:** `SaturdaysWidget`
- **Widget bundle ID:** `com.kendalldale.saturdays.widget`
- **App Group:** `group.com.kendalldale.saturdays`

---

## 0. Point the toolchain at Xcode (one time)

```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
xcodebuild -version            # should print Xcode 16.x
sudo xcodebuild -license accept
```

## 1. Sync + open the project

```bash
cd "/Users/kendalldale/Desktop/Ai Building/LifeClock"
npm run sync                   # copy index.html -> www, then cap sync ios
npm run open:ios               # or: open ios/App/App.xcodeproj
```

> Capacitor 8 iOS uses Swift Package Manager (not CocoaPods), so `cap sync`
> resolves packages directly — no `pod install`.

## 2. Add the App Group to the **main app** target

1. Select the **App** target → **Signing & Capabilities**.
2. Set your **Team** (requires the Apple Developer account).
3. **+ Capability → App Groups** → add **`group.com.kendalldale.saturdays`**.
   (Must match `APP_GROUP` in `index.html` and `WidgetStore.appGroup` in
   `SaturdayCalculator.swift`.)

## 3. Create the Widget Extension target

1. **File → New → Target… → Widget Extension**.
2. Product name: **`SaturdaysWidget`**. **Uncheck** "Include Live Activity" and
   "Include Configuration App Intent" (this is a static widget). Finish, and
   **Activate** the scheme if prompted.
3. Set the widget target's **Bundle Identifier** to
   **`com.kendalldale.saturdays.widget`** (Signing & Capabilities, or General →
   Identity).
4. Xcode generates template files in a new `SaturdaysWidget/` group. **Delete
   the generated `.swift` files, Assets.xcassets, and Info.plist** (move to
   Trash), then **add the files from this repo's `ios/SaturdaysWidget/`** to the
   target instead:
   - **File → Add Files to "App"…** → select all of `ios/SaturdaysWidget/`
     (the 3 `.swift` files, `Info.plist`, `Assets.xcassets`).
   - In the add dialog, set **Target membership = SaturdaysWidget** only
     (not the App target).
   - In **Build Settings** for the widget target, point **Info.plist File** at
     `ios/SaturdaysWidget/Info.plist` if Xcode didn't pick it up.

   > Only one `@main` may exist in the target — it lives in
   > `SaturdaysWidgetBundle.swift`. If you kept any generated bundle/widget
   > struct, delete it.

## 4. Add the App Group to the **widget** target too

1. Select the **SaturdaysWidget** target → **Signing & Capabilities** → set the
   same **Team**.
2. **+ Capability → App Groups** → check the same
   **`group.com.kendalldale.saturdays`**.
   (Both targets must share the group, or the widget reads nothing.)

## 5. The data bridge (already wired, FYI)

The app already mirrors the snapshot — no extra work needed. On every `save()`
and on boot, `index.html`'s `writeWidgetData()` writes JSON to the App Group:

```json
{ "saturdaysLeft": 2080, "birthday": "1990-05-12",
  "sex": "male", "adjustmentYears": 4, "asOf": "…" }
```

Because `@capacitor/preferences` is configured into the App Group suite and
prefixes keys with `CapacitorStorage.`, the widget reads it at
`UserDefaults(suiteName: "group.com.kendalldale.saturdays")
.string(forKey: "CapacitorStorage.saturdays_widget")`.

`widget-bridge.js` is the same logic factored into a reusable, documented
`syncWidgetData()` — use it as the reference for the contract, or if/when
index.html is modularized.

## 6. Build + run

1. Run the **App** scheme on a simulator/device and complete onboarding (this
   writes the first snapshot into the App Group).
2. Long-press the home screen → **+** → search **Saturdays** → add the **small**
   or **medium** widget.
   - **Small:** the big number + "Saturdays left".
   - **Medium:** the number + a "life lived" progress bar + next-Saturday
     countdown.
3. It refreshes ~twice daily and whenever you reopen the app.

---

## Keeping the math in sync

`SaturdayCalculator.swift` is a faithful 1:1 port of `index.html`
(`compute()` / `remainingYears()` / `expectedDeathAge()` / `firstSaturday()` /
`saturdaysBetween()`, and the `LE_TABLE`). **If you change the JS
life-expectancy table or the calculation, mirror it in the Swift** or the
widget will drift from the app.

## Troubleshooting

- **Widget shows "—":** no snapshot in the App Group. Open the app and finish
  onboarding; confirm both targets share `group.com.kendalldale.saturdays`.
- **Count looks wrong:** verify the LE table / `firstSaturday` / `*365.25`
  rounding in Swift still match `index.html`.
- **Build error about multiple `@main`:** delete the Xcode-generated bundle
  struct; only `SaturdaysWidgetBundle.swift` declares `@main`.

## Then: device test + TestFlight

- Set Universal device family (iPhone + iPad) on the App target.
- **Product → Archive** → distribute to **TestFlight**
  (requires the Apple Developer account, $99/yr).

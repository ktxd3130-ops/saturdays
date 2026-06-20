# Phase 1B — Wire up the Saturdays widget (Xcode)

Do this once full Xcode is installed. The Swift is already written (`SaturdaysWidget.swift`); these steps add it as a target and connect the shared data.

## 0. Point the toolchain at Xcode (one time)
```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
xcodebuild -version          # should print Xcode 16.x
sudo xcodebuild -license accept
```

## 1. Sync + open the project
```bash
cd "/Users/kendalldale/Desktop/Ai Building/LifeClock"
npm run sync                 # copy index.html -> www, then cap sync ios
npm run open:ios             # or: open ios/App/App.xcodeproj
```
> Capacitor 8 iOS uses Swift Package Manager (not CocoaPods), so `cap sync` resolves packages directly — no `pod install`.

## 2. Add the App Group to the main app target
1. Select the **App** target → **Signing & Capabilities**.
2. Set your **Team** (requires the Apple Developer account).
3. **+ Capability → App Groups**. Add **`group.com.kendalldale.saturdays`** (must match `APP_GROUP` in `index.html` and `SaturdaysWidget.swift`).

## 3. Create the Widget Extension target
1. **File → New → Target… → Widget Extension**.
2. Product name: **`SaturdaysWidget`**. Uncheck "Include Live Activity" and "Include Configuration App Intent" (this is a static widget). Finish. Activate the scheme if prompted.
3. Xcode generates a template `SaturdaysWidget/SaturdaysWidget.swift` (+ bundle/assets). **Replace** the generated `.swift` contents with `widget-src/SaturdaysWidget.swift` from this repo. Delete the generated `@main`/bundle struct if it created a separate `*Bundle.swift` (this file already declares `@main`).

## 4. Add the App Group to the WIDGET target too
1. Select the **SaturdaysWidget** target → **Signing & Capabilities** → set the same Team.
2. **+ Capability → App Groups** → check the same **`group.com.kendalldale.saturdays`**.
   (Both targets must share the group or the widget reads nothing.)

## 5. Build + run
1. Run the **App** scheme on a simulator/device, complete onboarding (this writes the snapshot into the App Group).
2. Long-press the home screen → **+** → search **Saturdays** → add the small or medium widget.
3. It should show your live Saturdays-left count. It refreshes ~twice daily and whenever you reopen the app.

## Verify the data bridge
- The app writes `CapacitorStorage.saturdays_widget` into `UserDefaults(suiteName: "group.com.kendalldale.saturdays")` as JSON `{saturdaysLeft, birthday, sex, adjustmentYears, asOf}`.
- The widget recomputes from `birthday + sex + adjustmentYears` (faithful port of `compute()`), falling back to the stored `saturdaysLeft`.

## If the count looks wrong
The Swift math mirrors `index.html`. If you change the JS life-expectancy table or `compute()`, update `SaturdaysWidget.swift` to match (LE table, `firstSaturday`, `saturdaysBetween`).

## Then: device test + TestFlight
- Set Universal device family (iPhone + iPad) on the App target.
- Archive (**Product → Archive**) → distribute to **TestFlight**. Requires the Apple Developer account ($99/yr).

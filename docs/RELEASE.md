# Releasing Saturdays

## Web (Vercel) — automatic
Pushing to `main` auto-deploys to **saturdays-vert.vercel.app** via Vercel's Git
integration. No manual step. (Project: `saturdays`, linked in `.vercel/`.)

## iOS (TestFlight / App Store) — `scripts/release-ios.sh`

> **Blocked until you enroll.** TestFlight and the App Store require a **paid
> Apple Developer Program membership ($99/yr)**. There is no API key and nothing
> to upload to until then. Enroll: https://developer.apple.com/programs/enroll/

### One-time setup (after enrolling)
1. **App record** — App Store Connect → Apps → **+** → New App. Bundle ID
   `com.kendalldale.saturdays`. Fill in name, screenshots, privacy, and the
   listing (draft in `APP_STORE_PLAN.md`).
2. **API key** — App Store Connect → Users and Access → Integrations →
   App Store Connect API → generate a key (role **App Manager**). Download
   `AuthKey_XXXX.p8` (one download only) to
   `~/.appstoreconnect/private_keys/`.
3. **Local secrets** — copy `scripts/.env.release.example` to
   `scripts/.env.release` (gitignored) and fill in the Key ID, Issuer ID, and
   `.p8` path.

### Every release
```bash
./scripts/release-ios.sh
```
This bumps the build number, syncs the web assets, archives a signed Release
build (distribution signing handled automatically via the API key), exports the
`.ipa`, and uploads to App Store Connect. The build appears in TestFlight after
Apple finishes processing (~5–30 min).

### Known gap before a polished 1.0
- The home-screen **widget does not work yet** — `@capacitor/preferences`
  doesn't support App Groups, so the widget can't read the app's data. The app
  itself is unaffected. See `memory/widget-appgroup-broken.md` and the tracked
  fix task. The widget extension target also isn't added to the Xcode project
  yet (`WIDGET_SETUP.md`), so current builds simply ship without a widget.

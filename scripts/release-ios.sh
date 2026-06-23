#!/usr/bin/env bash
#
# release-ios.sh — one-command TestFlight / App Store upload for Saturdays.
#
# Builds a signed Release archive, exports an .ipa, and uploads it to App Store
# Connect. Distribution signing is handled automatically by xcodebuild using an
# App Store Connect API key — no manual certificates or provisioning profiles.
#
# ─────────────────────────────────────────────────────────────────────────────
# ONE-TIME PREREQUISITES (all require a PAID Apple Developer Program membership):
#
#   1. Enroll in the Apple Developer Program ($99/yr):
#        https://developer.apple.com/programs/enroll/
#
#   2. Create the app record in App Store Connect (once):
#        https://appstoreconnect.apple.com  →  Apps  →  +  →  New App
#        Bundle ID: com.kendalldale.saturdays   (matches PRODUCT_BUNDLE_IDENTIFIER)
#
#   3. Create an App Store Connect API key:
#        App Store Connect → Users and Access → Integrations → App Store Connect API
#        → generate a key with role "App Manager". Download AuthKey_XXXXXXXXXX.p8
#        (you can only download it ONCE) and place it at:
#            ~/.appstoreconnect/private_keys/AuthKey_XXXXXXXXXX.p8
#
#   4. Create a local, gitignored scripts/.env.release (see .env.release.example):
#        ASC_KEY_ID=XXXXXXXXXX
#        ASC_ISSUER_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
#        ASC_KEY_PATH=/Users/you/.appstoreconnect/private_keys/AuthKey_XXXXXXXXXX.p8
#
# Then every release is just:   ./scripts/release-ios.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Load secrets (gitignored).
if [ -f scripts/.env.release ]; then
  set -a; . scripts/.env.release; set +a
fi
: "${ASC_KEY_ID:?Set ASC_KEY_ID (see scripts/.env.release.example)}"
: "${ASC_ISSUER_ID:?Set ASC_ISSUER_ID}"
: "${ASC_KEY_PATH:?Set ASC_KEY_PATH (path to your AuthKey_*.p8)}"
[ -f "$ASC_KEY_PATH" ] || { echo "API key not found at $ASC_KEY_PATH"; exit 1; }

PROJ="ios/App/App.xcodeproj"
SCHEME="App"
ARCHIVE="build/App.xcarchive"
EXPORT="build/export"
AUTH=(-allowProvisioningUpdates
      -authenticationKeyPath "$ASC_KEY_PATH"
      -authenticationKeyID "$ASC_KEY_ID"
      -authenticationKeyIssuerID "$ASC_ISSUER_ID")

echo "▸ Bumping build number…"
# App Store Connect rejects a build number it has already seen. Increment it.
( cd ios/App && agvtool next-version -all >/dev/null ) \
  || echo "  (agvtool bump skipped — bump CURRENT_PROJECT_VERSION manually if upload is rejected as a duplicate)"

echo "▸ Syncing web assets into the iOS project…"
npm run sync

echo "▸ Archiving (Release)…"
rm -rf "$ARCHIVE" "$EXPORT"
xcodebuild -project "$PROJ" -scheme "$SCHEME" -configuration Release \
  -destination 'generic/platform=iOS' -archivePath "$ARCHIVE" \
  "${AUTH[@]}" archive

echo "▸ Exporting .ipa…"
xcodebuild -exportArchive -archivePath "$ARCHIVE" -exportPath "$EXPORT" \
  -exportOptionsPlist scripts/ExportOptions.plist "${AUTH[@]}"

echo "▸ Uploading to App Store Connect…"
xcrun altool --upload-app -t ios -f "$EXPORT"/*.ipa \
  --apiKey "$ASC_KEY_ID" --apiIssuer "$ASC_ISSUER_ID"

echo "✓ Uploaded. It will appear in TestFlight after Apple finishes processing (usually 5–30 min)."

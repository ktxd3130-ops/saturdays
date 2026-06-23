/* widget-bridge.js — Saturdays → WidgetKit data bridge
 *
 * Mirrors a tiny snapshot of the user's state into the shared App Group so the
 * iOS WidgetKit extension can render the live Saturday count WITHOUT launching
 * the app. The widget (SaturdayCalculator.swift) recomputes from
 * birthday + sex + adjustmentYears, falling back to the stored saturdaysLeft.
 *
 * ── How this maps to the app ──────────────────────────────────────────────
 * index.html already inlines the equivalent of `syncWidgetData()` as
 * `writeWidgetData()`, and calls it from `save()` (i.e. after EVERY state
 * change) and on boot. This standalone module is the same logic factored out:
 * use it if/when index.html is modularized, or as the reference for the bridge
 * contract. Keep the JSON shape in sync with SaturdayCalculator.swift's
 * `WidgetStore` / `load()`.
 *
 * ── Why it works without a custom native plugin ───────────────────────────
 * @capacitor/preferences is configured (in the app's init) to use the App
 * Group suite `group.com.kendalldale.saturdays`, and Preferences prefixes
 * every key with "CapacitorStorage.". So writing key `saturdays_widget` here
 * lands at:
 *     UserDefaults(suiteName: "group.com.kendalldale.saturdays")
 *         .string(forKey: "CapacitorStorage.saturdays_widget")
 * which is exactly what the widget reads. No bespoke bridge plugin required.
 */

const APP_GROUP = 'group.com.kendalldale.saturdays'; // must match SaturdayCalculator.swift
const WIDGET_KEY = 'saturdays_widget';               // becomes CapacitorStorage.saturdays_widget

/**
 * Write the widget snapshot to the App Group.
 *
 * @param {Object}   input
 * @param {string}   input.birthday         'yyyy-MM-dd'
 * @param {string}   input.sex              'male' | 'female' | 'other'
 * @param {number}   input.saturdaysLeft    pre-computed count (fallback for the widget)
 * @param {number}   input.adjustmentYears  health-modifier year delta (can be negative)
 * @param {Object}  [deps]
 * @param {Function} deps.setPreference  async (key, value) => void — your @capacitor/preferences
 *                                        Preferences.set wrapper, App-Group-scoped.
 * @param {boolean} [deps.isNative=true] skip the write on web.
 * @returns {Promise<boolean>} true if a snapshot was written.
 */
export async function syncWidgetData(input, deps) {
  const { setPreference, isNative = true } = deps || {};
  if (!isNative) return false;                       // web has no widget
  if (!input || !input.birthday || !input.sex) return false;
  if (typeof setPreference !== 'function') {
    throw new Error('syncWidgetData: deps.setPreference is required');
  }

  const snapshot = {
    saturdaysLeft: Math.round(input.saturdaysLeft ?? 0),
    birthday: input.birthday,
    sex: input.sex,
    adjustmentYears: input.adjustmentYears ?? 0,
    asOf: new Date().toISOString(),
  };

  try {
    await setPreference(WIDGET_KEY, JSON.stringify(snapshot));
    // Best-effort immediate refresh. Standard Capacitor has no WidgetKit API,
    // so this is a no-op unless a custom reload plugin is registered. The
    // widget's own 12h timeline + reload-on-app-open keeps it fresh regardless.
    const reload = window?.Capacitor?.Plugins?.WidgetReload?.reloadAll;
    if (typeof reload === 'function') await reload({ kind: 'SaturdaysWidget' });
    return true;
  } catch (e) {
    // The widget mirror is best-effort — never let it break the UI.
    return false;
  }
}

export { APP_GROUP, WIDGET_KEY };

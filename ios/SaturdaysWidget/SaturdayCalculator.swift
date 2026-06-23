//  SaturdayCalculator.swift
//  Saturdays — WidgetKit extension
//
//  The Saturday math, ported faithfully from index.html (compute() /
//  remainingYears() / expectedDeathAge() / firstSaturday() / saturdaysBetween()).
//  The widget RE-COMPUTES from birthday + sex + adjustmentYears so the count
//  stays fresh between app opens, falling back to the stored snapshot int.
//
//  ⚠️ Keep this in sync with index.html. If the JS life-expectancy table or
//  compute() changes, mirror the change here (LE table, firstSaturday,
//  saturdaysBetween, the *365.25 death-date rounding).

import Foundation

// MARK: - Shared store (App Group)

enum WidgetStore {
    static let appGroup = "group.com.kendalldale.saturdays"
    // @capacitor/preferences prefixes every key with "CapacitorStorage."
    static let key = "CapacitorStorage.saturdays_widget"

    /// The raw snapshot the web app mirrors on every save/boot:
    /// { saturdaysLeft, birthday, sex, adjustmentYears, asOf }
    static func snapshot() -> [String: Any]? {
        guard let ud = UserDefaults(suiteName: appGroup),
              let raw = ud.string(forKey: key),
              let data = raw.data(using: .utf8),
              let obj = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
        else { return nil }
        return obj
    }
}

// MARK: - Result

/// Everything the widget views need. `pctLived` is 0–100, `daysUntilSaturday`
/// is 0 on Saturday itself (matches JS firstSaturday: today if today is Sat).
struct SaturdayCount {
    let left: Int
    let lived: Int
    let total: Int
    let pctLived: Double
    let daysUntilSaturday: Int
}

// MARK: - Math (port of index.html)

enum SaturdayCalculator {

    private static let secondsPerWeek: Double = 604_800          // MS_WEEK / 1000
    private static let secondsPerYear: Double = 365.25 * 86_400  // MS_YEAR / 1000

    /// age -> (male remaining yrs, female remaining yrs). Smoothed U.S. SSA
    /// period life tables — identical to LE_TABLE in index.html.
    private static let lifeExpectancy: [Int: (male: Double, female: Double)] = [
        0:  (76.3, 81.4), 10: (66.7, 71.7), 20: (57.2, 61.9), 30: (48.1, 52.3),
        40: (38.9, 42.8), 50: (30.0, 33.6), 60: (21.9, 25.0), 70: (14.6, 17.0),
        80: (8.3, 9.8),   90: (4.0, 4.6),  100: (2.0, 2.3),  110: (1.2, 1.3),
    ]

    /// Remaining years given current age + sex (linear interp between decades).
    static func remainingYears(age: Double, sex: String) -> Double {
        let idx: Int? = sex == "female" ? 1 : (sex == "male" ? 0 : nil)
        let lo = min(Int((age / 10).rounded(.down)) * 10, 110)
        let hi = min(lo + 10, 110)
        let f  = hi == lo ? 0 : (age - Double(lo)) / Double(hi - lo)
        func get(_ a: Int) -> Double {
            let r = lifeExpectancy[a] ?? lifeExpectancy[110]!
            guard let i = idx else { return (r.male + r.female) / 2 }
            return i == 0 ? r.male : r.female
        }
        return get(lo) * (1 - f) + get(hi) * f
    }

    static func expectedDeathAge(age: Double, sex: String) -> Double {
        age + remainingYears(age: age, sex: sex)
    }

    // MARK: Date helpers

    /// Parse a "yyyy-MM-dd" birthday at local midnight (matches `new Date(s+'T00:00:00')`).
    static func parseDate(_ s: String) -> Date? {
        let df = DateFormatter()
        df.calendar = Calendar(identifier: .gregorian)
        df.locale = Locale(identifier: "en_US_POSIX")
        df.timeZone = .current
        df.dateFormat = "yyyy-MM-dd"
        return df.date(from: s)
    }

    /// Fractional age in years (port of ageFrom()).
    static func ageFrom(_ birth: Date, at: Date = Date()) -> Double {
        let cal = Calendar.current
        let years = cal.dateComponents([.year], from: birth, to: at).year ?? 0
        let lastBday = cal.date(byAdding: .year, value: years, to: birth) ?? birth
        return Double(years) + at.timeIntervalSince(lastBday) / secondsPerYear
    }

    /// The coming Saturday (today if today is Saturday) at local midnight.
    static func firstSaturday(_ d: Date) -> Date {
        let cal = Calendar.current
        let start = cal.startOfDay(for: d)
        let wd = cal.component(.weekday, from: start) - 1   // 0=Sun … 6=Sat
        let add = ((6 - wd) + 7) % 7
        return cal.date(byAdding: .day, value: add, to: start) ?? start
    }

    static func saturdaysBetween(_ d1: Date, _ d2: Date) -> Int {
        max(0, Int((d2.timeIntervalSince(d1) / secondsPerWeek).rounded()))
    }

    // MARK: Compute

    /// Full count from the raw inputs. Returns nil if the birthday won't parse.
    static func compute(birthday: String, sex: String, adjustmentYears: Double,
                        now: Date = Date()) -> SaturdayCount? {
        guard let birth = parseDate(birthday) else { return nil }
        let cal = Calendar.current

        let age = ageFrom(birth, at: now)
        let deathAge = expectedDeathAge(age: age, sex: sex) + adjustmentYears
        let death = cal.date(byAdding: .day,
                             value: Int((deathAge * 365.25).rounded()),
                             to: birth) ?? birth

        let total = saturdaysBetween(firstSaturday(birth), firstSaturday(death))
        let lived = min(total, saturdaysBetween(firstSaturday(birth), firstSaturday(now)))
        let left  = max(0, total - lived)
        let pct   = total > 0 ? min(100, Double(lived) / Double(total) * 100) : 0

        // Days until the coming Saturday (0 if today is Saturday).
        let days = cal.dateComponents([.day],
                                      from: cal.startOfDay(for: now),
                                      to: firstSaturday(now)).day ?? 0

        return SaturdayCount(left: left, lived: lived, total: total,
                             pctLived: pct, daysUntilSaturday: max(0, days))
    }

    /// Read the App Group snapshot and recompute fresh. Falls back to the stored
    /// `saturdaysLeft` int if recompute fails (e.g. missing birthday).
    static func load(now: Date = Date()) -> SaturdayCount? {
        guard let obj = WidgetStore.snapshot() else { return nil }

        let birthday = obj["birthday"] as? String ?? ""
        let sex = obj["sex"] as? String ?? "other"
        let adj = (obj["adjustmentYears"] as? NSNumber)?.doubleValue ?? 0

        if let fresh = compute(birthday: birthday, sex: sex,
                               adjustmentYears: adj, now: now) {
            return fresh
        }
        // Degraded fallback: just the stored number, no progress/countdown.
        if let stored = (obj["saturdaysLeft"] as? NSNumber)?.intValue {
            return SaturdayCount(left: stored, lived: 0, total: 0,
                                 pctLived: 0, daysUntilSaturday: 0)
        }
        return nil
    }
}

//  SaturdaysWidget.swift
//  WidgetKit extension for "Saturdays: Memento Mori".
//
//  Reads the snapshot the web app mirrors into the shared App Group on every
//  save/boot (see writeWidgetData() in index.html), then RE-COMPUTES the
//  Saturdays-left count itself so the widget stays fresh between app opens.
//  The math is a faithful port of compute()/remainingYears()/firstSaturday()
//  in index.html — keep the two in sync if the JS changes.
//
//  Setup: see widget-src/SETUP.md. This file replaces the template the Xcode
//  "Widget Extension" target generates.

import WidgetKit
import SwiftUI

// MARK: - Shared store

private let APP_GROUP  = "group.com.kendalldale.saturdays"
// Capacitor Preferences prefixes keys with "CapacitorStorage."
private let WIDGET_KEY = "CapacitorStorage.saturdays_widget"

private let SECONDS_WEEK: Double = 604_800
private let SECONDS_YEAR: Double = 365.25 * 86_400

// age -> (male remaining yrs, female remaining yrs), smoothed SSA period tables
private let LE: [Int: (Double, Double)] = [
    0: (76.3, 81.4), 10: (66.7, 71.7), 20: (57.2, 61.9), 30: (48.1, 52.3),
    40: (38.9, 42.8), 50: (30.0, 33.6), 60: (21.9, 25.0), 70: (14.6, 17.0),
    80: (8.3, 9.8), 90: (4.0, 4.6), 100: (2.0, 2.3), 110: (1.2, 1.3)
]

// MARK: - Saturday math (port of index.html)

enum Sat {
    static func remainingYears(_ age: Double, _ sex: String) -> Double {
        let idx: Int? = sex == "female" ? 1 : (sex == "male" ? 0 : nil)
        let lo = min(Int((age / 10).rounded(.down)) * 10, 110)
        let hi = min(lo + 10, 110)
        let f  = hi == lo ? 0 : (age - Double(lo)) / Double(hi - lo)
        func get(_ a: Int) -> Double {
            let r = LE[a] ?? LE[110]!
            if let i = idx { return i == 0 ? r.0 : r.1 }
            return (r.0 + r.1) / 2
        }
        return get(lo) * (1 - f) + get(hi) * f
    }

    static func parseDate(_ s: String) -> Date? {
        let df = DateFormatter()
        df.calendar = Calendar(identifier: .gregorian)
        df.locale = Locale(identifier: "en_US_POSIX")
        df.timeZone = .current
        df.dateFormat = "yyyy-MM-dd"
        return df.date(from: s)
    }

    static func ageFrom(_ bday: Date, at: Date = Date()) -> Double {
        let cal = Calendar.current
        let years = cal.dateComponents([.year], from: bday, to: at).year ?? 0
        let lastBday = cal.date(byAdding: .year, value: years, to: bday) ?? bday
        return Double(years) + at.timeIntervalSince(lastBday) / SECONDS_YEAR
    }

    /// JS firstSaturday: the coming Saturday (today if today is Saturday).
    static func firstSaturday(_ d: Date) -> Date {
        let cal = Calendar.current
        let start = cal.startOfDay(for: d)
        let wd = cal.component(.weekday, from: start) - 1   // 0=Sun … 6=Sat
        let add = ((6 - wd) + 7) % 7
        return cal.date(byAdding: .day, value: add, to: start) ?? start
    }

    static func saturdaysBetween(_ d1: Date, _ d2: Date) -> Int {
        max(0, Int((d2.timeIntervalSince(d1) / SECONDS_WEEK).rounded()))
    }

    static func compute(birthday: String, sex: String, adjustmentYears: Double) -> Int? {
        guard let birth = parseDate(birthday) else { return nil }
        let age = ageFrom(birth)
        let expDeathAge = age + remainingYears(age, sex) + adjustmentYears
        let cal = Calendar.current
        let death = cal.date(byAdding: .day,
                             value: Int((expDeathAge * 365.25).rounded()),
                             to: birth) ?? birth
        let total = saturdaysBetween(firstSaturday(birth), firstSaturday(death))
        let lived = min(total, saturdaysBetween(firstSaturday(birth), firstSaturday(Date())))
        return max(0, total - lived)
    }

    /// Read the App Group snapshot; recompute fresh, falling back to the stored int.
    static func load() -> Int? {
        guard let ud = UserDefaults(suiteName: APP_GROUP),
              let raw = ud.string(forKey: WIDGET_KEY),
              let data = raw.data(using: .utf8),
              let obj = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
        else { return nil }

        let birthday = obj["birthday"] as? String ?? ""
        let sex = obj["sex"] as? String ?? "other"
        let adj = (obj["adjustmentYears"] as? NSNumber)?.doubleValue ?? 0
        if let fresh = compute(birthday: birthday, sex: sex, adjustmentYears: adj) {
            return fresh
        }
        return (obj["saturdaysLeft"] as? NSNumber)?.intValue
    }
}

// MARK: - Timeline

struct SatEntry: TimelineEntry {
    let date: Date
    let left: Int?
}

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> SatEntry {
        SatEntry(date: Date(), left: 2_000)
    }
    func getSnapshot(in context: Context, completion: @escaping (SatEntry) -> Void) {
        completion(SatEntry(date: Date(), left: Sat.load()))
    }
    func getTimeline(in context: Context, completion: @escaping (Timeline<SatEntry>) -> Void) {
        let entry = SatEntry(date: Date(), left: Sat.load())
        // Refresh ~twice a day; the count only changes weekly so this is plenty.
        let next = Calendar.current.date(byAdding: .hour, value: 12, to: Date())
                   ?? Date().addingTimeInterval(SECONDS_WEEK / 14)
        completion(Timeline(entries: [entry], policy: .after(next)))
    }
}

// MARK: - Theme + view

private extension Color {
    static let satBg     = Color(red: 0x0a / 255, green: 0x0a / 255, blue: 0x0b / 255)
    static let satInk    = Color(red: 0xf4 / 255, green: 0xf1 / 255, blue: 0xea / 255)
    static let satAccent = Color(red: 0xf0 / 255, green: 0xa0 / 255, blue: 0x4b / 255)
    static let satDim    = Color(red: 0x9a / 255, green: 0x95 / 255, blue: 0x8c / 255)
}

private func grouped(_ n: Int) -> String {
    let f = NumberFormatter(); f.numberStyle = .decimal
    return f.string(from: NSNumber(value: n)) ?? "\(n)"
}

struct SaturdaysWidgetEntryView: View {
    var entry: Provider.Entry
    @Environment(\.widgetFamily) var family

    var body: some View {
        VStack(spacing: family == .systemSmall ? 2 : 6) {
            Text(entry.left.map(grouped) ?? "—")
                .font(.system(size: family == .systemSmall ? 40 : 64,
                              weight: .bold, design: .rounded))
                .foregroundColor(.satInk)
                .minimumScaleFactor(0.5)
                .lineLimit(1)
            Text("Saturdays left")
                .font(.system(size: family == .systemSmall ? 12 : 15, weight: .semibold))
                .foregroundColor(.satAccent)
            if family != .systemSmall {
                Text("What are you doing with yours?")
                    .font(.system(size: 12))
                    .foregroundColor(.satDim)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - Widget

@main
struct SaturdaysWidget: Widget {
    let kind = "SaturdaysWidget"
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: Provider()) { entry in
            SaturdaysWidgetEntryView(entry: entry)
                .containerBackground(Color.satBg, for: .widget)
        }
        .configurationDisplayName("Saturdays")
        .description("How many Saturdays you have left.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

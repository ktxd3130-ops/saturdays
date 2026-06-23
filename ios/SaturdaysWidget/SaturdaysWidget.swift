//  SaturdaysWidget.swift
//  Saturdays — WidgetKit extension
//
//  Home-screen widget showing how many Saturdays you have left.
//   • systemSmall  — the big number + "Saturdays left"
//   • systemMedium — the number + a life-lived progress bar + next-Saturday countdown
//
//  The count is re-computed from the App Group snapshot on every timeline
//  refresh (see SaturdayCalculator). Theme matches the app: near-black bg,
//  amber accent, warm off-white ink.

import WidgetKit
import SwiftUI

// MARK: - Theme

private extension Color {
    static let satBg     = Color(red: 0x0a / 255, green: 0x0a / 255, blue: 0x0b / 255) // #0a0a0b
    static let satInk    = Color(red: 0xf4 / 255, green: 0xf1 / 255, blue: 0xea / 255) // warm white
    static let satAccent = Color(red: 0xf0 / 255, green: 0xa0 / 255, blue: 0x4b / 255) // #f0a04b amber
    static let satDim    = Color(red: 0x9a / 255, green: 0x95 / 255, blue: 0x8c / 255) // muted
    static let satTrack  = Color(red: 0x2a / 255, green: 0x27 / 255, blue: 0x22 / 255) // bar track
}

private func grouped(_ n: Int) -> String {
    let f = NumberFormatter(); f.numberStyle = .decimal
    return f.string(from: NSNumber(value: n)) ?? "\(n)"
}

// MARK: - Timeline

struct SatEntry: TimelineEntry {
    let date: Date
    let count: SaturdayCount?
}

struct Provider: TimelineProvider {
    private static let placeholder = SaturdayCount(
        left: 2_080, lived: 1_600, total: 3_680, pctLived: 43, daysUntilSaturday: 3
    )

    func placeholder(in context: Context) -> SatEntry {
        SatEntry(date: Date(), count: Self.placeholder)
    }

    func getSnapshot(in context: Context, completion: @escaping (SatEntry) -> Void) {
        let count = SaturdayCalculator.load() ?? Self.placeholder
        completion(SatEntry(date: Date(), count: count))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<SatEntry>) -> Void) {
        let now = Date()
        let entry = SatEntry(date: now, count: SaturdayCalculator.load(now: now))
        // The count only changes weekly, but refresh ~twice a day so the
        // next-Saturday countdown ticks down and the count rolls over promptly.
        let next = Calendar.current.date(byAdding: .hour, value: 12, to: now)
                   ?? now.addingTimeInterval(12 * 3_600)
        completion(Timeline(entries: [entry], policy: .after(next)))
    }
}

// MARK: - Views

/// The hero number + label, sized for the family. Used by both layouts.
private struct BigNumber: View {
    let count: SaturdayCount?
    let numberSize: CGFloat
    let labelSize: CGFloat
    var alignment: HorizontalAlignment = .center

    var body: some View {
        VStack(alignment: alignment, spacing: 2) {
            Text(count.map { grouped($0.left) } ?? "—")
                .font(.system(size: numberSize, weight: .bold, design: .rounded))
                .foregroundColor(.satInk)
                .minimumScaleFactor(0.5)
                .lineLimit(1)
            Text("Saturdays left")
                .font(.system(size: labelSize, weight: .semibold))
                .foregroundColor(.satAccent)
        }
    }
}

private struct SmallView: View {
    let count: SaturdayCount?
    var body: some View {
        BigNumber(count: count, numberSize: 44, labelSize: 13)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

private struct MediumView: View {
    let count: SaturdayCount?

    private var countdownLabel: String {
        guard let d = count?.daysUntilSaturday else { return "" }
        switch d {
        case 0:  return "Today is Saturday"
        case 1:  return "Next Saturday: tomorrow"
        default: return "Next Saturday: \(d) days"
        }
    }

    var body: some View {
        HStack(alignment: .center, spacing: 18) {
            BigNumber(count: count, numberSize: 60, labelSize: 14, alignment: .leading)

            VStack(alignment: .leading, spacing: 8) {
                if let c = count, c.total > 0 {
                    // % of life lived
                    HStack {
                        Text("Life lived")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.satDim)
                        Spacer()
                        Text("\(Int(c.pctLived.rounded()))%")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(.satInk)
                    }
                    ProgressBar(fraction: c.pctLived / 100)
                        .frame(height: 6)
                }
                Text(countdownLabel)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.satDim)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

/// A thin rounded progress bar, amber fill on a dim track.
private struct ProgressBar: View {
    let fraction: Double  // 0…1
    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                Capsule().fill(Color.satTrack)
                Capsule()
                    .fill(Color.satAccent)
                    .frame(width: max(4, geo.size.width * CGFloat(min(1, max(0, fraction)))))
            }
        }
    }
}

struct SaturdaysWidgetEntryView: View {
    var entry: Provider.Entry
    @Environment(\.widgetFamily) var family

    var body: some View {
        switch family {
        case .systemMedium: MediumView(count: entry.count)
        default:            SmallView(count: entry.count)
        }
    }
}

// MARK: - Widget

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

// MARK: - Preview

#Preview(as: .systemSmall) {
    SaturdaysWidget()
} timeline: {
    SatEntry(date: .now, count: SaturdayCount(left: 2_080, lived: 1_600,
              total: 3_680, pctLived: 43, daysUntilSaturday: 3))
}

#Preview(as: .systemMedium) {
    SaturdaysWidget()
} timeline: {
    SatEntry(date: .now, count: SaturdayCount(left: 2_080, lived: 1_600,
              total: 3_680, pctLived: 43, daysUntilSaturday: 3))
}

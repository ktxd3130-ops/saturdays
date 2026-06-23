//  SaturdaysWidgetBundle.swift
//  Saturdays — WidgetKit extension entry point.
//
//  The @main bundle. Add more widgets here later (e.g. an accessory/lock-screen
//  variant) by listing them inside the bundle body.

import WidgetKit
import SwiftUI

@main
struct SaturdaysWidgetBundle: WidgetBundle {
    var body: some Widget {
        SaturdaysWidget()
    }
}

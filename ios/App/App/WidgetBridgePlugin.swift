//  WidgetBridgePlugin.swift
//  Saturdays
//
//  Writes the widget snapshot DIRECTLY into the shared App Group suite.
//
//  Why this exists: @capacitor/preferences does NOT support iOS App Groups.
//  Its Preferences class always uses `UserDefaults.standard` and treats the
//  `group` option as a key *prefix* only — so the JS widget mirror landed in
//  the app's PRIVATE sandbox, which a widget extension (a separate sandbox)
//  can never read. This tiny local Capacitor plugin does the real App Group
//  write that Preferences can't, and kicks the widget timelines so the
//  home-screen count updates promptly.
//
//  JS side (index.html → writeWidgetData):
//      Capacitor.Plugins.WidgetBridge.write({ json, group, key })
//  Widget side (SaturdayCalculator.WidgetStore):
//      UserDefaults(suiteName: group)?.string(forKey: key)
//
//  The plugin auto-registers: Capacitor scans the Obj-C runtime for CAPPlugin
//  subclasses conforming to CAPBridgedPlugin, so just having this file in the
//  App target is enough — no manual registration needed.

import Foundation
import Capacitor
import WidgetKit

@objc(WidgetBridgePlugin)
public class WidgetBridgePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "WidgetBridgePlugin"
    public let jsName = "WidgetBridge"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "write", returnType: CAPPluginReturnPromise)
    ]

    private static let defaultGroup = "group.com.kendalldale.saturdays"
    private static let defaultKey = "saturdays_widget"

    /// Write the snapshot JSON into the shared App Group suite.
    /// Params: { json: String (required), group?: String, key?: String }
    @objc func write(_ call: CAPPluginCall) {
        guard let json = call.getString("json") else {
            call.reject("WidgetBridge.write: missing required 'json' string")
            return
        }
        let group = call.getString("group") ?? Self.defaultGroup
        let key = call.getString("key") ?? Self.defaultKey

        guard let defaults = UserDefaults(suiteName: group) else {
            call.reject("WidgetBridge.write: App Group '\(group)' is unavailable — check the App Groups entitlement on the app target")
            return
        }

        defaults.set(json, forKey: key)

        if #available(iOS 14.0, *) {
            WidgetCenter.shared.reloadAllTimelines()
        }
        call.resolve()
    }
}

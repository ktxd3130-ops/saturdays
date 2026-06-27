#!/usr/bin/env ruby
# One-shot: wire the SaturdaysWidget extension target + App Group entitlements
# + the WidgetBridge plugin source into App.xcodeproj. Idempotent: re-running
# detects existing objects and skips them.
require 'xcodeproj'

PROJECT = File.expand_path('App/App.xcodeproj', __dir__)
TEAM    = '9T25DV5M37'

project = Xcodeproj::Project.open(PROJECT)
app_target = project.targets.find { |t| t.name == 'App' }
raise 'App target not found' unless app_target

app_group = project.main_group['App'] # PBXGroup for App/

# ---------------------------------------------------------------------------
# 1. WidgetBridge plugin source -> App target
# ---------------------------------------------------------------------------
unless app_target.source_build_phase.files_references.any? { |r| r.path == 'WidgetBridgePlugin.swift' }
  ref = app_group.new_reference('WidgetBridgePlugin.swift')
  ref.last_known_file_type = 'sourcecode.swift'
  app_target.add_file_references([ref])
  puts 'added WidgetBridgePlugin.swift to App target'
end

# ---------------------------------------------------------------------------
# 2. App.entitlements -> App target (file ref + build setting)
# ---------------------------------------------------------------------------
unless app_group.files.any? { |r| r.path == 'App.entitlements' }
  app_group.new_reference('App.entitlements')
  puts 'added App.entitlements file reference'
end
app_target.build_configurations.each do |c|
  c.build_settings['CODE_SIGN_ENTITLEMENTS'] = 'App/App.entitlements'
end

# ---------------------------------------------------------------------------
# 3. Group for the widget source (lives at ios/SaturdaysWidget = ../SaturdaysWidget)
# ---------------------------------------------------------------------------
widget_group = project.main_group['SaturdaysWidget'] ||
               project.main_group.new_group('SaturdaysWidget', '../SaturdaysWidget')

def file_ref(group, name)
  group.files.find { |f| f.path == name } || group.new_reference(name)
end

swift_files = %w[SaturdaysWidget.swift SaturdaysWidgetBundle.swift SaturdayCalculator.swift]
assets_ref  = file_ref(widget_group, 'Assets.xcassets')
plist_ref   = file_ref(widget_group, 'Info.plist')
entitle_ref = file_ref(widget_group, 'SaturdaysWidget.entitlements')
swift_refs  = swift_files.map { |n| file_ref(widget_group, n) }

# ---------------------------------------------------------------------------
# 4. The widget extension target
# ---------------------------------------------------------------------------
widget = project.targets.find { |t| t.name == 'SaturdaysWidget' }
if widget.nil?
  widget = project.new_target(:app_extension, 'SaturdaysWidget', :ios, '17.0')
  puts 'created SaturdaysWidget app-extension target'

  widget.add_file_references(swift_refs)
  widget.add_resources([assets_ref])

  widget.build_configurations.each do |c|
    bs = c.build_settings
    bs['ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME'] = 'AccentColor'
    bs['ASSETCATALOG_COMPILER_WIDGET_BACKGROUND_COLOR_NAME'] = 'WidgetBackground'
    bs['CODE_SIGN_ENTITLEMENTS'] = '../SaturdaysWidget/SaturdaysWidget.entitlements'
    bs['CODE_SIGN_STYLE'] = 'Automatic'
    bs['CURRENT_PROJECT_VERSION'] = '1'
    bs['MARKETING_VERSION'] = '1.0'
    bs['DEVELOPMENT_TEAM'] = TEAM
    bs['GENERATE_INFOPLIST_FILE'] = 'NO'
    bs['INFOPLIST_FILE'] = '../SaturdaysWidget/Info.plist'
    bs['INFOPLIST_KEY_CFBundleDisplayName'] = 'Saturdays'
    bs['INFOPLIST_KEY_NSHumanReadableCopyright'] = ''
    bs['IPHONEOS_DEPLOYMENT_TARGET'] = '17.0'
    bs['LD_RUNPATH_SEARCH_PATHS'] = ['$(inherited)', '@executable_path/Frameworks', '@executable_path/../../Frameworks']
    bs['PRODUCT_BUNDLE_IDENTIFIER'] = 'com.kendalldale.saturdays.widget'
    bs['PRODUCT_NAME'] = '$(TARGET_NAME)'
    bs['SKIP_INSTALL'] = 'YES'
    bs['SWIFT_VERSION'] = '5.0'
    bs['TARGETED_DEVICE_FAMILY'] = '1,2'
    bs['SWIFT_EMIT_LOC_STRINGS'] = 'YES'
    bs['ENABLE_PREVIEWS'] = 'YES'
  end
else
  puts 'SaturdaysWidget target already exists — skipping creation'
end

# ---------------------------------------------------------------------------
# 5. Embed the appex into the app + target dependency
# ---------------------------------------------------------------------------
unless app_target.dependencies.any? { |d| d.target == widget }
  app_target.add_dependency(widget)
  puts 'added App -> SaturdaysWidget dependency'
end

embed_phase = app_target.copy_files_build_phases.find { |p| p.name == 'Embed App Extensions' }
if embed_phase.nil?
  embed_phase = app_target.new_copy_files_build_phase('Embed App Extensions')
  embed_phase.symbol_dst_subfolder_spec = :plug_ins # PlugIns (13)
  puts 'created Embed App Extensions phase'
end
unless embed_phase.files_references.include?(widget.product_reference)
  bf = embed_phase.add_file_reference(widget.product_reference)
  bf.settings = { 'ATTRIBUTES' => ['RemoveHeadersOnCopy'] }
  puts 'embedded SaturdaysWidget.appex'
end

project.save
puts 'saved project OK'

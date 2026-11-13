"""Execute the addon in Lua 5.1 with a strict, minimal WoW API contract double."""
from pathlib import Path
import sys
import unittest
import zipfile
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".test-tools" / "python"))
from lupa.lua51 import LuaRuntime

SOURCE = (ROOT / "ForeverIcyVeins" / "ForeverIcyVeins.lua").read_text(encoding="utf-8")
HARNESS = r'''
frames, timers, messages, bindings = {}, {}, {}, {}
now = 100
combat, playerClass, nativeAvailable, locale = false, "MAGE", true, "deDE"
SlashCmdList = {}
UISpecialFrames = {}
function print(message) table.insert(messages, message) end
function UnitClass() return "Mage", playerClass end
function GetLocale() return locale end
function InCombatLockdown() return combat end
function GetTime() return now end
function UnitAura() error("Legacy aura queries must not be used") end
function UnitBuff() error("Legacy buff queries must not be used") end
function CombatLogGetCurrentEventInfo() error("Combat log must not be used") end
C_Timer = { After = function(seconds, callback)
    table.insert(timers, { seconds = seconds, callback = callback })
end }

C_StringUtil = { CreateNumericRuleFormatter = function()
    return {
        rules = {},
        AddBreakpoint = function(self, rule) table.insert(self.rules, rule) end,
        FormatNumber = function(self, remaining)
            local selected, threshold = "", -math.huge
            for _, rule in ipairs(self.rules) do
                if remaining >= rule.threshold and rule.threshold >= threshold then
                    selected, threshold = rule.format, rule.threshold
                end
            end
            return selected
        end,
    }
end }
local bindingMethods = {}
function bindingMethods:SetFormatter(formatter) self.formatter = formatter end
function bindingMethods:SetExpiredText(text) self.expired = text end
function bindingMethods:SetZeroDurationText(text) self.zero = text end
function bindingMethods:SetUpdateInterval(interval) self.interval = interval end
function bindingMethods:SetFontString(font) self.font = font end
function bindingMethods:SetDuration(duration) self.duration = duration end
function bindingMethods:Enable() self.enabled = true end
function bindingMethods:Disable() self.enabled = false end
function bindingMethods:Copy()
    local copy = setmetatable({}, { __index = bindingMethods })
    for key, value in pairs(self) do copy[key] = value end
    table.insert(bindings, copy)
    return copy
end
C_DurationUtil = {
    CreateDurationTextBinding = function()
        local binding = setmetatable({}, { __index = bindingMethods })
        table.insert(bindings, binding)
        return binding
    end,
    CreateDuration = function()
        return { SetTimeFromStart = function(self, start, duration)
            self.start, self.duration = start, duration
        end }
    end,
}

local methods = {}
local function write(self, key, ...)
    assert(not self.restricted, "Addon accessed a restricted AuraButton")
    self[key] = {...}
end
function methods:SetSize(...) write(self, "size", ...) end
function methods:SetPoint(...) write(self, "point", ...) end
function methods:SetAllPoints(...) write(self, "allPoints", ...) end
function methods:ClearAllPoints() write(self, "point") end
function methods:SetScale(...) write(self, "scale", ...) end
function methods:SetAlpha(...) write(self, "alpha", ...) end
function methods:SetFrameStrata(...) write(self, "strata", ...) end
function methods:EnableMouse(...) write(self, "mouse", ...) end
function methods:SetTexture(...) write(self, "texture", ...) end
function methods:SetTexCoord(...) write(self, "texcoord", ...) end
function methods:SetBlendMode(...) write(self, "blend", ...) end
function methods:SetHeight(...) write(self, "height", ...) end
function methods:SetColorTexture(...) write(self, "color", ...) end
function methods:SetOrientation(...) write(self, "orientation", ...) end
function methods:SetThumbTexture(texture)
    self.thumb = setmetatable({ texture = texture }, { __index = methods })
end
function methods:GetThumbTexture() return self.thumb end
function methods:SetWordWrap(...) write(self, "wordWrap", ...) end
function methods:SetJustifyH(...) write(self, "justifyH", ...) end
function methods:SetJustifyV(...) write(self, "justifyV", ...) end
function methods:SetText(...) write(self, "textValue", ...) end
function methods:SetClampedToScreen(...) write(self, "clamped", ...) end
function methods:SetMovable(...) write(self, "movable", ...) end
function methods:RegisterForDrag(...) write(self, "dragButtons", ...) end
function methods:StartMoving() self.moving = true end
function methods:StopMovingOrSizing() self.moving = false end
function methods:SetChecked(value) self.checked = value end
function methods:GetChecked() return self.checked end
function methods:SetMinMaxValues(minimum, maximum) self.minimum, self.maximum = minimum, maximum end
function methods:SetValueStep(step) self.step = step end
function methods:SetObeyStepOnDrag(value) self.obeyStep = value end
function methods:SetValue(value)
    self.value = math.min(self.maximum, math.max(self.minimum, value))
    if self.scripts and self.scripts.OnValueChanged then self.scripts.OnValueChanged(self, self.value) end
end
function methods:Click()
    if self.kind == "CheckButton" then self.checked = not self.checked end
    self.scripts.OnClick(self)
end
function methods:Show()
    write(self, "shown", true)
    if self.scripts and self.scripts.OnShow then self.scripts.OnShow(self) end
end
function methods:Hide() write(self, "shown", false) end
function methods:CreateTexture(_, layer)
    assert(not self.restricted, "Creating a texture after native initialization")
    local texture = setmetatable({ layer = layer }, { __index = methods })
    table.insert(self.textures, texture)
    return texture
end
function methods:CreateFontString(_, layer, template)
    assert(not self.restricted)
    assert(template == "GameFontNormal" or template == "GameFontHighlightSmall")
    local font = setmetatable({ parent = self, layer = layer }, { __index = methods })
    table.insert(self.fontStrings, font)
    return font
end
function methods:SetApplicationBar(bar, options)
    assert(not self.restricted and bar.kind == "StatusBar" and bar.parent == self)
    self.applicationBar, self.applicationOptions = bar, options
end
function methods:SetDurationText(font, options)
    assert((not self.restricted or not combat) and font.parent.parent == self)
    self.durationBinding = options.binding:Copy()
    self.durationBinding:SetFontString(font)
end
function methods:RegisterEvent(event) self.events[event] = true end
function methods:UnregisterEvent(event) self.events[event] = nil end
function methods:SetScript(kind, callback)
    assert(kind == "OnEvent" or kind == "OnShow" or kind == "OnClick" or kind == "OnValueChanged"
        or kind == "OnDragStart" or kind == "OnDragStop", "Unexpected addon script: " .. kind)
    self.scripts = self.scripts or {}
    self.scripts[kind] = callback
    if kind == "OnEvent" then self.callback = callback end
end
function methods:SetUnit(unit)
    assert(unit == "player", "Must only track the player")
    self.unit = unit
end
local function validateFilters(filters)
    assert(type(filters.includeSpellIDs) == "table")
    for id, included in pairs(filters.includeSpellIDs) do
        assert(type(id) == "number" and id > 0 and id == math.floor(id))
        assert(included == true, "API requires an ID-keyed map, not an array")
    end
end
function methods:AddAuraSlot(key, filter, options)
    assert(self.kind == "AuraContainer")
    assert(filter == "HELPFUL", "Only helpful buffs are permitted")
    self.slots = self.slots or {}
    assert(not self.slots[key], "Slot keys must be unique")
    validateFilters(options.candidateFilters)
    local button = CreateFrame("AuraButton", nil, self, "CustomAuraButtonTemplate")
    options.initializeFrame(button)
    assert(button.mouse[1] == false, "Must allow clicks through")
    assert(button.applicationBar and button.durationBinding, "Native charge and duration bindings are required")
    button.restricted = true
    button.applicationBar.restricted = true
    button.durationBinding.font.restricted = true
    self.slots[key] = { button = button, filters = options.candidateFilters }
    self.slot, self.filters, self.button = key, options.candidateFilters, button
    nativeContainer = self
    return button
end
function methods:SetAuraSlotCandidateFilters(key, filters)
    assert(not combat, "Changing filters during combat")
    assert(self.slots[key])
    validateFilters(filters)
    self.filters = filters
    self.slots[key].filters = filters
end
function CreateFrame(kind, name, parent, template)
    if kind == "AuraContainer" then
        assert(nativeAvailable, "Native aura API missing")
        assert(template == "CustomAuraContainerTemplate")
    end
    local frame = setmetatable({
        kind = kind, name = name, parent = parent, template = template,
        textures = {}, fontStrings = {}, events = {}, shown = {true},
    }, { __index = methods })
    table.insert(frames, frame)
    if template == "BasicFrameTemplateWithInset" then
        frame.TitleText = setmetatable({}, { __index = methods })
    end
    if name then _G[name] = frame end
    return frame
end
UIParent = CreateFrame("Frame", "UIParent")
function Fire(event, ...)
    for _, frame in ipairs(frames) do
        if frame.events[event] and frame.callback then
            frame.callback(frame, event, ...)
        end
    end
end
function RunTimer(index) timers[index].callback() end
function Command(message) SlashCmdList.FOREVERICYVEINS(message) end
function NativeAura(applications, remaining)
    for _, slot in pairs(nativeContainer.slots) do
        local button = slot.button
        button.shown = { applications > 0 and remaining > 0 }
        button.applicationBar.shown = { applications >= button.applicationOptions.minApplications }
        local binding = button.durationBinding
        binding.font.text = remaining > 0 and binding.formatter:FormatNumber(remaining) or binding.expired
    end
end
function WingVisible(key)
    local button = nativeContainer.slots[key].button
    return button.shown[1] and button.applicationBar.shown[1] and button.durationBinding.font.text ~= ""
end
'''


def client(setup="", saved=None):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(HARNESS)
    if saved is not None:
        lua.globals().ForeverIcyVeinsDB = lua.table_from(saved)
    lua.execute(setup)
    lua.execute("local run = assert(loadstring(...)); run('ForeverIcyVeins')", SOURCE)
    lua.execute("Fire('ADDON_LOADED', 'ForeverIcyVeins')")
    return lua


class AddonTests(unittest.TestCase):
    def test_native_buff_contract_and_mirrored_art(self):
        lua = client()
        lua.execute('''
            assert(nativeContainer.unit == "player")
            assert(nativeContainer.filters.includeSpellIDs[400670])
            assert(not nativeContainer.filters.includeSpellIDs[429125])
            assert(not nativeContainer.filters.includeSpellIDs[425121])
            assert(not nativeContainer.filters.includeSpellIDs[12472])
            local count = 0
            for _ in pairs(nativeContainer.filters.includeSpellIDs) do count = count + 1 end
            assert(count == 1, "Only Fingers of Frost should trigger the effect")
            local left = nativeContainer.slots.FingersOfFrostLeft.button
            local right = nativeContainer.slots.FingersOfFrostRight.button
            assert(left.applicationOptions.minApplications == 1)
            assert(right.applicationOptions.minApplications == 2)
            local lf, rf = left.durationBinding.font, right.durationBinding.font
            assert(lf.point[4] == -rf.point[4])
            assert(left.durationBinding.formatter:FormatNumber(10):find("128:256:0:128:0:256", 1, true))
            assert(right.durationBinding.formatter:FormatNumber(10):find("128:256:128:0:0:256", 1, true))
            assert(left.durationBinding.interval == 0.02 and right.durationBinding.interval == 0.02)
            assert(not ForeverIcyVeinsFrame.mouse[1])
        ''')

    def test_preview_times_out_without_mutating_native_button(self):
        lua = client()
        lua.execute('''
            Command("test")
            assert(timers[1].seconds == 2.5 and timers[2].seconds == 5)
            assert(not nativeContainer.shown[1])
            local preview = frames[#frames].parent
            assert(preview.shown[1])
            RunTimer(1)
            assert(not preview.wings[1].shown[1] and preview.wings[-1].shown[1])
            assert(not nativeContainer.shown[1])
            RunTimer(2)
            assert(nativeContainer.shown[1])
            assert(not preview.shown[1])
            assert(not preview.bindings[-1].enabled and not preview.bindings[1].enabled)
        ''')

    def test_preview_restarts_without_stale_timeout(self):
        lua = client()
        lua.execute('''
            Command("test"); Command("test")
            local preview = frames[#frames].parent
            RunTimer(1); RunTimer(2)
            assert(not nativeContainer.shown[1])
            assert(preview.wings[1].shown[1])
            RunTimer(3)
            assert(not preview.wings[1].shown[1])
            RunTimer(4)
            assert(nativeContainer.shown[1])
        ''')

    def test_combat_cancels_preview_and_refuses_settings(self):
        lua = client()
        lua.execute('''
            Command("test")
            combat = true; Fire("PLAYER_REGEN_DISABLED")
            assert(nativeContainer.shown[1])
            local preview = frames[#frames].parent
            assert(not preview.shown[1])
            Command("scale 2"); Command("spell 400670"); Command("test")
            assert(ForeverIcyVeinsDB.scale == 1)
            assert(ForeverIcyVeinsDB.spellID == nil)
            assert(#timers == 2)
            Command("status")
            RunTimer(1); RunTimer(2)
            assert(nativeContainer.shown[1])
        ''')

    def test_charges_consumption_expiry_and_refresh(self):
        lua = client()
        lua.execute('''
            local left, right = "FingersOfFrostLeft", "FingersOfFrostRight"
            NativeAura(0, 0)
            assert(not WingVisible(left) and not WingVisible(right))
            NativeAura(2, 15)
            assert(WingVisible(left) and WingVisible(right))
            NativeAura(1, 8)
            assert(WingVisible(left) and not WingVisible(right))
            NativeAura(0, 8)
            assert(not WingVisible(left) and not WingVisible(right))
            NativeAura(2, 0)
            assert(not WingVisible(left) and not WingVisible(right))
            NativeAura(2, 4.5)
            assert(not WingVisible(left) and not WingVisible(right))
            NativeAura(2, 15)
            assert(WingVisible(left) and WingVisible(right), "Refresh must restore steady wings")
        ''')

    def test_native_blink_schedule_accelerates_only_in_last_five_seconds(self):
        lua = client()
        lua.execute('''
            local formatter = nativeContainer.slots.FingersOfFrostLeft.button.durationBinding.formatter
            assert(formatter:FormatNumber(15) ~= "")
            assert(formatter:FormatNumber(5.01) ~= "")
            assert(formatter:FormatNumber(5) ~= "")
            assert(formatter:FormatNumber(4.9) ~= "")
            assert(formatter:FormatNumber(4.5) == "")
            local previous, previousBoundary, previousGap, changes = true, 5, nil, 0
            for tick = 1, 4999 do
                local remaining = 5 - tick / 1000
                local visible = formatter:FormatNumber(remaining) ~= ""
                if visible ~= previous then
                    local gap = previousBoundary - remaining
                    if previousGap then assert(gap <= previousGap + 0.002) end
                    previousGap, previousBoundary, previous = gap, remaining, visible
                    changes = changes + 1
                end
            end
            assert(changes == 24)
        ''')

    def test_persisted_settings_apply_again_on_reload(self):
        lua = client()
        lua.execute('''
            Command("scale 1.3"); Command("alpha 0.6"); Command("pos 25 -50")
            Command("spell 400670")
        ''')
        saved = dict(lua.globals().ForeverIcyVeinsDB.items())
        reloaded = client(saved=saved)
        reloaded.execute('''
            assert(ForeverIcyVeinsFrame.scale[1] == 1.3)
            assert(ForeverIcyVeinsFrame.alpha[1] == 0.6)
            assert(ForeverIcyVeinsFrame.point[4] == 25)
            assert(ForeverIcyVeinsFrame.point[5] == -50)
            assert(nativeContainer.filters.includeSpellIDs[400670])
            assert(not nativeContainer.filters.includeSpellIDs[425121])
        ''')

    def test_clamps_settings_and_rejects_invalid_commands(self):
        lua = client(saved={"scale": float("nan"), "alpha": 9, "x": -5000, "y": "bad"})
        lua.execute('''
            assert(ForeverIcyVeinsDB.scale == 1)
            assert(ForeverIcyVeinsDB.alpha == 1)
            assert(ForeverIcyVeinsDB.x == -1500)
            assert(ForeverIcyVeinsDB.y == 0)
            Command("scale hello"); Command("pos 10 nope"); Command("spell nan")
            Command("spell 1.5"); Command("spell 1e999")
            assert(ForeverIcyVeinsDB.scale == 1)
            assert(ForeverIcyVeinsDB.x == -1500)
            assert(ForeverIcyVeinsDB.spellID == nil)
            Command("scale 100"); assert(ForeverIcyVeinsDB.scale == 2)
            Command("alpha -10"); assert(ForeverIcyVeinsDB.alpha == 0)
        ''')

    def test_blink_can_be_disabled_and_reenabled_without_changing_charges(self):
        lua = client()
        lua.execute('''
            assert(ForeverIcyVeinsDB.blink == true)
            Command("blink off")
            assert(ForeverIcyVeinsDB.blink == false)
            for _, slot in pairs(nativeContainer.slots) do
                local formatter = slot.button.durationBinding.formatter
                for tick = 1, 500 do assert(formatter:FormatNumber(tick / 100) ~= "") end
            end
            NativeAura(1, 4.5)
            assert(WingVisible("FingersOfFrostLeft") and not WingVisible("FingersOfFrostRight"))
            Command("blink on")
            NativeAura(2, 4.5)
            assert(not WingVisible("FingersOfFrostLeft") and not WingVisible("FingersOfFrostRight"))
            Command("blink invalid")
            assert(ForeverIcyVeinsDB.blink == true)
            combat = true; Command("blink off")
            assert(ForeverIcyVeinsDB.blink == true)
        ''')

    def test_blink_and_full_transparency_persist_on_reload(self):
        lua = client()
        lua.execute('Command("blink off"); Command("alpha 0")')
        reloaded = client(saved=dict(lua.globals().ForeverIcyVeinsDB.items()))
        reloaded.execute('''
            assert(ForeverIcyVeinsDB.blink == false)
            assert(ForeverIcyVeinsFrame.alpha[1] == 0)
            local formatter = nativeContainer.slots.FingersOfFrostLeft.button.durationBinding.formatter
            assert(formatter:FormatNumber(4.5) ~= "")
            Command("options")
            assert(ForeverFrostAlertOptions.parent == UIParent, "Hidden wings must not hide the menu")
            assert(ForeverFrostAlertOptions.controls[1].slider.value == 100)
            Command("reset")
            assert(ForeverIcyVeinsDB.blink and ForeverIcyVeinsDB.alpha == 0.9)
            assert(ForeverFrostAlertOptions.blink.checked == true)
        ''')

    def test_options_menu_controls_apply_save_and_preview(self):
        lua = client()
        lua.execute('''
            Command("")
            local menu = ForeverFrostAlertOptions
            assert(menu.shown[1] and UISpecialFrames[1] == "ForeverFrostAlertOptions")
            assert(menu.blink.checked == true)
            menu.blink:Click()
            assert(ForeverIcyVeinsDB.blink == false)
            menu.controls[1].slider:SetValue(75)
            assert(ForeverIcyVeinsDB.alpha == 0.25 and ForeverIcyVeinsFrame.alpha[1] == 0.25)
            menu.controls[2].slider:SetValue(125)
            menu.controls[3].slider:SetValue(200)
            menu.controls[4].slider:SetValue(-40)
            assert(ForeverIcyVeinsDB.scale == 1.25 and ForeverIcyVeinsDB.x == 200 and ForeverIcyVeinsDB.y == -40)
            menu.preview:Click()
            assert(#timers == 2 and not nativeContainer.shown[1])
            menu.reset:Click()
            assert(ForeverIcyVeinsDB.scale == 1 and ForeverIcyVeinsDB.x == 0 and ForeverIcyVeinsDB.blink)
            assert(menu.controls[1].slider.value == 10)
            menu.close:Click()
            assert(not menu.shown[1])
            Command("options"); assert(menu.shown[1])
        ''')

    def test_combat_closes_menu_and_blocks_widget_changes(self):
        lua = client()
        lua.execute('''
            Command("options")
            local menu = ForeverFrostAlertOptions
            combat = true; Fire("PLAYER_REGEN_DISABLED")
            assert(not menu.shown[1])
            menu.controls[1].slider:SetValue(100)
            menu.blink:Click()
            menu.reset:Click(); menu.preview:Click()
            assert(ForeverIcyVeinsDB.alpha == 0.9 and ForeverIcyVeinsDB.blink == true)
            assert(#timers == 0)
            Command("options"); assert(not menu.shown[1])
        ''')

    def test_reset_and_auto_restore_filters(self):
        lua = client()
        lua.execute('''
            Command("spell 429125"); Command("spell auto")
            assert(nativeContainer.filters.includeSpellIDs[400670])
            assert(not nativeContainer.filters.includeSpellIDs[429125])
            Command("spell 400670"); Command("scale 2"); Command("pos 50 30")
            Command("reset")
            assert(ForeverIcyVeinsDB.scale == 1 and ForeverIcyVeinsDB.x == 0)
            assert(ForeverIcyVeinsDB.spellID == nil)
            assert(nativeContainer.filters.includeSpellIDs[400670])
        ''')

    def test_migrates_legacy_buff_override_without_resetting_layout(self):
        for old_id in (429125, 425121):
            with self.subTest(old_id=old_id):
                lua = client(saved={"spellID": old_id, "scale": 1.5, "x": 25})
                lua.execute('''
                    assert(ForeverIcyVeinsDB.spellID == nil)
                    assert(nativeContainer.filters.includeSpellIDs[400670])
                    assert(not nativeContainer.filters.includeSpellIDs[429125])
                    assert(not nativeContainer.filters.includeSpellIDs[425121])
                    assert(ForeverIcyVeinsDB.scale == 1.5 and ForeverIcyVeinsDB.x == 25)
                ''')

    def test_non_mage_does_not_create_an_effect(self):
        lua = client('playerClass = "WARRIOR"')
        lua.execute('assert(nativeContainer == nil and SlashCmdList.FOREVERICYVEINS == nil)')

    def test_missing_native_api_reports_error(self):
        lua = client("nativeAvailable = false")
        lua.execute('''
            assert(not ForeverIcyVeinsFrame.shown[1])
            assert(SlashCmdList.FOREVERICYVEINS == nil)
            assert(messages[1]:find("nicht gestartet"))
        ''')

    def test_english_feedback_and_version_match_toc(self):
        version = re.search(r"^## Version: (\S+)$", (ROOT / "ForeverIcyVeins/ForeverIcyVeins.toc").read_text(), re.MULTILINE).group(1)
        lua = client('locale = "enUS"')
        lua.globals().expectedVersion = version
        lua.execute('''
            Command("status")
            assert(messages[1]:find("Version " .. expectedVersion, 1, true))
            assert(messages[1]:find("Fingers of Frost", 1, true))
            Command("test")
            assert(messages[2]:find("Showing a preview", 1, true))
            combat = true; Command("scale 2")
            assert(messages[3]:find("outside combat", 1, true))
        ''')

    def test_menu_uses_client_language_with_english_fallback(self):
        for locale, preview, reset, close, transparency in [
            ("deDE", "Vorschau", "Zuruecksetzen", "Schliessen", "Transparenz: 10%"),
            ("enUS", "Preview", "Reset", "Close", "Transparency: 10%"),
            ("enGB", "Preview", "Reset", "Close", "Transparency: 10%"),
            ("frFR", "Preview", "Reset", "Close", "Transparency: 10%"),
        ]:
            with self.subTest(locale=locale):
                lua = client(f'locale = "{locale}"')
                lua.execute('Command("options")')
                menu = lua.globals().ForeverFrostAlertOptions
                self.assertEqual(menu.preview.textValue[1], preview)
                self.assertEqual(menu.reset.textValue[1], reset)
                self.assertEqual(menu.close.textValue[1], close)
                self.assertEqual(menu.controls[1].text.textValue[1], transparency)

    def test_only_initializes_for_own_addon_once(self):
        lua = client()
        lua.execute('''
            local count = #frames
            Fire("ADDON_LOADED", "OtherAddon")
            Fire("ADDON_LOADED", "ForeverIcyVeins")
            assert(#frames == count)
        ''')

    def test_release_contains_only_installable_addon(self):
        toc = ROOT / "ForeverIcyVeins/ForeverIcyVeins.toc"
        version = re.search(r"^## Version: (\S+)$", toc.read_text(), re.MULTILINE).group(1)
        archive_path = ROOT / "dist" / f"ForeverFrostAlert-{version}-forever.zip"
        if not archive_path.exists():
            self.skipTest("Build the release ZIP to validate packaging")
        with zipfile.ZipFile(archive_path) as archive:
            names = {name.replace("\\", "/") for name in archive.namelist()}
            self.assertEqual(names, {
                "ForeverIcyVeins/ForeverIcyVeins.toc",
                "ForeverIcyVeins/ForeverIcyVeins.lua",
                "ForeverIcyVeins/LICENSE.txt",
                "ForeverIcyVeins/NOTICE.txt",
            })
            for name in archive.namelist():
                relative = name.replace("\\", "/")
                source = {
                    "ForeverIcyVeins/LICENSE.txt": ROOT / "LICENSE",
                    "ForeverIcyVeins/NOTICE.txt": ROOT / "NOTICE",
                }.get(relative, ROOT / relative)
                self.assertEqual(archive.read(name), source.read_bytes())
        expected = archive_path.with_suffix(".zip.sha256").read_text().split()[0]
        self.assertEqual(hashlib.sha256(archive_path.read_bytes()).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)

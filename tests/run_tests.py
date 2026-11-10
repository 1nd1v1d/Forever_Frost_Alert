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
frames, timers, messages = {}, {}, {}
combat, playerClass, nativeAvailable, locale = false, "MAGE", true, "deDE"
SlashCmdList = {}
function print(message) table.insert(messages, message) end
function UnitClass() return "Mage", playerClass end
function GetLocale() return locale end
function InCombatLockdown() return combat end
function UnitAura() error("Legacy aura queries must not be used") end
function UnitBuff() error("Legacy buff queries must not be used") end
function CombatLogGetCurrentEventInfo() error("Combat log must not be used") end
C_Timer = { After = function(seconds, callback)
    table.insert(timers, { seconds = seconds, callback = callback })
end }

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
function methods:Show() write(self, "shown", true) end
function methods:Hide() write(self, "shown", false) end
function methods:CreateTexture(_, layer)
    assert(not self.restricted, "Creating a texture after native initialization")
    local texture = setmetatable({ layer = layer }, { __index = methods })
    table.insert(self.textures, texture)
    return texture
end
function methods:RegisterEvent(event) self.events[event] = true end
function methods:UnregisterEvent(event) self.events[event] = nil end
function methods:SetScript(kind, callback)
    assert(kind == "OnEvent", "Unexpected addon script: " .. kind)
    self.callback = callback
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
    assert(not self.slot, "Only one effect slot is needed")
    validateFilters(options.candidateFilters)
    local button = CreateFrame("AuraButton", nil, self, "CustomAuraButtonTemplate")
    options.initializeFrame(button)
    assert(button.mouse[1] == false, "Must allow clicks through")
    assert(#button.textures == 2, "Both sides must share the native button")
    button.restricted = true
    self.slot, self.filters, self.button = key, options.candidateFilters, button
    nativeContainer = self
    return button
end
function methods:SetAuraSlotCandidateFilters(key, filters)
    assert(not combat, "Changing filters during combat")
    assert(key == self.slot)
    validateFilters(filters)
    self.filters = filters
end
function CreateFrame(kind, name, parent, template)
    if kind == "AuraContainer" then
        assert(nativeAvailable, "Native aura API missing")
        assert(template == "CustomAuraContainerTemplate")
    end
    local frame = setmetatable({
        kind = kind, name = name, parent = parent, template = template,
        textures = {}, events = {}, shown = {true},
    }, { __index = methods })
    table.insert(frames, frame)
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
            local left, right = unpack(nativeContainer.button.textures)
            assert(left.texture[1] == 449489 and right.texture[1] == 449489)
            assert(left.point[4] == -right.point[4])
            assert(right.texcoord[1] == 1 and right.texcoord[2] == 0)
            assert(left.blend[1] == "ADD" and right.blend[1] == "ADD")
            assert(not ForeverIcyVeinsFrame.mouse[1])
        ''')

    def test_preview_times_out_without_mutating_native_button(self):
        lua = client()
        lua.execute('''
            Command("test")
            assert(timers[1].seconds == 5)
            assert(not nativeContainer.shown[1])
            assert(frames[#frames].shown[1])
            RunTimer(1)
            assert(nativeContainer.shown[1])
            assert(not frames[#frames].shown[1])
        ''')

    def test_preview_restarts_without_stale_timeout(self):
        lua = client()
        lua.execute('''
            Command("test"); Command("test")
            RunTimer(1)
            assert(not nativeContainer.shown[1])
            RunTimer(2)
            assert(nativeContainer.shown[1])
        ''')

    def test_combat_cancels_preview_and_refuses_settings(self):
        lua = client()
        lua.execute('''
            Command("test")
            combat = true; Fire("PLAYER_REGEN_DISABLED")
            assert(nativeContainer.shown[1])
            assert(not frames[#frames].shown[1])
            Command("scale 2"); Command("spell 400670"); Command("test")
            assert(ForeverIcyVeinsDB.scale == 1)
            assert(ForeverIcyVeinsDB.spellID == nil)
            assert(#timers == 1)
            Command("status")
            RunTimer(1)
            assert(nativeContainer.shown[1])
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
            Command("alpha -10"); assert(ForeverIcyVeinsDB.alpha == 0.15)
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

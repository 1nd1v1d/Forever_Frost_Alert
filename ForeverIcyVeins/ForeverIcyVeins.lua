local addonName = ...
local _, playerClass = UnitClass("player")
if playerClass ~= "MAGE" then
    return
end

-- Blizzard's built-in Frozen Fingers art; no external textures or libraries.
local FROST_TEXTURE = 449489
local SLOTS = { [-1] = "FingersOfFrostLeft", [1] = "FingersOfFrostRight" }
local DEFAULTS = { scale = 1, alpha = 0.9, x = 0, y = 0 }
-- The proc aura, not the talent or the separate Icy Veins haste cooldown.
local DEFAULT_SPELLS = { [400670] = true }
local VERSION = "0.2.0"
local L = GetLocale() == "deDE" and {
    preview = "5 Sekunden Vorschau: zwei Aufladungen, dann eine; zunehmend schnelleres Blinken.",
    spellHelp = "Bei abweichender Buff-ID: /fiv spell ID; Standard wiederherstellen: /fiv spell auto",
    status = "Version %s; Eisige Finger; Skalierung %.2f; Deckkraft %.2f; Position %.0f / %.0f; Buff-ID %s.",
    combat = "Vorschau und Einstellungen sind ausserhalb des Kampfes verfuegbar.",
    position = "Position: /fiv pos X Y (z.B. /fiv pos 0 -50)",
    spell = "/fiv spell ID oder /fiv spell auto",
    saved = "Gespeichert. Mit /fiv test ansehen.",
    failed = "Die Forever-Auraanzeige konnte nicht gestartet werden: ",
} or {
    preview = "Showing a preview for 5 seconds: two charges, then one, with accelerating blinking.",
    spellHelp = "Override the buff ID: /fiv spell ID; restore the default: /fiv spell auto",
    status = "Version %s; Fingers of Frost; Scale %.2f; Opacity %.2f; Position %.0f / %.0f; Buff ID %s.",
    combat = "Preview and settings are available outside combat.",
    position = "Position: /fiv pos X Y (e.g. /fiv pos 0 -50)",
    spell = "/fiv spell ID or /fiv spell auto",
    saved = "Saved. Use /fiv test to preview.",
    failed = "Could not start the Forever aura display: ",
}
local settings, root, container, preview
local previewGeneration = 0

local function Say(message)
    print("|cff80dfffForever Frost Alert:|r " .. message)
end

local function Number(value, fallback, minimum, maximum)
    value = tonumber(value)
    if not value or value ~= value or value == math.huge or value == -math.huge then
        return fallback
    end
    return math.min(maximum, math.max(minimum, value))
end

local function SpellFilters()
    local spells = DEFAULT_SPELLS
    if settings.spellID then
        spells = { [settings.spellID] = true }
    end
    return { includeSpellIDs = spells }
end

local function UpdateSpellFilters()
    for _, side in ipairs({ -1, 1 }) do
        container:SetAuraSlotCandidateFilters(SLOTS[side], SpellFilters())
    end
end

local function BlinkFormatter(art)
    local formatter = C_StringUtil.CreateNumericRuleFormatter()
    -- Preconfigure a display rule for every half-cycle. Blizzard evaluates
    -- these against the real remaining duration; Lua never reads secret time.
    -- Frequency rises continuously from 1 Hz at 5 seconds to 4 Hz at expiry:
    -- phase(t) = t + 0.3*t*t, with t = seconds since the warning began.
    for halfCycle = 25, 1, -1 do
        local elapsed = (math.sqrt(1 + 0.6 * halfCycle) - 1) / 0.6
        formatter:AddBreakpoint({
            threshold = math.max(0, 5 - elapsed),
            format = (halfCycle - 1) % 2 == 0 and art or "",
        })
    end
    formatter:AddBreakpoint({ threshold = 5, format = art })
    return formatter
end

local function CreateWing(parent, side)
    -- Inline artwork lets a native duration text binding render or clear the
    -- wing using the formatter, without comparing hidden aura data in Lua.
    local left, right = 0, 128
    if side == 1 then
        left, right = 128, 0
    end
    local art = string.format("|T%d:256:128:0:0:128:256:%d:%d:0:256|t", FROST_TEXTURE, left, right)
    local wing = parent:CreateFontString(nil, "ARTWORK", "GameFontNormal")
    wing:SetSize(512, 300)
    wing:SetPoint("CENTER", parent, "CENTER", side * 145, 0)
    wing:SetWordWrap(false)
    wing:SetJustifyH("CENTER")
    wing:SetJustifyV("MIDDLE")
    local binding = C_DurationUtil.CreateDurationTextBinding()
    binding:SetFormatter(BlinkFormatter(art))
    binding:SetExpiredText("")
    binding:SetZeroDurationText("")
    binding:SetUpdateInterval(0.02)
    return wing, binding
end

local function ApplySettings()
    root:ClearAllPoints()
    root:SetPoint("CENTER", UIParent, "CENTER", settings.x, settings.y)
    root:SetScale(settings.scale)
    root:SetAlpha(settings.alpha)
end

local function StopPreview()
    previewGeneration = previewGeneration + 1
    if preview then
        preview:Hide()
        for _, binding in pairs(preview.bindings) do
            binding:Disable()
        end
    end
    if container then
        container:Show()
    end
end

local function ShowPreview()
    if not preview then
        preview = CreateFrame("Frame", nil, root)
        preview:SetAllPoints(root)
        preview:EnableMouse(false)
        preview.wings, preview.bindings = {}, {}
        for _, side in ipairs({ -1, 1 }) do
            local holder = CreateFrame("Frame", nil, preview)
            holder:SetAllPoints(preview)
            holder:EnableMouse(false)
            local wing, binding = CreateWing(holder, side)
            binding:SetFontString(wing)
            preview.wings[side], preview.bindings[side] = holder, binding
        end
    end
    -- A separate, ordinary frame: never fake a buff on the native AuraButton.
    StopPreview()
    container:Hide()
    local duration = C_DurationUtil.CreateDuration()
    duration:SetTimeFromStart(GetTime(), 5)
    for _, side in ipairs({ -1, 1 }) do
        preview.wings[side]:Show()
        preview.bindings[side]:SetDuration(duration)
        preview.bindings[side]:Enable()
    end
    preview:Show()
    local generation = previewGeneration
    C_Timer.After(2.5, function()
        if generation == previewGeneration then
            preview.wings[1]:Hide()
        end
    end)
    C_Timer.After(5, function()
        if generation == previewGeneration then
            StopPreview()
        end
    end)
    Say(L.preview)
end

local function Help()
    Say("/fiv test | scale 0.5-2 | alpha 0.15-1 | pos X Y | reset | status")
    Say(L.spellHelp)
end

local function Command(message)
    local command, arguments = message:match("^%s*(%S*)%s*(.-)%s*$")
    command = command:lower()
    if command == "status" then
        Say(string.format(L.status, VERSION, settings.scale, settings.alpha, settings.x, settings.y,
            settings.spellID and tostring(settings.spellID) or "400670"))
        return
    end
    if command == "" or command == "help" then
        Help()
        return
    end
    if InCombatLockdown() then
        Say(L.combat)
        return
    end

    if command == "test" then
        ShowPreview()
        return
    elseif command == "reset" then
        for key, value in pairs(DEFAULTS) do
            settings[key] = value
        end
        settings.spellID = nil
        UpdateSpellFilters()
    elseif command == "scale" or command == "alpha" then
        local minimum, maximum = 0.5, 2
        if command == "alpha" then
            minimum, maximum = 0.15, 1
        end
        local value = Number(arguments, nil, minimum, maximum)
        if not value then
            Help()
            return
        end
        settings[command] = value
    elseif command == "pos" then
        local x, y = arguments:match("^(%S+)%s+(%S+)$")
        x = Number(x, nil, -1500, 1500)
        y = Number(y, nil, -1000, 1000)
        if not x or not y then
            Say(L.position)
            return
        end
        settings.x, settings.y = x, y
    elseif command == "spell" then
        local spellID = tonumber(arguments)
        if arguments:lower() == "auto" then
            settings.spellID = nil
        elseif spellID and spellID > 0 and spellID < 10000000 and spellID == math.floor(spellID) then
            settings.spellID = spellID
        else
            Say(L.spell)
            return
        end
        UpdateSpellFilters()
    else
        Help()
        return
    end
    ApplySettings()
    Say(L.saved)
end

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:SetScript("OnEvent", function(self, event, loadedAddon)
    if event == "PLAYER_REGEN_DISABLED" then
        -- No preview may survive into combat and look like a real active buff.
        StopPreview()
        return
    end
    if loadedAddon ~= addonName then
        return
    end
    self:UnregisterEvent("ADDON_LOADED")

    settings = type(ForeverIcyVeinsDB) == "table" and ForeverIcyVeinsDB or {}
    settings.scale = Number(settings.scale, DEFAULTS.scale, 0.5, 2)
    settings.alpha = Number(settings.alpha, DEFAULTS.alpha, 0.15, 1)
    settings.x = Number(settings.x, DEFAULTS.x, -1500, 1500)
    settings.y = Number(settings.y, DEFAULTS.y, -1000, 1000)
    local spellID = Number(settings.spellID, nil, 1, 9999999)
    settings.spellID = spellID and math.floor(spellID) or nil
    -- Migrate an explicit override from 0.1.0 to the corrected proc.
    if settings.spellID == 429125 or settings.spellID == 425121 then
        settings.spellID = nil
    end
    ForeverIcyVeinsDB = settings

    root = CreateFrame("Frame", "ForeverIcyVeinsFrame", UIParent)
    root:SetSize(512, 256)
    root:SetFrameStrata("HIGH")
    root:EnableMouse(false)
    ApplySettings()

    -- Set up the native button before PLAYER_LOGIN. Afterwards its layout is
    -- protected; commands only transform the independent parent frame.
    local ok, result = pcall(function()
        local native = CreateFrame("AuraContainer", nil, root, "CustomAuraContainerTemplate")
        native:SetAllPoints(root)
        native:EnableMouse(false)
        for _, side in ipairs({ -1, 1 }) do
            native:AddAuraSlot(SLOTS[side], "HELPFUL", {
                candidateFilters = SpellFilters(),
                initializeFrame = function(button)
                    button:SetSize(512, 256)
                    button:SetPoint("CENTER", native, "CENTER")
                    button:EnableMouse(false)
                    local charges = CreateFrame("StatusBar", nil, button)
                    charges:SetAllPoints(button)
                    charges:EnableMouse(false)
                    local wing, binding = CreateWing(charges, side)
                    button:SetApplicationBar(charges, {
                        minApplications = side == -1 and 1 or 2,
                        maxApplications = 2,
                    })
                    button:SetDurationText(wing, { binding = binding })
                end,
            })
        end
        native:SetUnit("player")
        return native
    end)
    if not ok then
        root:Hide()
        Say(L.failed .. tostring(result))
        return
    end
    container = result
    self:RegisterEvent("PLAYER_REGEN_DISABLED")
    SLASH_FOREVERICYVEINS1 = "/fiv"
    SlashCmdList.FOREVERICYVEINS = Command
end)

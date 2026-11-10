local addonName = ...
local _, playerClass = UnitClass("player")
if playerClass ~= "MAGE" then
    return
end

-- Blizzard's built-in Frozen Fingers art; no external textures or libraries.
local FROST_TEXTURE = 449489
local SLOT = "FingersOfFrost"
local DEFAULTS = { scale = 1, alpha = 0.9, x = 0, y = 0 }
-- The proc aura, not the talent or the separate Icy Veins haste cooldown.
local DEFAULT_SPELLS = { [400670] = true }
local VERSION = "0.1.2"
local L = GetLocale() == "deDE" and {
    preview = "Vorschau fuer 5 Sekunden.",
    spellHelp = "Bei abweichender Buff-ID: /fiv spell ID; Standard wiederherstellen: /fiv spell auto",
    status = "Version %s; Eisige Finger; Skalierung %.2f; Deckkraft %.2f; Position %.0f / %.0f; Buff-ID %s.",
    combat = "Vorschau und Einstellungen sind ausserhalb des Kampfes verfuegbar.",
    position = "Position: /fiv pos X Y (z.B. /fiv pos 0 -50)",
    spell = "/fiv spell ID oder /fiv spell auto",
    saved = "Gespeichert. Mit /fiv test ansehen.",
    failed = "Die Forever-Auraanzeige konnte nicht gestartet werden: ",
} or {
    preview = "Showing a preview for 5 seconds.",
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

local function DrawFrost(parent)
    -- Both sides belong to the same native AuraButton, so they disappear
    -- together when Blizzard removes the buff, including dispels and death.
    for _, side in ipairs({ -1, 1 }) do
        local texture = parent:CreateTexture(nil, "ARTWORK")
        texture:SetTexture(FROST_TEXTURE)
        texture:SetSize(128, 256)
        texture:SetPoint("CENTER", parent, "CENTER", side * 145, 0)
        texture:SetBlendMode("ADD")
        if side == 1 then
            texture:SetTexCoord(1, 0, 0, 1)
        end
    end
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
        DrawFrost(preview)
    end
    -- A separate, ordinary frame: never fake a buff on the native AuraButton.
    StopPreview()
    container:Hide()
    preview:Show()
    local generation = previewGeneration
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
        container:SetAuraSlotCandidateFilters(SLOT, SpellFilters())
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
        container:SetAuraSlotCandidateFilters(SLOT, SpellFilters())
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
        native:AddAuraSlot(SLOT, "HELPFUL", {
            candidateFilters = SpellFilters(),
            initializeFrame = function(button)
                button:SetSize(512, 256)
                button:SetPoint("CENTER", native, "CENTER")
                button:EnableMouse(false)
                DrawFrost(button)
            end,
        })
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

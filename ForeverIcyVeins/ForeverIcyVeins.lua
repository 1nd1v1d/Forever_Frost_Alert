local addonName = ...
local _, playerClass = UnitClass("player")
if playerClass ~= "MAGE" then
    return
end

-- Blizzard's built-in Frozen Fingers art; no external textures or libraries.
local FROST_TEXTURE = 449489
local SLOTS = { [-1] = "FingersOfFrostLeft", [1] = "FingersOfFrostRight" }
local DEFAULTS = { scale = 1, alpha = 0.9, x = 0, y = 0, blink = true }
-- The proc aura, not the talent or the separate Icy Veins haste cooldown.
local DEFAULT_SPELLS = { [400670] = true }
local VERSION = "0.3.1"
local L = GetLocale() == "deDE" and {
    preview = "5 Sekunden Vorschau: zwei Aufladungen, dann eine; mit deinen Anzeige-Einstellungen.",
    spellHelp = "Bei abweichender Buff-ID: /fiv spell ID; Standard wiederherstellen: /fiv spell auto",
    status = "Version %s; Eisige Finger; Skalierung %.2f; Deckkraft %.2f; Position %.0f / %.0f; Blinken %s; Buff-ID %s.",
    combat = "Vorschau und Einstellungen sind ausserhalb des Kampfes verfuegbar.",
    position = "Position: /fiv pos X Y (z.B. /fiv pos 0 -50)",
    spell = "/fiv spell ID oder /fiv spell auto",
    saved = "Gespeichert. Mit /fiv test ansehen.",
    failed = "Die Forever-Auraanzeige konnte nicht gestartet werden: ",
    blink = "Blinken in den letzten 5 Sekunden",
    transparency = "Transparenz: %d%%",
    scale = "Groesse: %d%%",
    x = "Horizontal: %d",
    y = "Vertikal: %d",
    previewButton = "Vorschau",
    resetButton = "Zuruecksetzen",
    close = "Schliessen",
    menuHint = "Wird sofort pro Charakter gespeichert. Aenderungen ausserhalb des Kampfes.",
    enabled = "an",
    disabled = "aus",
    blinkHelp = "/fiv blink on oder /fiv blink off",
} or {
    preview = "Showing a preview for 5 seconds: two charges, then one, using your display settings.",
    spellHelp = "Override the buff ID: /fiv spell ID; restore the default: /fiv spell auto",
    status = "Version %s; Fingers of Frost; Scale %.2f; Opacity %.2f; Position %.0f / %.0f; Blinking %s; Buff ID %s.",
    combat = "Preview and settings are available outside combat.",
    position = "Position: /fiv pos X Y (e.g. /fiv pos 0 -50)",
    spell = "/fiv spell ID or /fiv spell auto",
    saved = "Saved. Use /fiv test to preview.",
    failed = "Could not start the Forever aura display: ",
    blink = "Blink during the last 5 seconds",
    transparency = "Transparency: %d%%",
    scale = "Size: %d%%",
    x = "Horizontal: %d",
    y = "Vertical: %d",
    previewButton = "Preview",
    resetButton = "Reset",
    close = "Close",
    menuHint = "Saved immediately per character. Change settings outside combat.",
    enabled = "on",
    disabled = "off",
    blinkHelp = "/fiv blink on or /fiv blink off",
}
local settings, root, container, preview, options, appliedBlink
local nativeWings = {}
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
    if not settings.blink then
        formatter:AddBreakpoint({ threshold = 0, format = art })
        return formatter
    end
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
    return wing, binding, art
end

local function ApplySettings()
    root:ClearAllPoints()
    root:SetPoint("CENTER", UIParent, "CENTER", settings.x, settings.y)
    root:SetScale(settings.scale)
    root:SetAlpha(settings.alpha)
    if container and appliedBlink ~= settings.blink then
        -- Native binding configuration may be changed outside combat. Rebind
        -- explicitly: do not rely on copied formatters sharing mutable state.
        for _, record in ipairs(nativeWings) do
            record.binding:SetFormatter(BlinkFormatter(record.art))
            record.button:SetDurationText(record.wing, { binding = record.binding })
        end
        if preview then
            for side, binding in pairs(preview.bindings) do
                binding:SetFormatter(BlinkFormatter(preview.art[side]))
            end
        end
        appliedBlink = settings.blink
    end
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
        preview.wings, preview.bindings, preview.art = {}, {}, {}
        for _, side in ipairs({ -1, 1 }) do
            local holder = CreateFrame("Frame", nil, preview)
            holder:SetAllPoints(preview)
            holder:EnableMouse(false)
            local wing, binding, art = CreateWing(holder, side)
            binding:SetFontString(wing)
            preview.wings[side], preview.bindings[side] = holder, binding
            preview.art[side] = art
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

local function OpenOptions()
    if not options then
        local panel = CreateFrame("Frame", "ForeverFrostAlertOptions", UIParent, "BasicFrameTemplateWithInset")
        options = panel
        panel:SetSize(440, 420)
        panel:SetPoint("CENTER", UIParent, "CENTER")
        panel:SetFrameStrata("DIALOG")
        panel:SetClampedToScreen(true)
        panel:SetMovable(true)
        panel:EnableMouse(true)
        panel:RegisterForDrag("LeftButton")
        panel:SetScript("OnDragStart", panel.StartMoving)
        panel:SetScript("OnDragStop", panel.StopMovingOrSizing)
        panel.TitleText:SetText("Forever Frost Alert")
        table.insert(UISpecialFrames, "ForeverFrostAlertOptions")

        local function Change(key, value)
            if InCombatLockdown() then
                panel:Hide()
                Say(L.combat)
                return
            end
            settings[key] = value
            ApplySettings()
            panel.Refresh()
        end

        panel.blink = CreateFrame("CheckButton", nil, panel, "UICheckButtonTemplate")
        panel.blink:SetPoint("TOPLEFT", panel, "TOPLEFT", 20, -38)
        local caption = panel.blink:CreateFontString(nil, "ARTWORK", "GameFontNormal")
        caption:SetPoint("LEFT", panel.blink, "RIGHT", 4, 0)
        caption:SetText(L.blink)
        panel.blink:SetScript("OnClick", function(self)
            Change("blink", self:GetChecked() == true)
        end)

        local function Slider(key, label, minimum, maximum, step, y, fromSetting, toSetting)
            local slider = CreateFrame("Slider", nil, panel)
            slider:SetSize(360, 18)
            slider:SetPoint("TOPLEFT", panel, "TOPLEFT", 35, y)
            slider:SetOrientation("HORIZONTAL")
            slider:EnableMouse(true)
            local track = slider:CreateTexture(nil, "BACKGROUND")
            track:SetPoint("LEFT", slider, "LEFT", 0, 0)
            track:SetPoint("RIGHT", slider, "RIGHT", 0, 0)
            track:SetHeight(6)
            track:SetColorTexture(0.3, 0.35, 0.4, 1)
            slider:SetThumbTexture("Interface\\Buttons\\UI-SliderBar-Button-Horizontal")
            slider:GetThumbTexture():SetSize(16, 24)
            slider:SetMinMaxValues(minimum, maximum)
            slider:SetValueStep(step)
            slider:SetObeyStepOnDrag(true)
            local text = slider:CreateFontString(nil, "ARTWORK", "GameFontNormal")
            text:SetPoint("BOTTOMLEFT", slider, "TOPLEFT", 0, 6)
            slider:SetScript("OnValueChanged", function(_, value)
                if panel.syncing then return end
                value = math.floor(value / step + 0.5) * step
                Change(key, toSetting(value))
            end)
            return { slider = slider, text = text, label = label, value = fromSetting }
        end
        local function Identity(value) return value end
        panel.controls = {
            Slider("alpha", L.transparency, 0, 100, 1, -105,
                function() return (1 - settings.alpha) * 100 end, function(value) return 1 - value / 100 end),
            Slider("scale", L.scale, 50, 200, 5, -165,
                function() return settings.scale * 100 end, function(value) return value / 100 end),
            Slider("x", L.x, -1500, 1500, 5, -225, function() return settings.x end, Identity),
            Slider("y", L.y, -1000, 1000, 5, -285, function() return settings.y end, Identity),
        }
        panel.Refresh = function()
            panel.syncing = true
            panel.blink:SetChecked(settings.blink)
            for _, control in ipairs(panel.controls) do
                local value = math.floor(control.value() + 0.5)
                control.slider:SetValue(value)
                control.text:SetText(string.format(control.label, value))
            end
            panel.syncing = false
        end
        local hint = panel:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
        hint:SetPoint("BOTTOMLEFT", panel, "BOTTOMLEFT", 20, 60)
        hint:SetSize(400, 28)
        hint:SetText(L.menuHint)

        local function Button(label, x, callback)
            local button = CreateFrame("Button", nil, panel, "UIPanelButtonTemplate")
            button:SetSize(120, 24)
            button:SetPoint("BOTTOMLEFT", panel, "BOTTOMLEFT", x, 20)
            button:SetText(label)
            button:SetScript("OnClick", callback)
            return button
        end
        panel.preview = Button(L.previewButton, 20, function()
            if InCombatLockdown() then return end
            ShowPreview()
        end)
        panel.reset = Button(L.resetButton, 160, function()
            if InCombatLockdown() then return end
            for key, value in pairs(DEFAULTS) do settings[key] = value end
            settings.spellID = nil
            UpdateSpellFilters()
            ApplySettings()
            panel.Refresh()
        end)
        panel.close = Button(L.close, 300, function() panel:Hide() end)
        panel:SetScript("OnShow", panel.Refresh)
    end
    options.Refresh()
    options:Show()
end

local function Help()
    Say("/fiv options | test | blink on/off | scale 0.5-2 | alpha 0-1 | pos X Y | reset | status")
    Say(L.spellHelp)
end

local function Command(message)
    local command, arguments = message:match("^%s*(%S*)%s*(.-)%s*$")
    command = command:lower()
    if command == "status" then
        Say(string.format(L.status, VERSION, settings.scale, settings.alpha, settings.x, settings.y,
            settings.blink and L.enabled or L.disabled,
            settings.spellID and tostring(settings.spellID) or "400670"))
        return
    end
    if command == "help" then
        Help()
        return
    end
    if InCombatLockdown() then
        Say(L.combat)
        return
    end

    if command == "" or command == "options" then
        OpenOptions()
        return
    elseif command == "test" then
        ShowPreview()
        return
    elseif command == "reset" then
        for key, value in pairs(DEFAULTS) do
            settings[key] = value
        end
        settings.spellID = nil
        UpdateSpellFilters()
    elseif command == "blink" then
        arguments = arguments:lower()
        if arguments ~= "on" and arguments ~= "off" then
            Say(L.blinkHelp)
            return
        end
        settings.blink = arguments == "on"
    elseif command == "scale" or command == "alpha" then
        local minimum, maximum = 0.5, 2
        if command == "alpha" then
            minimum, maximum = 0, 1
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
    if options then options.Refresh() end
    Say(L.saved)
end

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:SetScript("OnEvent", function(self, event, loadedAddon)
    if event == "PLAYER_REGEN_DISABLED" then
        -- No preview may survive into combat and look like a real active buff.
        StopPreview()
        if options then options:Hide() end
        return
    end
    if loadedAddon ~= addonName then
        return
    end
    self:UnregisterEvent("ADDON_LOADED")

    settings = type(ForeverIcyVeinsDB) == "table" and ForeverIcyVeinsDB or {}
    settings.scale = Number(settings.scale, DEFAULTS.scale, 0.5, 2)
    settings.alpha = Number(settings.alpha, DEFAULTS.alpha, 0, 1)
    if type(settings.blink) ~= "boolean" then settings.blink = DEFAULTS.blink end
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
    -- protected. Later changes only transform the independent parent frame or
    -- reconfigure native duration bindings outside combat; no layout is changed.
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
                    local wing, binding, art = CreateWing(charges, side)
                    button:SetApplicationBar(charges, {
                        minApplications = side == -1 and 1 or 2,
                        maxApplications = 2,
                    })
                    button:SetDurationText(wing, { binding = binding })
                    nativeWings[#nativeWings + 1] = { button = button, wing = wing, binding = binding, art = art }
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
    appliedBlink = settings.blink
    self:RegisterEvent("PLAYER_REGEN_DISABLED")
    SLASH_FOREVERICYVEINS1 = "/fiv"
    SlashCmdList.FOREVERICYVEINS = Command
end)

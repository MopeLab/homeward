-- 本局三格声音草稿、桌上邮戳与玩家自己的回放。
---@displayName 雨夜明信片
---@start
---@end

local Scope = require("official.core.runtime_scope")
local Logger = require("official.core.logger")
local scope, scopeError = Scope.from(self)
local log = Logger.create("homeward-card")
local Text = typeof(CS.UnityEngine.UI.Text)
local Button = typeof(CS.UnityEngine.UI.Button)
local hud = "walkHud/"
local card = "cardPanelRoot/"
local controls = card .. "controls/"
local settings = card .. "settings/"
local nodes, texts, listeners = {}, {}, {}
local host

-- Source + beat is stable across card order, replacement and contributor.
local catalogue = {
    S01 = {name="雨棚铁皮", art="Tin", A={"棚上碎雨","细雨敲在铁皮上。",2.6},
           B={"铁皮重滴","一颗重雨滴把棚边敲颤。",2.8}},
    S02 = {name="檐下接雨盆", art="Basin", A={"盆中双响","两滴挨得很近，水纹叠在一起。",2.6},
           B={"迟来一滴","等了半晌，盆心又响一声。",2.8}},
    S07 = {name="宿舍亮窗", art="Window", A={"走啦，吃饭去","楼下传来室友的招呼。",2.6},
           B={"远去的脚步","楼梯间的脚步渐渐远去。",2.8}}
}
local artNames = {"Tin","Basin","Window"}
local draft, sealed = {}, false
local panelOpen, toolsShown, settingsOpen = false, true, false
local pending, swapMode, swapFrom, replaceAt = nil, false, nil, nil
local zone, previewBeat, previewSource = nil, nil, nil
local walkMessage = "如果只能寄三种声音回家，你会选哪三种？"
local caption, showCaption = "家里：你那边也下雨了？我刚把窗关上。", true
local volume, ambience = 0.8, true
local info = "点一格，听听这一声。"
local soundEnds, advanceAt, sequenceAt, sequenceIndex = 0, 0, 0, nil
local lastZonePoll = -1
local initialized = false
local openingEnds = 0
-- The pass-around table owns its two hands and its finished card for this run.
-- Only the first hand reads the personal draft. Guest collection never writes it.
local desk, lastLetter
local marks = {A="◇", B="○"}
local names = {A="甲", B="乙"}

local function writing()
    return desk and desk.phase ~= "letter"
end

local function sheet()
    if not desk then return draft end
    if desk.phase == "confirm" or desk.phase == "letter" then return desk.slots end
    return desk.hands[desk.owner]
end

local function finished()
    return desk and desk.phase == "letter" or (not desk and sealed)
end

local function now()
    return CS.UnityEngine.Time.realtimeSinceStartup
end

local function get(path)
    if nodes[path] == nil and scope ~= nil then
        nodes[path] = scope:GetGameObjectByPath(path)
        if nodes[path] == nil then log:warnOnce("path-" .. path,"控件不存在",path) end
    end
    return nodes[path]
end

local function visible(path, enabled)
    local go = get(path)
    if go ~= nil and go.activeSelf ~= enabled then go:SetActive(enabled) end
end

local function label(path, value)
    local component = texts[path]
    if component == nil then
        local go = get(path)
        component = go and go:GetComponent(Text)
        if component == nil and go ~= nil and CS.TMPro ~= nil then
            component = go:GetComponent(typeof(CS.TMPro.TMP_Text))
        end
        texts[path] = component
    end
    if component ~= nil then component.text = value end
end

local function buttonLabel(path, text)
    local name = path:match("([^/]+)$")
    label(path .. "/" .. name .. "Label",text)
end

local function bind(path, callback)
    local go = get(path)
    local button = go and go:GetComponent(Button)
    if button ~= nil then
        button.onClick:AddListener(callback)
        table.insert(listeners,{button=button, callback=callback})
    end
end

local function companion()
    if host == nil and scope ~= nil then host = scope:GetScript("RainHost.lua") end
    return host
end

local function mix(ducked)
    local audio = companion()
    if audio ~= nil and type(audio.SetMix) == "function" then audio.SetMix(ambience,volume,ducked) end
end

local function stopSound()
    soundEnds, advanceAt, sequenceAt, sequenceIndex = 0, 0, 0, nil
    local audio = companion()
    if audio ~= nil and type(audio.StopBeat) == "function" then audio.StopBeat() end
    mix(false)
end

local function play(source, beat)
    local entry = catalogue[source][beat]
    local audio = companion()
    local duration
    if audio ~= nil and type(audio.PlayBeat) == "function" then
        mix(true)
        duration = audio.PlayBeat(source,beat)
    end
    if type(duration) ~= "number" or duration <= 0 then duration = entry[3] end
    soundEnds = now() + duration
    caption = entry[2]
    return soundEnds
end

local function render()
    visible("walkHud",not panelOpen)
    visible("cardPanelRoot",panelOpen)
    if not panelOpen then
        local current = catalogue[zone]
        label(hud .. "sourceLabel",current and current.name or (zone == "desk" and "窗边回信桌" or "檐下听雨"))
        local tableEntry = zone == "desk" and not desk
        local canCollect = current ~= nil and (desk ~= nil or not sealed)
        visible(hud .. "listenBtn",tableEntry or canCollect)
        visible(hud .. "keepBtn",(tableEntry and lastLetter ~= nil) or (canCollect and previewSource == zone))
        buttonLabel(hud .. "listenBtn",tableEntry and "合写一封" or (previewBeat and "再听一遍" or "听一听"))
        buttonLabel(hud .. "keepBtn",tableEntry and "上封合写" or (previewBeat == "B" and "收下落点" or "收下蓄势"))
        buttonLabel(hud .. "cardEntryBtn",desk and ("乙的声音 · " .. #desk.hands.B .. "/3") or
            (zone == "desk" and "坐到回信桌" or ("明信片 · " .. #draft .. "/3")))
        label(hud .. "walkCaption",showCaption and caption ~= "" and caption or walkMessage)
        return
    end
    local quiet = finished() and not toolsShown and sequenceIndex == nil
    visible(card .. "paperWakeBtn",quiet)
    visible(card .. "controls",not quiet and not settingsOpen and sequenceIndex == nil)
    visible(card .. "settings",not quiet and settingsOpen and sequenceIndex == nil)
    visible(card .. "closeBtn",not quiet)
    visible(card .. "feedbackLine",not quiet)
    buttonLabel(card .. "closeBtn",sequenceIndex and "跳到卡面" or (settingsOpen and "返回" or (writing() and "离席" or "收起")))
    local heading = sealed and "给家里的一封信" or "雨夜明信片"
    local postmark = sealed and "雨夜邮戳  ·  寄自开学后的第一个雨夜" or "寄自开学后的第一个雨夜"
    if desk then
        local titles = {first="甲选第一格", guest="乙选第二格", third="一起定第三格", confirm="把卡递给对方", letter="我们合寄的一封信"}
        heading = titles[desk.phase]
        postmark = finished() and "◇ 甲的窗格章　　○ 乙的雨圈章" or
            (desk.phase == "confirm" and ("等" .. names[desk.owner == "A" and "B" or "A"] .. "按章") or (marks[desk.owner] .. " " .. names[desk.owner] .. "的声音 · 点一格试听"))
    end
    label(card .. "mailHeading",heading)
    label(card .. "postmarkBtn/postmarkLabel",postmark)
    label(card .. "feedbackLine",info)
    buttonLabel(controls .. "stampBtn",sealed and "再写一封" or (replaceAt and "确认替换" or "盖章寄出"))
    buttonLabel(controls .. "swapBtn",pending and "放弃替换" or (swapMode and "取消交换" or "交换两格"))
    visible(controls .. "swapBtn",not sealed)
    visible(controls .. "stampBtn",not desk or desk.phase ~= "confirm")
    visible(controls .. "soundBtn",not writing() or desk.phase == "confirm")
    buttonLabel(controls .. "soundBtn",writing() and "重新提议" or "声音设置")
    visible(controls .. "playBtn",not writing() or desk.phase == "confirm")
    buttonLabel(controls .. "playBtn","顺序试听")
    if desk then
        local phase = desk.phase
        visible(controls .. "swapBtn",phase == "guest" or phase == "third" or phase == "confirm")
        buttonLabel(controls .. "swapBtn",phase == "guest" and "去收一声" or
            (phase == "third" and ("换" .. names[desk.owner == "A" and "B" or "A"] .. "来提议") or "按章合寄"))
        buttonLabel(controls .. "stampBtn",({first="选好，递给乙",guest="放入第二格",third="提议这拍",confirm="重新提议",letter="回到个人草稿"})[phase])
    end
    buttonLabel(settings .. "rainBtn",ambience and "环境声 · 开" or "环境声 · 关")
    buttonLabel(settings .. "captionBtn",showCaption and "字幕 · 开" or "字幕 · 关")
    for i = 1,3 do
        local prefix = card .. "slot" .. i .. "/slot" .. i
        local item = sheet()[i]
        local revealed = sequenceIndex == nil or i <= sequenceIndex
        local title = item and catalogue[item.source][item.beat][1] or "待收一声"
        if not revealed then title = "· · ·"
        elseif sequenceIndex == i then title = "正在听 · " .. title end
        if desk and item and revealed then
            if item.owner then title = marks[item.owner] .. " " .. title
            elseif desk.selected == i then title = "已选 · " .. title end
        end
        label(prefix .. "Title",title)
        for _, art in ipairs(artNames) do
            visible(prefix .. art,revealed and item ~= nil and catalogue[item.source].art == art)
        end
    end
end

local function resetEdit()
    pending, replaceAt, swapFrom, swapMode = nil,nil,nil,false
end

local function audition()
    local source = catalogue[zone]
    if (sealed and not desk) or source == nil then return end
    stopSound()
    openingEnds = 0
    previewSource, previewBeat = zone, "A"
    advanceAt = play(zone,"A") + 0.2
    walkMessage = "现在可以收下蓄势，或再等一拍。"
    render()
end

local function openCard()
    stopSound()
    panelOpen, toolsShown, settingsOpen = true,true,false
    previewSource, previewBeat = nil,nil
    caption = ""
    info = #draft == 0 and "回到雨棚，听一听，再收下喜欢的一拍。" or "点一格可试听，也可以交换两格。"
    if zone == "desk" and #draft < 3 then info = "纸上还空着 " .. (3-#draft) .. " 格。再去听听。" end
    if desk then info = zone == "desk" and "乙点自己的声音，试听后放入第二格。" or "带回喜欢的一拍，回到暖窗旁的桌子。" end
    render()
end

local function collect()
    if (sealed and not desk) or previewSource ~= zone or previewBeat == nil then return end
    local item = {source=zone,beat=previewBeat}
    stopSound()
    play(item.source,item.beat)
    local title = catalogue[item.source][item.beat][1]
    local hand = desk and desk.hands.B or draft
    for _, old in ipairs(hand) do
        if old.source == item.source and old.beat == item.beat then
            walkMessage = "这拍已收好，再听一遍。"
            caption = title .. " · 已在卡上"
            render()
            return
        end
    end
    if #hand < 3 then
        table.insert(hand,item)
        walkMessage = desk and ("乙已收下「" .. title .. "」。可回桌选第二格。") or ("已收下「" .. title .. "」。")
        caption = walkMessage
    elseif desk then
        caption = "乙已带回三拍。回桌点选要写的那一格。"
    else
        resetEdit()
        pending, panelOpen, toolsShown, settingsOpen = item,true,true,false
        info = "卡已满。点想换的格，再确认「" .. title .. "」。"
    end
    render()
end

local function nextInSequence()
    sequenceIndex = sequenceIndex + 1
    local item = sheet()[sequenceIndex]
    if item == nil then
        stopSound()
        toolsShown = not finished()
        info = "这一封，听完了。"
    else
        sequenceAt = play(item.source,item.beat) + 0.32
        info = "第 " .. sequenceIndex .. " 格 · " .. catalogue[item.source][item.beat][1]
        if showCaption then info = info .. "　" .. caption end
    end
    render()
end

local function sequence()
    if writing() and desk.phase ~= "confirm" then return end
    if #sheet() == 0 then info = "先在雨棚收下一拍。"; render(); return end
    stopSound()
    sequenceIndex, settingsOpen = 0,false
    nextInSequence()
end

local function returnToDraft(message)
    stopSound()
    desk = nil
    openCard()
    info = message
    render()
end

local function startTable()
    if #draft == 0 then
        openCard()
        info = "先去收一拍，回来让甲选第一格。"
        render()
        return
    end
    stopSound()
    resetEdit()
    openingEnds = 0
    previewSource, previewBeat, caption = nil,nil,""
    local firstHand = GetDraft()
    desk = {phase="first",owner="A",hands={A=firstHand,B={}},slots={}}
    lastLetter = nil
    panelOpen, toolsShown, settingsOpen = true,true,false
    info = "甲先点一拍试听，选好后把设备递给乙。"
    render()
end

local function guestWalk(message)
    stopSound()
    desk.selected = nil
    panelOpen, caption, previewSource, previewBeat = false,"",nil,nil
    walkMessage = message
    render()
end

local function chooseForTable()
    if desk.phase == "letter" then returnToDraft("个人明信片已取回。"); return end
    if desk.phase == "confirm" then return end
    if zone ~= "desk" then info = "回到暖窗旁的桌子，再把声音放上卡。"; render(); return end
    local item = desk.selected and sheet()[desk.selected]
    if not item then info = "先点有声音的一格试听。"; render(); return end
    stopSound()
    local choice = {source=item.source,beat=item.beat,owner=desk.owner}
    desk.selected = nil
    if desk.phase == "first" then
        desk.slots[1],desk.phase,desk.owner = choice,"guest","B"
        guestWalk("现在递给乙。离桌找喜欢的声音，收好再回来。")
    elseif desk.phase == "guest" then
        desk.slots[2],desk.phase = choice,"third"
        info = "乙可以提议第三拍，也可换甲从自己的声音里选。"
    else
        desk.slots[3],desk.phase = choice,"confirm"
        info = "请递给" .. names[desk.owner == "A" and "B" or "A"] .. "。听过三格，再按章合寄。"
    end
    render()
end

local function otherTableAction()
    if desk.phase == "guest" then
        guestWalk("乙去听一声，收下喜欢的那拍，再回桌。")
    elseif desk.phase == "third" then
        stopSound()
        desk.owner = desk.owner == "A" and "B" or "A"
        desk.selected = nil
        info = "请递给" .. names[desk.owner] .. "，点一格试听，再提议第三拍。"
    elseif desk.phase == "confirm" and not sequenceIndex and zone == "desk" then
        desk.phase, lastLetter = "letter",desk.slots
        sequence()
    end
    render()
end

local function slot(i)
    if sequenceIndex then return end
    if desk then
        local item = sheet()[i]
        if not item then return end
        stopSound()
        play(item.source,item.beat)
        toolsShown = true
        if writing() and desk.phase ~= "confirm" then desk.selected = i end
        info = showCaption and caption or catalogue[item.source][item.beat][1]
    elseif pending then
        replaceAt = i
        play(pending.source,pending.beat)
        info = "听过新声后，点「确认替换」换掉第 " .. i .. " 格。"
    elseif swapMode then
        if draft[i] == nil then
            info = "请选择有声音的格子。"
        elseif swapFrom == nil then
            swapFrom = i
            info = "已选第 " .. i .. " 格。再点另一格。"
        elseif swapFrom ~= i then
            draft[swapFrom],draft[i] = draft[i],draft[swapFrom]
            resetEdit()
            info = "已交换。顺序试听可以听到新的次序。"
        end
    elseif draft[i] then
        toolsShown = true
        local item = draft[i]
        play(item.source,item.beat)
        info = showCaption and caption or catalogue[item.source][item.beat][1]
    end
    render()
end

local function stamp()
    if desk then chooseForTable(); return end
    if sealed then
        stopSound()
        draft, sealed, panelOpen = {},false,false
        resetEdit()
        previewBeat, previewSource, caption = nil,nil,""
        walkMessage = "再写一封。今天还想带走什么？"
    elseif pending and replaceAt then
        draft[replaceAt] = pending
        info = "已把新声放进第 " .. replaceAt .. " 格。"
        resetEdit()
    elseif pending then
        info = "先点想换掉的那一格。"
    elseif #draft < 3 then
        info = "还差 " .. (3-#draft) .. " 格。收起明信片，再去听听。"
    elseif zone ~= "desk" then
        info = "三格已齐。去暖窗旁的回信桌盖章。"
    else
        sealed = true
        resetEdit()
        sequence()
    end
    render()
end

local function close()
    if sequenceIndex then
        stopSound()
        toolsShown, info = not finished(),"已跳到卡面。"
    elseif settingsOpen then
        settingsOpen, info = false,"点一格可以单独试听。"
    elseif desk then
        returnToDraft(finished() and "个人明信片已取回。桌边可重听上封合写。" or "已离席。你的个人明信片还在。")
    else
        stopSound()
        resetEdit()
        panelOpen, caption = false,""
    end
    render()
end

local function changeVolume(by)
    volume = math.max(0,math.min(1,volume+by))
    mix(soundEnds>now())
    info = "音量 " .. math.floor(volume*100+0.5) .. "%"
    render()
end

-- 交给 02 的本局只读副本。断开或取消合写时仍可返回这份草稿。
function GetDraft()
    local copy = {}
    for i, item in ipairs(draft) do copy[i] = {source=item.source,beat=item.beat} end
    return copy,sealed
end

function Start()
    if not scope then log:warnOnce("scope","明信片控件不可用",scopeError); return end
    bind(hud .. "listenBtn",function()
        if zone == "desk" and not desk then startTable() else audition() end
    end)
    bind(hud .. "keepBtn",function()
        if zone == "desk" and not desk and lastLetter then
            stopSound()
            desk = {phase="letter",slots=lastLetter}
            panelOpen,toolsShown,settingsOpen = true,true,false
            info = "点邮戳，重听你们合寄的三格。"
            render()
        else collect() end
    end)
    bind(hud .. "cardEntryBtn",openCard)
    bind(card .. "closeBtn",close)
    bind(card .. "paperWakeBtn",function()
        toolsShown = true
        info = "轻点邮戳，从头再听。"
        render()
    end)
    bind(card .. "postmarkBtn",function()
        if sequenceIndex then close()
        else toolsShown = true; sequence() end
    end)
    bind(controls .. "playBtn",sequence)
    bind(controls .. "stampBtn",stamp)
    bind(controls .. "swapBtn",function()
        if desk then otherTableAction(); return end
        if pending or swapMode then resetEdit(); info = "保留当前卡序。"
        else swapMode = true; info = "依次点想交换的两个格子。" end
        render()
    end)
    bind(controls .. "soundBtn",function()
        if writing() and desk.phase == "confirm" then
            stopSound()
            desk.phase,desk.selected,desk.slots[3] = "third",nil,nil
            info = "再点一拍，提议后递给另一位。"
            render()
        else settingsOpen = true; changeVolume(0) end
    end)
    bind(settings .. "rainBtn",function() ambience = not ambience; changeVolume(0) end)
    bind(settings .. "captionBtn",function() showCaption = not showCaption; render() end)
    bind(settings .. "quieterBtn",function() changeVolume(-0.2) end)
    bind(settings .. "louderBtn",function() changeVolume(0.2) end)
    for i = 1,3 do
        local slotIndex = i
        bind(card .. "slot" .. i,function() slot(slotIndex) end)
    end
    initialized = true
    openingEnds = now() + 5.0
    render()
end

function Update()
    if not initialized then return end
    local t = now()
    if t-lastZonePoll >= 0.12 then
        lastZonePoll = t
        local spatial = companion()
        local current = spatial and type(spatial.GetZone) == "function" and spatial.GetZone() or nil
        if current ~= zone then
            zone = current
            if writing() and desk.phase ~= "guest" and zone ~= "desk" then
                returnToDraft("已离开回信桌，个人明信片已取回。")
            end
            if not panelOpen then
                if advanceAt>0 then stopSound() end
                previewSource, previewBeat = nil,nil
                if t >= openingEnds then caption = "" end
                walkMessage = desk and (zone == "desk" and "乙回到桌边。打开乙的声音，选第二格。" or "乙听一听，收好喜欢的那拍再回桌。") or
                              zone == "desk" and "坐到桌边，整理你的三格声音。" or
                              (catalogue[zone] and "点「听一听」，等到喜欢的那一拍。"
                               or "沿雨棚走走，听听立柱后面。")
            end
            render()
        end
    end
    if openingEnds > 0 and t >= openingEnds then
        openingEnds, caption = 0,""
        render()
    end
    if advanceAt>0 and t>=advanceAt then
        advanceAt = 0
        previewBeat = "B"
        play(previewSource,"B")
        walkMessage = "收下落点，或再听一遍。"
        render()
    end
    if sequenceIndex and t>=sequenceAt then nextInSequence() end
    if soundEnds>0 and t>=soundEnds then soundEnds=0; mix(false) end
end

function OnDestroy()
    for _, item in ipairs(listeners) do item.button.onClick:RemoveListener(item.callback) end
    listeners = {}
    if initialized and host ~= nil then stopSound() end
end

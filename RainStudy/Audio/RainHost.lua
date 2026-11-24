-- 三格卡的本地回听和跨柱雨声。HostStart / HostUpdate / HostBeat 由场景组装时提供。
---@displayName 雨棚声音与回信桌
---@start
---@var S01A:UnityEngine.AudioClip=nil
---@name 铁皮碎雨音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S01AVolume:number=0.88
---@name 铁皮碎雨音量
---@var S01AMaxDistance:number=20
---@name 铁皮碎雨最大作用范围
---@var S01B:UnityEngine.AudioClip=nil
---@name 铁皮重滴音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S01BVolume:number=0.88
---@name 铁皮重滴音量
---@var S01BMaxDistance:number=20
---@name 铁皮重滴最大作用范围
---@var S02A:UnityEngine.AudioClip=nil
---@name 两圈水纹音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S02AVolume:number=0.86
---@name 两圈水纹音量
---@var S02AMaxDistance:number=20
---@name 两圈水纹最大作用范围
---@var S02B:UnityEngine.AudioClip=nil
---@name 迟来一滴音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S02BVolume:number=0.86
---@name 迟来一滴音量
---@var S02BMaxDistance:number=20
---@name 迟来一滴最大作用范围
---@var S03A:UnityEngine.AudioClip=nil
---@name 链条绷紧音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S03AVolume:number=0.85
---@name 链条绷紧音量
---@var S03AMaxDistance:number=20
---@name 链条绷紧最大作用范围
---@var S03B:UnityEngine.AudioClip=nil
---@name 卷门顿住音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S03BVolume:number=0.85
---@name 卷门顿住音量
---@var S03BMaxDistance:number=20
---@name 卷门顿住最大作用范围
---@var S04A:UnityEngine.AudioClip=nil
---@name 竹盖轻碰音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S04AVolume:number=0.85
---@name 竹盖轻碰音量
---@var S04AMaxDistance:number=20
---@name 竹盖轻碰最大作用范围
---@var S04B:UnityEngine.AudioClip=nil
---@name 蒸汽呼出音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S04BVolume:number=0.85
---@name 蒸汽呼出音量
---@var S04BMaxDistance:number=20
---@name 蒸汽呼出最大作用范围
---@var S05A:UnityEngine.AudioClip=nil
---@name 两下车铃音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S05AVolume:number=0.85
---@name 两下车铃音量
---@var S05AMaxDistance:number=20
---@name 两下车铃最大作用范围
---@var S05B:UnityEngine.AudioClip=nil
---@name 铃声渐远音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S05BVolume:number=0.85
---@name 铃声渐远音量
---@var S05BMaxDistance:number=20
---@name 铃声渐远最大作用范围
---@var S06A:UnityEngine.AudioClip=nil
---@name 钥匙相碰音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S06AVolume:number=0.85
---@name 钥匙相碰音量
---@var S06AMaxDistance:number=20
---@name 钥匙相碰最大作用范围
---@var S06B:UnityEngine.AudioClip=nil
---@name 钥匙转开音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S06BVolume:number=0.85
---@name 钥匙转开音量
---@var S06BMaxDistance:number=20
---@name 钥匙转开最大作用范围
---@var S07A:UnityEngine.AudioClip=nil
---@name 室友招呼音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S07AVolume:number=0.9
---@name 室友招呼音量
---@var S07AMaxDistance:number=20
---@name 室友招呼最大作用范围
---@var S07B:UnityEngine.AudioClip=nil
---@name 楼梯脚步音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var S07BVolume:number=0.9
---@name 楼梯脚步音量
---@var S07BMaxDistance:number=20
---@name 楼梯脚步最大作用范围
---@var RainBed:UnityEngine.AudioClip=nil
---@name 环境雨音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var RainBedVolume:number=0.59
---@name 环境雨音量
---@var RainBedMaxDistance:number=34
---@name 环境雨最大作用范围
---@var FamilyVoice:UnityEngine.AudioClip=nil
---@name 家人语音音效
---@refFrom asset
---@assetCategory Music
---@dataType Audio
---@var FamilyVoiceVolume:number=0.95
---@name 家人语音音量
---@var FamilyVoiceMaxDistance:number=22
---@name 家人语音最大作用范围
---@end

local UE = CS.UnityEngine
local readSettings = {
    S01A = function() return S01A, S01AVolume, S01AMaxDistance end,
    S01B = function() return S01B, S01BVolume, S01BMaxDistance end,
    S02A = function() return S02A, S02AVolume, S02AMaxDistance end,
    S02B = function() return S02B, S02BVolume, S02BMaxDistance end,
    S03A = function() return S03A, S03AVolume, S03AMaxDistance end,
    S03B = function() return S03B, S03BVolume, S03BMaxDistance end,
    S04A = function() return S04A, S04AVolume, S04AMaxDistance end,
    S04B = function() return S04B, S04BVolume, S04BMaxDistance end,
    S05A = function() return S05A, S05AVolume, S05AMaxDistance end,
    S05B = function() return S05B, S05BVolume, S05BMaxDistance end,
    S06A = function() return S06A, S06AVolume, S06AMaxDistance end,
    S06B = function() return S06B, S06BVolume, S06BMaxDistance end,
    S07A = function() return S07A, S07AVolume, S07AMaxDistance end,
    S07B = function() return S07B, S07BVolume, S07BMaxDistance end,
    RainBed = function() return RainBed, RainBedVolume, RainBedMaxDistance end,
    FamilyVoice = function() return FamilyVoice, FamilyVoiceVolume, FamilyVoiceMaxDistance end,
}

local ambientOn, masterVolume, duck = true, .8, false
local playerZ, initialized, openingPending = 0, false, true
local card, rain, roof, bowl
local channels = {}
local nextDrop = 0
local dropIndex = 0
local crossfade = 0
local bedGain = 1
local studyFrame = nil

local function clamp01(value)
    return math.max(0, math.min(1, value))
end

local function makeChannel(name, x, y, z)
    local emitter = UE.GameObject("Homeward_" .. name)
    local source = emitter:AddComponent(typeof(UE.AudioSource))
    source.playOnAwake = false
    source.spatialBlend = 1
    source.rolloffMode = UE.AudioRolloffMode.Linear
    local channel = { emitter = emitter, source = source, offset = UE.Vector3(x, y, z) }
    table.insert(channels, channel)
    return channel
end

local function anchorScenery()
    local frame = type(GetStudyFrame) == "function" and GetStudyFrame() or nil
    if frame == nil then return false end
    if studyFrame ~= frame then
        for _, channel in ipairs({rain, roof, bowl}) do
            channel.emitter.transform:SetParent(frame, false)
            channel.emitter.transform.localPosition = channel.offset
        end
        studyFrame = frame
    end
    return true
end

local function stop(channel)
    if channel then
        channel.source:Stop()
        channel.source.clip = nil
        channel.key = nil
    end
end

-- A changed or cleared inspector reference also stops its previous sound.
local function apply(channel, gain)
    if channel.key == nil then return false end
    local clip, volume, limit = readSettings[channel.key]()
    if clip == nil or clip ~= channel.source.clip or limit <= 0 then
        stop(channel)
        return false
    end
    channel.source.minDistance = math.min(2, limit * .2)
    channel.source.maxDistance = limit
    channel.source.volume = clamp01(masterVolume * volume * gain)
    if channel.source.volume <= 0 then
        stop(channel)
        return false
    end
    return true
end

local function play(channel, key, looped, gain)
    stop(channel)
    if not readSettings[key] then return 0 end
    local clip = readSettings[key]()
    if clip == nil then return 0 end
    channel.key = key
    channel.source.clip = clip
    channel.source.loop = looped
    local duration = clip.length
    if apply(channel, gain) then channel.source:Play() end
    return duration
end

local function ensureReady()
    if initialized then return end
    card = makeChannel("Card", 0, 1.3, 0)
    rain = makeChannel("Rain", 0, 3.4, 4)
    roof = makeChannel("Tin", -1.25, 2.75, 2.3)
    bowl = makeChannel("Basin", 1.42, .48, 5.5)
    initialized = true
end

local function placeCard()
    -- The card is held by the listener, including at the window and on future shores.
    local camera = UE.Camera.main
    if camera then card.emitter.transform.position = camera.transform.position
    elseif studyFrame then
        card.emitter.transform.position = studyFrame:TransformPoint(UE.Vector3(0, 1.4, playerZ))
    end
end

function PlayBeat(sourceId, beat)
    openingPending = false
    local key = tostring(sourceId) .. tostring(beat)
    if not readSettings[key] then return 0 end
    ensureReady()
    placeCard()
    local duration = play(card, key, false, 1)
    if type(HostBeat) == "function" then HostBeat(sourceId, beat) end
    return duration
end

function StopBeat()
    openingPending = false
    stop(card)
end

function SetMix(enabled, volume, ducked)
    ambientOn = enabled == true
    masterVolume = clamp01(tonumber(volume) or 1)
    duck = ducked == true
end

function UpdateRain(positionZ)
    if type(positionZ) == "number" then playerZ = positionZ end
end

function Start()
    ensureReady()
    if type(HostStart) == "function" then HostStart() end
end

function Update()
    if type(HostUpdate) == "function" then HostUpdate() end
    ensureReady()
    placeCard()
    local dt = math.min(.2, UE.Time.deltaTime)
    -- The single uninterrupted bed masks the material change. Only the near drip
    -- and faint room response move from corrugated sheet to enclosed enamel.
    local target = clamp01((playerZ - 2.8) / 2.4)
    crossfade = crossfade + (target - crossfade) * math.min(1, 6 * dt)
    if openingPending and FamilyVoice ~= nil and UE.Camera.main ~= nil then
        openingPending = false
        play(card, "FamilyVoice", false, 1)
    end
    if card.key then apply(card, 1) end
    local isReading = duck or card.source.isPlaying
    local targetGain = isReading and .27 or 1
    bedGain = bedGain + (targetGain - bedGain) * math.min(1, dt * 7)
    if not anchorScenery() or not ambientOn or masterVolume <= 0 then
        stop(rain)
        stop(roof)
        stop(bowl)
        return
    end
    local rainLevel = bedGain * (.95 - .27 * crossfade)
    if rain.key then apply(rain, rainLevel) end
    if not rain.source.isPlaying and RainBed ~= nil then play(rain, "RainBed", true, rainLevel) end
    local roofGain = .72 * (1 - crossfade) * bedGain
    local bowlGain = .76 * crossfade * bedGain
    if roof.key then apply(roof, roofGain) end
    if bowl.key then apply(bowl, bowlGain) end
    nextDrop = nextDrop - dt
    if nextDrop <= 0 then
        dropIndex = dropIndex + 1
        local beat = dropIndex % 3 == 0 and "B" or "A"
        -- Use a single nearby accent per cycle. Crossfade and 3D rolloff control its depth.
        if crossfade < .5 then play(roof, "S01" .. beat, false, roofGain)
        else play(bowl, "S02" .. beat, false, bowlGain) end
        nextDrop = (crossfade < .5 and 2.6 or 3.15) + (dropIndex % 3) * .13
    end
end

function OnDisable()
    for _, channel in ipairs(channels) do stop(channel) end
end

function OnDestroy()
    for _, channel in ipairs(channels) do
        stop(channel)
        UE.Object.Destroy(channel.emitter)
    end
    channels = {}
    initialized = false
end

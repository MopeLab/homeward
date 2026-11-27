---@displayName 蒸笼盖沿的白汽
---@start
---@var Steam:UnityEngine.GameObject=nil
---@name 蒸笼白汽
---@refFrom asset
---@assetCategory Effect
---@dataType Prefab
---@end
local Effect = require("official.effect.playback")
local Scope = require("official.core.runtime_scope").from(self)
local Clock = CS.UnityEngine.Time
local host, spout
local lastStart, retryAt = nil, 0

function Update()
    if not Steam or not Scope or Clock.time < retryAt then return end
    if not host then host = Scope:GetScript("RainHost.lua") end
    if host and not spout then
        local frame = host.GetStudyFrame()
        spout = frame and frame:Find("ShoreRoute/SteamSpout")
    end
    if not spout then
        retryAt = Clock.time + .15
        return
    end
    local source, beat, began = host.GetShoreBeat()
    if source ~= "S04" or beat ~= "B" or began == lastStart then return end
    -- The lid is already settling if an archived effect arrives very late.
    if not began or Clock.time - began > .65 then return end
    local instance, reason = Effect.spawn(self, Steam, spout.position, {parent=spout})
    if instance or reason ~= Effect.Reason.NotReady then
        lastStart = began
    else
        retryAt = Clock.time + .10
    end
end

---@displayName 盆沿的细雨
---@start
---@var GutterRain:UnityEngine.GameObject=nil
---@name 漏檐细雨
---@refFrom asset
---@assetCategory Effect
---@dataType Prefab
---@end
local Effect = require("official.effect.playback")
local U = CS.UnityEngine
local handle, failure
local retryAt = 0

local function begin()
    if handle or GutterRain == nil then return end
    local at = self.transform:TransformPoint(U.Vector3(0, 0.224, 0))
    handle, failure = Effect.create(self, GutterRain, at, {parent=self})
end

function Start() begin() end

function Update()
    if handle or U.Time.time < retryAt then return end
    retryAt = U.Time.time + 1
    if not failure or failure == Effect.Reason.NotReady then begin() end
end

function RainStatus()
    if not handle then return failure or "waiting" end
    return handle:IsReady() and "ready" or "loading"
end

function OnDestroy()
    if handle then handle:Release() end
    handle = nil
end

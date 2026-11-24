-- 与 RainStudy 的局部米制坐标对齐；明信片 UI 自己的 Canvas 不作为世界坐标系。
local locationScope = require("official.core.runtime_scope").from(self)
local frame, localActor, activeZone, placed
local points = {
    {"S01", -1.25, 2.3, 2.5}, {"S02", 1.42, 5.5, 2.1},
    {"desk", -1.2, 8, 2.0}, {"S07", 1.4, 8.8, 1.9}
}
local sampleAt = 0
local V3 = CS.UnityEngine.Vector3
local clock = CS.UnityEngine.Time
local movingPart, baseScale, motionId, motionBeat, motionStart
local parts = {}

-- Retain the original ceiling for movement and camera queries. Only its drawn
-- sheet flexes; the collider uses the same mesh at its stationary rest pose.
local function keepRoofContact(roof)
    if not roof or roof.parent:Find("RoofContact") then return end
    local unity = CS.UnityEngine
    local surface = roof:GetComponent(typeof(unity.MeshFilter))
    if not surface or not surface.sharedMesh then return end
    local contact = unity.GameObject("RoofContact")
    contact.layer = roof.gameObject.layer
    contact.transform:SetParent(roof.parent, false)
    contact.transform.localPosition = roof.localPosition
    contact.transform.localRotation = roof.localRotation
    contact.transform.localScale = roof.localScale
    contact:AddComponent(typeof(unity.MeshCollider)).sharedMesh = surface.sharedMesh
end

function HostStart()
    local host = locationScope and locationScope:GetRuntimeHostRoot()
    if host then
        frame = host.transform
        parts.S02 = frame:Find("map-rainwalk/basin/Model/BasinRipple")
        parts.S01 = frame:Find("map-rainwalk/campus/Model/RoofSkin")
        keepRoofContact(parts.S01)
    end
end

function GetZone()
    return activeZone
end

function GetStudyFrame()
    return frame
end

function HostBeat(sourceId, beat)
    if movingPart and baseScale then movingPart.localScale = baseScale end
    movingPart = parts[sourceId]
    if not movingPart then return end
    baseScale = movingPart.localScale
    motionId, motionBeat, motionStart = sourceId, beat, clock.time
end

local function animateBeat()
    if not movingPart then return end
    local t = clock.time - motionStart
    if t > 2.0 then
        movingPart.localScale = baseScale
        movingPart = nil
        return
    end
    if motionId == "S02" then
        local cycle = motionBeat == "A" and 0.48 or 1.05
        local swell = 0.44 + 0.75 * math.min(1, (t % cycle) / cycle)
        movingPart.localScale = V3(baseScale.x * swell, baseScale.y, baseScale.z * swell)
    elseif motionId == "S01" then
        local vibration = (motionBeat == "A" and 0.004 or 0.008) * math.sin(t * 38) * math.exp(-t * 4)
        movingPart.localScale = V3(baseScale.x, baseScale.y * (1 + vibration), baseScale.z)
    end
end

function HostUpdate()
    animateBeat()
    if clock.time < sampleAt then return end
    sampleAt = clock.time + 0.065
    if not frame then HostStart() end
    if not frame then return end
    if not localActor then localActor = CS.DouyinActorService.GetLocalActor() end
    if not localActor or not localActor.isLocal then return end
    if not placed then
        -- 默认出生地与步道重合。脚底提高到步道表面，仅在本局开始时一次。
        localActor:Teleport(frame:TransformPoint(V3(0, 0.18, 0)), frame.rotation)
        placed = true
    end
    local p = frame:InverseTransformPoint(localActor.position)
    if UpdateRain then UpdateRain(p.z) end
    activeZone = nil
    if math.abs(p.y) > 2.4 then return end
    local nearest = math.huge
    for _, point in ipairs(points) do
        local distance = (p.x - point[2]) ^ 2 + (p.z - point[3]) ^ 2
        if distance <= point[4] ^ 2 and distance < nearest then
            nearest, activeZone = distance, point[1]
        end
    end
end


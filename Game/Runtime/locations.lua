-- 与 RainStudy 的局部米制坐标对齐；明信片 UI 自己的 Canvas 不作为世界坐标系。
local locationScope = require("official.core.runtime_scope").from(self)
local frame, localActor, activeZone, placed
local points = {
    {"S01", -1.25, 2.3, 2.5}, {"S02", 1.42, 5.5, 2.1},
    {"desk", -1.2, 8, 2.0}, {"S07", 1.4, 8.8, 1.9},
    {"bow",0,15,2.15}, {"marketDock",-11,20.5,2.0}, {"duskDock",11,20.5,2.0},
    {"S03",-12.8,25.4,2.35}, {"S04",-9.2,30.5,2.35},
    {"S05",9.2,25.4,2.35}, {"S06",12.8,30.5,2.35}
}
local sampleAt = 0
local V3 = CS.UnityEngine.Vector3
local clock = CS.UnityEngine.Time
local movingPart, baseScale, basePosition, baseAngles, motionId, motionBeat, motionStart, motionLength
local parts, lamps = {}, {}
local lensBlocks = {}
local bowBeam, bowAim
local region, crossing, arriveAt, litBank = "home",nil,0,nil
local lastDry, outsideSince
local recoveries = 0
local waterRings,ringMaterial,ringRoot = {},nil,nil
local nextDrop,dropSlot,ringSeed,contactCount = 0,0,27113,0

local function ringRandom()
    ringSeed=(ringSeed*48271)%2147483647
    return ringSeed/2147483647
end

local function prepareWaterRings()
    local U=CS.UnityEngine
    local shader=U.Shader.Find("Sprites/Default")
    if not shader then return end
    ringRoot=U.GameObject("RiverRipples")
    ringRoot.transform:SetParent(frame,false)
    ringMaterial=U.Material(shader)
    for i=1,12 do
        local node=U.GameObject("Ripple"..i)
        node.transform:SetParent(ringRoot.transform,false)
        local line=node:AddComponent(typeof(U.LineRenderer))
        line.useWorldSpace=false
        line.sharedMaterial=ringMaterial
        line.positionCount=33
        -- An almost-closed crest leaves a small break on its lee side.
        for j=0,32 do
            local angle=j/32*math.pi*1.92
            line:SetPosition(j,V3(math.cos(angle),0,.91*math.sin(angle)))
        end
        line.enabled=false
        waterRings[i]={line=line,transform=node.transform}
    end
end

local function startRing(slot,x,z,start,radius,lifetime,alpha)
    local r=waterRings[slot]
    if not r then return end
    r.start,r.radius,r.life,r.alpha=start,radius,lifetime,alpha
    r.transform.localPosition=V3(x,-.366,z)
    r.transform.localEulerAngles=V3(0,360*ringRandom(),0)
end

local function animateWater()
    if #waterRings==0 or not localActor then return end
    local now=clock.time
    if now>=nextDrop then
        local p=frame:InverseTransformPoint(localActor.position)
        dropSlot=dropSlot%10+1
        startRing(dropSlot,p.x+(ringRandom()-.5)*11,p.z+(ringRandom()-.5)*11,
            now,.13+.23*ringRandom(),.78+.45*ringRandom(),.53)
        nextDrop=now+.12+.06*ringRandom()
    end
    for _,r in ipairs(waterRings) do
        if r.start then
            local t=(now-r.start)/r.life
            r.line.enabled=t>=0 and t<1
            if t>=1 then
                r.start=nil
            elseif t>=0 then
                local size=r.radius*(.09+t*(1.5-.59*t))
                r.transform.localScale=V3(size,1,size)
                local alpha=r.alpha*math.min(1,10*t)*(1-t)
                local color=CS.UnityEngine.Color(.48,.67,.70,alpha)
                r.line.startColor=color
                r.line.endColor=color
                r.line.widthMultiplier=.009+.010*(1-t)
            end
        end
    end
end

function GetRiverContactCount() return contactCount end
local landings = {
    market={-11,20.5,0}, dusk={11,20.5,0}, home={0,9.7,210}, bow={0,15,0}
}
local allowed = {
    bow={market=true,dusk=true}, marketDock={dusk=true,home=true},
    duskDock={market=true,home=true}, desk={bow=true}
}

local function rigNavigationLights(route)
    local U = CS.UnityEngine
    for _,spec in ipairs({
        {"CentralBoat/BowGlass","bow"}, {"MarketBoat/BowGlass","market"}, {"DuskBoat/BowGlass","dusk"},
        {"CentralBoat/SternGlass","home"}, {"MarketBoat/SternGlass","home"}, {"DuskBoat/SternGlass","home"}
    }) do
        local glass = route:Find(spec[1])
        local renderer = glass and glass:GetComponent(typeof(U.Renderer))
        if renderer and renderer.sharedMaterial and renderer.sharedMaterial:HasProperty("_EmissionPower") then
            local material = U.Material(renderer.sharedMaterial)
            material:EnableKeyword("_EMISSION")
            material:SetTexture("_EmissionTex",U.Texture2D.whiteTexture)
            material:SetTexture("_EmissionMask",U.Texture2D.whiteTexture)
            material:SetColor("_EmissionColor",spec[2]=="dusk" and U.Color(.67,.83,1,1) or U.Color(1,.66,.28,1))
            material:SetFloat("_EmissionPower",.32)
            renderer.sharedMaterial=material
            table.insert(lensBlocks,{material,spec[2]})
        end
    end
    local bow = route:Find("HarborBowLamp")
    if bow then
        local holder = U.GameObject("TurningBowLight")
        holder.transform:SetParent(bow,false)
        bowBeam = holder:AddComponent(typeof(U.Light))
        bowBeam.type=U.LightType.Spot
        bowBeam.range=24
        bowBeam.spotAngle=30
        bowBeam.intensity=2.2
        bowBeam.color=U.Color(1,.78,.47,1)
    end
end

function ReleaseShoreLights()
    local U = CS.UnityEngine
    if ringRoot then U.Object.Destroy(ringRoot) end
    if ringMaterial then U.Object.Destroy(ringMaterial) end
    waterRings,ringMaterial,ringRoot={},nil,nil
    for _,lens in ipairs(lensBlocks) do U.Object.Destroy(lens[1]) end
    lensBlocks={}
    if bowBeam then U.Object.Destroy(bowBeam.gameObject) end
    bowBeam=nil
end

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
        local route = frame:Find("ShoreRoute")
        if route then
            if route:Find("RiverSurface") then prepareWaterRings() end
            local actorParts = {ShutterEdge="S03",SteamerLid="S04",BellCap="S05",DoorLeaf="S06"}
            local markers = {HarborBowLamp="bow",MarketBerthLamp="market",DuskBerthLamp="dusk",ReturnLamp="home"}
            local descendants = route:GetComponentsInChildren(typeof(CS.UnityEngine.Transform),true)
            for i=0,descendants.Length-1 do
                local t = descendants[i]
                if actorParts[t.name] then parts[actorParts[t.name]] = t end
                if markers[t.name] then
                    local light = t:GetComponent(typeof(CS.UnityEngine.Light))
                    if light then lamps[markers[t.name]] = {light, light.intensity} end
                end
            end
            rigNavigationLights(route)
        end
    end
end

function GetZone()
    return activeZone
end

function GetStudyFrame()
    return frame
end

function GetVoyageState() return region,crossing,litBank end

local function lightRoute(destination, sailing)
    litBank = destination
    for key, entry in pairs(lamps) do
        local selected = key == destination or (key == "bow" and destination ~= nil)
        entry[1].intensity = entry[2] * (selected and (sailing and 1.85 or 1.45) or 0.78)
    end
    for _,lens in ipairs(lensBlocks) do
        local key=lens[2]
        local selected=key==destination or (key=="bow" and (destination=="market" or destination=="dusk"))
        lens[1]:SetFloat("_EmissionPower",selected and (sailing and 2.8 or 1.9) or .32)
    end
    local target=lamps[destination]
    if bowBeam and target and destination~="bow" then
        local delta=target[1].transform.position-bowBeam.transform.position
        if delta.sqrMagnitude>.01 then bowAim=CS.UnityEngine.Quaternion.LookRotation(delta) end
    end
end

function PreviewBank(destination)
    if crossing or not allowed[activeZone] or not allowed[activeZone][destination] then return 0 end
    if destination ~= "market" and destination ~= "dusk" then return 0 end
    lightRoute(destination,false)
    return PlayShoreCue(destination)
end

function BeginVoyage(destination)
    if not localActor or crossing or not allowed[activeZone] or not allowed[activeZone][destination] then return false end
    crossing, arriveAt, activeZone = destination,clock.time + 1.35,"sailing"
    lightRoute(destination,true)
    return true
end

local function land(destination)
    local at = landings[destination]
    local angle = math.rad(at[3])
    local forward = frame:TransformDirection(V3(math.sin(angle),0,math.cos(angle)))
    localActor:Teleport(frame:TransformPoint(V3(at[1],0.16,at[2])),CS.UnityEngine.Quaternion.LookRotation(forward))
    region = (destination == "bow") and "home" or destination
    lastDry,outsideSince = nil,nil
    lightRoute(region,false)
end

-- Distances are measured from the actual top edges of the three walks and decks,
-- independently of the world's terrain or water collider beneath the player's feet.
local hull = {
    {-2.12,.71},{-1.88,.823},{-1.36,.99},{-.65,1.035},{.44,1.025},
    {1.14,.936},{1.63,.79},{1.97,.64},{2.12,.54}
}

local function deckClearance(x,z)
    local width = hull[1][2]
    for i=2,#hull do
        local a,b = hull[i-1],hull[i]
        if z <= b[1] then
            width = a[2] + (b[2]-a[2])*math.max(0,(z-a[1])/(b[1]-a[1]))
            break
        end
        width = b[2]
    end
    return math.min(width-math.abs(x),z+2.12,2.12-z)
end

local function groundHeight(z)
    return region == "dusk" and math.max(0,math.min(.7,(z-24)*.1)) or 0
end

local function recoverFromWater(p)
    local x0 = region=="market" and -11 or (region=="dusk" and 11 or 0)
    local x,z = p.x-x0,p.z
    local clear, safeZ
    if region == "home" then
        local campus = math.min(2.9-math.abs(x),z+3,11-z)
        local pier = math.min(.93-math.abs(x),z-10.622,12.658-z)
        clear = math.max(campus,pier,deckClearance(x,z-14.52))
        safeZ = math.max(-2.25,math.min(16.05,z))
    else
        local shore = math.min(3.2-math.abs(x),z-20.2,33.5-z)
        clear = math.max(shore,deckClearance(x,z-18.35))
        -- At the back of either lane the last house closes off the path.
        safeZ = math.max(16.95,math.min(32.5,z))
    end
    local height = groundHeight(z)
    if clear >= -.12 and p.y >= height-.18 then
        outsideSince = nil
        -- Keep a position the player physically occupied, bounded away from the edge.
        if clear >= .55 and p.y >= height-.06 and p.y <= height+.17 then
            lastDry = V3(p.x,height+.13,z)
        end
        return false
    end
    outsideSince = outsideSince or clock.time
    local elapsed = clock.time-outsideSince
    -- A jump can briefly pass outside a plank before landing back on it.
    if elapsed < .12 or (p.y > height+.18 and elapsed < 1.8) then return false end
    local safeX,safeY = x0,groundHeight(safeZ)+.13
    if lastDry then
        local visitedDistance = (lastDry.x-p.x)^2+(lastDry.z-z)^2
        local centreDistance = (safeX-p.x)^2+(safeZ-z)^2
        if visitedDistance <= centreDistance then
            safeX,safeY,safeZ = lastDry.x,lastDry.y,lastDry.z
        end
    end
    if #waterRings>0 then
        startRing(11,p.x,z,clock.time,.78,1.4,.85)
        startRing(12,p.x,z,clock.time+.14,.55,1.12,.66)
        contactCount=contactCount+1
    end
    localActor:Teleport(frame:TransformPoint(V3(safeX,safeY,safeZ)),localActor.rotation)
    recoveries,outsideSince = recoveries+1,nil
    return true
end

function GetWaterRecoveryCount() return recoveries end

function GetShoreBeat() return motionId,motionBeat,motionStart end

local function restorePart()
    if movingPart then
        movingPart.localPosition = basePosition
        movingPart.localScale = baseScale
        movingPart.localEulerAngles = baseAngles
    end
    movingPart = nil
end

function HostBeat(sourceId, beat, duration)
    restorePart()
    motionId, motionBeat, motionStart = sourceId, beat, clock.time
    motionLength = 2
    if (sourceId == "S02" and beat == "A") or (sourceId == "S03" and beat == "B") then
        motionLength = math.max(2, duration or 0)
    end
    movingPart = parts[sourceId]
    if not movingPart then return end
    baseScale, basePosition, baseAngles = movingPart.localScale, movingPart.localPosition, movingPart.localEulerAngles
end

function HostStopBeat()
    if motionId == "S02" and motionBeat == "A" then restorePart() end
end

local function springHit(t, at, amplitude, frequency, damping)
    local age = t - at
    if age < 0 then return 0 end
    return amplitude * math.sin(age * frequency) * math.exp(-age * damping)
end

local function animateBeat()
    if not movingPart then return end
    local t = clock.time - motionStart
    if t > motionLength then
        restorePart()
        return
    end
    if motionId == "S02" then
        local age = t - 1.22
        if motionBeat == "A" then
            age = t - .225
            if age >= 0 then age = age % 1.125 end
        end
        local swell = age < 0 and 1 or .44 + .56 * math.min(1, age / .62)
        movingPart.localScale = V3(baseScale.x * swell, baseScale.y, baseScale.z * swell)
    elseif motionId == "S01" then
        local vibration = springHit(t, .10, .003, 38, 8) + springHit(t, .43, .003, 38, 8)
        if motionBeat == "B" then vibration = vibration + springHit(t, 1.13, .014, 38, 7) end
        movingPart.localScale = V3(baseScale.x, baseScale.y * (1 + vibration), baseScale.z)
    elseif motionId == "S03" or motionId == "S04" then
        local lift
        if motionId == "S03" then
            local rise = math.max(0, math.min(1, (t - .09) / .70))
            local settle = math.max(0, math.min(1, (motionLength - t) / .62))
            lift = (motionBeat == "A" and .14 or .19) * rise * settle
            if motionBeat == "B" then
                lift = lift + springHit(t, .76, .055, 32, 8) + springHit(t, 2.60, .035, 32, 9)
            end
        else
            lift = motionBeat == "A" and .022 * math.abs(math.sin(t*12))*math.exp(-t*3) or .11*math.sin(math.pi*t/2)
        end
        movingPart.localPosition = V3(basePosition.x,basePosition.y+lift,basePosition.z)
    elseif motionId == "S05" then
        local wobble = springHit(t, motionBeat == "A" and 0 or .13, 7, 44, 7)
        if motionBeat == "A" then wobble = wobble + springHit(t, .30, 7, 44, 7) end
        movingPart.localEulerAngles = V3(baseAngles.x,baseAngles.y,baseAngles.z+wobble)
    elseif motionId == "S06" then
        local turn = springHit(t, .15, .7, 23, 8) + springHit(t, .46, .7, 23, 8)
        if motionBeat == "B" then
            local open = math.max(0, math.min(1, (t - 1.0) / .22, (2 - t) / .42))
            turn = 8 * open
        end
        movingPart.localEulerAngles = V3(baseAngles.x,baseAngles.y+turn,baseAngles.z)
    end
end

function HostUpdate()
    animateWater()
    -- At water level the stock orbit can put its near plane below the quay.
    -- Keep a low side view while the local player is walking this route.
    if placed and localActor and localActor.isLocal then
        local camera = CS.DouyinCameraService
        local pitch = camera.GetPitch()
        if pitch and pitch < -4 then camera.SetPitch(-4) end
    end
    if bowBeam and bowAim then
        bowBeam.transform.rotation=CS.UnityEngine.Quaternion.Slerp(bowBeam.transform.rotation,bowAim,math.min(1,clock.deltaTime*6))
    end
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
    if crossing then
        if clock.time < arriveAt then return end
        land(crossing)
        crossing = nil
    end
    local p = frame:InverseTransformPoint(localActor.position)
    if recoverFromWater(p) then
        p = frame:InverseTransformPoint(localActor.position)
    end
    if UpdateRain then UpdateRain(p.z,region) end
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


-- Run from the repository root using nvim --headless -u NONE -i NONE -l <this file>.
-- Local regression for the real host/card Lua. Unity geometry, audio output, and touch need the preview.
local function vector(x,y,z) return {x=x,y=y,z=z} end
local timer = {time=0,realtimeSinceStartup=0}
local actor = {isLocal=true,position=vector(0,0,0),teleports=0}
function actor:Teleport(p,r) self.position,self.rotation,self.teleports=p,r,self.teleports+1 end
local frame = {Find=function() return nil end, rotation={}}
function frame:InverseTransformPoint(p) return p end
function frame:TransformPoint(p) return p end
function frame:TransformDirection(p) return p end
local nodes, clicks, played, cues = {},{},{},{}
local host,card = {},{}
local scope = {}
function scope:GetRuntimeHostRoot() return {transform=frame} end
function scope:GetScript() return host end
function scope:GetGameObjectByPath(path)
    if nodes[path] then return nodes[path] end
    local listener = {}
    function listener:AddListener(f) clicks[path]=f end
    function listener:RemoveListener() clicks[path]=nil end
    local node = {activeSelf=true,component={onClick=listener}}
    function node:GetComponent() return self.component end
    function node:SetActive(value) self.activeSelf=value end
    nodes[path]=node
    return node
end
local U = {Time=timer,Vector3=vector,Quaternion={LookRotation=function(v) return v end},UI={Text="text",Button="button"}}
local engine = {UnityEngine=U,DouyinActorService={GetLocalActor=function() return actor end},
    DouyinCameraService={GetPitch=function() return 0 end}}
local function loadBound(env,path)
    setmetatable(env,{__index=_G})
    env.CS,env.typeof = engine,function(v) return v end
    env.require=function(name)
        if name == "official.core.runtime_scope" then return {from=function() return scope end} end
        assert(name == "official.core.logger")
        return {create=function() return {warnOnce=function(_,_,m) error(m) end} end}
    end
    setfenv(assert(loadfile(path)),env)()
end
loadBound(host,"Game/Runtime/locations.lua")
loadBound(card,"Game/Card/RainCard.lua")
function host.PlayBeat(source,beat) table.insert(played,source..beat); host.HostBeat(source,beat); return 2 end
function host.PlayShoreCue(destination) table.insert(cues,destination); return 2 end
function host.SetMix() end
function host.StopBeat() end
host.HostStart(); card.Start()
local function tick(dt)
    timer.time=timer.time+dt
    timer.realtimeSinceStartup=timer.time
    host.HostUpdate(); card.Update()
end
local H,C,O = "walkHud/","cardPanelRoot/","cardPanelRoot/controls/"
local function choice(path,caption)
    local parent = path
    while parent do
        assert(not nodes[parent] or nodes[parent].activeSelf,"hidden control "..parent)
        parent=parent:match("^(.*)/[^/]+$")
    end
    if caption then
        local label=path.."/"..path:match("[^/]+$").."Label"
        assert(nodes[label].component.text == caption,nodes[label].component.text)
    end
    assert(clicks[path],path)()
end
local function walk(x,z,zone,h)
    actor.position=vector(x,h or 0,z)
    tick(.3)
    assert(host.GetZone()==zone,tostring(host.GetZone()).." != "..tostring(zone))
end
local function collect(beat)
    choice(H.."listenBtn")
    if beat=="B" then tick(2.25) end
    choice(H.."keepBtn")
end
local function order()
    local items, sealed = card.GetDraft()
    local keys={}
    for _,v in ipairs(items) do keys[#keys+1]=v.source..v.beat end
    return table.concat(keys,","), sealed
end
local function land(region,zone,x,z)
    assert(host.GetZone()=="sailing")
    local hops=actor.teleports
    assert(not host.BeginVoyage(region),"double sailing")
    tick(.8)
    assert(hops==actor.teleports and host.GetZone()=="sailing")
    tick(.65)
    assert(actor.teleports==hops+1 and host.GetVoyageState()==region and host.GetZone()==zone)
    assert(actor.position.x==x and actor.position.z==z)
end
local function homeViaLamp()
    choice(H.."keepBtn","暖灯返航")
    land("home","S07",0,9.7)
    assert(actor.rotation.z<0)
end
local function seal(expected)
    walk(-1.2,8,"desk")
    choice(H.."cardEntryBtn"); choice(O.."stampBtn","盖章寄出")
    tick(2.5); tick(2.5); tick(2.5)
    assert(select(2,order()) and order()==expected)
    assert(table.concat(played,",",#played-2)==expected)
end
tick(.3)
walk(-1.25,2.3,"S01"); collect("B")
walk(0,15,"bow"); choice(H.."listenBtn","← 听早市"); choice(H.."keepBtn","听暮路 →")
assert(table.concat(cues,",")=="market,dusk" and order()=="S01B")
choice(H.."listenBtn"); choice(H.."cardEntryBtn","靠岸 · 早市"); land("market","marketDock",-11,20.5)
walk(-12.8,25.4,"S03"); collect("A"); assert(order()=="S01B,S03A")
walk(-9.2,30.5,"S04"); choice(H.."listenBtn"); tick(2.25)
assert(played[#played]=="S04B")
walk(-11,20.5,"marketDock"); choice(H.."listenBtn","听暮路"); choice(H.."cardEntryBtn","靠岸 · 放学路")
land("dusk","duskDock",11,20.5)
walk(12.8,30.5,"S06",.65); collect("B")
local source,beat,start=host.GetShoreBeat()
assert(source=="S06" and beat=="B" and start==timer.time)
walk(11,20.5,"duskDock"); homeViaLamp(); seal("S01B,S03A,S06B")
choice(C.."paperWakeBtn"); choice(O.."stampBtn","再写一封")
assert(order()=="")
choice(H.."keepBtn","再去听听"); land("home","bow",0,15)
choice(H.."keepBtn"); choice(H.."cardEntryBtn"); land("dusk","duskDock",11,20.5)
walk(9.2,25.4,"S05",.14); collect("A")
walk(11,20.5,"duskDock"); homeViaLamp(); collect("A")
walk(1.42,5.5,"S02"); collect("B"); seal("S05A,S07A,S02B")
choice(C.."paperWakeBtn"); choice(C.."closeBtn")
choice(H.."listenBtn","合写一封"); choice(C.."slot1"); choice(O.."stampBtn")
walk(0,15,"bow"); choice(H.."listenBtn"); choice(H.."cardEntryBtn"); land("market","marketDock",-11,20.5)
walk(-9.2,30.5,"S04"); collect("A")
walk(-11,20.5,"marketDock"); homeViaLamp(); walk(-1.2,8,"desk")
choice(H.."cardEntryBtn"); choice(C.."slot1"); choice(O.."stampBtn")
choice(O.."swapBtn"); choice(C.."slot2"); choice(O.."stampBtn"); choice(O.."swapBtn","按章合寄")
tick(2.5); tick(2.5); tick(2.5)
assert(table.concat(played,",",#played-2)=="S05A,S04A,S07A")
assert(order()=="S05A,S07A,S02B" and select(2,order()))
card.OnDestroy(); assert(next(clicks)==nil)
print("PASS: both bow cues, preview and confirm, four shore sources, change bank, return, relaunch with empty card, two sealed endings and their playback, guest shore trip and co-signed card.")

-- Offline interaction regression. The real Unity renderer, audio and phone are tested separately.
local elapsed, zone, heard = 0, "S01", {}
local nodes, hooks = {}, {}
local host = {}
function host.PlayBeat(source,beat) heard[#heard+1]=source..beat; return 2 end
function host.StopBeat() end
function host.SetMix(rain, volume, ducked) host.mix={rain,volume,ducked} end
CS = {UnityEngine={Time={realtimeSinceStartup=0}, UI={Text="text",Button="button"}}}
typeof = function(value) return value end
local ready = false
local scope = {GetScript=function() return ready and host or nil end}
function scope:GetGameObjectByPath(path)
    if nodes[path] then return nodes[path] end
    local click = {}
    function click:AddListener(f) hooks[path]=f end
    function click:RemoveListener() hooks[path]=nil end
    local component = {onClick=click}
    local go = {activeSelf=true, component=component}
    function go:GetComponent() return component end
    function go:SetActive(value) self.activeSelf=value end
    nodes[path]=go
    return go
end
package.preload["official.core.runtime_scope"]=function() return {from=function() return scope end} end
package.preload["official.core.logger"]=function() return {create=function() return {warnOnce=function() end} end} end
dofile("RainStudy/Card/RainCard.lua")
local function tick(delta)
    elapsed=elapsed+delta
    CS.UnityEngine.Time.realtimeSinceStartup=elapsed
    Update()
end
local H,C,S="walkHud/","cardPanelRoot/","cardPanelRoot/controls/"
local function click(path)
    local prefix=""
    for part in path:gmatch("[^/]+") do
        prefix=prefix=="" and part or prefix.."/"..part
        if nodes[prefix] then assert(nodes[prefix].activeSelf,"hidden control "..prefix) end
    end
    assert(hooks[path],"unbound "..path)()
end
local function getOrder()
    local items,stamped=GetDraft()
    local order={}
    for _,item in ipairs(items) do order[#order+1]=item.source..item.beat end
    return table.concat(order,","),stamped
end
local function collect(source,beat)
    zone=source; tick(0.3); click(H.."listenBtn")
    if beat=="B" then tick(2.25) end
    click(H.."keepBtn")
end
Start(); tick(0.25)
ready=true; tick(0.25) -- Companion exists before its zone callback is ready.
host.GetZone=function() return zone end
tick(0.25)
assert(nodes[H.."walkCaption"].component.text:find("刚把窗关上"))
collect("S01","A"); collect("S01","A"); assert(getOrder()=="S01A")
collect("S01","B"); collect("S02","A"); assert(getOrder()=="S01A,S01B,S02A")
collect("S02","B"); click(C.."slot2"); click(S.."swapBtn"); assert(getOrder()=="S01A,S01B,S02A")
click(C.."closeBtn")
collect("S02","B"); click(C.."slot2"); assert(getOrder()=="S01A,S01B,S02A")
click(S.."stampBtn"); assert(getOrder()=="S01A,S02B,S02A")
click(S.."playBtn"); tick(2.4); tick(2.4); tick(2.4)
assert(table.concat(heard,",",#heard-2)=="S01A,S02B,S02A")
click(S.."swapBtn"); click(C.."slot1"); click(C.."slot3")
assert(getOrder()=="S02A,S02B,S01A")
click(S.."soundBtn"); click(C.."settings/rainBtn"); click(C.."settings/quieterBtn")
assert(not host.mix[1] and math.abs(host.mix[2]-0.6)<0.001)
click(C.."settings/captionBtn"); click(C.."closeBtn")
click(S.."stampBtn"); assert(select(2,getOrder())==false)
click(C.."closeBtn"); zone="desk"; tick(0.3); click(H.."cardEntryBtn"); click(S.."stampBtn")
assert(select(2,getOrder()))
assert(nodes[C.."slot1/slot1Basin"].activeSelf and not nodes[C.."slot2/slot2Basin"].activeSelf)
tick(2.4); assert(nodes[C.."slot2/slot2Basin"].activeSelf)
click(C.."closeBtn"); assert(nodes[C.."paperWakeBtn"].activeSelf)
click(C.."paperWakeBtn"); assert(nodes[C.."controls"].activeSelf)
click(C.."postmarkBtn"); tick(2.4); tick(2.4); tick(2.4)
assert(table.concat(heard,",",#heard-2)=="S02A,S02B,S01A")
assert(not nodes[C.."controls"].activeSelf)
click(C.."slot1"); assert(heard[#heard]=="S02A")
click(S.."stampBtn"); assert(getOrder()=="")
OnDestroy(); assert(next(hooks)==nil)
print("OK: draft, duplicate, both beats, audition before replace, two replay orders, settings, stamp at desk, progressive reveal, skip, paper tap, postmark replay, slot, new card, cleanup")

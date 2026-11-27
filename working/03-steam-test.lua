local time = {time=0}
CS = {UnityEngine={Time=time}}
self, Steam = {}, {}
local spout = {position={x=-9.44,y=1.32,z=30.5}}
local frame = {Find=function(_,path) assert(path=="ShoreRoute/SteamSpout"); return spout end}
local source, beat, began
local host = {
    GetStudyFrame=function() return frame end,
    GetShoreBeat=function() return source, beat, began end
}
local calls, plays, ready = 0, 0, true
package.preload["official.core.runtime_scope"] = function()
    return {from=function() return {GetScript=function(_,name) assert(name=="RainHost.lua"); return host end} end}
end
package.preload["official.effect.playback"] = function()
    return {Reason={NotReady="effect-not-ready"},spawn=function(owner,key,position,options)
        assert(owner==self and key==Steam and position==spout.position and options.parent==spout)
        calls=calls+1
        if ready then plays=plays+1; return {} end
        return nil,"effect-not-ready"
    end}
end
dofile("Game/ShoreRoute/Steam/ShoreSteam.lua")
Update()
source, beat, began = "S04", "A", 0
Update()
assert(calls==0)
beat, began, time.time="B",.4,.4
Update(); Update(); assert(plays==1)
time.time=2; Update(); assert(plays==1)
ready, began, time.time=false,2.3,2.3
Update(); Update(); assert(calls==2)
ready, time.time=true,2.42
Update(); Update(); assert(calls==3 and plays==2)
began, time.time=3,4
Update(); assert(calls==3)
print("Steam trigger checks passed")

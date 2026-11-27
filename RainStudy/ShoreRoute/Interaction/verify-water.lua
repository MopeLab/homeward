-- Exercise the real location script. The desktop driver separately tests the mesh and camera.
local clock={time=0,deltaTime=.08}
local function vec(x,y,z) return {x=x,y=y,z=z} end
local frame={Find=function() end,rotation={}}
function frame:InverseTransformPoint(p) return p end
function frame:TransformDirection(p) return p end
function frame:TransformPoint(p) return p end
local actor={isLocal=true,position=vec(0,0,0),rotation={}}
function actor:Teleport(p,r) self.position,self.rotation=p,r end
local scope={GetRuntimeHostRoot=function() return {transform=frame} end}
package.preload["official.core.runtime_scope"]=function() return {from=function() return scope end} end
CS={UnityEngine={Time=clock,Vector3=vec,Quaternion={LookRotation=function(v) return v end}},DouyinActorService={GetLocalActor=function() return actor end}}
dofile("RainStudy/Runtime/locations.lua")
local function tick(n)
    for _=1,n or 1 do clock.time=clock.time+.08;HostUpdate() end
end
local function stand(x,y,z,n) actor.position=vec(x,y,z);tick(n) end
local function sail(to) assert(BeginVoyage(to));tick(21) end
local function drop(x,y,z,safeX,safeZ)
    local n=GetWaterRecoveryCount()
    stand(x,y,z,5)
    assert(GetWaterRecoveryCount()==n+1, "missing or duplicate recovery")
    assert(math.abs(actor.position.x-safeX)<.01 and math.abs(actor.position.z-safeZ)<.01,"wrong berth")
end
HostStart();tick()
stand(1.8,0,1.4);drop(3.5,-.38,1.4,1.8,1.4)
stand(0,0,15.7);drop(1.6,0,15.7,0,15.7)
local n=GetWaterRecoveryCount()
stand(.7,1.1,15.8,5);stand(1.2,.7,15.8,4);stand(.5,.06,15.8,3)
assert(GetWaterRecoveryCount()==n,"jump intercept")
stand(0,.02,15);sail("market")
stand(-11,.015,17);drop(-13,0,17,-11,17)
stand(-11,0,20.5);sail("dusk")
stand(11,.015,17);drop(13,-.38,17,11,17)
n=GetWaterRecoveryCount()
for z=24,31,.1 do stand(11,(z-24)*.1,z,2) end
stand(11,1.56,30.2,5);stand(11,.62,30.2,2)
assert(GetWaterRecoveryCount()==n,"slope intercept")
stand(11,.62,30.2);drop(15,-.38,30.2,11,30.2)
assert(math.abs(actor.position.y-.75)<.01)
print("PASS: campus side, central deck, both berths, raised lane, low water floor, normal jump, slope and region transitions")

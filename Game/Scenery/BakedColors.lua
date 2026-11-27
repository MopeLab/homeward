---@displayName 檐下固定光照
local U = CS.UnityEngine
local changes = {}
-- The runtime importer flattens each single-mesh GLB to its Model root.
local expected = {walkway=true,campus=true,["old-eaves"]=true,desk=true}
local shoreReceivers = {
    MarketBank=true,DuskBank=true,HarborPier=true,MarketMasonry=true,DuskMasonry=true,
    FerryTimber=true,PierTimber=true,ShutterFrame=true,SteamerHearth=true,
    BicycleFrame=true,DoorFrame=true,FarShore=true,FarShoreRoofline=true,
    RiverSurface=true,RainRiverSurface=true
}
local props = {"_BaseTex","_BaseColor","_ColorPower","_UseVertexColor","_RimPower","_EmissionTex","_EmissionMask","_EmissionColor","_EmissionPower","_ORM","_Metallic","_Smoothness","_AOIntensity"}
local unsupported = 0
local riverMaterial
local riverTexture

local function adapt(original)
    if original == nil or original.shader.name ~= "Douyin/AI/PBR/EnvLit_AI" then return nil end
    for _, property in ipairs(props) do
        if not original:HasProperty(property) then return nil end
    end
    local color = original:GetTexture("_BaseTex")
    if color == nil then return nil end
    local m = U.Material(original)
    m:SetTexture("_EmissionTex",color)
    m:SetTextureScale("_EmissionTex",original:GetTextureScale("_BaseTex"))
    m:SetTextureOffset("_EmissionTex",original:GetTextureOffset("_BaseTex"))
    m:SetTexture("_EmissionMask",U.Texture2D.whiteTexture)
    m:SetColor("_EmissionColor",U.Color.white)
    m:SetFloat("_EmissionPower",1)
    m:EnableKeyword("_EMISSION")
    m:SetColor("_BaseColor",U.Color.black)
    m:SetFloat("_ColorPower",0)
    m:SetFloat("_UseVertexColor",0)
    m:SetFloat("_RimPower",0)
    m:SetTexture("_ORM",U.Texture2D.whiteTexture)
    m:SetFloat("_Metallic",1)
    m:SetFloat("_Smoothness",0)
    m:SetFloat("_AOIntensity",0)
    return m
end

function Start()
    local list = self.gameObject:GetComponentsInChildren(typeof(U.Renderer),true)
    for i=0,list.Length-1 do
        local r = list[i]
        local parent = r.transform.parent
        local isStaticModel = r.name == "Model" and parent and expected[parent.name]
        local isCampusPiece = (r.name == "CampusStructure" or r.name == "RoofSkin") and parent
            and parent.name == "Model" and parent.parent and parent.parent.name == "campus"
        local isShore = self.gameObject.name == "ShoreRoute" and
            (shoreReceivers[r.name] or (r.name == "Model" and parent and shoreReceivers[parent.name]))
        if isStaticModel or isCampusPiece or isShore then
            local original=r.sharedMaterials
            local changed=r.sharedMaterials
            local m=original.Length==1 and adapt(original[0]) or nil
            if m then
                if r.name=="RiverSurface" or r.name=="RainRiverSurface" or
                    (parent and parent.name=="RiverSurface") then
                    local texture=m:GetTexture("_BaseTex")
                    if MakeRiverDisplayTexture then
                        local ok,display=pcall(MakeRiverDisplayTexture)
                        if ok and display then
                            riverTexture=display
                            texture=display
                            m:SetTexture("_BaseTex",display)
                            m:SetTexture("_EmissionTex",display)
                        end
                    end
                    texture.wrapMode=U.TextureWrapMode.Repeat
                    texture.filterMode=U.FilterMode.Trilinear
                    texture.anisoLevel=4
                    m:SetTextureScale("_BaseTex",U.Vector2(.71,1.19))
                    m:SetFloat("_Metallic",0)
                    m:SetFloat("_ColorPower",.40)
                    m:SetColor("_BaseColor",U.Color(.36,.43,.45,1))
                    riverMaterial=m
                end
                changed[0]=m
                r.sharedMaterials=changed
                table.insert(changes,{r,original,m})
            else
                unsupported=unsupported+1
            end
        end
    end
end

function GetDisplayState() return #changes,unsupported end
function Update()
    if not riverMaterial then return end
    local t=U.Time.time
    riverMaterial:SetTextureOffset("_EmissionTex",U.Vector2((.009*t)%1,(.019*t)%1))
    riverMaterial:SetTextureOffset("_BaseTex",U.Vector2((-.013*t)%1,(.006*t)%1))
end
function OnDestroy()
    riverMaterial=nil
    for _,v in ipairs(changes) do
        if v[1] then v[1].sharedMaterials=v[2] end
        U.Object.Destroy(v[3])
    end
    changes={}
    if riverTexture then U.Object.Destroy(riverTexture); riverTexture=nil end
end

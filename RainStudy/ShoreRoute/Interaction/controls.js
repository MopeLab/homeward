const U=CS.UnityEngine;
const types = {rect:puer.$typeof(U.RectTransform), text:puer.$typeof(U.UI.Text), canvas:puer.$typeof(U.Canvas)};
const controls={}, labels={}, channels={}, coords={};
for(const name of ["listenBtn","keepBtn","cardEntryBtn","slot1","slot2","slot3","postmarkBtn","stampBtn","swapBtn","soundBtn","closeBtn","paperWakeBtn"]) {
  const active=U.GameObject.Find(name);
  // "keep" starts hidden before an audition. Its known real rect allows the two quick taps to land on beat A.
  const hidden=!active && name==="keepBtn" && U.GameObject.Find("walkHud");
  const go=active || (hidden && hidden.transform.Find("keepBtn").gameObject);
  if (!go) continue;
  const rect=go.GetComponent(types.rect), canvas=go.GetComponentInParent(types.canvas);
  // The sheet's centre is covered by slot 2. Touch its exposed lower-left corner to wake it.
  const x=name==="paperWakeBtn" ? rect.rect.xMin+rect.rect.width*.035 : rect.rect.center.x;
  const y=name==="paperWakeBtn" ? rect.rect.yMin+rect.rect.height*.12 : rect.rect.center.y;
  const mid=rect.TransformPoint(new U.Vector3(x,y,0));
  const at=U.RectTransformUtility.WorldToScreenPoint(canvas && canvas.renderMode!==0 ? canvas.worldCamera : null,mid);
  coords[name]=[at.x/U.Screen.width,1-at.y/U.Screen.height];
  if (active) controls[name]=coords[name];
}
for(const name of ["sourceLabel","walkCaption","feedbackLine","cardEntryBtnLabel","listenBtnLabel","keepBtnLabel","swapBtnLabel","stampBtnLabel","slot1Title","slot2Title","slot3Title","mailHeading","postmarkLabel"]) {
  const go=U.GameObject.Find(name);
  if (go) labels[name]=go.GetComponent(types.text).text;
}
for(const name of ["Card","ShoreCue","Market","Dusk","Rain"]) {
  const go=U.GameObject.Find("Homeward_"+name);
  if (!go) continue;
  const source=go.GetComponent(puer.$typeof(U.AudioSource));
  channels[name]={playing:source.isPlaying,clip:source.clip && source.clip.GetInstanceID(),gain:source.volume};
}
const marker=U.GameObject.Find("ShoreRoute").transform;
const p=marker.parent.InverseTransformPoint(CS.DouyinActorService.GetLocalActor().position);
const lamps={};
const beam=marker.Find("HarborBowLamp/TurningBowLight");
if (beam) {
  const d=beam.forward;
  lamps.forward=[d.x,d.y,d.z];
  for (const bank of ["MarketBoat","DuskBoat"]) {
    const glass=marker.Find(bank+"/BowGlass").GetComponent(puer.$typeof(U.Renderer));
    lamps[bank]=glass.sharedMaterial.GetFloat("_EmissionPower");
  }
}
return {frame:U.Time.frameCount,p:[p.x,p.y,p.z],controls,coords,labels,channels,lamps};

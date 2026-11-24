// Read the ordinary player state and the visible UI after real input.
const U = CS.UnityEngine;
const actor = CS.DouyinActorService.GetLocalActor();
const screen = [U.Screen.width, U.Screen.height];
const controls = {};
for (const name of ["listenBtn","keepBtn","cardEntryBtn","closeBtn","slot1","slot2","slot3","playBtn","swapBtn","stampBtn","soundBtn","rainBtn","captionBtn","quieterBtn","louderBtn","postmarkBtn"]) {
  const go = U.GameObject.Find(name);
  if (!go) continue;
  const rect = go.GetComponent(puer.$typeof(U.RectTransform));
  if (!rect) continue;
  const canvas = go.GetComponentInParent(puer.$typeof(U.Canvas));
  const point = rect.TransformPoint(new U.Vector3(rect.rect.center.x,rect.rect.center.y,0));
  const at = U.RectTransformUtility.WorldToScreenPoint(canvas && canvas.renderMode !== 0 ? canvas.worldCamera : null,point);
  controls[name] = [at.x/screen[0],1-at.y/screen[1]].map(v=>Math.round(v*10000)/10000);
}
const labels = {};
for (const name of ["sourceLabel","walkCaption","feedbackLine","slot1Title","slot2Title","slot3Title","postmarkLabel","keepBtnLabel","rainBtnLabel","captionBtnLabel","listenBtnLabel","cardEntryBtnLabel","mailHeading","swapBtnLabel","stampBtnLabel"]) {
  const go = U.GameObject.Find(name);
  const label = go && go.GetComponent(puer.$typeof(U.UI.Text));
  if (label) labels[name] = label.text;
}
const p = actor && actor.position;
const sources = U.Object.FindObjectsOfType(puer.$typeof(U.AudioSource));
const playing = [];
for (let i=0;i<sources.Length;i++) {
  const source = sources.get_Item(i);
  if (source.isPlaying && source.clip) playing.push([source.name,source.clip.name,source.volume]);
}
return {screen,position:p && [p.x,p.y,p.z],controls,labels,playing};

const U=CS.UnityEngine;
const type=x=>puer.$typeof(x);
const track=U.GameObject.Find("Homeward_Card").GetComponent(type(U.AudioSource));
const panel=U.GameObject.Find("cardPanelRoot").transform;
const feedback=panel.Find("feedbackLine").GetComponent(type(U.UI.Text));
const rows=[];
let previous="";
for(let frame=0;frame<500;frame++) {
  const clip=track.isPlaying && track.clip ? track.clip.GetInstanceID() : null;
  const signature=String(clip)+feedback.text;
  if(signature!==previous) {
    const artwork=[];
    for(let slot=1;slot<=3;slot++) {
      const root=panel.Find("slot"+slot);
      const visible=["Tin","Basin","Shutter","Steamer","Bell","Lock","Window"]
        .filter(a=>root.Find("slot"+slot+a)?.gameObject.activeInHierarchy);
      const symbol=root.Find("slot"+slot+"ShoreLabel");
      if(symbol && symbol.gameObject.activeInHierarchy) visible.push(symbol.GetComponent(type(U.UI.Text)).text);
      artwork.push(visible);
    }
    rows.push({time:U.Time.realtimeSinceStartup,clip,title:feedback.text,artwork});
    previous=signature;
  }
  if(!feedback.gameObject.activeInHierarchy && rows.length>1) break;
  await awaitFrames(1);
}
return rows;

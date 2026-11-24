const U=CS.UnityEngine;
const card=U.GameObject.Find("Homeward_Card").GetComponent(puer.$typeof(U.AudioSource));
const panel=U.GameObject.Find("cardPanelRoot");
const captions=panel.transform.Find("feedbackLine").GetComponent(puer.$typeof(U.UI.Text));
const samples=[];
let previous="";
for(let i=0;i<220;i++) {
  const id=card.isPlaying && card.clip ? card.clip.GetInstanceID() : null;
  const title=captions.text;
  const signature=String(id)+title;
  if(signature!==previous) {
    const artwork=[];
    for(let slot=1;slot<=3;slot++) {
      const prefix="slot"+slot+"/slot"+slot;
      artwork.push(["Tin","Basin","Window"].filter(art=>panel.transform.Find(prefix+art).gameObject.activeInHierarchy));
    }
    samples.push({time:U.Time.realtimeSinceStartup,clip:id,title,artwork});
    previous=signature;
  }
  if(!panel.transform.Find("feedbackLine").gameObject.activeInHierarchy && samples.length>1) break;
  await awaitFrames(2);
}
return samples;

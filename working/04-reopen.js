const U = CS.UnityEngine;
const type = value => puer.$typeof(value);
const samples = [];
let artworks = null;
const start = U.Time.realtimeSinceStartup;
do {
  const hud = U.GameObject.Find("walkHud");
  const card = U.GameObject.Find("Homeward_Card");
  if (hud && card) {
    if (!artworks) {
      const panel = hud.transform.parent.Find("cardPanelRoot");
      artworks = [1, 2, 3].flatMap(i => ["Tin","Basin","Shutter","Steamer","Bell","Lock","Window"].map(art => {
        const go = panel.Find("slot" + i + "/slot" + i + art).gameObject;
        const image = go.GetComponent(type(U.UI.Image));
        const raw = go.GetComponent(type(U.UI.RawImage));
        return [go.name, !!(image && image.sprite || raw && raw.texture)];
      }));
    }
    const audio = card.GetComponent(type(U.AudioSource));
    const subtitle = hud.transform.Find("walkCaption").GetComponent(type(U.UI.Text)).text;
    samples.push({subtitle, cursor: audio.timeSamples, playing: audio.isPlaying,
                  clip: audio.clip ? audio.clip.name : null, length: audio.clip ? audio.clip.length : 0});
  }
  await awaitFrames(3);
} while (U.Time.realtimeSinceStartup - start < 2.7);
return {artworks, samples};

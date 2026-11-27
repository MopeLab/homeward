const U = CS.UnityEngine;
const type = value => puer.$typeof(value);
const names = ["Card", "Rain", "Market", "Dusk", "ShoreCue"];
const channels = {};
for (const name of names) {
  const go = U.GameObject.Find("Homeward_" + name);
  if (go) channels[name] = go.GetComponent(type(U.AudioSource));
}
const arts = ["Tin", "Basin", "Shutter", "Steamer", "Bell", "Lock", "Window"];
const panel = U.GameObject.Find("slot1")?.transform.parent;
const targetName = PART;
const part = targetName ? U.GameObject.Find(targetName)?.transform : null;
const triple = point => [point.x, point.y, point.z];
const rows = [];
const start = U.Time.realtimeSinceStartup;
let nextSample = start;
do {
  const t = U.Time.realtimeSinceStartup;
  if (t < nextSample) { await awaitFrames(1); continue; }
  nextSample = t + .145;
  const states = {};
  for (const [name, audio] of Object.entries(channels)) {
    const clip = audio.clip;
    states[name] = {
      clip: clip ? clip.GetInstanceID() : null,
      name: clip ? clip.name : null,
      length: clip ? clip.length : 0,
      rate: clip ? clip.frequency : 0,
      cursor: audio.timeSamples,
      gain: audio.volume,
      playing: audio.isPlaying,
      loop: audio.loop,
    };
  }
  const hud = U.GameObject.Find("walkCaption");
  const feedback = panel?.Find("feedbackLine")?.gameObject;
  const read = go => go?.activeInHierarchy ? go.GetComponent(type(U.UI.Text)).text : "";
  const images = panel ? [1, 2, 3].map(i => {
    const slot = panel.Find("slot" + i);
    return arts.filter(art => slot.Find("slot" + i + art).gameObject.activeInHierarchy);
  }) : [];
  const steam = U.GameObject.Find("SteamSpout");
  const particles = steam ? steam.GetComponentsInChildren(type(U.ParticleSystem), true) : null;
  let particleCount = 0;
  for (let i = 0; particles && i < particles.Length; i++) particleCount += particles.get_Item(i).particleCount;
  rows.push({t, channels: states, caption: read(hud || feedback),
             images, particleCount, part: part ? [triple(part.localPosition),
                 triple(part.localEulerAngles), triple(part.localScale)] : null});
  if (SECONDS > 0) await awaitFrames(1);
} while (U.Time.realtimeSinceStartup < start + SECONDS);
return rows;

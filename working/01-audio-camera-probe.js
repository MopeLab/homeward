// Desktop runtime only. Start while stationary in a listening zone.
const U = CS.UnityEngine;
const type = x => puer.$typeof(x);
const find = n => U.GameObject.Find(n);
const channel = n => find("Homeward_" + n).GetComponent(type(U.AudioSource));
const channels = ["Card", "Rain", "Tin", "Basin"].map(channel);
const actor = CS.DouyinActorService.GetLocalActor();
const map = find("map-rainwalk");
const renderers = map.GetComponentsInChildren(type(U.MeshRenderer), false);
const button = find("listenBtn").GetComponent(type(U.UI.Button));
const source = find("sourceLabel").GetComponent(type(U.UI.Text)).text;
const observations = [], onsets = [], taps = [];
const lastClip = [], lastTime = [];
const startFrame = U.Time.frameCount;
const v = p => [p.x, p.y, p.z].map(n => +n.toFixed(4));
let maxGap = 0, lastFrame = startFrame, signature = "";
for (let step = 0; step < 340; step++) {
    const frame = U.Time.frameCount;
    maxGap = Math.max(maxGap, frame - lastFrame);
    lastFrame = frame;
    if ([5, 111, 218].includes(step)) {
        button.onClick.Invoke();
        taps.push(frame);
    }
    for (let i = 0; i < channels.length; i++) {
        const ch = channels[i];
        const clip = ch.isPlaying && ch.clip ? ch.clip.GetInstanceID() : null;
        const time = ch.time;
        if (clip !== null && (clip !== lastClip[i] || time + .05 < lastTime[i]))
            onsets.push({frame, channel: ch.name, clip, time});
        lastClip[i] = clip;
        lastTime[i] = time;
    }
    const camera = U.Camera.main;
    let visible = 0;
    for (let i = 0; i < renderers.Length; i++) {
        const r = renderers.get_Item(i);
        if (r.enabled && r.isVisible) visible++;
    }
    const state = {actor: v(actor.position), map: map.activeInHierarchy, visible,
        camera: camera ? {id: camera.GetInstanceID(), position: v(camera.transform.position),
            forward: v(camera.transform.forward), mask: camera.cullingMask,
            enabled: camera.enabled, near: camera.nearClipPlane, far: camera.farClipPlane,
            fov: camera.fieldOfView} : null};
    const next = JSON.stringify(state);
    if (next !== signature) observations.push({frame, state});
    signature = next;
    if (step < 339) await awaitFrames(1);
}
return {source, samples: 340, startFrame, endFrame: lastFrame, maxGap, taps, onsets, observations};

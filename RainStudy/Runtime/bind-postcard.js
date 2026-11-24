// Replace the unbound first UI proof with the final interactive layout.
await scene.nodes.remove({nodes:["n10"]});
const ui = await scene.assets.instantiateUI({parent:"n1",resource:"hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/xffusbt754fr9moj.glb"});
const audioParams = {
  "S01A": {
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/popweo53x1ohwecl.wav"
  },
  "S01B": {
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/tgcsxepr5w0m7rou.wav"
  },
  "S02A": {
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/ap7i6n8g120i5vma.wav"
  },
  "S02B": {
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/jb6db9pg6nlatksl.wav"
  },
  "S07A": {
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/a61e63ja6nf5e409.wav"
  },
  "S07B": {
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/wo52bpaz09kmpzh9.wav"
  },
  "RainBed": {
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/90r7nmq08vmdt45x.wav"
  },
  "FamilyVoice": {
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/jn7e4en8eslqvepx.wav"
  }
};
const audio = await scene.scripts.bind({nodes:[ui.root],script:"5ef17e0b-a118-4c30-ac36-1a2e7563b0c5",params:audioParams});
const card = await scene.scripts.bind({nodes:[ui.root],script:"09f664cf-75c7-4064-8ef5-576b619e1875"});
const gutter = await scene.scripts.bind({nodes:["n6"],script:"a28cb725-aa28-494e-9147-ce88849867c2",params:{GutterRain:{uri:"hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/4fyha4t0qfw44gbw.wprefab"}}});
const display = await scene.scripts.bind({nodes:["n11"],script:"adf88912-b803-4df4-9604-aefdce797cdc"});
return {ui,audio,card,gutter,display};

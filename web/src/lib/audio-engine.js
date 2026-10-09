const state={
  level:0,low:0,mid:0,high:0,transient:0,bell500:0,
  lowRaw:0,midRaw:0,highRaw:0,
  running:false,deviceId:"",sensitivity:1.6,source:"none",
  sampleRate:0,updatedAt:0
};
window.ELISA_AUDIO=state;

let ctx,analyser,source,stream,data,prevLevel=0,raf=0,mediaElement=null;
const mediaNodes=new WeakMap();
const audioBus=typeof BroadcastChannel!=="undefined"?new BroadcastChannel("elisa-audio"):null;
let lastBusPublish=0;
const avg=(arr,a,b)=>{let s=0,n=0;for(let i=a;i<=b&&i<arr.length;i++){s+=arr[i];n++}return n?s/n/255:0};
const clamp01=v=>Math.max(0,Math.min(1,v));
const smooth=(current,target,attack=.28,release=.09)=>current+(target-current)*(target>current?attack:release);

function publish(){
  state.updatedAt=performance.now();
  const detail={
    level:state.level,low:state.low,mid:state.mid,high:state.high,transient:state.transient,bell500:state.bell500,
    lowRaw:state.lowRaw,midRaw:state.midRaw,highRaw:state.highRaw,
    running:state.running,deviceId:state.deviceId,sensitivity:state.sensitivity,
    source:state.source,sampleRate:state.sampleRate,updatedAt:state.updatedAt
  };
  window.dispatchEvent(new CustomEvent("elisa-audio",{detail}));
  // Cross-window audio bus: /regia becomes the browser audio authority.
  // Throttled to ~30fps so Hydra/web receive the same LOW/MID/HIGH/HIT without flooding.
  const now=performance.now();
  if(audioBus&&now-lastBusPublish>32){audioBus.postMessage({type:"audio-frame",...detail});lastBusPublish=now}
  // Stable adapter for Hydra / other browser clients.
  window.ELISA_AUDIO.get=()=>({...state});
}

function loop(){
  if(!analyser||!ctx)return;
  analyser.getByteFrequencyData(data);
  const nyquist=ctx.sampleRate/2,hzPerBin=nyquist/data.length;
  const bin=hz=>Math.max(0,Math.min(data.length-1,Math.floor(hz/hzPerBin)));
  const sens=state.sensitivity;

  const levelRaw=clamp01(avg(data,bin(40),bin(12000))*sens);
  state.lowRaw=clamp01(avg(data,bin(40),bin(180))*sens);
  state.midRaw=clamp01(avg(data,bin(180),bin(2200))*sens);
  state.highRaw=clamp01(avg(data,bin(2200),bin(12000))*sens);

  state.level=smooth(state.level,levelRaw,.32,.10);
  state.low=smooth(state.low,state.lowRaw,.30,.075);
  state.mid=smooth(state.mid,state.midRaw,.25,.085);
  state.high=smooth(state.high,state.highRaw,.22,.10);
  // Narrow midrange bell detector centered around 500 Hz, independent of broad MID.
  const bellRaw=clamp01(avg(data,bin(420),bin(620))*sens*2.5);
  state.bell500=smooth(state.bell500,bellRaw,.48,.16);

  const rise=Math.max(0,levelRaw-prevLevel);
  const hit=rise>.045?clamp01(rise*12):0;
  state.transient=Math.max(hit,state.transient*.80);
  prevLevel=levelRaw;
  publish();
  raf=requestAnimationFrame(loop);
}

function setup(){
  analyser=ctx.createAnalyser();
  analyser.fftSize=2048;
  analyser.smoothingTimeConstant=.68;
  data=new Uint8Array(analyser.frequencyBinCount);
  state.sampleRate=ctx.sampleRate;
  loop();
}

export async function listAudioInputs(){
  const d=await navigator.mediaDevices.enumerateDevices();
  return d.filter(x=>x.kind==="audioinput");
}

export async function startAudio(deviceId=""){
  stopAudio();
  const audioConstraints={echoCancellation:false,noiseSuppression:false,autoGainControl:false};
  if(deviceId)audioConstraints.deviceId={exact:deviceId};
  stream=await navigator.mediaDevices.getUserMedia({audio:audioConstraints,video:false});
  ctx=new AudioContext();await ctx.resume();setup();
  source=ctx.createMediaStreamSource(stream);source.connect(analyser);
  state.running=true;state.deviceId=deviceId;state.source="input";publish();return state;
}

export async function startTrack(element){
  stopAudio();mediaElement=element;
  await element.play();
  ctx=new AudioContext();await ctx.resume();setup();
  const captured=element.captureStream?.()||element.mozCaptureStream?.();
  if(captured){
    stream=captured;source=ctx.createMediaStreamSource(captured);source.connect(analyser);
  }
  state.running=true;state.deviceId="";state.source="track";publish();
  return state;
}

export function stopAudio({keepContext=false}={}){
  if(raf)cancelAnimationFrame(raf);raf=0;
  if(stream)stream.getTracks().forEach(t=>t.stop());stream=null;
  if(mediaElement){mediaElement.pause();mediaElement=null}
  try{source?.disconnect()}catch{}
  try{analyser?.disconnect()}catch{}
  if(ctx&&!keepContext){ctx.close();ctx=null}
  analyser=null;source=null;data=null;
  state.running=false;state.source="none";state.sampleRate=0;
  state.level=state.low=state.mid=state.high=state.transient=state.bell500=0;
  state.lowRaw=state.midRaw=state.highRaw=0;prevLevel=0;publish();
}

export function setSensitivity(v){state.sensitivity=Math.max(.1,Math.min(6,Number(v)||1));publish()}

// Public contract: every visual layer reads this same state.
// WEB: window.ELISA_AUDIO.low / mid / high / transient
// HYDRA (same page/context): () => ELISA_AUDIO.low etc.
// TouchDesigner can later receive this exact state through the show-control bridge.
window.ELISA_AUDIO.get=()=>({...state});

const state={level:0,low:0,mid:0,high:0,transient:0,running:false,deviceId:"",sensitivity:1.6};
window.ELISA_AUDIO=state;
let ctx,analyser,source,stream,data,prevLevel=0,raf=0;

const avg=(arr,a,b)=>{let s=0,n=0;for(let i=a;i<=b&&i<arr.length;i++){s+=arr[i];n++}return n?s/n/255:0};

function loop(){
  analyser.getByteFrequencyData(data);
  const nyquist=ctx.sampleRate/2, hzPerBin=nyquist/data.length;
  const bin=(hz)=>Math.max(0,Math.min(data.length-1,Math.floor(hz/hzPerBin)));
  const rawLevel=avg(data,bin(40),bin(12000));
  const sens=state.sensitivity;
  state.level=Math.min(1,rawLevel*sens);
  state.low=Math.min(1,avg(data,bin(40),bin(180))*sens);
  state.mid=Math.min(1,avg(data,bin(180),bin(2200))*sens);
  state.high=Math.min(1,avg(data,bin(2200),bin(12000))*sens);
  const rise=Math.max(0,state.level-prevLevel);
  state.transient=Math.max(rise>0.055?Math.min(1,rise*10):0,state.transient*.82);
  prevLevel=state.level;
  window.dispatchEvent(new CustomEvent("elisa-audio",{detail:{...state}}));
  raf=requestAnimationFrame(loop);
}

export async function listAudioInputs(){
  const devices=await navigator.mediaDevices.enumerateDevices();
  return devices.filter(d=>d.kind==="audioinput");
}

export async function startAudio(deviceId=""){
  stopAudio();
  stream=await navigator.mediaDevices.getUserMedia({audio:deviceId?{deviceId:{exact:deviceId}}:{echoCancellation:false,noiseSuppression:false,autoGainControl:false},video:false});
  ctx=new AudioContext();
  await ctx.resume();
  analyser=ctx.createAnalyser();
  analyser.fftSize=2048;
  analyser.smoothingTimeConstant=.78;
  data=new Uint8Array(analyser.frequencyBinCount);
  source=ctx.createMediaStreamSource(stream);
  source.connect(analyser);
  state.running=true;
  state.deviceId=deviceId;
  loop();
  return state;
}

export function stopAudio(){
  if(raf)cancelAnimationFrame(raf);
  if(stream)stream.getTracks().forEach(t=>t.stop());
  if(ctx)ctx.close();
  state.running=false; state.level=state.low=state.mid=state.high=state.transient=0;
}

export function setSensitivity(v){state.sensitivity=Math.max(.1,Math.min(6,Number(v)||1));}

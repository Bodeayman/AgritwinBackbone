"""Demo web UI (moved verbatim from the original single-file app)."""

HTML_PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plant Diagnosis</title>
<style>
:root{--green:#1b7a3d;--green-d:#145c2e;--bg:#f2f6f2;--card:#fff;--muted:#6b7a6e}
*{box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:#223;margin:0}
header{background:linear-gradient(135deg,var(--green),#2ea15c);color:#fff;padding:28px 20px;text-align:center}
header h1{margin:0;font-size:1.8rem}
header p{margin:6px 0 0;opacity:.9}
main{max-width:1000px;margin:0 auto;padding:20px 15px 40px}
.steps{display:flex;gap:8px;margin:18px 0}
.step{flex:1;text-align:center;padding:10px;border-radius:10px;background:#e3ebe4;color:var(--muted);font-weight:600;font-size:.9rem}
.step.active{background:var(--green);color:#fff}
.card{background:var(--card);border-radius:14px;padding:18px;margin:14px 0;box-shadow:0 2px 10px rgba(0,0,0,.07)}
.card h3{margin:0 0 12px}
#drop{border:2px dashed #9dc3ab;border-radius:12px;padding:26px;text-align:center;color:var(--muted);cursor:pointer;transition:.2s}
#drop:hover,#drop.over{border-color:var(--green);background:#eef7f0;color:var(--green-d)}
#filePreview{max-height:120px;border-radius:8px;margin-top:10px;display:none}
.btn{background:var(--green);color:#fff;border:0;border-radius:10px;padding:12px 22px;font-size:1rem;font-weight:600;cursor:pointer;margin:6px 6px 0 0}
.btn:hover{background:var(--green-d)}
.btn:disabled{opacity:.6;cursor:wait}
.btn.ghost{background:#e3ebe4;color:var(--green-d)}
.btn.ghost:hover{background:#d3e0d5}
.layout{display:flex;gap:16px;flex-wrap:wrap}
#stageWrap{flex:1 1 420px}
#stage{position:relative;display:inline-block;max-width:100%;border-radius:10px;overflow:hidden}
#stage img{max-width:100%;display:block}
.box{position:absolute;border:3px solid #7CFC00;cursor:pointer;border-radius:4px}
.box:hover{background:rgba(124,252,0,.15)}
.box.sel{border-color:#ff3b30;box-shadow:0 0 0 2px #ff3b30}
.box span{position:absolute;top:-24px;left:-3px;background:#7CFC00;color:#063;font-size:12px;font-weight:700;padding:2px 7px;border-radius:6px;white-space:nowrap}
.box.sel span{background:#ff3b30;color:#fff}
#leafList{flex:1 1 220px;display:flex;flex-direction:column;gap:10px;max-height:480px;overflow-y:auto}
.leaf{display:flex;gap:10px;align-items:center;border:2px solid #e0e7e1;border-radius:10px;padding:8px;cursor:pointer;transition:.15s;background:#fff}
.leaf:hover{border-color:#9dc3ab}
.leaf.sel{border-color:#ff3b30;background:#fff5f4}
.leaf img{width:72px;height:72px;object-fit:cover;border-radius:8px}
.leaf b{font-size:.95rem}
.leaf small{color:var(--muted)}
#verdict{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
#verdict .disease{font-size:1.6rem;font-weight:800;color:var(--green-d)}
.badge{font-weight:800;padding:6px 14px;border-radius:20px;color:#fff}
.badge.hi{background:#1b7a3d}.badge.mid{background:#d9930d}.badge.lo{background:#c0392b}
.bars{margin-top:12px}
.barrow{display:grid;grid-template-columns:110px 1fr 52px;gap:8px;align-items:center;margin:6px 0;font-size:.9rem}
.barrow .track{background:#e7ede8;border-radius:6px;height:12px;overflow:hidden}
.barrow .fill{background:linear-gradient(90deg,#2ea15c,#1b7a3d);height:100%;border-radius:6px}
.barrow.top{font-weight:700}
.imgs{display:flex;gap:14px;flex-wrap:wrap;margin-top:12px}
.imgs figure{margin:0;flex:1 1 200px;text-align:center}
.imgs img{width:100%;max-width:280px;border-radius:10px;border:1px solid #dde5de}
.imgs figcaption{font-size:.85rem;color:var(--muted);margin-top:6px}
.hint{color:var(--muted);font-size:.9rem}
.sliders{display:flex;gap:22px;flex-wrap:wrap;margin-bottom:14px;align-items:end}
.sliders label{font-size:.9rem;display:flex;flex-direction:column;gap:6px;min-width:200px;flex:1}
.sliders input[type=range]{width:100%;accent-color:var(--green)}
.hidden{display:none!important}
footer{text-align:center;color:var(--muted);font-size:.8rem;padding:20px}
</style></head><body>
<header><h1>&#x1F33F; Plant Disease Diagnosis</h1>
<p>Segment leaves &rarr; pick the leaf of interest &rarr; get the diagnosis with visual explanation</p></header>
<main>
<div class="steps">
  <div class="step active" id="s1">1 &middot; Upload</div>
  <div class="step" id="s2">2 &middot; Select leaf</div>
  <div class="step" id="s3">3 &middot; Diagnosis</div>
</div>

<div class="card"><h3>Upload a photo</h3>
  <div id="drop">Drop an image here or click to browse
    <div><img id="filePreview"></div>
  </div>
  <input type="file" id="file" accept="image/*" class="hidden">
  <button class="btn" id="segBtn" onclick="segment()">Segment leaves</button>
</div>

<div class="card hidden" id="selectCard"><h3>Select the leaf of interest</h3>
  <div class="sliders">
    <label>Score thresh <b id="scoreVal">0.50</b>
      <input type="range" id="scoreSlider" min="0.05" max="0.95" step="0.05" value="0.5"></label>
    <label>Mask thresh <b id="maskVal">0.50</b>
      <input type="range" id="maskSlider" min="0.05" max="0.95" step="0.05" value="0.5"></label>
    <span class="hint" id="segHint"></span>
  </div>
  <div class="layout">
    <div id="stageWrap"><div id="stage"><img id="img"><div id="boxes"></div></div></div>
    <div id="leafList"></div>
  </div>
  <p class="hint" id="leafCount"></p>
  <button class="btn" id="diagBtn" onclick="classify()">Diagnose selected leaf</button>
  <button class="btn ghost hidden" id="wholeBtn" onclick="classifyWhole()">No leaves? Classify whole image</button>
</div>

<div class="card hidden" id="resultCard"><h3>Diagnosis</h3><div id="result"></div></div>
</main>
<footer>Mask R-CNN segmentation &middot; ResNet-50 classifier &middot; Grad-CAM explanation</footer>
<script>
let data=null, selected=-1;
const $=id=>document.getElementById(id);
function setStep(n){[1,2,3].forEach(i=>$('s'+i).classList.toggle('active',i<=n));}
$('drop').onclick=()=>$('file').click();
$('file').onchange=()=>{
  const f=$('file').files[0]; if(!f)return;
  $('filePreview').src=URL.createObjectURL(f); $('filePreview').style.display='block';
};
['dragover','dragleave','drop'].forEach(ev=>$('drop').addEventListener(ev,e=>{
  e.preventDefault(); $('drop').classList.toggle('over',ev==='dragover');
  if(ev==='drop'&&e.dataTransfer.files.length){
    $('file').files=e.dataTransfer.files;
    $('filePreview').src=URL.createObjectURL(e.dataTransfer.files[0]);
    $('filePreview').style.display='block';
  }
}));
async function segment(){
  const f=$('file').files[0];
  if(!f){alert('Choose an image first');return;}
  $('segBtn').disabled=true; $('segBtn').textContent='Segmenting...';
  try{
    const fd=new FormData(); fd.append('file',f);
    const st=parseFloat($('scoreSlider').value), mt=parseFloat($('maskSlider').value);
    const r=await fetch(`/api/segment?score_thresh=${st}&mask_thresh=${mt}`,{method:'POST',body:fd});
    data=await r.json();
    if(data.detail){alert(data.detail);return;}
    selected=-1;
    $('img').src='data:image/jpeg;base64,'+data.image;
    renderLeaves();
    $('selectCard').classList.remove('hidden');
    $('resultCard').classList.add('hidden');
    setStep(2);
    $('selectCard').scrollIntoView({behavior:'smooth'});
  }finally{$('segBtn').disabled=false;$('segBtn').textContent='Segment leaves';}
}
function renderLeaves(){
  const boxes=$('boxes'); boxes.innerHTML='';
  data.leaves.forEach(l=>{
    const [x1,y1,x2,y2]=l.bbox, W=data.width, H=data.height;
    const d=document.createElement('div');
    d.className='box'; d.id='box'+l.id;
    d.style.cssText=`left:${x1/W*100}%;top:${y1/H*100}%;width:${(x2-x1)/W*100}%;height:${(y2-y1)/H*100}%`;
    d.innerHTML=`<span>#${l.id} &middot; ${(l.score*100).toFixed(0)}%</span>`;
    d.onclick=()=>select(l.id);
    boxes.appendChild(d);
  });
  const list=$('leafList'); list.innerHTML='';
  data.leaves.forEach(l=>{
    const c=document.createElement('div');
    c.className='leaf'; c.id='leaf'+l.id;
    c.innerHTML=`<img src="data:image/jpeg;base64,${l.thumb}"><div><b>Leaf #${l.id}</b><br><small>seg score ${(l.score*100).toFixed(1)}%</small></div>`;
    c.onclick=()=>select(l.id); list.appendChild(c);
  });
  const n=data.leaves.length;
  $('leafCount').textContent=n?`Found ${n} leaf${n>1?'s':''} — click one to select it.`:'No leaves detected at these thresholds. Lower the sliders or classify the whole image.';
  $('diagBtn').classList.toggle('hidden',!n);
  $('wholeBtn').classList.toggle('hidden',!!n);
  if(n)select(Math.min(selected<0?0:selected,n-1)); else selected=-1;
}
async function resegment(){
  if(!data)return;
  const st=parseFloat($('scoreSlider').value), mt=parseFloat($('maskSlider').value);
  $('scoreVal').textContent=st.toFixed(2); $('maskVal').textContent=mt.toFixed(2);
  $('segHint').textContent='Re-segmenting...';
  try{
    const r=await fetch('/api/resegment',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({image_id:data.image_id,score_thresh:st,mask_thresh:mt})});
    const j=await r.json();
    if(j.detail){$('segHint').textContent='Error: '+j.detail;return;}
    data.leaves=j.leaves;
    renderLeaves();
    $('segHint').textContent='';
  }catch(e){$('segHint').textContent='Re-segment failed';}
}
$('scoreSlider').addEventListener('change',resegment);
$('maskSlider').addEventListener('change',resegment);
$('scoreSlider').addEventListener('input',e=>$('scoreVal').textContent=parseFloat(e.target.value).toFixed(2));
$('maskSlider').addEventListener('input',e=>$('maskVal').textContent=parseFloat(e.target.value).toFixed(2));
function select(id){
  selected=id;
  data.leaves.forEach(l=>{
    $('box'+l.id).classList.toggle('sel',l.id===id);
    $('leaf'+l.id).classList.toggle('sel',l.id===id);
  });
}
function classify(){ if(selected<0){alert('Select a leaf first');return;} runClassify(selected); }
function classifyWhole(){ runClassify(-1); }
async function runClassify(leaf_id){
  $('diagBtn').disabled=true; $('diagBtn').textContent='Diagnosing...';
  try{
    const r=await fetch('/api/classify',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({image_id:data.image_id,leaf_id})});
    const j=await r.json();
    if(j.detail){alert(j.detail);return;}
    const pct=j.confidence*100;
    const cls=pct>=70?'hi':pct>=40?'mid':'lo';
    const rows=Object.entries(j.probs).sort((a,b)=>b[1]-a[1])
      .map(([k,v],i)=>`<div class="barrow${i===0?' top':''}"><span>${k}</span><div class="track"><div class="fill" style="width:${(v*100).toFixed(1)}%"></div></div><span>${(v*100).toFixed(1)}%</span></div>`).join('');
    $('result').innerHTML=
      `<div id="verdict"><span class="disease">${leaf_id===-1?'Whole image':'Leaf #'+leaf_id} &rarr; ${j.disease}</span><span class="badge ${cls}">${pct.toFixed(1)}% confident</span></div>
       <div class="bars">${rows}</div>
       <div class="imgs">
         <figure><img src="data:image/jpeg;base64,${j.model_view}"><figcaption>What the model sees (224&times;224 input)</figcaption></figure>
         <figure><img src="data:image/jpeg;base64,${j.gradcam}"><figcaption>Grad-CAM: regions driving &ldquo;${j.disease}&rdquo; (red = strong)</figcaption></figure>
       </div>`;
    $('resultCard').classList.remove('hidden');
    setStep(3);
    $('resultCard').scrollIntoView({behavior:'smooth'});
  }finally{$('diagBtn').disabled=false;$('diagBtn').textContent='Diagnose selected leaf';}
}
</script></body></html>"""

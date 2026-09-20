"""Plant-diagnosis web app: segment leaves -> pick one -> classify + Grad-CAM.

    uvicorn app:app --reload

Segmenter:  experiments/exp-7/maskrcnn_best.pth  (Mask R-CNN, bg + leaf)
Classifier: experiments/exp-7/best_model.pt      (ResNet-50, 6 diseases)
Grad-CAM:   hooks on classifier.layer4 for the predicted class.
"""

import base64
import io
import uuid

import numpy as np
import torch
import torchvision
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from PIL import Image
from pydantic import BaseModel
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torchvision.transforms.functional import normalize, to_tensor

SEGMENTER_PATH = "experiments/exp-7/maskrcnn_best.pth"
CLASSIFIER_PATH = "experiments/exp-7/best_model.pt"
CLASSES = ["Anthracnose", "Black Spot", "Canker", "Greening", "Healthy", "Root Rot"]
SCORE_THRESH = 0.5
MASK_THRESH = 0.5
IMG_SIZE = 224
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI(title="Plant Diagnosis")
STORE: dict = {}  # image_id -> {"image": PIL, "leaves": [{"bbox","score","mask"}]}


# ---------------------------------------------------------------- models
def load_segmenter():
    m = maskrcnn_resnet50_fpn(weights=None)
    m.roi_heads.box_predictor = FastRCNNPredictor(
        m.roi_heads.box_predictor.cls_score.in_features, 2)
    m.roi_heads.mask_predictor = MaskRCNNPredictor(
        m.roi_heads.mask_predictor.conv5_mask.in_channels, 256, 2)
    m.load_state_dict(torch.load(SEGMENTER_PATH, map_location=DEVICE))
    return m.to(DEVICE).eval()


def load_classifier():
    m = torchvision.models.resnet50(weights=None)
    m.fc = torch.nn.Linear(m.fc.in_features, len(CLASSES))
    m.load_state_dict(torch.load(CLASSIFIER_PATH, map_location=DEVICE))
    return m.to(DEVICE).eval()


segmenter = load_segmenter()
classifier = load_classifier()


# ---------------------------------------------------------------- helpers
def encode_jpg(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def segment_leaves(img: Image.Image, score_thresh=SCORE_THRESH, mask_thresh=MASK_THRESH):
    """Return list of {bbox [x1,y1,x2,y2], score, mask (bool HxW)}."""
    with torch.no_grad():
        out = segmenter([to_tensor(img).to(DEVICE)])[0]
    keep = (out["scores"] >= score_thresh) & (out["labels"] == 1)
    boxes = out["boxes"][keep].cpu()
    scores = out["scores"][keep].cpu()
    masks = (out["masks"][keep, 0] > mask_thresh).cpu().numpy()
    w, h = img.size
    leaves = []
    for box, score, mask in zip(boxes, scores, masks):
        x1, y1, x2, y2 = [max(0, int(v)) for v in box.tolist()]
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1 or not mask.any():
            continue
        leaves.append({"bbox": [x1, y1, x2, y2],
                       "score": float(score), "mask": mask})
    leaves.sort(key=lambda l: l["score"], reverse=True)
    return leaves


def masked_crop(img: Image.Image, mask: np.ndarray | None, bbox: list | None):
    arr = np.array(img)
    if mask is not None:
        arr = arr * mask[:, :, None]
    if bbox is not None:
        x1, y1, x2, y2 = bbox
        arr = arr[y1:y2, x1:x2]
    return Image.fromarray(arr)


def classify_transform(img: Image.Image):
    """Longest side -> 224, pad to 224x224, ImageNet normalize (matches training).

    Returns (tensor, canvas) where canvas is the 224x224 PIL image the model sees.
    """
    w, h = img.size
    s = IMG_SIZE / max(w, h)
    img = img.resize((round(w * s), round(h * s)))
    canvas = Image.new("RGB", (IMG_SIZE, IMG_SIZE))
    canvas.paste(img, ((IMG_SIZE - img.width) // 2, (IMG_SIZE - img.height) // 2))
    return normalize(to_tensor(canvas), MEAN, STD), canvas


def _jet(x: np.ndarray) -> np.ndarray:
    """Jet colormap for a [0,1] array -> uint8 RGB (no extra deps)."""
    x = np.clip(x, 0, 1)
    r = np.clip(1.5 - np.abs(4 * x - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * x - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * x - 1), 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)


def gradcam_predict(x: torch.Tensor, canvas: Image.Image):
    """Single forward pass: softmax probs + Grad-CAM heatmap overlay on canvas.

    Returns (probs list, overlay PIL image 224x224).
    """
    feats, grads = {}, {}

    def _save_act(m, i, o):
        feats["a"] = o

    def _save_grad(m, gi, go):
        grads["g"] = go[0]

    fh = classifier.layer4.register_forward_hook(_save_act)
    bh = classifier.layer4.register_full_backward_hook(_save_grad)
    try:
        classifier.zero_grad()
        logits = classifier(x.unsqueeze(0).to(DEVICE))
        probs = torch.softmax(logits, 1)[0]
        best = int(probs.argmax())
        logits[0, best].backward()
    finally:
        fh.remove()
        bh.remove()
    A = feats["a"][0].detach()   # C,h,w
    G = grads["g"][0].detach()   # C,h,w
    cam = (G.mean(dim=(1, 2))[:, None, None] * A).sum(0).clamp(min=0)
    cam = cam / (cam.max() + 1e-8)
    heat = np.array(Image.fromarray((cam.cpu().numpy() * 255).astype(np.uint8))
                    .resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)) / 255.0
    base = np.array(canvas).astype(np.float32)
    overlay = Image.fromarray(
        (0.55 * base + 0.45 * _jet(heat).astype(np.float32)).clip(0, 255).astype(np.uint8))
    return probs.cpu().tolist(), overlay


def thumb(img: Image.Image, mask, bbox, size=256):
    crop = masked_crop(img, mask, bbox)
    crop.thumbnail((size, size))
    return encode_jpg(crop)


def predict_disease(crop: Image.Image):
    """Classify one leaf crop (or whole image).

    Returns (disease, confidence, probs dict, model_view PIL, gradcam PIL).
    """
    x, canvas = classify_transform(crop)
    with torch.enable_grad():
        probs, overlay = gradcam_predict(x, canvas)
    best = int(np.argmax(probs))
    return (CLASSES[best], round(probs[best], 4),
            {c: round(p, 4) for c, p in zip(CLASSES, probs)},
            canvas, overlay)


def diagnose_photo(img, leaf_id: int = 0,
                   score_thresh: float = SCORE_THRESH,
                   mask_thresh: float = MASK_THRESH):
    """Full pipeline in one call: photo -> leaves + disease + Grad-CAM.

    Args:
        img: PIL image, raw image bytes, or file path.
        leaf_id: which detected leaf to diagnose (0 = highest score);
                 -1 = skip selection, classify the whole image.
        score_thresh / mask_thresh: segmenter thresholds.

    Returns dict with:
        leaves: [{bbox, score, mask}], leaf_id, bbox (or None),
        disease, confidence, probs, model_view (PIL), gradcam (PIL).
    """
    if isinstance(img, (bytes, bytearray)):
        img = Image.open(io.BytesIO(img)).convert("RGB")
    elif isinstance(img, str):
        img = Image.open(img).convert("RGB")
    score_thresh, mask_thresh = _clamp_thresh(score_thresh, mask_thresh)
    leaves = segment_leaves(img, score_thresh, mask_thresh)
    if leaf_id == -1:
        crop, bbox = img, None
    else:
        if not leaves:
            raise ValueError("No leaves detected; use leaf_id=-1 for whole image")
        if not 0 <= leaf_id < len(leaves):
            raise ValueError(f"Invalid leaf_id {leaf_id} ({len(leaves)} leaves found)")
        crop = masked_crop(img, leaves[leaf_id]["mask"], leaves[leaf_id]["bbox"])
        bbox = leaves[leaf_id]["bbox"]
    disease, confidence, probs, canvas, overlay = predict_disease(crop)
    return {"leaves": leaves, "leaf_id": leaf_id, "bbox": bbox,
            "disease": disease, "confidence": confidence, "probs": probs,
            "model_view": canvas, "gradcam": overlay}


# ---------------------------------------------------------------- routes
@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_PAGE


@app.post("/api/segment")
async def api_segment(file: UploadFile = File(...),
                      score_thresh: float = SCORE_THRESH,
                      mask_thresh: float = MASK_THRESH):
    try:
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image file")
    score_thresh, mask_thresh = _clamp_thresh(score_thresh, mask_thresh)
    leaves = segment_leaves(img, score_thresh, mask_thresh)
    image_id = uuid.uuid4().hex
    STORE[image_id] = {"image": img, "leaves": leaves}
    return {
        "image_id": image_id,
        "width": img.width, "height": img.height,
        "image": encode_jpg(img),
        "score_thresh": score_thresh, "mask_thresh": mask_thresh,
        "leaves": serialize_leaves(img, leaves),
    }


def _clamp_thresh(score_thresh: float, mask_thresh: float):
    return (min(1.0, max(0.0, score_thresh)),
            min(1.0, max(0.0, mask_thresh)))


def serialize_leaves(img, leaves):
    return [
        {"id": i, "bbox": l["bbox"], "score": round(l["score"], 3),
         "thumb": thumb(img, l["mask"], l["bbox"])}
        for i, l in enumerate(leaves)
    ]


class ResegmentRequest(BaseModel):
    image_id: str
    score_thresh: float = SCORE_THRESH
    mask_thresh: float = MASK_THRESH


@app.post("/api/resegment")
def api_resegment(req: ResegmentRequest):
    """Re-run segmentation on the stored upload with new thresholds."""
    entry = STORE.get(req.image_id)
    if entry is None:
        raise HTTPException(404, "Image expired, upload again")
    score_thresh, mask_thresh = _clamp_thresh(req.score_thresh, req.mask_thresh)
    leaves = segment_leaves(entry["image"], score_thresh, mask_thresh)
    entry["leaves"] = leaves
    return {
        "image_id": req.image_id,
        "score_thresh": score_thresh, "mask_thresh": mask_thresh,
        "leaves": serialize_leaves(entry["image"], leaves),
    }


class ClassifyRequest(BaseModel):
    image_id: str
    leaf_id: int = -1  # -1 = whole image


@app.post("/api/classify")
def api_classify(req: ClassifyRequest):
    entry = STORE.get(req.image_id)
    if entry is None:
        raise HTTPException(404, "Image expired, upload again")
    img, leaves = entry["image"], entry["leaves"]
    if req.leaf_id == -1:
        crop = img
    else:
        if not 0 <= req.leaf_id < len(leaves):
            raise HTTPException(400, "Invalid leaf_id")
        crop = masked_crop(img, leaves[req.leaf_id]["mask"],
                           leaves[req.leaf_id]["bbox"])
    disease, confidence, probs, canvas, overlay = predict_disease(crop)
    return {
        "disease": disease,
        "confidence": confidence,
        "probs": probs,
        "model_view": encode_jpg(canvas),
        "gradcam": encode_jpg(overlay),
    }


@app.post("/api/diagnose")
async def api_diagnose(file: UploadFile = File(...), leaf_id: int = 0,
                       score_thresh: float = SCORE_THRESH,
                       mask_thresh: float = MASK_THRESH):
    """One-shot: photo in -> leaves + disease + Grad-CAM out."""
    try:
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image file")
    try:
        out = diagnose_photo(img, leaf_id, score_thresh, mask_thresh)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "disease": out["disease"],
        "confidence": out["confidence"],
        "probs": out["probs"],
        "leaf_id": out["leaf_id"],
        "bbox": out["bbox"],
        "leaves": serialize_leaves(img, out["leaves"]),
        "model_view": encode_jpg(out["model_view"]),
        "gradcam": encode_jpg(out["gradcam"]),
    }


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

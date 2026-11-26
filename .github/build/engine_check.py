# © 2026 Enrico Migliorati. All rights reserved.
"""Check of a local engine on a clean machine (GitHub Actions, Mac with an Apple chip): installs what engine.json lists, downloads the
engine code, and checks that the runner loads it (imports, stand-ins, image reader, surface grid, photo preparation).
With an HF_TOKEN in the environment it also builds a real model from a test picture. Usage: python engine_check.py engines/sf3d"""
import json
import os
import subprocess
import sys
import urllib.request
import zipfile

eng = os.path.abspath(sys.argv[1])
spec = json.load(open(os.path.join(eng, "engine.json")))
work = os.path.abspath("engine-check")
os.makedirs(work, exist_ok=True)


def fail(msg):
    print("::error::" + msg.replace("\n", " ")[:900], flush=True)
    sys.exit(1)


def pip(*pk):
    return subprocess.call([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--prefer-binary", *pk])


for st in spec.get("steps", []):
    if not any(pip(*pk) == 0 for pk in (st.get("alternatives") or [st.get("pkgs", [])])):
        fail("installation failed: " + st.get("label", ""))
print("::notice::libraries installed", flush=True)

src = os.path.join(work, "src")
zp = os.path.join(work, "src.zip")
urllib.request.urlretrieve(spec["source"]["url"], zp)
with zipfile.ZipFile(zp) as z:
    for name in z.namelist():
        parts = name.split("/", 1)
        if len(parts) < 2 or not parts[1]:
            continue
        t = os.path.join(src, parts[1])
        if name.endswith("/"):
            os.makedirs(t, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(t), exist_ok=True)
            with z.open(name) as fi, open(t, "wb") as fo:
                fo.write(fi.read())

code = r'''
import importlib.util, os, sys, json
eng, src, work = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, src)
spec = importlib.util.spec_from_file_location("runner", os.path.join(eng, "runner.py"))
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
r.install_shims()
import torch
import sf3d.system as system
from sf3d.models.tokenizers.dinov2 import Dinov2Model
from transformers.models.dinov2.configuration_dinov2 import Dinov2Config
m = Dinov2Model(Dinov2Config(**r.DINO_LARGE))
n = sum(p.numel() for p in m.parameters())
print("::notice::image reader built: %.0f M parameters" % (n / 1e6), flush=True)
assert 280e6 < n < 330e6, n
from sf3d.models.isosurface import MarchingTetrahedraHelper
h = MarchingTetrahedraHelper(160, os.path.join(src, "load", "tets", "160_tets.npz"))
print("::notice::surface grid: %d points" % h.grid_vertices.shape[0], flush=True)
from PIL import Image, ImageDraw
im = Image.new("RGB", (800, 600), "white"); d = ImageDraw.Draw(im)
d.ellipse((250, 150, 550, 500), fill=(120, 120, 120)); d.rectangle((380, 60, 420, 160), fill=(100, 100, 100))
p = os.path.join(work, "test.png"); im.save(p)
out = r.prepare_photo(p, False, work)
assert out.size == (512, 512) and out.mode == "RGBA", (out.size, out.mode)
a = out.getchannel("A"); print("::notice::photo prepared, subject pixels: %d" % sum(1 for v in a.getdata() if v > 128), flush=True)
out2 = r.prepare_photo(p, True, work)
print("::notice::background removal works", flush=True)
print("device:", "mps" if torch.backends.mps.is_available() else "cpu", "ram GB:", round(r.ram_gb(), 1), flush=True)
'''
rc = subprocess.call([sys.executable, "-c", code, eng, src, work])
if rc != 0:
    fail("the runner does not load the engine code (exit %d)" % rc)

if os.environ.get("HF_TOKEN"):
    w = os.path.join(work, "weights")
    from huggingface_hub import hf_hub_download
    for f in spec["weights"]["files"]:
        hf_hub_download(spec["weights"]["hf_repo"], f, local_dir=w)
    out = os.path.join(work, "result.obj")
    rc = subprocess.call([sys.executable, os.path.join(eng, spec["runner"]), "--input", os.path.join(work, "test.png"),
                          "--output", out, "--src", src, "--weights", w, "--work", work, "--remove_bg", "0"])
    if rc != 0 or not os.path.exists(out):
        fail("the engine did not build the model (exit %d)" % rc)
    import trimesh
    m = trimesh.load(out)
    print("::notice::model built: %d faces, watertight %s" % (len(m.faces), m.is_watertight), flush=True)
else:
    print("::notice::no HF_TOKEN: the real model was not built", flush=True)
print("ENGINE CHECK PASSED", flush=True)

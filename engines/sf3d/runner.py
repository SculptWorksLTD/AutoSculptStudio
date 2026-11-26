# AutoSculpt Studio - (c) 2026 Enrico Migliorati. All rights reserved.
import argparse
import json
import os
import sys
import time
import types

def say(kind, *parts, **values):
    line = ' '.join([kind, *[str(p) for p in parts]])
    if values:
        line += '\t' + json.dumps(values)
    print('\n' + line, flush=True)

def watch_parent():
    import threading
    parent = os.getppid()

    def run():
        while True:
            time.sleep(2)
            if os.getppid() != parent:
                os._exit(1)
    threading.Thread(target=run, daemon=True).start()
watch_parent()
DINO_LARGE = dict(hidden_size=1024, num_hidden_layers=24, num_attention_heads=16, mlp_ratio=4, patch_size=14, image_size=518, num_channels=3, hidden_act='gelu', layer_norm_eps=1e-06, qkv_bias=True, layerscale_value=1.0, drop_path_rate=0.0, use_swiglu_ffn=False, hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0)

def install_shims():

    def stub(name, **attrs):
        try:
            m = sys.modules.get(name) or __import__(name)
            if all((hasattr(m, k) for k in attrs)) and getattr(m, '__file__', None):
                return
        except Exception:
            pass
        mod = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(mod, k, v)
        sys.modules[name] = mod

    class Unused:

        def __init__(self, *a, **k):
            pass

        def __getattr__(self, name):
            raise RuntimeError('texture step not available in this engine')
    stub('texture_baker', TextureBaker=Unused)
    stub('uv_unwrapper', Unwrapper=Unused)
    stub('gpytoolbox')
    stub('pynanoinstantmeshes')
    stub('open_clip')
    import torch.nn as nn

    class NoEstimator(nn.Module):

        def __init__(self, cfg=None):
            super().__init__()

        def forward(self, *a, **k):
            return {}
    mod = types.ModuleType('as_noestimator')
    mod.NoEstimator = NoEstimator
    sys.modules['as_noestimator'] = mod

def ram_gb():
    try:
        if sys.platform == 'darwin':
            import subprocess
            return int(subprocess.check_output(['sysctl', '-n', 'hw.memsize']).strip()) / 2 ** 30
        return os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 2 ** 30
    except Exception:
        return 0

def prepare_photo(path, remove_bg, work, ratio=0.85):
    import numpy as np
    from PIL import Image
    img = Image.open(path)
    img.load()
    if max(img.size) > 2000:
        img.thumbnail((2000, 2000))
    if img.mode == 'RGBA' and np.asarray(img)[:, :, 3].min() < 250:
        rgba = img
    elif remove_bg:
        say('PROGRESS', '0.06', 'Removing the background (the first time it downloads a small model)')
        import rembg
        try:
            session = rembg.new_session('isnet-general-use')
        except Exception:
            session = rembg.new_session()
        rgba = rembg.remove(img.convert('RGB'), session=session)
    else:
        rgb = np.asarray(img.convert('RGB')).astype(np.float32)
        a = np.clip((765 - rgb.sum(axis=2)) / 30.0, 0, 1)
        rgba = Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), 'RGBA')
    arr = np.asarray(rgba.convert('RGBA')).astype(np.float32) / 255.0
    alpha = arr[:, :, 3]
    mask = alpha > 0.5
    if mask.sum() < 50:
        raise RuntimeError('The subject was not found in the photo: try a photo with a plain background')
    try:
        from scipy import ndimage
        lab, n = ndimage.label(mask)
        if n > 1:
            sizes = np.bincount(lab.ravel())
            sizes[0] = 0
            keep = sizes >= max(200, sizes.max() * 0.02)
            mask = keep[lab]
            alpha = alpha * mask
        filled = ndimage.binary_fill_holes(mask)
        small = filled & ~mask
        lab2, n2 = ndimage.label(small)
        if n2:
            sizes = np.bincount(lab2.ravel())
            sizes[0] = 0
            fill = (sizes <= max(64, mask.sum() * 0.004))[lab2] & small
            mask = mask | fill
            alpha = np.where(fill, 1.0, alpha)
    except Exception:
        pass
    rows, cols = np.where(mask)
    y0, y1, x0, x1 = (rows.min(), rows.max() + 1, cols.min(), cols.max() + 1)
    crop = arr[y0:y1, x0:x1].copy()
    crop[:, :, 3] = alpha[y0:y1, x0:x1]
    h, w = crop.shape[:2]
    side = int(max(h, w) / ratio)
    canvas = np.zeros((side, side, 4), dtype=np.float32)
    oy, ox = ((side - h) // 2, (side - w) // 2)
    canvas[oy:oy + h, ox:ox + w] = crop
    out = Image.fromarray((canvas * 255).astype(np.uint8), 'RGBA').resize((512, 512), Image.LANCZOS)
    if work:
        try:
            out.save(os.path.join(work, 'prepared_input.png'))
        except Exception:
            pass
    return out

def load_model(weights, device):
    from omegaconf import OmegaConf
    from safetensors.torch import load_file
    import sf3d.models.tokenizers.dinov2 as dino
    from transformers.models.dinov2.configuration_dinov2 import Dinov2Config
    dino.Dinov2Model.from_pretrained = classmethod(lambda cls, *a, **k: cls(Dinov2Config(**DINO_LARGE)))
    from sf3d.system import SF3D
    cfg = OmegaConf.load(os.path.join(weights, 'config.yaml'))
    OmegaConf.resolve(cfg)
    cfg.image_estimator_cls = 'as_noestimator.NoEstimator'
    cfg.global_estimator_cls = 'as_noestimator.NoEstimator'
    model = SF3D(cfg)
    state = load_file(os.path.join(weights, 'model.safetensors'))
    state = {k: v for k, v in state.items() if not k.startswith(('image_estimator.', 'global_estimator.'))}
    missing, unexpected = model.load_state_dict(state, strict=False)
    params = {n for n, _ in model.named_parameters()}
    missing = [k for k in missing if k in params and (not k.startswith(('image_estimator.', 'global_estimator.')))]
    if missing:
        raise RuntimeError('The model file does not match the engine (missing: %s)' % ', '.join(missing[:4]))
    del state
    model.eval()
    return model.to(device)

def shape(model, image, device):
    import torch
    from sf3d.utils import create_intrinsic_from_fov_deg, default_cond_c2w
    with torch.no_grad():
        mask, rgb = model.prepare_image(image)
        c2w = default_cond_c2w(model.cfg.default_distance).to(device)
        intr, intr_n = create_intrinsic_from_fov_deg(model.cfg.default_fovy_deg, model.cfg.cond_image_size, model.cfg.cond_image_size)
        batch = {'rgb_cond': model.image_processor(rgb, model.cfg.cond_image_size), 'mask_cond': model.image_processor(mask, model.cfg.cond_image_size), 'c2w_cond': c2w.view(1, 1, 4, 4), 'intrinsic_cond': intr.to(device).view(1, 1, 3, 3), 'intrinsic_normed_cond': intr_n.to(device).view(1, 1, 3, 3)}
        codes, _ = model.get_scene_codes(batch)
        if device == 'mps':
            torch.mps.synchronize()
        say('PROGRESS', '0.75', 'Building the surface')
        mesh = model.triplane_to_meshes(codes)[0]
        return (mesh.v_pos.detach().float().cpu().numpy(), mesh.t_pos_idx.detach().cpu().numpy())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--src', required=True, help='folder with the Stable Fast 3D code')
    ap.add_argument('--weights', required=True, help='folder with config.yaml and model.safetensors')
    ap.add_argument('--device', default='auto')
    ap.add_argument('--remove_bg', default='1')
    ap.add_argument('--work', default=None)
    a = ap.parse_args()
    os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK', '1')
    sys.path.insert(0, a.src)
    say('PROGRESS', '0.02', 'Starting the engine')
    import numpy as np
    import torch
    install_shims()
    if a.device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() and ram_gb() >= 30 else 'cpu'
    else:
        device = a.device
    os.environ['SF3D_USE_CPU'] = '1' if device == 'cpu' else '0'
    image = prepare_photo(a.input, a.remove_bg == '1', a.work)
    say('PROGRESS', '0.15', 'Loading the reconstruction model')
    t0 = time.time()

    def run(dev):
        model = load_model(a.weights, dev)
        say('PROGRESS', '0.35', {'mps': 'Rebuilding the shape (Apple chip)', 'cuda': 'Rebuilding the shape (NVIDIA graphics card)'}.get(dev, 'Rebuilding the shape (processor)'))
        return shape(model, image, dev)
    try:
        verts, faces = run(device)
    except Exception:
        if device == 'cpu':
            raise
        say('PROGRESS', '0.35', 'The graphics chip does not support a step, continuing on the processor')
        os.environ['SF3D_USE_CPU'] = '1'
        verts, faces = run('cpu')
    if verts is None or len(faces) == 0:
        raise RuntimeError('The model produced no surface: try another photo')
    say('PROGRESS', '0.92', 'Cleaning and orienting the model')
    import trimesh
    mesh = trimesh.Trimesh(np.asarray(verts, dtype=np.float32), np.asarray(faces), process=True)
    try:
        parts = mesh.split(only_watertight=False)
        if len(parts) > 1:
            mesh = max(parts, key=lambda m: len(m.faces))
    except Exception:
        pass
    for fix in (lambda: mesh.update_faces(mesh.nondegenerate_faces()), lambda: mesh.update_faces(mesh.unique_faces()), mesh.remove_unreferenced_vertices, lambda: trimesh.repair.fill_holes(mesh), lambda: trimesh.repair.fix_normals(mesh)):
        try:
            fix()
        except Exception:
            pass
    try:
        if mesh.volume < 0:
            mesh.invert()
    except Exception:
        pass
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    mesh.export(a.output)
    say('PROGRESS', '1', 'Done in {s} seconds', s=round(time.time() - t0))
    say('RESULT', a.output)
if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        import traceback
        traceback.print_exc()
        say('ERROR', str(exc).replace('\n', ' ')[:400])
        sys.exit(1)

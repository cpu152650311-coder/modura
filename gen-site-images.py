#!/usr/bin/env python3
"""Generate site images via GPT Image 2 API. Supports text-to-image and image-to-image."""
import requests, base64, json, argparse, sys, time, io, os
from pathlib import Path
from urllib.parse import urlparse

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

GENERATIONS_URL = "https://api.inferera.com/v1/images/generations"
EDITS_URL = "https://api.inferera.com/v1/images/edits"

def is_url(path):
    try:
        return urlparse(str(path)).scheme in ("http", "https")
    except Exception:
        return False

def load_reference_image(reference, base_url=None):
    ref_str = str(reference).strip()
    if not ref_str:
        raise ValueError("Reference field is empty")
    if is_url(ref_str):
        print(f"  Downloading reference: {ref_str[:120]}...")
        resp = requests.get(ref_str, timeout=30)
        resp.raise_for_status()
        print(f"  Downloaded: {len(resp.content):,} bytes")
        return resp.content
    ref_path = Path(ref_str)
    if ref_path.is_absolute() and ref_path.exists():
        print(f"  Reading reference: {ref_path}")
        return ref_path.read_bytes()
    if base_url and not is_url(ref_str):
        full_url = base_url.rstrip("/") + "/" + ref_str.lstrip("/")
        if is_url(full_url):
            print(f"  Downloading reference: {full_url[:120]}...")
            resp = requests.get(full_url, timeout=30)
            resp.raise_for_status()
            print(f"  Downloaded: {len(resp.content):,} bytes")
            return resp.content
    if ref_path.exists():
        print(f"  Reading reference: {ref_path.resolve()}")
        return ref_path.read_bytes()
    raise FileNotFoundError(f"Cannot load reference: {reference}")

def generate_text_to_image(prompt, api_key):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "gpt-image-2", "prompt": prompt, "size": "1024x1024", "quality": "low"}
    resp = requests.post(GENERATIONS_URL, headers=headers, json=payload, timeout=90)
    if resp.status_code != 200:
        raise RuntimeError(f"API error {resp.status_code}: {resp.text[:500]}")
    data = resp.json()["data"][0]
    if "url" in data:
        return requests.get(data["url"], timeout=30).content
    elif "b64_json" in data:
        return base64.b64decode(data["b64_json"])
    raise ValueError(f"No image in response: {list(data.keys())}")

def generate_image_to_image(prompt, reference_bytes, api_key):
    ref_b64 = base64.b64encode(reference_bytes).decode("utf-8")
    data_uri = f"data:image/webp;base64,{ref_b64}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "images": [{"image_url": data_uri}],
        "size": "1024x1024",
        "quality": "low",
    }
    resp = requests.post(EDITS_URL, headers=headers, json=payload, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"Edits API error {resp.status_code}: {resp.text[:500]}")
    data = resp.json()["data"][0]
    if "url" in data:
        return requests.get(data["url"], timeout=30).content
    elif "b64_json" in data:
        return base64.b64decode(data["b64_json"])
    raise ValueError(f"No image in response: {list(data.keys())}")

def generate_image(entry, api_key, base_url=None):
    prompt = entry["prompt"]
    reference = entry.get("reference")
    if reference:
        print("  Mode: image-to-image")
        ref_bytes = load_reference_image(reference, base_url)
        if len(ref_bytes) > 5_000_000:
            print(f"  Warning: reference >5MB ({len(ref_bytes):,} bytes)")
        return generate_image_to_image(prompt, ref_bytes, api_key), "reference-to-image"
    else:
        print("  Mode: text-to-image")
        return generate_text_to_image(prompt, api_key), "text-to-image"

def save_as_webp(raw_bytes, output_path, quality=85):
    output_path = Path(output_path)
    if HAS_PIL:
        try:
            img = Image.open(io.BytesIO(raw_bytes))
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
            img = img.convert("RGB")
            img.save(output_path, "WEBP", quality=quality)
            return output_path
        except Exception:
            pass
    output_path.write_bytes(raw_bytes)
    return output_path

def load_manifest(path):
    if path and Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_manifest(manifest, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def load_api_key(cli_key=None):
    if cli_key:
        return cli_key
    if os.environ.get("AIHUBMIX_API_KEY"):
        return os.environ["AIHUBMIX_API_KEY"]
    for search_dir in [Path("."), Path(__file__).parent.parent]:
        env_file = search_dir / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("AIHUBMIX_API_KEY="):
                        return line.split("=", 1)[1].strip()
    return None

def main():
    parser = argparse.ArgumentParser(description="Generate site images via GPT Image 2")
    parser.add_argument("--prompts", required=True, help="Path to image-strategy.json")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--manifest", default="image-manifest.json", help="Manifest path")
    parser.add_argument("--api-key", help="API key (or set AIHUBMIX_API_KEY env)")
    parser.add_argument("--start-from", type=int, default=0, help="Resume from index")
    parser.add_argument("--force", action="store_true", help="Force regenerate")
    parser.add_argument("--limit", type=int, default=0,
                       help="Generate only first N images (0=all). For Phase 2 sample generation.")
    parser.add_argument('--quality', default='low', choices=['low'],
                       help='QUALITY IS LOCKED TO LOW. medium/high BLOCKED to prevent cost spikes.')
    args = parser.parse_args()

    # ═══════════════════════════════════════════════════════════════
    # QUALITY GUARD — only "low" permitted. $0.006/image.
    # ═══════════════════════════════════════════════════════════════
    if args.quality != 'low':
        print("=" * 60)
        print("⛔ QUALITY BLOCKED: --quality={}".format(args.quality))
        print("   Only 'low' ($0.006/image) is permitted.")
        print("=" * 60)
        sys.exit(1)

    api_key = load_api_key(args.api_key)
    if not api_key:
        print("ERROR: No API key. Set AIHUBMIX_API_KEY or use --api-key")
        sys.exit(1)

    prompts_path = Path(args.prompts)
    if not prompts_path.exists():
        print(f"ERROR: {args.prompts} not found")
        sys.exit(1)

    with open(prompts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    images = data.get("images", [])
    meta = data.get("meta", {})
    style_prefix = meta.get("stylePrefix", "")
    reference_base_url = meta.get("referenceBaseUrl")

    if not images:
        print("ERROR: No images in array")
        sys.exit(1)

    print(f"Images: {len(images)}  Start: {args.start_from}  Limit: {args.limit if args.limit else 'all'}  Output: {args.out}")
    if style_prefix:
        print(f"Style prefix: {style_prefix[:100]}...")
    if reference_base_url:
        print(f"Reference base URL: {reference_base_url}")
    print("=" * 60)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(args.manifest)
    success = 0
    generated = 0  # count of actually generated (not skipped) images
    failed_entries = []

    for i, img in enumerate(images):
        if i < args.start_from:
            continue

        # Check limit (counts only generated, not skipped)
        if args.limit and generated >= args.limit:
            print(f"Limit reached ({args.limit} generated). Stopping.")
            break

        img_id = img["id"]
        output_path = out_dir / f"{img_id}.webp"

        if not args.force and output_path.exists() and img_id in manifest:
            src = manifest[img_id].get("source", "?")
            print(f"[{i+1}/{len(images)}] SKIP {img_id} (source={src})")
            success += 1
            continue

        print(f"[{i+1}/{len(images)}] {img_id}  role={img.get('role','?')}  page={img.get('page','?')}")

        try:
            full_prompt = img["prompt"].strip()
            if style_prefix:
                full_prompt = f"{full_prompt}. {style_prefix}"
            if len(full_prompt) > 4000:
                full_prompt = full_prompt[:4000]

            preview = full_prompt[:150] + "..." if len(full_prompt) > 150 else full_prompt
            print(f"  Prompt: {preview}")

            entry = dict(img)
            entry["prompt"] = full_prompt

            raw_bytes, source = generate_image(entry, api_key, reference_base_url)
            save_as_webp(raw_bytes, output_path)

            fsize = output_path.stat().st_size
            manifest[img_id] = {
                "id": img_id, "file": f"{img_id}.webp",
                "role": img["role"], "page": img["page"],
                "display": img.get("display", "default"),
                "size_bytes": fsize, "source": source,
            }
            save_manifest(manifest, args.manifest)
            print(f"  => OK ({fsize:,} bytes, {source})")
            success += 1
            generated += 1

        except Exception as e:
            print(f"  => FAIL: {e}")
            failed_entries.append({"index": i, "id": img_id, "error": str(e)})
            time.sleep(2)

        if i < len(images) - 1:
            time.sleep(1)

    print("=" * 60)
    print(f"Done. Success: {success}  Failed: {len(failed_entries)}")
    print(f"Manifest: {args.manifest}")
    if failed_entries:
        fail_path = out_dir / "failed-images.json"
        with open(fail_path, "w", encoding="utf-8") as f:
            json.dump(failed_entries, f, indent=2, ensure_ascii=False)
        print(f"Failed: {fail_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()

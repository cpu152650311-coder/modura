#!/usr/bin/env python3
"""
Generate favicon assets from a logo image (via GPT Image 2 text-to-image).
Automatically removes background with AI (rembg) for transparent logo output.
Outputs: favicon.ico, apple-touch-icon.png, logo-512.png, logo-192.png, logo-transparent.png

Usage:
  python gen-favicon.py --prompt "minimalist abstract logo for a LED lighting brand, no text" --out ./generated
  python gen-favicon.py --source ./generated/logo.webp --out ./generated
"""
import requests, base64, argparse, sys, io, os
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("ERROR: Pillow required. pip install Pillow")
    sys.exit(1)

try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False
    print("WARNING: rembg not installed. Logo will have solid background.")
    print("  Install: pip install rembg")

GENERATIONS_URL = "https://api.inferera.com/v1/images/generations"


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


def generate_logo(prompt, api_key):
    """Generate a logo image via GPT Image 2 text-to-image."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "size": "1024x1024",
        "quality": "low",
    }
    resp = requests.post(GENERATIONS_URL, headers=headers, json=payload, timeout=90)
    if resp.status_code != 200:
        raise RuntimeError(f"API error {resp.status_code}: {resp.text[:500]}")
    data = resp.json()["data"][0]
    if "url" in data:
        return requests.get(data["url"], timeout=30).content
    elif "b64_json" in data:
        return base64.b64decode(data["b64_json"])
    raise ValueError(f"No image in response: {list(data.keys())}")


def remove_background(source_bytes):
    """Use AI (rembg) to remove background and return RGBA bytes."""
    if not HAS_REMBG:
        print("  Skipping background removal (rembg not installed)")
        return source_bytes

    print("  Removing background with AI (rembg)...")
    input_img = Image.open(io.BytesIO(source_bytes))
    if input_img.mode != "RGBA":
        input_img = input_img.convert("RGBA")

    output = remove(input_img)
    buf = io.BytesIO()
    output.save(buf, format="PNG")
    result = buf.getvalue()
    print(f"  Background removed: {len(source_bytes):,} → {len(result):,} bytes")
    return result


def generate_favicons(source_bytes, out_dir):
    """Generate all favicon sizes from a transparent source image."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(io.BytesIO(source_bytes))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")

    # Ensure RGBA for transparency preservation
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    assets = {
        "favicon.ico": [(16, 16), (32, 32)],
        "apple-touch-icon.png": (180, 180),
        "icon-192.png": (192, 192),
        "icon-512.png": (512, 512),
    }

    results = {}
    for filename, sizes in assets.items():
        if filename == "favicon.ico":
            ico_path = out_dir / filename
            # Create separate resized images for each ICO size
            img_16 = img.resize((16, 16), Image.LANCZOS)
            img_32 = img.resize((32, 32), Image.LANCZOS)
            img_16.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32)])
            results[filename] = ico_path.stat().st_size
        elif isinstance(sizes, tuple):
            out_path = out_dir / filename
            resized = img.resize(sizes, Image.LANCZOS)
            resized.save(out_path, "PNG")
            results[filename] = out_path.stat().st_size

    return results


def main():
    parser = argparse.ArgumentParser(description="Generate favicon assets from a logo image")
    parser.add_argument("--prompt", help="Text prompt to generate a logo via GPT Image 2")
    parser.add_argument("--source", help="Path to existing logo image (skip generation)")
    parser.add_argument("--out", default="./generated", help="Output directory")
    parser.add_argument("--api-key", help="API key (or set AIHUBMIX_API_KEY env)")
    parser.add_argument("--no-remove-bg", action="store_true",
                       help="Skip AI background removal (keep original background)")
    args = parser.parse_args()

    if not args.prompt and not args.source:
        print("ERROR: Specify --prompt (to generate a logo) or --source (to use existing image)")
        sys.exit(1)

    api_key = load_api_key(args.api_key)
    if not api_key:
        print("ERROR: No API key. Set AIHUBMIX_API_KEY or use --api-key")
        sys.exit(1)

    if args.source:
        source_path = Path(args.source)
        if not source_path.exists():
            print(f"ERROR: {args.source} not found")
            sys.exit(1)
        source_bytes = source_path.read_bytes()
        print(f"Using existing logo: {args.source} ({len(source_bytes):,} bytes)")
    else:
        # Prompt should instruct white/contrast background for clean removal
        enhanced_prompt = f"{args.prompt}, isolated on pure white background, no shadows, clean edges"
        print(f"Generating logo: {enhanced_prompt[:120]}...")
        source_bytes = generate_logo(enhanced_prompt, api_key)
        # Save raw logo
        logo_raw_path = Path(args.out) / "logo-raw.webp"
        logo_raw_path.parent.mkdir(parents=True, exist_ok=True)
        logo_raw_path.write_bytes(source_bytes)
        print(f"Raw logo saved: {logo_raw_path} ({len(source_bytes):,} bytes)")

    # AI background removal
    if not args.no_remove_bg:
        source_bytes = remove_background(source_bytes)
        # Save transparent logo
        logo_transparent_path = Path(args.out) / "logo-transparent.png"
        logo_transparent_path.write_bytes(source_bytes)
        print(f"Transparent logo saved: {logo_transparent_path}")

    print("Generating favicon assets...")
    results = generate_favicons(source_bytes, args.out)
    for name, size in results.items():
        print(f"  {name}: {size:,} bytes")

    # HTML snippet
    print("\n<!-- Add to <head> -->")
    print('<link rel="icon" type="image/x-icon" href="/generated/favicon.ico">')
    print('<link rel="apple-touch-icon" sizes="180x180" href="/generated/apple-touch-icon.png">')
    print('<link rel="icon" type="image/png" sizes="192x192" href="/generated/icon-192.png">')
    print('<link rel="icon" type="image/png" sizes="512x512" href="/generated/icon-512.png">')
    print("Done.")


if __name__ == "__main__":
    main()

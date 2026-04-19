"""
build.py — static site builder for 예금하기 좋은 날
Run: python build.py
"""

import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
DIST = ROOT / "dist"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_SRC = ROOT / "assets"
ASSETS_DST = DIST / "assets"
DATA_DIR = ROOT / "data"

SITE_URL = "https://example.github.io"  # update to real Pages URL when known

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> list:
    """Return parsed JSON list, or empty list if file is missing/invalid."""
    if not path.exists():
        return []
    try:
        with path.open(encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return payload.get("items", [])
    except (json.JSONDecodeError, OSError):
        pass
    return []


def kst_now() -> str:
    """Current time formatted as 'YYYY-MM-DD HH:MM KST'."""
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d %H:%M KST")


def render(env: Environment, template_name: str, out_path: Path, **ctx) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmpl = env.get_template(template_name)
    out_path.write_text(tmpl.render(**ctx), encoding="utf-8")
    print(f"  rendered  {out_path.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build() -> None:
    print("=== build start ===")

    # 1. Clean & recreate dist
    if DIST.exists():
        for item in DIST.iterdir():
            if item.name == ".gitkeep":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    DIST.mkdir(exist_ok=True)

    # 2. Load data
    cma_items = load_json(DATA_DIR / "cma.json")
    deposit_items = load_json(DATA_DIR / "deposit.json")
    parking_items = load_json(DATA_DIR / "parking.json")
    etf_items = load_json(DATA_DIR / "etf.json")
    updated_at = kst_now()
    print(
        f"  data      cma={len(cma_items)} rows, deposit={len(deposit_items)} rows, "
        f"parking={len(parking_items)} rows, etf={len(etf_items)} rows"
    )

    # 3. Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
    )

    # 4. Render pages
    render(
        env, "index.html.j2", DIST / "index.html",
        updated_at=updated_at,
        cma_items=cma_items,
        deposit_items=deposit_items,
    )

    render(
        env, "cma.html.j2", DIST / "cma" / "index.html",
        updated_at=updated_at,
        cma_items=cma_items,
    )

    render(
        env, "parking.html.j2", DIST / "parking" / "index.html",
        updated_at=updated_at,
        parking_items=parking_items,
    )

    render(
        env, "etf.html.j2", DIST / "etf" / "index.html",
        updated_at=updated_at,
        etf_items=etf_items,
    )

    render(
        env, "deposit.html.j2", DIST / "deposit" / "index.html",
        updated_at=updated_at,
        deposit_items=deposit_items,
    )

    # 5. sitemap.xml
    pages = ["", "cma/", "parking/", "etf/", "deposit/"]
    sitemap_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    today = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")
    for slug in pages:
        sitemap_lines.append(
            f"  <url><loc>{SITE_URL}/{slug}</loc><lastmod>{today}</lastmod></url>"
        )
    sitemap_lines.append("</urlset>")
    sitemap_path = DIST / "sitemap.xml"
    sitemap_path.write_text("\n".join(sitemap_lines), encoding="utf-8")
    print(f"  rendered  {sitemap_path.relative_to(ROOT)}")

    # 6. robots.txt
    robots_path = DIST / "robots.txt"
    robots_path.write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )
    print(f"  rendered  {robots_path.relative_to(ROOT)}")

    # 7. Copy assets
    if ASSETS_SRC.exists():
        shutil.copytree(ASSETS_SRC, ASSETS_DST, dirs_exist_ok=True)
        print(f"  copied    assets/ → dist/assets/")

    # 8. Summary
    dist_files = list(DIST.rglob("*"))
    file_count = sum(1 for f in dist_files if f.is_file())
    print(f"\n=== build complete: {file_count} files in dist/ ===")


if __name__ == "__main__":
    build()

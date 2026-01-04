from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Iterable, List, Tuple

import cv2
import numpy as np


OPACITIES = [0.20, 0.35, 0.50, 0.65, 0.80]


@dataclass(frozen=True)
class PreviewAsset:
    label: str
    path: str


def encode_png(image: np.ndarray) -> str:
    success, encoded = cv2.imencode(".png", image)
    if not success:
        raise ValueError("Failed to encode PNG")
    return base64.b64encode(encoded.tobytes()).decode("utf-8")


def build_opacity_panels(image_png: str, overlay_png: str) -> str:
    panels: List[str] = []
    for opacity in OPACITIES:
        panels.append(
            f"""
        <div class=\"panel\">
          <div class=\"panel-title\">Opacity {opacity:.2f}</div>
          <div class=\"stack\">
            <img src=\"data:image/png;base64,{image_png}\" style=\"opacity: {opacity:.2f};\" />
            <img src=\"data:image/png;base64,{overlay_png}\" />
          </div>
        </div>
        """
        )
    return "".join(panels)


def build_debug_section(debug_images: Iterable[Tuple[str, str]]) -> str:
    items = list(debug_images)
    if not items:
        return ""
    debug_items = "".join(
        f"""
        <div class=\"debug-item\">
          <div class=\"panel-title\">{label}</div>
          <img src=\"data:image/png;base64,{data}\" />
        </div>
        """
        for label, data in items
    )
    return f"""
    <div class=\"debug\">
      <h2>Debug views</h2>
      <div class=\"debug-grid\">
        {debug_items}
      </div>
    </div>
    """


def build_asset_list(assets: Iterable[PreviewAsset]) -> str:
    items = list(assets)
    if not items:
        return ""
    rows = "".join(
        f"<tr><td>{asset.label}</td><td><code>{asset.path}</code></td></tr>" for asset in items
    )
    return f"""
    <div class=\"assets\">
      <h2>Build assets</h2>
      <table>
        <thead><tr><th>Label</th><th>Path</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """


def build_parameters_section(parameters: dict) -> str:
    if not parameters:
        return ""
    rows = "".join(
        f"<tr><td>{key}</td><td><code>{value}</code></td></tr>" for key, value in parameters.items()
    )
    return f"""
    <div class=\"parameters\">
      <h2>Parameters</h2>
      <table>
        <thead><tr><th>Key</th><th>Value</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """


def wrap_html(title: str, panels: str, assets: str, parameters: str, debug: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      font-family: "Inter", system-ui, sans-serif;
      background: #f5f5f7;
      color: #1d1d1f;
    }}
    header {{
      padding: 20px 24px 8px;
    }}
    .grid {{
      display: grid;
      gap: 20px;
      padding: 12px 24px 24px;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    }}
    .panel {{
      background: white;
      border-radius: 12px;
      padding: 12px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }}
    .panel-title {{
      font-size: 13px;
      margin-bottom: 8px;
      color: #555;
    }}
    .stack {{
      position: relative;
      width: 100%;
    }}
    .stack img {{
      width: 100%;
      display: block;
    }}
    .stack img + img {{
      position: absolute;
      left: 0;
      top: 0;
    }}
    .debug, .assets, .parameters {{
      padding: 0 24px 24px;
    }}
    .debug-grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }}
    .debug-item img {{
      width: 100%;
      border-radius: 8px;
      background: white;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid #eee;
      text-align: left;
      font-size: 13px;
    }}
    th {{
      background: #f0f0f5;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p>Overlay preview sweep with varying background opacity.</p>
  </header>
  <section class=\"grid\">
    {panels}
  </section>
  {assets}
  {parameters}
  {debug}
</body>
</html>
"""

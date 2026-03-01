"""
Mermaid Diagram Renderer -- Convert Mermaid syntax to SVG/PNG files.

Requires: @mermaid-js/mermaid-cli (npm install -g @mermaid-js/mermaid-cli)

Usage:
    from tools.mermaid_renderer import render_mermaid
    svg_path = render_mermaid("flowchart TD\\n    A-->B", "my_diagram", fmt="svg")
"""

import json
import subprocess
import shutil
import tempfile
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / ".tmp" / "diagrams"


def _find_mmdc() -> str:
    """Locate the mmdc binary."""
    path = shutil.which("mmdc")
    if path:
        return path
    npm_global = subprocess.run(
        ["npm", "root", "-g"], capture_output=True, text=True
    )
    if npm_global.returncode == 0:
        candidate = Path(npm_global.stdout.strip()).parent / "bin" / "mmdc"
        if candidate.exists():
            return str(candidate)
    raise FileNotFoundError(
        "mmdc not found. Install with: npm install -g @mermaid-js/mermaid-cli"
    )


def render_mermaid(
    mermaid_code: str,
    filename: str = "diagram",
    fmt: str = "svg",
    output_dir: str = None,
    theme: str = "default",
    background: str = "white",
    width: int = None,
    height: int = None,
) -> str:
    """
    Render Mermaid diagram code to an image file.

    Args:
        mermaid_code: Mermaid diagram syntax (e.g. "flowchart TD\\n    A-->B")
        filename: Output filename without extension
        fmt: Output format - "svg", "png", or "pdf"
        output_dir: Directory for output (defaults to .tmp/diagrams/)
        theme: Mermaid theme - "default", "dark", "forest", "neutral"
        background: Background color (e.g. "white", "transparent")
        width: Width in pixels (PNG only)
        height: Height in pixels (PNG only)

    Returns:
        Absolute path to the generated file.
    """
    mmdc = _find_mmdc()

    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{filename}.{fmt}"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as tmp:
        tmp.write(mermaid_code)
        tmp_path = tmp.name

    config = {"theme": theme}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as cfg:
        json.dump(config, cfg)
        cfg_path = cfg.name

    try:
        cmd = [
            mmdc,
            "-i", tmp_path,
            "-o", str(output_path),
            "-b", background,
            "-c", cfg_path,
        ]
        if width and fmt == "png":
            cmd.extend(["-w", str(width)])
        if height and fmt == "png":
            cmd.extend(["-H", str(height)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            raise RuntimeError(f"mmdc failed: {result.stderr}")

        if not output_path.exists():
            raise FileNotFoundError(f"Output not created: {output_path}")

        return str(output_path.resolve())
    finally:
        Path(tmp_path).unlink(missing_ok=True)
        Path(cfg_path).unlink(missing_ok=True)


def render_flowchart(nodes: list, edges: list, filename: str = "flowchart", **kwargs) -> str:
    """
    Render a flowchart from structured data.

    Args:
        nodes: List of dicts with "id" and "label" keys
        edges: List of dicts with "from", "to", and optional "label" keys
        filename: Output filename
        **kwargs: Passed to render_mermaid()
    """
    lines = ["flowchart TD"]
    for node in nodes:
        nid = node["id"].replace(" ", "_")
        label = node.get("label", node["id"])
        lines.append(f"    {nid}[\"{label}\"]")
    for edge in edges:
        src = edge["from"].replace(" ", "_")
        dst = edge["to"].replace(" ", "_")
        label = edge.get("label")
        if label:
            lines.append(f"    {src} -->|\"{label}\"| {dst}")
        else:
            lines.append(f"    {src} --> {dst}")
    return render_mermaid("\n".join(lines), filename, **kwargs)


def render_system_diagram(systems: list, filename: str = "system_overview", **kwargs) -> str:
    """
    Render a plant system overview diagram from FMEA structure data.

    Args:
        systems: List of system dicts from plant data, each with "name" and "equipment"/"msrEquipment"
        filename: Output filename
        **kwargs: Passed to render_mermaid()
    """
    lines = ["flowchart TD"]
    for i, system in enumerate(systems):
        sys_id = f"sys{i}"
        sys_name = system.get("name", f"System {i+1}")
        lines.append(f"    subgraph {sys_id} [\"{sys_name}\"]")

        for j, eq in enumerate(system.get("equipment", [])):
            eq_id = f"eq{i}_{j}"
            eq_name = eq.get("name", f"Equipment {j+1}")
            lines.append(f"        {eq_id}[\"{eq_name}\"]")

        for j, msr in enumerate(system.get("msrEquipment", [])):
            msr_id = f"msr{i}_{j}"
            msr_name = msr.get("name", f"MSR {j+1}")
            lines.append(f"        {msr_id}([\"{msr_name}\"])")

        lines.append("    end")

    return render_mermaid("\n".join(lines), filename, **kwargs)


if __name__ == "__main__":
    test_diagram = """flowchart TD
    A[Anlagendaten] --> B[Strukturanalyse]
    B --> C[Funktionsanalyse]
    C --> D[Fehleranalyse]
    D --> E[RPZ-Berechnung]
    E --> F[Massnahmen]
    F --> G[Report]"""

    try:
        path = render_mermaid(test_diagram, "test_pipeline", fmt="svg")
        print(f"Diagram rendered: {path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")

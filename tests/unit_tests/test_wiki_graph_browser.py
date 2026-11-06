"""The wiki's graph page in a real browser: selection, the radial layout and the domain node.

Runs the exported graph.html in headless Chrome with a probe script that drives the page and records what it sees.
Skipped when no Chrome or Chromium is installed.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from taxonomy_generator.wiki import build, write

from tests.unit_tests.test_wiki_export import _inputs, _taxonomy, _value

_CANDIDATES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
               "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
               "/Applications/Chromium.app/Contents/MacOS/Chromium"]
CHROME = next((c for c in (shutil.which(n) or (n if Path(n).is_file() else None) for n in _CANDIDATES) if c), None)
pytestmark = pytest.mark.skipif(CHROME is None, reason="needs Chrome or Chromium")

# Records script errors from the first line on, before d3 and the page script load.
ERRORS = '<script>window.__errs=[];addEventListener("error",(e)=>__errs.push(String(e.message)));</script>'

# Drives the page once it has loaded, and writes what it saw to <body data-probe>.
PROBE = r"""<script>
addEventListener("load", () => setTimeout(() => {
  const out = { errors: window.__errs };
  const nodes = () => [...document.querySelectorAll("g.node")];
  const find = (kind, label) => nodes().find((e) => e.__data__.kind === kind && (!label || e.__data__.label === label));
  const lit = (kind) => nodes().filter((e) => e.__data__.kind === kind && !e.classList.contains("dim-out")).length;
  const canvas = document.getElementById("canvas"), cx = canvas.clientWidth / 2, cy = canvas.clientHeight / 2;
  try {
    out.dimensions = nodes().filter((e) => e.__data__.kind === "dimension").length;
    out.domain_label = find("domain").__data__.label;
    find("dimension", "Source of truth").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    out.lit_dimensions = lit("dimension");

    const view = () => document.querySelector("#svg > g").getAttribute("transform"), before = view();
    const radial = document.querySelector('input[name="layout"][value="radial"]');
    radial.checked = true; radial.dispatchEvent(new Event("change"));
    const d = find("domain").__data__;
    out.domain_offset = Math.hypot(d.x - cx, d.y - cy);
    out.ring = nodes().filter((e) => e.__data__.kind === "dimension").map((e) => Math.hypot(e.__data__.x - d.x, e.__data__.y - d.y));
    out.lit_after_switch = lit("dimension");
    // The storage dimension's values in ring order (by angle about the dimension), as statuses.
    const st = find("dimension", "Storage engine").__data__, base = Math.atan2(st.y - d.y, st.x - d.x);
    const rel = (v) => { let a = Math.atan2(v.y - d.y, v.x - d.x) - base; while (a > Math.PI) a -= 2 * Math.PI;
      while (a <= -Math.PI) a += 2 * Math.PI; return a; };
    out.storage_statuses = nodes().map((e) => e.__data__).filter((v) => v.kind === "value" && /^(Faster reads|Local SSD|Tape|Object store)$/.test(v.label))
      .sort((a, b) => rel(a) - rel(b)).map((v) => v.status);
    out.refitted = view() !== before;
    const box = canvas.getBoundingClientRect();
    out.off_screen = nodes().filter((e) => { const r = e.getBoundingClientRect();
      return r.right < box.left || r.left > box.right || r.bottom < box.top || r.top > box.bottom; }).length;

    // Rotate the rings by 90 degrees: every dimension turns about the domain, staying on its ring.
    const angleOf = (e) => Math.atan2(e.__data__.y - d.y, e.__data__.x - d.x) * 180 / Math.PI;
    const first = find("dimension", "Source of truth"), a0 = angleOf(first);
    out.rotate_shown = getComputedStyle(document.getElementById("rotate-row")).display !== "none";
    const slider = document.getElementById("rotate");
    slider.value = String((Number(slider.value) + 90) % 360); slider.dispatchEvent(new Event("input"));
    out.turned = ((angleOf(first) - a0) % 360 + 360) % 360;
    out.ring_after_turn = nodes().filter((e) => e.__data__.kind === "dimension").map((e) => Math.hypot(e.__data__.x - d.x, e.__data__.y - d.y));

    // Drag the domain away and drop it: it goes back to the centre.
    const el = find("domain"), r0 = el.getBoundingClientRect();
    const at = (type, x, y, target) => target.dispatchEvent(new MouseEvent(type,
      { bubbles: true, cancelable: true, view: window, clientX: x, clientY: y, button: 0, buttons: type === "mouseup" ? 0 : 1 }));
    const x0 = r0.left + r0.width / 2, y0 = r0.top + r0.height / 2;
    at("mousedown", x0, y0, el); at("mousemove", x0 + 120, y0 + 80, window); at("mouseup", x0 + 120, y0 + 80, window);
    out.dropped_offset = Math.hypot(d.fx - cx, d.fy - cy);
  } catch (e) { out.errors.push("probe: " + e.message); }
  document.body.setAttribute("data-probe", JSON.stringify(out));
}, 0));
</script>"""


def _three_dimensions():
    """The toy taxonomy plus a third dimension that no relation reaches."""
    tax = _taxonomy()
    extra = {"id": "3", "name": "Storage engine", "description": "Where are bytes written?", "relations": [],
             "evidence": {"codes": 2, "documents": 1, "sources": 1},
             "values": [_value("3.1", "Faster reads", "outcome", ["s02_p01"]),
                        _value("3.2", "Local SSD", "accepted", ["s02_p01"]),
                        _value("3.3", "Tape", "rejected", ["s02_p01"]),
                        _value("3.4", "Object store", "accepted", ["s02_p01"])]}
    tax["selected_clusters"].append(extra)
    tax["iterations"][0]["clusters"].insert(2, extra)
    return tax


def _probe(tmp_path: Path) -> dict:
    write(build(_inputs(taxonomy=_three_dimensions(), domain="Git hosting")), tmp_path / "wiki", "toy")
    page = tmp_path / "wiki" / "html" / "graph.html"
    html = page.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>" + ERRORS, 1).replace("</body>", PROBE + "</body>", 1)
    page.write_text(html, encoding="utf-8")
    run = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                          "--user-data-dir=" + str(tmp_path / "profile"), "--window-size=1280,900",
                          "--virtual-time-budget=5000", "--dump-dom", page.as_uri()],
                         capture_output=True, text=True, timeout=120)
    m = re.search(r'data-probe="([^"]*)"', run.stdout)
    assert m, "the probe did not report: " + run.stderr[-2000:]
    return json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&"))


def test_graph_page_selection_radial_layout_and_domain_in_a_browser(tmp_path):
    out = _probe(tmp_path)
    assert out["errors"] == []
    assert out["dimensions"] == 3 and out["domain_label"] == "Git hosting"
    # Selecting a dimension lights it and the dimension it relates to, not every dimension (the domain links to all
    # of them, and must not be expanded).
    assert out["lit_dimensions"] == 2
    assert out["lit_after_switch"] == 2  # switching the layout keeps the selection
    # Radial: the domain at the centre, the dimensions on one ring around it.
    assert out["domain_offset"] < 1
    ring = out["ring"]
    assert max(ring) - min(ring) < 0.15 * max(ring), ring
    # A dimension's values are grouped by status on the ring, in the legend's order.
    assert out["storage_statuses"] == ["accepted", "accepted", "rejected", "outcome"]
    # Switching the layout with a node selected re-fits the view, so nothing is left off screen.
    assert out["refitted"] and out["off_screen"] == 0
    # The rotation slider (shown for the radial layout) turns the rings about the domain.
    assert out["rotate_shown"]
    assert abs(out["turned"] - 90) < 1, out["turned"]
    assert out["ring_after_turn"] == pytest.approx(ring, abs=1)
    # A dragged domain goes back to the centre when dropped.
    assert out["dropped_offset"] < 1

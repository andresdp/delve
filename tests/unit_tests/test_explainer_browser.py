"""The explainer page in a real browser: no script errors, selection, tabs and the radial subgraph's labels.

Runs an explainer rendered next to the toy wiki in headless Chrome with a probe script that drives the page and
records what it sees. Skipped when no Chrome or Chromium is installed.
"""

import json
import re
import subprocess
from pathlib import Path

import pytest

from taxonomy_generator.wiki import build, explainer, write
from taxonomy_generator.wiki import query as q
from tests.unit_tests.test_ddspace_rationale import _sample
from tests.unit_tests.test_wiki_export import POINTS, _inputs, _taxonomy
from tests.unit_tests.test_wiki_graph_browser import CHROME, ERRORS

pytestmark = pytest.mark.skipif(CHROME is None, reason="needs Chrome or Chromium")

# Long labels, as on real data (C1): a dimension label longer than the gap between the rings.
LONG_DIMENSION = "Where the authoritative copy of every record lives"
LONG_VALUE = "Quorum of local disks on every node"

PROBE = r"""<script>
addEventListener("load", () => setTimeout(() => {
  const out = { errors: window.__errs };
  const nodes = () => [...document.querySelectorAll("g.node")];
  const lit = () => nodes().filter((e) => !e.classList.contains("dim-out")).map((e) => e.__data__.id).sort();
  const greyed = () => nodes().filter((e) => e.classList.contains("greyed")).map((e) => e.__data__.id).sort();
  const positions = () => nodes().map((e) => [e.__data__.id, Math.round(e.__data__.x), Math.round(e.__data__.y)]);
  const click = (el) => el.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  const overlaps = (a, b) => { const r = a.getBoundingClientRect(), s = b.getBoundingClientRect();
    return r.left < s.right && s.left < r.right && r.top < s.bottom && s.top < r.bottom; };
  const label = (e) => e.querySelector("text");
  try {
    out.nodes = nodes().length;
    out.before = positions();
    // Select A1's choice of Disk quorum in the text.
    click(document.querySelector('[data-panel="A1"] .choice .vref[data-node="v:1.1"]'));
    out.selected_lit = lit();
    out.info = document.getElementById("info").textContent;
    out.greyed_a1 = greyed();
    // Switch to A2: the same subgraph, A2's choices lit, the selection fade cleared.
    click(document.querySelector('.tab[data-tab="A2"]'));
    out.after = positions();
    out.faded_after_tab = nodes().filter((e) => e.classList.contains("dim-out")).length;
    out.greyed_a2 = greyed();
    out.hint = document.getElementById("info").textContent;
    // Labels on the rings: no dimension label over a value label, no value label over a requirement label.
    const kind = (k) => nodes().filter((e) => e.__data__.kind === k);
    out.dim_value = [], out.value_req = [];
    kind("dimension").forEach((d) => kind("value").forEach((v) => {
      if (overlaps(label(d), label(v))) out.dim_value.push([d.__data__.label, v.__data__.label]); }));
    kind("value").forEach((v) => kind("requirement").forEach((r) => {
      if (overlaps(label(v), label(r))) out.value_req.push([v.__data__.label, r.__data__.label]); }));
  } catch (e) { out.errors.push("probe: " + e.message); }
  document.body.setAttribute("data-probe", JSON.stringify(out));
}, 0));
</script>"""


def _probe(tmp_path: Path) -> dict:
    tax = _taxonomy()
    tax["selected_clusters"][0]["name"] = LONG_DIMENSION
    tax["selected_clusters"][0]["values"][0]["label"] = LONG_VALUE
    root = tmp_path / "wiki"
    write(build(_inputs(taxonomy=tax, design_points=POINTS)), root, "toy")
    html = root / "html"
    page = explainer.write_page(_sample(), q.load(root / "raw" / "graph.json"), html, wiki_html=html)
    text = page.read_text(encoding="utf-8")
    assert LONG_DIMENSION in text and LONG_VALUE in text
    page.write_text(text.replace("<head>", "<head>" + ERRORS, 1).replace("</body>", PROBE + "</body>", 1),
                    encoding="utf-8")
    run = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                          "--user-data-dir=" + str(tmp_path / "profile"), "--window-size=1280,900",
                          "--virtual-time-budget=5000", "--dump-dom", page.as_uri()],
                         capture_output=True, text=True, timeout=120)
    m = re.search(r'data-probe="([^"]*)"', run.stdout)
    assert m, "the probe did not report: " + run.stderr[-2000:]
    return json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&"))


def test_explainer_selection_tabs_and_labels_in_a_browser(tmp_path):
    out = _probe(tmp_path)
    assert out["errors"] == []
    assert out["nodes"] > 0
    # Selecting A1's choice lights its value, its dimension and the requirement that drives it (Q1).
    assert {"v:1.1", "d:1", "r:Q1"} <= set(out["selected_lit"])
    assert "r:R1" not in out["selected_lit"]  # drives the other choice, not this one
    assert "Chosen in A1" in out["info"]
    # A1 lights its choices; the others are greyed.
    assert "v:1.1" not in out["greyed_a1"] and "v:2.1" not in out["greyed_a1"] and "v:1.2" in out["greyed_a1"]
    # Switching tabs keeps the subgraph (same nodes, same places) and drops the selection fade.
    assert out["after"] == out["before"]
    assert out["faded_after_tab"] == 0
    assert "v:1.2" not in out["greyed_a2"] and "v:1.1" in out["greyed_a2"]
    assert "Select a dimension" in out["hint"]
    # Each ring sits outside the labels of the ring inside it.
    assert out["dim_value"] == [], out["dim_value"]
    assert out["value_req"] == [], out["value_req"]

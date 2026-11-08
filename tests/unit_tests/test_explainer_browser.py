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
from tests.unit_tests.test_wiki_graph_browser import CHROME, ERRORS, load

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
  const inPoint = () => nodes().filter((e) => e.classList.contains("in-point")).map((e) => e.__data__.id).sort();
  const onPath = () => [...document.querySelectorAll("line.link.on-path")].map((e) => e.__data__.source + "|" + e.__data__.target).sort();
  const nodeOf = (id) => nodes().find((e) => e.__data__.id === id);
  const positions = () => nodes().map((e) => [e.__data__.id, Math.round(e.__data__.x), Math.round(e.__data__.y)]);
  const click = (el) => el.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  const overlaps = (a, b) => { const r = a.getBoundingClientRect(), s = b.getBoundingClientRect();
    return r.left < s.right && s.left < r.right && r.top < s.bottom && s.top < r.bottom; };
  const label = (e) => e.querySelector("text");
  try {
    out.nodes = nodes().length;
    out.before = positions();
    // The trajectory tab opens first: every investigated value is lit, and an arc links each step to its parent.
    out.first_tab = document.querySelector('.tab[aria-selected="true"]').dataset.tab;
    out.greyed_trajectory = greyed();
    out.point_trajectory = inPoint();
    out.arcs = document.querySelectorAll("svg.lineage path").length;
    // Selecting step 3 (its column) lights its point only, and marks its column and its entry.
    click(document.querySelector('.step-h[data-step="3"]'));
    out.greyed_step3 = greyed();
    out.point_step3 = inPoint();
    out.step_info = document.getElementById("info").textContent;
    out.step_marked = document.querySelectorAll('.sel[data-step="3"]').length;
    click(document.querySelector('.tab[data-tab="A1"]'));
    // Select A1's choice of Disk quorum in the text.
    click(document.querySelector('[data-panel="A1"] .choice .vref[data-node="v:1.1"]'));
    out.selected_lit = lit();
    out.selected_path = onPath();
    out.info = document.getElementById("info").textContent;
    out.greyed_a1 = greyed();
    out.point_a1 = inPoint();
    // A dimension: its path to the centre and the values of it that design points take.
    click(nodeOf("d:1"));
    out.dim_lit = lit();
    out.dim_path = onPath();
    // Switch to A2: the same subgraph, A2's choices lit, the selection fade cleared.
    click(document.querySelector('.tab[data-tab="A2"]'));
    out.after = positions();
    out.faded_after_tab = nodes().filter((e) => e.classList.contains("dim-out")).length;
    out.greyed_a2 = greyed();
    out.point_a2 = inPoint();
    out.hint = document.getElementById("info").textContent;
    // Design points: one node per step; selecting one shows its step.
    out.points = nodes().filter((e) => e.__data__.kind === "point").map((e) => e.__data__.id).sort();
    click(nodeOf("p:1"));
    out.point_lit = lit();
    out.point_info = document.getElementById("info").textContent;
    // The toggle shows every value the space offers; by default only the explored and considered ones.
    const shown = () => nodes().filter((e) => e.style.display !== "none").length;
    out.shown_default = shown();
    const box = document.getElementById("show-all"); box.checked = true; box.dispatchEvent(new Event("change"));
    out.shown_all = shown();
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
    # The trajectory opens first; the fixture's steps visit v:1.1, v:2.1 and v:1.2; step 2 refines step 1.
    assert out["first_tab"] == "trajectory"
    explored = {"v:1.1", "v:2.1", "v:1.2", "d:1", "d:2"}
    assert not explored & set(out["greyed_trajectory"])          # explored: every value a step or choice takes
    assert set(out["greyed_trajectory"]) and all(i.startswith(("v:", "d:")) for i in out["greyed_trajectory"])
    assert out["point_trajectory"] == []                           # no step selected: no single point outlined
    assert out["arcs"] == 1
    assert out["greyed_step3"] == out["greyed_trajectory"]         # explored stays lit whatever is shown
    assert out["point_step3"] == ["p:3", "v:1.2"]                 # step 3's point and its values are outlined
    assert "step 3" in out["step_info"] and "explore" in out["step_info"]
    assert out["step_marked"] >= 3  # its column header, its cells and its entry in the list
    # Selecting A1's choice lights its ancestors (its dimension, the centre) and the design points that take it.
    assert {"v:1.1", "d:1", "domain", "p:1", "p:2"} <= set(out["selected_lit"])
    assert not {"r:Q1", "d:2", "v:2.1", "v:1.2", "p:3"} & set(out["selected_lit"])  # not on its paths
    assert {"domain|d:1", "d:1|v:1.1", "v:1.1|p:1", "v:1.1|p:2"} <= set(out["selected_path"])
    assert "Chosen in A1" in out["info"]
    assert out["point_a1"] == ["p:1", "v:1.1", "v:2.1"]
    # A dimension lights the centre and the paths down to the values design points take, and those points.
    assert set(out["dim_lit"]) == {"d:1", "domain", "v:1.1", "v:1.2", "p:1", "p:2", "p:3"}
    assert {"domain|d:1", "d:1|v:1.1", "d:1|v:1.2"} <= set(out["dim_path"])
    # Switching tabs keeps the subgraph (same nodes, same places) and drops the selection fade.
    assert out["after"] == out["before"]
    assert out["faded_after_tab"] == 0
    assert out["point_a2"] == ["p:3", "v:1.2"]
    # One point per step; a point lights its values, their dimensions and the requirements it is judged against.
    assert out["points"] == ["p:1", "p:2", "p:3"]
    assert {"p:1", "v:1.1", "v:2.1", "d:1", "d:2", "domain", "r:R1", "r:Q1", "r:C1"} <= set(out["point_lit"])
    assert "step 1" in out["point_info"] and "Design point" in out["point_info"]
    assert out["shown_all"] > out["shown_default"]
    assert "Select a dimension" in out["hint"]
    # Each ring sits outside the labels of the ring inside it.
    assert out["dim_value"] == [], out["dim_value"]
    assert out["value_req"] == [], out["value_req"]


def test_a_standalone_explainer_folder_carries_the_layout_script_and_loads(tmp_path):
    root = tmp_path / "wiki"
    write(build(_inputs(design_points=POINTS)), root, "toy")
    out = tmp_path / "out"
    page = explainer.write_standalone(_sample(), q.load(root / "raw" / "graph.json"), out)
    assert (out / "assets" / "graph-layout.js").is_file()
    assert 'src="../assets/graph-layout.js"' in page.read_text(encoding="utf-8")
    seen = load(page, tmp_path / "profile")
    assert seen["errors"] == []
    assert seen["layout"] == "object" and seen["nodes"] > 0

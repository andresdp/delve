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
    // The ADRs tab opens first; explored dimensions and values are coloured, no point outlined.
    out.first_tab = document.querySelector('.tab[aria-selected="true"]').dataset.tab;
    out.tabs = [...document.querySelectorAll(".tab")].map((e) => e.dataset.tab);
    out.greyed_trajectory = greyed();
    out.point_trajectory = inPoint();
    // The trajectory tab: an arc links each step to its parent; selecting step 3 outlines its point.
    click(document.querySelector('.tab[data-tab="trajectory"]'));
    out.arcs = document.querySelectorAll("svg.lineage path").length;
    out.lane_arrows = document.querySelectorAll("svg.lane-arrows > path").length;
    click(document.querySelector('.node-chip[data-step="2"]'));
    out.chip_point = inPoint();
    click(document.querySelector('.step-h[data-step="3"]'));
    out.greyed_step3 = greyed();
    out.point_step3 = inPoint();
    out.step_info = document.getElementById("info").textContent;
    out.step_marked = document.querySelectorAll('.sel[data-step="3"]').length;
    click(document.querySelector('.tab[data-tab="adrs"]'));
    // An alternative outlines its point; an option outlines its values and the step that evaluated it.
    click(document.querySelector('.solution[data-alt="A1"]'));
    out.point_a1 = inPoint();
    out.alt_info = document.getElementById("info").textContent;
    click(document.querySelector('.option[data-option="ADR1:O2"]'));
    out.point_option = inPoint();
    // A value in an option: its lineage, up to the centre and down through points to requirements.
    click(document.querySelector('.option[data-option="ADR1:O1"] .vref[data-node="v:1.1"]'));
    out.selected_lit = lit();
    out.selected_path = onPath();
    out.info = document.getElementById("info").textContent;
    click(nodeOf("d:1"));
    out.dim_lit = lit();
    out.dim_path = onPath();
    // The compare view: the same subgraph, every alternative outlined, the selection fade cleared.
    click(document.querySelector('.tab[data-tab="compare"]'));
    out.after = positions();
    out.faded_after_tab = nodes().filter((e) => e.classList.contains("dim-out")).length;
    out.point_compare = inPoint();
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
    // The dividers: arrow keys move them (the graph column and the graph grow), a double-click resets them.
    const canvasBox = () => document.getElementById("canvas").getBoundingClientRect();
    const key = (el, k) => el.dispatchEvent(new KeyboardEvent("keydown", { key: k, bubbles: true }));
    const v = document.querySelector(".splitter-v"), h = document.querySelector(".splitter-h");
    out.split_before = [Math.round(canvasBox().width), Math.round(canvasBox().height)];
    key(v, "ArrowLeft"); key(v, "ArrowLeft"); key(h, "ArrowDown"); key(h, "ArrowDown");
    out.split_after = [Math.round(canvasBox().width), Math.round(canvasBox().height)];
    out.split_var = document.documentElement.style.getPropertyValue("--split-left");
    v.dispatchEvent(new MouseEvent("dblclick", { bubbles: true }));
    out.split_reset = document.documentElement.style.getPropertyValue("--split-left");
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
    # The ADRs tab opens first; the fixture's steps visit v:1.1, v:2.1 and v:1.2; step 2 refines step 1.
    explored = {"v:1.1", "v:2.1", "v:1.2", "d:1", "d:2"}
    assert out["tabs"] == ["adrs", "compare", "trajectory"] and out["first_tab"] == "adrs"
    assert not explored & set(out["greyed_trajectory"])          # explored: every value a step or choice takes
    assert set(out["greyed_trajectory"]) and all(i.startswith(("v:", "d:")) for i in out["greyed_trajectory"])
    assert out["point_trajectory"] == []                           # nothing selected: no point outlined
    assert out["arcs"] == 1
    assert out["lane_arrows"] == 1                                 # step 2 refines step 1, along lane A
    assert out["chip_point"] == ["p:2", "v:1.1"]                   # a lane chip selects its point
    assert out["greyed_step3"] == out["greyed_trajectory"]         # explored stays lit whatever is shown
    assert out["point_step3"] == ["p:3", "v:1.2"]                 # step 3's point and its values are outlined
    # The details panel reads like the story: what the point is, its rating in words, thought, move, observation.
    info = out["step_info"]
    assert "Design point" in info and "#3 · New approach B" in info and "Approach B, round 2" in info
    assert "it meets every constraint" in info and "Thought" in info and "Observed" in info
    assert "In the decisions" in info and "A write-ahead log in S3" in info
    assert out["step_marked"] >= 3  # its column header, its cells and its entry in the list
    assert out["point_a1"] == ["p:1", "v:1.1", "v:2.1"] and "Three-phase commit" in out["alt_info"]
    assert out["point_option"] == ["p:3", "v:1.2"]                # ADR1's O2, evaluated at step 3
    # A value: its ancestors, the points that take it and the requirements those points are judged against.
    assert {"v:1.1", "d:1", "domain", "p:1", "p:2", "r:R1", "r:Q1", "r:C1"} <= set(out["selected_lit"])
    assert not {"d:2", "v:2.1", "v:1.2", "p:3"} & set(out["selected_lit"])  # not on its paths
    assert {"domain|d:1", "d:1|v:1.1", "v:1.1|p:1", "v:1.1|p:2", "p:1|r:Q1"} <= set(out["selected_path"])
    assert "Chosen in A1" in out["info"]
    assert "Value · an option for" in out["info"] and "In the trajectory" in out["info"] and "First tried in #1" in out["info"]
    # A dimension: the centre, its explored values, their points and those points' requirements.
    assert set(out["dim_lit"]) == {"d:1", "domain", "v:1.1", "v:1.2", "p:1", "p:2", "p:3", "r:R1", "r:Q1", "r:C1"}
    assert {"domain|d:1", "d:1|v:1.1", "d:1|v:1.2"} <= set(out["dim_path"])
    assert out["after"] == out["before"]
    assert out["faded_after_tab"] == 0
    assert out["point_compare"] == ["p:1", "p:3", "v:1.1", "v:1.2", "v:2.1"]
    # One point per step; a point lights its values, their dimensions and the requirements it is judged against.
    assert out["points"] == ["p:1", "p:2", "p:3"]
    assert {"p:1", "v:1.1", "v:2.1", "d:1", "d:2", "domain", "r:R1", "r:Q1", "r:C1"} <= set(out["point_lit"])
    assert "#1 · Seed of approach A" in out["point_info"] and "Design point" in out["point_info"]
    assert "It became alternative A1" in out["point_info"]
    assert out["shown_all"] > out["shown_default"]
    assert out["split_after"][0] > out["split_before"][0] and out["split_after"][1] > out["split_before"][1]
    assert out["split_var"] == "46%" and out["split_reset"] == "50%"
    assert "Select anything in the graph" in out["hint"]
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

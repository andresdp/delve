// The radial layout shared by the wiki's graph page and the explainer pages: one ring per kind, outwards from the
// domain node at the centre, each dimension an angular sector holding its values. Loaded as a plain script after
// d3.min.js; it exposes one global, DelveLayout. The pages keep their own state (selection, filters, the domain
// node, tabs) and pass in what differs between them.
(function (root) {
  "use strict";

  const STATUS_ORDER = ["accepted", "mixed", "rejected", "outcome"];

  // Targets { r, x, y } per node id, around (cx, cy).
  //   rings:       ring kinds from the centre ("domain" sits at the centre); a ring with no node leaves no gap
  //   ringOf:      kind -> ring (default: the kind itself)
  //   spacing:     ring -> arc length per node; a ring's radius grows with the nodes on it
  //   statusOrder: within a dimension, values of the same status sit together, in this order (default STATUS_ORDER)
  //   stagger:     every other value of a dimension sits this far further out (default 24: twice the room between
  //                neighbouring values)
  //   ringGap:     the least distance between neighbouring rings (default 110)
  //   rotation:    radians; turns every ring about the centre
  //   labelReach:  optional (ringNodes) -> how far past its node a ring's outward labels reach; the next ring then
  //                starts at least labelGap (default 26) beyond them
  //   restJitter:  nodes placed by their neighbours' mean angle alternate this many radians either side of it
  //   inward:      rings whose labels point inwards (see orientLabels): such a ring starts beyond its own labels'
  //                reach from the centre, and its labels do not push the next ring out
  //   inset:       ring -> distance; that ring moves out to sit at most this far inside the next ring (use it for an
  //                inward ring, whose labels then do not cross the next ring's nodes)
  //   even:        rings whose nodes sit evenly around the whole ring, in node order, clockwise from the top
  //                (every other one of them turned by half a slot)
  function radialTargets(nodes, links, cx, cy, opts) {
    const o = opts || {};
    const rings = o.rings, spacing = o.spacing;
    const ringOf = o.ringOf || ((kind) => kind);
    const statusOrder = o.statusOrder || STATUS_ORDER;
    const stagger = o.stagger == null ? 24 : o.stagger;
    const ringGap = o.ringGap == null ? 110 : o.ringGap;
    const labelGap = o.labelGap == null ? 26 : o.labelGap;
    const rotation = o.rotation || 0, restJitter = o.restJitter || 0, labelReach = o.labelReach || null;
    const inward = new Set(o.inward || []), inset = o.inset || {}, even = o.even || [];

    // Each dimension gets an angular sector centred on it, holding its shown values. A sector's size is its value
    // count plus a padding of half the mean count: a dimension with two values still gets room on the ring, and the
    // padding leaves a gap between neighbouring dimensions' values.
    const angle = new Map(), values = new Map(), outset = new Map();
    links.filter((l) => l.type === "has_value").forEach((l) => {
      if (!values.has(l.source)) values.set(l.source, []);
      values.get(l.source).push(l.target);
    });
    const dims = nodes.filter((n) => n.kind === "dimension");
    // Within a dimension, values of the same status sit together, in the legend's order (stable within a status).
    const statusOf = new Map(nodes.map((n) => [n.id, n.status]));
    const rank = (id) => { const i = statusOrder.indexOf(statusOf.get(id)); return i < 0 ? statusOrder.length : i; };
    values.forEach((vs) => vs.sort((a, b) => rank(a) - rank(b)));
    const own = (d) => values.get(d.id) || [];
    const pad = Math.max(1, d3.sum(dims, (d) => own(d).length) / (dims.length || 1) / 2);
    const total = d3.sum(dims, (d) => own(d).length + pad) || 1;
    // The value ring counts the padding as slots, so neighbouring values sit spacing.value apart along the ring.
    const count = {};
    nodes.forEach((n) => { const k = ringOf(n.kind); count[k] = (count[k] || 0) + 1; });
    const slots = { ...count, value: Math.max(count.value || 0, total) };
    const radiusOf = {};
    let r = 0, reach = 0;
    const present = rings.filter((k) => count[k]);
    present.forEach((k) => {
      if (k === "domain") { radiusOf[k] = 0; return; }
      const ringNodes = nodes.filter((n) => ringOf(n.kind) === k);
      r = Math.max(r + ringGap, slots[k] * spacing[k] / (2 * Math.PI));
      if (labelReach) r = Math.max(r, inward.has(k) ? labelReach(ringNodes) + labelGap : reach + labelGap);
      radiusOf[k] = r;
      if (labelReach) reach = r + (k === "value" ? stagger : 0) + (inward.has(k) ? labelGap : labelReach(ringNodes));
    });
    present.forEach((k, i) => {
      const next = present[i + 1];
      if (inset[k] != null && next) radiusOf[k] = Math.max(radiusOf[k], radiusOf[next] - inset[k]);
    });
    let start = -Math.PI / 2;
    dims.forEach((d) => {
      const vs = own(d), span = 2 * Math.PI * (vs.length + pad) / total, used = span * vs.length / (vs.length + pad);
      angle.set(d.id, start + span / 2);
      vs.forEach((v, i) => {
        angle.set(v, start + (span - used) / 2 + used * (i + 0.5) / vs.length);
        if (i % 2) outset.set(v, stagger);
      });
      start += span;
    });
    // Everything else (sources, systems, design points, requirements, values whose dimension is hidden): the mean
    // angle of its placed neighbours, or evenly spaced when it has none.
    const near = new Map(nodes.map((n) => [n.id, []]));
    links.forEach((l) => { near.get(l.source)?.push(l.target); near.get(l.target)?.push(l.source); });
    const rest = nodes.filter((n) => n.kind !== "domain" && !angle.has(n.id));
    rest.forEach((n, i) => {
      const as = near.get(n.id).filter((x) => angle.has(x)).map((x) => angle.get(x));
      angle.set(n.id, as.length ? Math.atan2(d3.sum(as, Math.sin), d3.sum(as, Math.cos)) + (i % 2 ? restJitter : -restJitter)
        : -Math.PI / 2 + 2 * Math.PI * i / rest.length);
    });
    even.forEach((k, j) => {  // alternate rings start half a slot apart, so equal counts do not line up
      const ring = nodes.filter((n) => ringOf(n.kind) === k);
      ring.forEach((n, i) => angle.set(n.id, -Math.PI / 2 + 2 * Math.PI * (i + (j % 2 ? 0 : 0.5)) / ring.length));
    });
    const target = new Map();
    nodes.forEach((n) => {
      const rr = (radiusOf[ringOf(n.kind)] || 0) + (outset.get(n.id) || 0), a = (angle.get(n.id) || 0) + rotation;
      target.set(n.id, { r: rr, x: cx + rr * Math.cos(a), y: cy + rr * Math.sin(a) });
    });
    return target;
  }

  // Labels (a d3 selection of the nodes' <text>) point outwards along their node's radius, read left to right on
  // both halves. The domain's label, and every label when outward is false, sits centred above its node (centreDy).
  //   radius: (node) -> its drawn radius; the label starts 4px past it
  //   inward: optional (node) -> whether its label points inwards, towards the centre, instead
  function orientLabels(labels, cx, cy, opts) {
    const o = opts || {};
    const outward = o.outward !== false, centreDy = o.centreDy || "-0.9em", radius = o.radius;
    labels.each(function (d) {
      const t = d3.select(this);
      if (!outward || d.kind === "domain") { t.attr("transform", null).attr("text-anchor", "middle").attr("dx", 0).attr("dy", centreDy); return; }
      const deg = Math.atan2(d.y - cy, d.x - cx) * 180 / Math.PI, left = Math.abs(deg) > 90;
      const sign = (left ? -1 : 1) * (o.inward && o.inward(d) ? -1 : 1);
      t.attr("transform", "rotate(" + (left ? deg + 180 : deg) + ")").attr("text-anchor", sign > 0 ? "start" : "end")
        .attr("dx", sign * (radius(d) + 4)).attr("dy", "0.35em");
    });
  }

  root.DelveLayout = { STATUS_ORDER, radialTargets, orientLabels };
})(window);

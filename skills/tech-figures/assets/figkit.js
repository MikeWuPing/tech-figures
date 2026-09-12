/* ============================================================
   figkit.js —— 连接线绘制
   按元素自动布线，横平竖直，端点带小圆点。
   用法：wire('#a', '#b', {side:'v'})  —— 从 a 底部连到 b 顶部
   ============================================================ */
(function () {
  const NS = "http://www.w3.org/2000/svg";

  function box(el) {
    const r = el.getBoundingClientRect();
    const f = document.querySelector(".fig").getBoundingClientRect();
    return { x: r.left - f.left, y: r.top - f.top, w: r.width, h: r.height,
             cx: r.left - f.left + r.width / 2, cy: r.top - f.top + r.height / 2 };
  }

  const SIDES = {
    t: (b, p) => [b.cx, b.y + (p ?? 0)],
    b: (b, p) => [b.cx, b.y + b.h + (p ?? 0)],
    l: (b, p) => [b.x + (p ?? 0), b.cy],
    r: (b, p) => [b.x + b.w + (p ?? 0), b.cy],
  };

  let uid = 0;

  /**
   * @param {string} a   起点选择器
   * @param {string} b   终点选择器
   * @param {object} o   { from:'b'|'t'|'l'|'r', to:..., color, w, dash, dot, arrow }
   */
  window.wire = function (a, b, o) {
    o = o || {};
    const ea = document.querySelector(a), eb = document.querySelector(b);
    const svg = document.querySelector(".wires");
    if (!ea || !eb || !svg) return;

    const A = box(ea), B = box(eb);
    const f = o.from || "b", t = o.to || "t";
    const [x0, y0] = SIDES[f](A, o.padA);
    let [x1, y1] = SIDES[t](B, o.padB);
    const color = o.color || "rgba(140,168,196,.72)";
    const w = o.w ?? 1.4;

    let d;
    if (o.straight) {
      // 直落：保持起点的 x 一路走到底，落到目标边上。
      // 用于"芯片坐在基板上"这类扇入——多根线各走各的，不收到中心点。
      x1 = x0;
      y1 = t === "t" ? B.y : (t === "b" ? B.y + B.h : B.cy);
      d = `M ${x0} ${y0} L ${x1} ${y1}`;
    } else {
    // 正交路由：先沿起点方向走一段，再横/竖折到终点
    const vert = (f === "b" || f === "t") && (t === "b" || t === "t");
    const horiz = (f === "l" || f === "r") && (t === "l" || t === "r");
    if (vert) {
      const mid = o.mid ?? (y0 + y1) / 2;
      d = `M ${x0} ${y0} L ${x0} ${mid} L ${x1} ${mid} L ${x1} ${y1}`;
    } else if (horiz) {
      const mid = o.mid ?? (x0 + x1) / 2;
      d = `M ${x0} ${y0} L ${mid} ${y0} L ${mid} ${y1} L ${x1} ${y1}`;
    } else if (f === "b" || f === "t") {
      d = `M ${x0} ${y0} L ${x0} ${y1} L ${x1} ${y1}`;
    } else {
      d = `M ${x0} ${y0} L ${x1} ${y0} L ${x1} ${y1}`;
    }
    }

    const g = document.createElementNS(NS, "g");
    const path = document.createElementNS(NS, "path");
    path.setAttribute("d", d);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", color);
    path.setAttribute("stroke-width", w);
    path.setAttribute("stroke-linejoin", "round");
    path.setAttribute("stroke-linecap", "round");
    if (o.dash) path.setAttribute("stroke-dasharray", o.dash);
    if (o.arrow !== false) {
      const id = "ah" + (++uid);
      let defs = svg.querySelector("defs");
      if (!defs) { defs = document.createElementNS(NS, "defs"); svg.appendChild(defs); }
      const mk = document.createElementNS(NS, "marker");
      mk.setAttribute("id", id);
      mk.setAttribute("viewBox", "0 0 10 10");
      mk.setAttribute("refX", "8"); mk.setAttribute("refY", "5");
      mk.setAttribute("markerWidth", "6"); mk.setAttribute("markerHeight", "6");
      mk.setAttribute("orient", "auto-start-reverse");
      const tip = document.createElementNS(NS, "path");
      tip.setAttribute("d", "M 0 1 L 9 5 L 0 9 z");
      tip.setAttribute("fill", color);
      mk.appendChild(tip); defs.appendChild(mk);
      path.setAttribute("marker-end", `url(#${id})`);
    }
    g.appendChild(path);

    // 端点小圆点
    if (o.dot !== false) {
      [[x0, y0], [x1, y1]].forEach(([x, y]) => {
        const c = document.createElementNS(NS, "circle");
        c.setAttribute("cx", x); c.setAttribute("cy", y); c.setAttribute("r", 3.1);
        c.setAttribute("fill", "#0f1319");
        c.setAttribute("stroke", color);
        c.setAttribute("stroke-width", 1.3);
        g.appendChild(c);
      });
    }
    svg.appendChild(g);
    return g;
  };

  /* 批量：每组 [起点, 终点, 选项] */
  window.wires = function (list) { list.forEach(a => wire(a[0], a[1], a[2])); };
})();

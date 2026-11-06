  /* Layout math. One function answers where every mark sits, which way it
     faces, and where the lines run, for any count from 6 to 24. The frame is
     the drawing's own: build.py writes the viewBox, the ring's radius and the
     inset that keeps a mark's own width inside the edge, so no number here
     repeats one from build.py. */
  const frameOf = svg => {
    const box = svg.viewBox.baseVal;
    const ring = svg.querySelector('.center-ring');
    const inset = Number(svg.dataset.inset) || 0;
    return {
      w: box.width,
      cx: box.width / 2,
      cy: box.height / 2,
      x0: inset,
      x1: box.width - inset,
      y0: inset,
      y1: box.height - inset,
      ring: ring ? Number(ring.getAttribute('r')) : 0,
      mark: Number(svg.dataset.mark) || 0,
    };
  };
  const wobble = (index, salt) => {
    const value = Math.sin(index * 12.9898 + salt * 78.233) * 43758.5453;
    return value - Math.floor(value);
  };

  /* Every curve bows the same way: the control point steps off the segment's
     own perpendicular by 12 percent of its length. The length comes back with
     the path so a line can be handed its own dash pattern before it is
     attached, which keeps the draw off the layout path. */
  const curve = ([x1, y1], [x2, y2]) => {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const cx = x1 + dx / 2 + dy * .12;
    const cy = y1 + dy / 2 - dx * .12;
    let length = 0;
    let px = x1;
    let py = y1;
    for (let s = 1; s <= 8; s += 1) {
      const t = s / 8;
      const u = 1 - t;
      const x = u * u * x1 + 2 * u * t * cx + t * t * x2;
      const y = u * u * y1 + 2 * u * t * cy + t * t * y2;
      length += Math.hypot(x - px, y - py);
      px = x;
      py = y;
    }
    return {
      d: `M${x1.toFixed(1)} ${y1.toFixed(1)}Q${cx.toFixed(1)} ${cy.toFixed(1)} ${x2.toFixed(1)} ${y2.toFixed(1)}`,
      length: Math.ceil(length) + 2,
    };
  };

  const layoutFor = (name, count, angles, frame) => {
    const { w, cx, cy, x0, x1, y0, y1, ring, mark } = frame;
    const spanX = x1 - x0;
    const spanY = y1 - y0;
    const points = [];
    const lines = [];
    const seeded = i => (angles[i] === undefined ? i * 29 - 40 : angles[i]);
    if (name === 'orbit') {
      const radius = Math.min(spanX, spanY) / 2;
      for (let i = 0; i < count; i += 1) {
        const angle = i / count * Math.PI * 2 - Math.PI / 2;
        const x = cx + Math.cos(angle) * radius;
        const y = cy + Math.sin(angle) * radius;
        points.push([x, y, angle * 180 / Math.PI + 90]);
        const stop = (ring + 8) / radius;
        lines.push(curve([x, y], [cx + (x - cx) * stop, cy + (y - cy) * stop]));
      }
      return { points, lines, ring: true };
    }
    if (name === 'groups') {
      /* Each group is a loose circle: the mark that convenes it sits in the
         middle and its partners sit around it at seeded angles and distances.
         The clusters alternate above and below the center line by enough to
         clear each other, so the row is never straight. */
      const groups = Math.min(4, Math.max(2, Math.round(count / 4)));
      /* A partner never sits closer to its convener than one mark, and the
         clusters are spaced from their own radius, so more groups make
         smaller circles instead of overlapping ink. */
      const near = Math.max(mark * 1.85, Math.min(96, spanX / (2 * groups) - 22));
      const radius = near * 1.25 + mark;
      const lo = Math.max(x0, radius + 20);
      const hi = Math.min(x1, w - radius - 20);
      const gap = groups > 1 ? (hi - lo) / (groups - 1) : 0;
      const lift = Math.max(spanY * .1, Math.sqrt(Math.max(0, 4 * radius * radius - gap * gap)) / 2 + 6);
      const size = Math.ceil(count / groups);
      const members = [];
      for (let i = 0; i < count; i += 1) {
        const group = Math.min(groups - 1, Math.floor(i / size));
        members[group] = (members[group] || 0) + 1;
      }
      const placed = [];
      for (let i = 0; i < count; i += 1) {
        const group = Math.min(groups - 1, Math.floor(i / size));
        placed[group] = (placed[group] || 0) + 1;
        const seat = placed[group] - 1;
        const axis = seeded(group * 5 % count);
        const gx = groups > 1 ? lo + gap * group : (lo + hi) / 2;
        const gy = cy + (group % 2 ? 1 : -1) * lift * (.96 + wobble(group, 8) * .1);
        if (!seat) {
          points.push([gx, gy, seeded(group * 7 % count)]);
          continue;
        }
        const step = Math.PI * 2 / (members[group] - 1);
        const angle = wobble(group, 9) * Math.PI * 2 + (seat - 1 + (wobble(i, 10) - .5) * .34) * step;
        const reach = near * (1 + wobble(i, 11) * .25);
        points.push([gx + Math.cos(angle) * reach, gy + Math.sin(angle) * reach, axis]);
      }
      /* Lines run from each partner to the mark that convenes its group, so
         the drawing says the same thing the caption does. */
      let start = 0;
      members.forEach(total => {
        for (let i = 1; i < total; i += 1) lines.push(curve(points[start + i], points[start]));
        start += total;
      });
      return { points, lines, ring: false };
    }
    if (name === 'network') {
      /* A constellation, not a second ring. The marks sit on a golden-angle
         spiral, so the middle of the frame carries ink instead of being the
         hole in a circle, and every mark reaches to its two nearest partners.
         The orbit is the other layout that fills the frame, and two rings
         would read as the same picture twice. */
      const gold = Math.PI * (3 - Math.sqrt(5));
      for (let i = 0; i < count; i += 1) {
        const reach = Math.sqrt((i + .55) / count);
        const angle = i * gold;
        points.push([
          cx + Math.cos(angle) * reach * spanX / 2 * (.9 + wobble(i, 3) * .2),
          cy + Math.sin(angle) * reach * spanY / 2 * (.9 + wobble(i, 4) * .2),
          seeded(i),
        ]);
      }
      const drawn = new Set();
      for (let i = 0; i < count; i += 1) {
        const near = points
          .map((point, j) => [j, Math.hypot(point[0] - points[i][0], point[1] - points[i][1])])
          .filter(([j]) => j !== i)
          .sort((a, b) => a[1] - b[1])
          .slice(0, 2);
        near.forEach(([j]) => {
          const pair = i < j ? `${i}:${j}` : `${j}:${i}`;
          if (drawn.has(pair)) return;
          drawn.add(pair);
          lines.push(curve(points[i], points[j]));
        });
      }
      return { points, lines, ring: false };
    }
    const cols = Math.max(1, Math.round(Math.sqrt(count * spanX / spanY)));
    const rows = Math.ceil(count / cols);
    const cellW = spanX / cols;
    const cellH = spanY / rows;
    for (let i = 0; i < count; i += 1) {
      const row = Math.floor(i / cols);
      const col = i % cols;
      const inRow = Math.min(cols, count - row * cols);
      /* Alternate rows step sideways and every mark is jittered, so a field of
         marks reads as scattered rather than as a lattice. */
      points.push([
        x0 + (cols - inRow) * cellW / 2 + (col + .5) * cellW + (row % 2 ? .24 : -.24) * cellW
          + (wobble(i, 1) - .5) * cellW * .4,
        y0 + (row + .5) * cellH + (wobble(i, 2) - .5) * cellH * .4,
        seeded(i),
      ]);
    }
    return { points, lines, ring: false };
  };

  /* The drawing engine. One state in, one state out; a state that arrives
     mid-transition cancels the pending draw so the stage is never mixed. */
  const makeStage = (svg, source) => {
    if (!svg) return null;
    const marks = [...svg.querySelectorAll('.mark')];
    if (!marks.length) return null;
    const frame = frameOf(svg);
    const label = svg.querySelector('.center-label');
    /* getComputedTextLength returns 0 inside a display:none container, so a
       print copy cannot measure itself. It takes the fit the live stage
       worked out instead. */
    if (label && source && source.label) {
      ['textLength', 'lengthAdjust'].forEach(name => {
        if (source.label.hasAttribute(name)) label.setAttribute(name, source.label.getAttribute(name));
      });
    } else if (label && label.getComputedTextLength) {
      // The word may reach across the ring, less a fifth of a mark each side.
      const room = (frame.ring - frame.mark * .2) * 2;
      const width = label.getComputedTextLength();
      if (width > room) {
        label.setAttribute('textLength', room.toFixed(1));
        label.setAttribute('lengthAdjust', 'spacingAndGlyphs');
      }
    }
    return {
      svg,
      marks,
      label,
      frame,
      lines: svg.querySelector('.connections'),
      ring: svg.querySelector('.center-ring'),
      count: Number(svg.dataset.marks) || marks.length,
      angles: marks.map(mark => Number(mark.dataset.angle)),
      leaving: [],
      pending: null,
      timer: 0,
      token: 0,
    };
  };

  const setState = (stage, name, highlight) => {
    if (!stage) return;
    const plan = layoutFor(name, stage.count, stage.angles, stage.frame);
    /* The state names itself on the drawing, so the stylesheet can carry the
       color of each layout. Only the scrolly reads it; the cover keeps ink. */
    stage.svg.dataset.state = name;
    stage.token += 1;
    const token = stage.token;
    clearTimeout(stage.timer);
    stage.marks.forEach((mark, i) => {
      const point = plan.points[i];
      if (!point) return;
      mark.style.transform = `translate(${point[0].toFixed(1)}px,${point[1].toFixed(1)}px) rotate(${point[2].toFixed(1)}deg)`;
      mark.classList.toggle('is-highlight', highlight.has(i));
    });
    if (stage.lines) {
      /* Anything still arriving is stale: drop it rather than cross-fade it. */
      stage.leaving.forEach(node => node.remove());
      if (stage.pending) stage.pending.forEach(node => node.remove());
      stage.leaving = [...stage.lines.children];
      stage.leaving.forEach(node => node.classList.add('is-leaving'));
      const last = Math.max(1, plan.lines.length - 1);
      const spread = TIME.lineLast - TIME.lineFirst;
      const fresh = plan.lines.map((line, i) => {
        const path = document.createElementNS(NS, 'path');
        path.setAttribute('d', line.d);
        path.style.setProperty('--len', line.length);
        path.style.setProperty('--d', (TIME.lineFirst + i * spread / last).toFixed(0) + 'ms');
        return path;
      });
      stage.lines.append(...fresh);
      stage.pending = fresh;
    }
    const showRing = plan.ring ? '1' : '0';
    /* The last line finishes drawing here: the draw starts at --draw-start,
       runs for --dur-draw and the last line waits --line-delay-last. */
    const drawn = TIME.drawStart + TIME.draw + TIME.lineLast;
    if (stage.ring) stage.ring.style.opacity = showRing;
    if (stage.label) stage.label.style.opacity = showRing;
    stage.svg.style.setProperty('--ring-delay', (plan.ring ? drawn : 0) + 'ms');
    stage.timer = setTimeout(() => {
      if (stage.token !== token) return;
      stage.leaving.forEach(node => node.remove());
      stage.leaving = [];
      stage.pending = null;
    }, drawn + TIME.draw);
  };

  /* Scrub blending. setState fires one state per card and lets the transitions
     travel; the scrolly can also drive the stage straight from the scroll
     position, with the same layout math. planFor caches a plan per state,
     because a scroll frame asks for the same few plans over and over. The
     cache keys on the stage, so a print copy — a stage of its own — never
     reads the live stage's plans. */
  const planCache = new WeakMap();
  const planFor = (stage, name) => {
    let cache = planCache.get(stage);
    if (!cache) {
      cache = new Map();
      planCache.set(stage, cache);
    }
    if (!cache.has(name)) {
      cache.set(name, layoutFor(name, stage.count, stage.angles, stage.frame));
    }
    return cache.get(name);
  };

  /* A mark turns the short way around: from 350 to 10 degrees is 20 degrees
     forward, not 340 back. */
  const lerpAngle = (a, b, t) => a + ((b - a + 540) % 360 - 180) * t;

  /* One blend in, one frame out. Marks travel the straight line between their
     places in the two plans, the ring and its label follow the same share,
     and the accent lands on the marks of whichever state is nearer. The line
     work is the caller's: it holds the two sets and writes their opacities,
     because only it knows where the segment starts and ends. Nothing here is
     timed — every write is the scroll position, so a paused reader never
     meets it. */
  const blend = (stage, from, to, t, highlight) => {
    if (!stage) return;
    const planA = planFor(stage, from);
    const planB = planFor(stage, to);
    stage.marks.forEach((mark, i) => {
      const a = planA.points[i];
      const b = planB.points[i];
      if (!a || !b) return;
      const x = a[0] + (b[0] - a[0]) * t;
      const y = a[1] + (b[1] - a[1]) * t;
      mark.style.transform = `translate(${x.toFixed(1)}px,${y.toFixed(1)}px) rotate(${lerpAngle(a[2], b[2], t).toFixed(1)}deg)`;
      mark.classList.toggle('is-highlight', highlight.has(i));
    });
    const ring = Number(planA.ring) + (Number(planB.ring) - Number(planA.ring)) * t;
    if (stage.ring) stage.ring.style.opacity = ring.toFixed(3);
    if (stage.label) stage.label.style.opacity = ring.toFixed(3);
  };

  /* Transitions stay off until the first state is on screen, so nothing
     travels in from the corner on load. */
  const goLive = stage => {
    if (!stage) return;
    stage.svg.getBoundingClientRect();
    stage.svg.classList.add('is-live');
  };


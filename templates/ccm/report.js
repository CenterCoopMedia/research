/* Scroll selects a visual state. It never captures wheel or touch input.
   The drawing's mark count and every seeded angle come from the markup that
   build.py wrote, so nothing here repeats a number that lives in build.py. */
(() => {
  const root = document.documentElement;
  const NS = 'http://www.w3.org/2000/svg';
  /* Every duration here is the token the stylesheet animates with, read once
     at startup, so a timing can never be changed in one file and left behind
     in the other. */
  const ms = name => {
    const raw = getComputedStyle(root).getPropertyValue(name).trim();
    const value = parseFloat(raw) || 0;
    return raw.endsWith('ms') ? value : value * 1000;
  };
  const TIME = {
    travel: ms('--dur-travel'),
    draw: ms('--dur-draw'),
    drawStart: ms('--draw-start'),
    markStep: ms('--intro-mark-step'),
    strokeStep: ms('--intro-stroke-step'),
    lineFirst: ms('--line-delay-first'),
    lineLast: ms('--line-delay-last'),
  };


  /* The one object the partials share. A component asks for the work it needs
     at startup with onReady, and the work it needs on each frame the reader
     scrolls with onFrame. 99-boot.js runs the ready list last of all, so a
     component that throws while it builds leaves the reader the plain page. */
  const kit = {
    root,
    ms,
    tokens: TIME,
    ready: [],
    frame: [],
    onReady: work => kit.ready.push(work),
    onFrame: work => kit.frame.push(work),
  };



  /* The hint that a box holds more to the side. It goes away at the end of the
     scroll, so it always means there is something further along. The table
     wrapper and the diagram frame both carry .scroll-edge, so the two read the
     same and one rule states the treatment.

     scrollWidth and clientWidth can differ by a couple of px with nothing to
     scroll to: subpixel rounding, a border, a rotated glyph's own bounding
     box. SCROLL_EDGE_SLACK absorbs that noise; a box that actually holds more
     is short a column or a row, which is tens of px, not a handful. */
  const SCROLL_EDGE_SLACK = 4;
  kit.onReady(() => {
    document.querySelectorAll('.scroll-edge').forEach(box => {
      const mark = () => {
        /* Two tests, because the noise has two sources. The table wrapper
           only takes overflow-x below 760px, so above it the box cannot
           scroll whatever its scrollWidth says, and the slack above absorbs
           the subpixel remainder on a box that can. Without both, the hint
           paints a shade over the last column of a table the reader can
           already see whole. */
        const scrolls = getComputedStyle(box).overflowX !== 'visible';
        const room = box.scrollWidth - box.clientWidth - box.scrollLeft;
        if (scrolls && room > SCROLL_EDGE_SLACK) box.dataset.scroll = 'more';
        else delete box.dataset.scroll;
      };
      box.addEventListener('scroll', mark, { passive: true });
      addEventListener('resize', mark, { passive: true });
      mark();
    });
  });

  /* The contents panel and the section the reader is in. Everything the panel
     needs lives here: the current section, click outside, escape, and focus on
     the landing target. The panel itself is a native <details>, so it still
     opens with this script disabled.

     One reading of the page decides the current section. The panel marks it
     with aria-current and an accent rule, the header names it, and 50-share.js
     appends it to the address Copy link writes. */
  const initContents = () => {
    const contents = document.querySelector('.contents');
    if (!contents) return null;
    const slot = document.querySelector('.header-section');
    const summary = contents.querySelector('summary');
    /* The section links alone. The panel also carries the header's own links to
       the guide and the examples below 560px, and those point at another page:
       link.hash is empty for them, and querySelector('') throws. */
    const links = [...contents.querySelectorAll('a[href^="#"]')];
    const rows = links.map(link => ({
      link,
      target: document.querySelector(link.hash),
      top: 0,
    }));
    /* Section tops are measured when the page changes shape, not on every
       frame, so following the scroll costs one comparison for each section. */
    const measure = () => rows.forEach(row => {
      if (row.target) row.top = row.target.getBoundingClientRect().top + scrollY;
    });
    const readable = document.getElementById('main');
    if (readable) new ResizeObserver(measure).observe(readable);
    addEventListener('resize', measure);
    let current = '';
    const markCurrent = () => {
      const line = scrollY + innerHeight / 2;
      let found = null;
      rows.forEach(row => { if (row.target && row.top <= line) found = row; });
      const id = found ? found.target.id : '';
      if (id === current) return;
      current = id;
      /* 50-share.js reads this for the fragment it copies. */
      kit.section = id;
      rows.forEach(row => {
        if (row === found) row.link.setAttribute('aria-current', 'true');
        else row.link.removeAttribute('aria-current');
      });
      /* The header swaps the title at once. No crossfade: the reader is
         scrolling, and a title that fades reads as a second thing moving. */
      if (slot) slot.textContent = found ? found.link.textContent : '';
    };
    contents.addEventListener('toggle', () => { if (contents.open) markCurrent(); });
    links.forEach(link => link.addEventListener('click', () => {
      contents.open = false;
      const target = document.querySelector(link.hash);
      if (!target) return;
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    }));
    /* A click on the scrim reports the <details> itself as the target. */
    document.addEventListener('click', event => {
      if (contents.open && (event.target === contents || !contents.contains(event.target))) contents.open = false;
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && contents.open && summary) { contents.open = false; summary.focus(); }
    });
    return markCurrent;
  };
  const syncContents = initContents();

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


  const media = matchMedia('(prefers-reduced-motion: reduce)');
  const motion = document.querySelector('.motion-button');
  const motionLabel = motion && (motion.querySelector('.motion-label') || motion);
  let paused = media.matches;
  const setMotion = () => {
    root.classList.toggle('no-motion', paused);
    /* The stylesheet stops at .01ms under prefers-reduced-motion unless this
       class says the reader asked for motion back. */
    root.classList.toggle('motion-on', !paused);
    if (!motion) return;
    const label = paused ? 'Resume motion' : 'Pause motion';
    if (motionLabel) motionLabel.textContent = label;
    motion.setAttribute('aria-label', label);
    motion.setAttribute('aria-pressed', String(paused));
  };
  setMotion();
  if (motion) {
    motion.hidden = false;
    motion.addEventListener('click', () => { paused = !paused; setMotion(); });
  }
  media.addEventListener('change', event => { paused = event.matches; setMotion(); });



  /* The comparison slider. Side by side is the base state and stays the
     print state; this file lays the two pictures over each other and hands
     the reader the divider. */
  const initCompare = () => {
    document.querySelectorAll('.compare').forEach(compare => {
      const pair = compare.querySelector('.compare-pair');
      const control = compare.querySelector('.compare-control');
      const range = compare.querySelector('.compare-control input');
      if (!pair || !control || !range) return;
      control.hidden = false;
      compare.classList.add('is-overlay');
      /* The step is read off the input, so the arrow keys and the drag can
         never land on two different values of the same divider. */
      const step = Number(range.step) || 1;
      const apply = value => {
        const snapped = Math.round(Math.min(100, Math.max(0, value)) / step) * step;
        range.value = snapped;
        pair.style.setProperty('--split', range.value + '%');
        range.setAttribute('aria-valuetext', range.value + ' percent');
      };
      apply(Number(range.value));
      range.addEventListener('input', () => apply(Number(range.value)));
      /* Dragging is a second way to move the divider and never the only one:
         the range input above is the single pointer path WCAG 2.5.7 asks a
         drag to be offered beside. */
      const follow = event => {
        const box = pair.getBoundingClientRect();
        if (box.width) apply((event.clientX - box.left) / box.width * 100);
      };
      pair.addEventListener('pointerdown', event => {
        pair.setPointerCapture(event.pointerId);
        follow(event);
      });
      pair.addEventListener('pointermove', event => {
        if (pair.hasPointerCapture(event.pointerId)) follow(event);
      });
      pair.addEventListener('pointerup', event => {
        pair.releasePointerCapture(event.pointerId);
      });
    });
  };
  kit.onReady(initCompare);


  /* A findings numeral counts up once, on first view, and lands on the exact
     value the build wrote. The markup already holds that value, so a reader
     with no script, with motion paused, or with reduced motion set reads the
     number and nothing moves.

     The curve is the one --ease-draw states, cubic ease out, so the last
     digit settles rather than snapping. */
  const initCount = () => {
    const numerals = [...document.querySelectorAll('article[data-count] .finding-value')];
    if (!numerals.length || !('IntersectionObserver' in window)) return;
    const duration = kit.ms('--dur-count');
    const paused = () => root.classList.contains('no-motion');
    /* A reader who prints while a numeral is still counting would otherwise
       get the frame the sheet caught. Every numeral lands first. */
    const settled = numerals.map(node => node.textContent);
    let printing = false;
    addEventListener('beforeprint', () => {
      printing = true;
      numerals.forEach((node, index) => { node.textContent = settled[index]; });
    });

    const shape = (digits, value) => {
      const places = digits.includes('.') ? digits.split('.')[1].length : 0;
      const grouped = digits.includes(',');
      const text = value.toFixed(places);
      return grouped ? Number(text).toLocaleString('en-US', {
        minimumFractionDigits: places, maximumFractionDigits: places,
      }) : text;
    };

    const run = node => {
      const item = node.closest('article');
      const digits = item.dataset.count;
      const target = Number(digits.replace(/,/g, ''));
      const final = node.textContent;
      if (!isFinite(target) || paused() || printing) return;
      const started = performance.now();
      const step = now => {
        const share = Math.min(1, (now - started) / duration);
        if (share === 1 || paused() || printing) { node.textContent = final; return; }
        const eased = 1 - Math.pow(1 - share, 3);
        node.textContent = item.dataset.before + shape(digits, target * eased)
          + item.dataset.after;
        requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    const watch = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        watch.unobserve(entry.target);
        run(entry.target);
      });
    }, { rootMargin: '0px 0px -10% 0px' });
    numerals.forEach(node => watch.observe(node));
  };
  kit.onReady(initCount);


  /* The definition popover. The button and the popover attribute do the work:
     the browser opens it on click, on tap, on Enter and on Space, closes it on
     Escape and on a click outside, and reports the open state to assistive
     technology. This file adds the two things the platform does not give:
     the pointer that rests on a term opens the definition, and the popover is
     placed by hand where anchor positioning is not supported. */
  const initDefinitions = () => {
    const terms = [...document.querySelectorAll('.definition-term')];
    if (!terms.length) return;
    /* The button does nothing without the popover API, so a browser that has
       no showPopover keeps the plain link to the glossary entry. The class
       says so, because the enhanced class the boot file adds is for the whole
       page and cannot speak for one control. Nothing below this line runs, so
       the button is bound to nothing either. */
    if (typeof terms[0].showPopover !== 'function') {
      root.classList.add('no-popover');
      return;
    }
    const px = name => parseFloat(getComputedStyle(root).getPropertyValue(name)) || 0;
    const anchored = CSS.supports('position-area', 'block-end');
    const fine = matchMedia('(hover:hover) and (pointer:fine)');
    const delay = kit.ms('--dur-intent');
    const popovers = new Set();
    /* The one anchor name on the page. A popover opened by a click takes the
       button that opened it as its implicit anchor, but a popover opened by
       the pointer has no invoker to take, so the button the reader is on
       carries the name and the popover points at it. One name is enough,
       because one popover is open at a time. */
    const ANCHOR = '--definition-open';
    let named = null;
    let timer = 0;
    /* A definition the reader opened stays open until they dismiss it. Only one
       the pointer opened closes when the pointer leaves, which is what WCAG
       1.4.13 asks of content that appears on hover. */
    let byHover = false;
    let shown = null;

    const hold = () => clearTimeout(timer);
    const closeSoon = popover => {
      hold();
      timer = setTimeout(() => {
        if (byHover && popover.matches(':popover-open')) popover.hidePopover();
      }, delay);
    };

    /* The popover sits under the term, inside the window on both axes, and
       above the term when there is no room under it. */
    const place = (popover, button) => {
      const gap = px('--s2');
      const edge = px('--gutter');
      const term = button.getBoundingClientRect();
      popover.style.margin = '0';
      popover.style.inset = 'auto';
      popover.style.left = '0px';
      popover.style.top = '0px';
      const box = popover.getBoundingClientRect();
      const room = innerWidth - box.width - edge;
      const left = Math.max(edge, Math.min(term.left, room));
      let top = term.bottom + gap;
      if (top + box.height > innerHeight - edge) {
        top = Math.max(edge, term.top - box.height - gap);
      }
      popover.style.left = `${Math.round(left)}px`;
      popover.style.top = `${Math.round(top)}px`;
    };

    const replace = () => {
      if (shown && shown.popover.matches(':popover-open')) place(shown.popover, shown.button);
    };

    terms.forEach(button => {
      const popover = document.getElementById(button.getAttribute('popovertarget'));
      if (!popover) return;
      popovers.add(popover);
      const own = () => {
        shown = { popover, button };
        if (!anchored) return;
        if (named && named !== button) named.style.removeProperty('anchor-name');
        named = button;
        button.style.setProperty('anchor-name', ANCHOR);
        popover.style.setProperty('position-anchor', ANCHOR);
      };
      button.addEventListener('focus', own);
      button.addEventListener('pointerdown', () => { byHover = false; hold(); own(); });
      button.addEventListener('keydown', () => { byHover = false; own(); });
      button.addEventListener('pointerenter', event => {
        if (!fine.matches || event.pointerType === 'touch') return;
        own();
        hold();
        timer = setTimeout(() => {
          byHover = true;
          if (!popover.matches(':popover-open')) popover.showPopover();
        }, delay);
      });
      button.addEventListener('pointerleave', () => closeSoon(popover));
    });

    popovers.forEach(popover => {
      /* The pointer travels from the term onto the popover, so the popover
         holds itself open while it is under the pointer. */
      popover.addEventListener('pointerenter', hold);
      popover.addEventListener('pointerleave', () => closeSoon(popover));
      popover.addEventListener('toggle', event => {
        if (event.newState !== 'open') {
          if (shown && shown.popover === popover) shown = null;
          return;
        }
        if (!anchored && shown && shown.popover === popover) place(popover, shown.button);
      });
      /* The glossary entry is on the same page, so the popover closes as the
         reader leaves for it. */
      const more = popover.querySelector('.definition-more');
      if (more) more.addEventListener('click', () => popover.hidePopover());
    });

    if (anchored) return;
    addEventListener('scroll', replace, { passive: true, capture: true });
    addEventListener('resize', replace);
  };
  kit.onReady(initDefinitions);


  /* A figure reveals itself once. One observer starts the bars and the lines
     when the chart first reaches the viewport, and one class stops them from
     ever starting again, so a reader who scrolls back sees the figure it left
     rather than the drawing of it. The end state is the base state, so a
     browser that runs no animation still reads the figure correctly. */
  const initFigures = () => {
    const charts = [...document.querySelectorAll('.chart')];
    if (!charts.length || !('IntersectionObserver' in window)) return;
    const settle = kit.ms('--dur-draw') + kit.ms('--stagger-cap');
    const watch = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const chart = entry.target;
        watch.unobserve(chart);
        chart.classList.add('in-view');
        setTimeout(() => chart.classList.add('drawn'), settle);
      });
    }, { rootMargin: '0px 0px -10% 0px' });
    charts.forEach(chart => watch.observe(chart));
  };
  kit.onReady(initFigures);


  /* The signup form. The markup posts on its own with no script at all, so
     everything here improves a form that already works: inline errors on the
     field, a summary of them at the top, and one sentence at the end that
     names what the reader gave. Every string the reader sees comes from the
     markup, so the copy lives in one file.

     There are two sends. Without `data-inline` the script checks the fields
     and then lets the native post run, so the endpoint answers with its own
     page. With it the script posts with fetch and the reader stays here, which
     works only when the endpoint sends CORS headers: without them the browser
     rejects an answer the endpoint already accepted, and the page would tell
     the reader their reply failed when it landed. */
  const initForm = () => {
    const form = document.querySelector('.signup');
    if (!form) return;
    const status = document.querySelector('.form-status');
    const summary = form.querySelector('.form-summary');
    const summaryList = summary.querySelector('ul');
    const sendError = form.querySelector('.form-send-error');
    const button = form.querySelector('button[type="submit"]');
    const trap = form.querySelector('.form-trap input');
    const fields = [...form.querySelectorAll('.form-input')];
    const inline = form.dataset.inline === 'true';
    let sending = false;

    /* Our own wording replaces the browser's bubbles. The attribute stays off
       the markup, so with this script gone the browser still checks a field
       before the page posts. */
    form.noValidate = true;

    const labelOf = input => document.querySelector(`label[for="${input.id}"]`).textContent;
    const errorOf = input => document.getElementById(`${input.id}-error`);

    const messageFor = input => {
      if (input.validity.valueMissing) return input.dataset.requiredError || '';
      if (input.validity.typeMismatch) return input.dataset.formatError || '';
      return '';
    };

    /* A field is checked when the reader leaves it. Once it has shown an
       error it is checked on every keystroke, so the message goes as soon as
       the reader fixes it. Nothing is checked while they are still typing the
       first time. */
    const check = input => {
      const message = messageFor(input);
      const error = errorOf(input);
      error.querySelector('.error-text').textContent = message;
      error.hidden = !message;
      if (message) {
        input.setAttribute('aria-invalid', 'true');
        input.dataset.live = 'true';
      } else {
        input.removeAttribute('aria-invalid');
      }
      return !message;
    };

    /* A reader on their way to the button gets no message on the way out of
       the field. The message would grow the form between the press and the
       release, the button would move out from under the pointer, and the
       click would be lost. The submit checks every field a moment later. */
    let pressing = false;
    button.addEventListener('pointerdown', () => { pressing = true; });
    document.addEventListener('pointerup', () => { pressing = false; });

    fields.forEach(input => {
      input.addEventListener('blur', () => { if (!pressing) check(input); });
      input.addEventListener('input', () => { if (input.dataset.live) check(input); });
    });

    const showSummary = broken => {
      summaryList.replaceChildren(...broken.map(input => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = `#${input.id}`;
        link.textContent = messageFor(input);
        item.append(link);
        return item;
      }));
      summary.hidden = false;
      summary.focus();
    };

    /* The end of the flow. The form goes and one sentence takes its place,
       and it names the reader's own answer so they can see it landed. The
       sentence takes the first field the reader filled: an empty field names
       nothing, and one of the fields is always required, so the short sentence
       is there for the trap alone. */
    const succeed = () => {
      const first = fields.find(input => input.value.trim());
      status.textContent = first
        ? form.dataset.success
            .replace('{field}', labelOf(first).toLowerCase())
            .replace('{value}', first.value)
        : form.dataset.successEmpty;
      form.hidden = true;
      status.hidden = false;
      status.focus();
    };

    const send = () => {
      sending = true;
      const label = button.textContent;
      button.textContent = button.dataset.sending;
      form.setAttribute('aria-busy', 'true');
      /* The two attributes, never the properties of the same name: a field
         called "action" would hide `form.action` behind its own input. The
         build stops such a name, and this reads the attribute in any case. */
      fetch(form.getAttribute('action'), {
        method: form.getAttribute('method'),
        body: new FormData(form),
        headers: { Accept: 'application/json' },
      }).then(response => {
        if (!response.ok) throw new Error(response.status);
        succeed();
      }).catch(() => {
        sending = false;
        button.textContent = label;
        form.removeAttribute('aria-busy');
        sendError.hidden = false;
      });
    };

    form.addEventListener('submit', event => {
      if (sending) { event.preventDefault(); return; }
      sendError.hidden = true;
      /* Nothing leaves the page until every field passes, so a reader never
         waits on a post that the endpoint will reject. */
      const broken = fields.filter(input => !check(input));
      if (broken.length) { event.preventDefault(); showSummary(broken); return; }
      summary.hidden = true;
      /* A filled trap is a machine, so the page answers it and posts nothing. */
      if (trap && trap.value) { event.preventDefault(); succeed(); return; }
      /* The native post runs from here unless the form asked for the inline
         send. The page is about to go, so it changes nothing on the way out. */
      if (!inline) return;
      event.preventDefault();
      send();
    });
  };
  kit.onReady(initForm);


  /* The gallery. The strip scrolls by hand with no scripting at all, so this
     file only adds the two buttons and the count that says where the reader
     is. Nothing here starts a timer: a picture changes when the reader asks
     for it and at no other time. */
  const initGallery = () => {
    document.querySelectorAll('.gallery').forEach(gallery => {
      const strip = gallery.querySelector('.gallery-strip');
      const bar = gallery.querySelector('.gallery-bar');
      const count = gallery.querySelector('.gallery-count');
      const items = [...gallery.querySelectorAll('.gallery-item')];
      if (!strip || !bar || items.length < 2) return;
      const steps = [...bar.querySelectorAll('.gallery-step')];
      /* Both offsets are measured from the same corner, so the difference is
         the item's own place inside the strip whatever the page is doing. */
      const left = item => item.offsetLeft - strip.offsetLeft;
      const room = () => strip.scrollWidth - strip.clientWidth;
      const current = () => {
        /* At the end of the strip the last item is the one the reader has
           reached. Its leading edge never crosses the half-width line,
           because the strip has no room left to bring it there. */
        if (room() > 0 && strip.scrollLeft >= room() - 1) return items.length - 1;
        let index = 0;
        items.forEach((item, i) => {
          if (left(item) - strip.scrollLeft <= item.offsetWidth / 2) index = i;
        });
        return index;
      };
      const mark = () => {
        /* A strip wide enough to show every picture has nothing to step
           through, so the bar goes away rather than offering two buttons
           that cannot move it. */
        bar.hidden = room() < 1;
        const line = (current() + 1) + ' of ' + items.length;
        /* The count is a status region, so it is written only when it
           changes; writing the same line again would say it again. */
        if (count && count.textContent !== line) count.textContent = line;
        steps.forEach(button => {
          /* The button moves the strip, so it is spent when the strip has
             run out of room in that direction. */
          button.disabled = Number(button.dataset.step) < 0
            ? strip.scrollLeft < 1
            : strip.scrollLeft >= room() - 1;
        });
      };
      steps.forEach(button => button.addEventListener('click', () => {
        const target = items[current() + Number(button.dataset.step)];
        if (target) strip.scrollLeft = left(target);
        mark();
      }));
      let pending = false;
      const later = () => {
        if (pending) return;
        pending = true;
        requestAnimationFrame(() => { mark(); pending = false; });
      };
      strip.addEventListener('scroll', later, { passive: true });
      addEventListener('resize', later);
      mark();
    });
  };
  kit.onReady(initGallery);


  /* The lightbox. A native <dialog> already holds focus inside itself,
     closes on Escape and paints its own backdrop, so this file adds the four
     things it does not do: the trigger, the click outside, the close button,
     and the focus return. */
  const initLightbox = () => {
    document.querySelectorAll('.media-figure.has-lightbox').forEach(figure => {
      const dialog = figure.querySelector('.lightbox');
      const image = figure.querySelector(':scope > img, :scope > a > img');
      if (!dialog || !image) return;
      /* Where the browser has no modal dialog the fallback has to stay: the
         link opens the picture's own file, and a button in its place would
         open nothing at all. Cite is checked the same way in 50-share.js. */
      if (typeof dialog.showModal !== 'function') return;
      /* Scripts off, the picture is a link to its own file. A picture drawn
         into a data: URI has no file to open, so the markup leaves the link
         out and the button below is the only trigger it ever had. A link
         goes somewhere and a button acts, so the link becomes a button once
         this file has run. */
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'lightbox-open';
      button.setAttribute('aria-haspopup', 'dialog');
      (figure.querySelector('a.lightbox-open') || image).replaceWith(button);
      button.append(image);
      button.addEventListener('click', () => dialog.showModal());
      /* A click on the backdrop is a click outside the dialog's own box. */
      dialog.addEventListener('click', event => {
        const box = dialog.getBoundingClientRect();
        const inside = event.clientX >= box.left && event.clientX <= box.right
          && event.clientY >= box.top && event.clientY <= box.bottom;
        if (!inside) dialog.close();
      });
      dialog.addEventListener('close', () => button.focus());
      const close = dialog.querySelector('.lightbox-close');
      if (close) close.addEventListener('click', () => dialog.close());
    });
  };
  kit.onReady(initLightbox);


  /* The sidenote in the margin. The stylesheet measures the column between the
     reading column and the figure width; this file decides whether that column
     is wide enough to use, puts each note level with its own reference, and
     moves a note down when it would land on the note above it.

     The id the reference points at travels with the copy that is on the page,
     so the reference always lands the reader on a note they can see and the
     note the reference describes is always the one they hear. */
  const initNotes = () => {
    const columns = [...document.querySelectorAll('.sidenotes')];
    if (!columns.length) return;
    const px = name => parseFloat(getComputedStyle(root).getPropertyValue(name)) || 0;
    /* The narrowest column that still holds about 28 characters at --t0. Under
       it a note stops being a line of prose and becomes a stack of words, so
       the footnote at the end of the section is the better copy. */
    const LEAST = px('--s10') + px('--s7');
    const GAP = px('--s4');
    /* The width the stylesheet opens the margin column at, written the same
       way here so the two cannot drift apart. It is the width the wide layout
       folds its rail at as well, so a note goes to the side or to the foot at
       one width in either layout. */
    const margin = matchMedia('(min-width:1001px)');

    const rows = columns.map(column => {
      const section = column.closest('.section');
      const feet = [...section.querySelectorAll('.footnote-list > li')];
      const notes = [...column.querySelectorAll('.sidenote')].map((note, index) => ({
        note,
        foot: feet[index],
        id: feet[index] ? feet[index].id : '',
      }));
      return { section, column, notes };
    });

    /* The blocks that share the rail with the notes. A pull quote in the wide
       layout floats out of the column into the rail, and it is placed by the
       sentence it lifts rather than by this file, so the notes read its box
       and stand clear of it. In the reading layout it floats nowhere and the
       list is empty. Document order is vertical order here, because each one
       is placed by the paragraph it sits in. */
    const shared = (row, top) => [...row.section.querySelectorAll('.pullquote')]
      .filter(quote => getComputedStyle(quote).cssFloat !== 'none')
      .map(quote => {
        const box = quote.getBoundingClientRect();
        return { top: box.top - top, bottom: box.bottom - top };
      });

    /* Each note goes level with the top of its own reference, and a note that
       would land on the note above it, or on a block the rail already holds,
       goes under it instead. The answer is whether the stack that comes out of
       that still ends inside its section: four long notes beside three lines of
       text run past the end of the section and onto the section under it, and a
       stack like that belongs at the foot of the section instead. */
    const place = row => {
      const top = row.column.getBoundingClientRect().top;
      const taken = shared(row, top);
      const wanted = row.notes.map(pair => {
        const reference = document.getElementById(pair.note.dataset.ref);
        return reference ? reference.getBoundingClientRect().top - top : 0;
      });
      let floor = 0;
      row.notes.forEach((pair, index) => {
        let at = Math.max(wanted[index], floor);
        const height = pair.note.offsetHeight;
        taken.forEach(block => {
          if (at < block.bottom && at + height + GAP > block.top) {
            at = block.bottom + GAP;
          }
        });
        pair.note.style.top = `${Math.round(at)}px`;
        floor = at + height + GAP;
      });
      const last = row.notes[row.notes.length - 1];
      if (!last) return true;
      return last.note.getBoundingClientRect().bottom
        <= row.section.getBoundingClientRect().bottom;
    };

    const hand = (row, toSide) => {
      row.notes.forEach(pair => {
        if (!pair.id) return;
        const keep = toSide ? pair.note : pair.foot;
        const give = toSide ? pair.foot : pair.note;
        give.removeAttribute('id');
        keep.id = pair.id;
      });
    };

    /* The column is measured with the stylesheet's own arithmetic: it is shown
       for the length of one measurement and hidden again, inside one task, so
       nothing is painted in between. */
    const room = row => {
      row.column.style.display = 'block';
      const width = row.column.getBoundingClientRect().width;
      row.column.style.display = '';
      return width;
    };

    /* The column has to be wide enough to read and tall enough to hold the
       stack. The height is known only after the notes are placed, so the
       section takes the margin column, the notes are placed in it, and the
       section gives it back when the stack ends below the section does. */
    const sync = () => rows.forEach(row => {
      let fits = margin.matches && room(row) >= LEAST;
      row.section.classList.toggle('notes-side', fits);
      if (fits) {
        fits = place(row);
        if (!fits) row.section.classList.remove('notes-side');
      }
      hand(row, fits);
    });

    /* A section changes height when an image or a figure above the note lands,
       and it changes width when the window does, so the notes are placed again
       from the section itself rather than from the window alone. */
    const watch = new ResizeObserver(sync);
    rows.forEach(row => watch.observe(row.section));
    margin.addEventListener('change', sync);
    sync();
  };
  kit.onReady(initNotes);

  /* The reading progress rule. It reports the reader's place in <main>, not in
     the document, because the header above it and the colophon below it are
     not part of the read. */
  const bar = document.querySelector('.reading-progress');
  const readable = document.getElementById('main');
  if (bar && readable) {
    let start = 0;
    let run = 1;
    let said = -1;
    const update = () => {
      const share = Math.min(1, Math.max(0, (scrollY - start) / run));
      /* scaleX, never width: the rule never asks the page to lay out again,
         and it never transitions, so a reader who asked for reduced motion
         still sees it follow the scroll. */
      bar.style.transform = `scaleX(${share.toFixed(4)})`;
      const percent = Math.round(share * 100);
      if (percent === said) return;
      said = percent;
      bar.setAttribute('aria-valuenow', String(percent));
    };
    /* The geometry is measured when it changes, not on every frame, so the
       frame does one write and no layout read. A ResizeObserver reports its
       first measurement as soon as it observes, so nothing measures twice.
       The new geometry gives a new place in the read, so the rule is drawn
       again at the end of each measurement. Without that the rule and
       aria-valuenow keep the number the old height gave them until the reader
       scrolls. */
    const measure = () => {
      const box = readable.getBoundingClientRect();
      start = box.top + scrollY;
      run = Math.max(1, box.height - innerHeight);
      update();
    };
    new ResizeObserver(measure).observe(readable);
    addEventListener('resize', measure);
    kit.onFrame(update);
  }

  const header = document.querySelector('.site-header');
  const setStageHeight = () => {
    const bar = header ? header.offsetHeight : 68;
    root.style.setProperty('--stage-h-safe', (innerHeight - bar) + 'px');
  };
  setStageHeight();

  /* The cover draws itself in once per load, then behaves like any other art. */
  const hero = makeStage(document.querySelector('[data-art="hero"]'));
  if (hero) {
    const accents = new Set([0, Math.round(hero.count / 3), Math.round(hero.count * 2 / 3)]);
    if (!paused) {
      /* Mark by mark and stroke by stroke, then the lines follow the last
         stroke rather than a number typed in here. */
      const strokes = Math.max(...hero.marks.map(mark => mark.children.length));
      const drawn = TIME.markStep * (hero.count - 1) + TIME.strokeStep * (strokes - 1) + TIME.draw;
      hero.svg.classList.add('is-intro');
      hero.svg.style.setProperty('--draw-start', drawn + 'ms');
      setTimeout(() => {
        hero.svg.classList.remove('is-intro');
        hero.svg.style.removeProperty('--draw-start');
      }, drawn + TIME.draw + TIME.lineLast);
    }
    setState(hero, 'network', accents);
    goLive(hero);
  }

  const readHighlight = data => new Set(
    (data.highlight || '').split(' ').filter(Boolean).map(Number)
  );

  /* The blend eases each segment on the arrival curve, read off the token so
     the stage settles the way everything else on the page arrives. A scrubbed
     state follows the scroll position; the curve keeps the marks arriving
     with the reader instead of tracking the finger one to one. The solver is
     the standard Newton pass over the bezier's x, then a read of its y. */
  const bezier = spec => {
    const match = /cubic-bezier\(([^)]+)\)/.exec(spec);
    if (!match) return t => t;
    const [x1, y1, x2, y2] = match[1].split(',').map(Number);
    if ([x1, y1, x2, y2].some(Number.isNaN)) return t => t;
    const sample = (a1, a2, t) => ((1 - 3 * a2 + 3 * a1) * t + (3 * a2 - 6 * a1)) * t * t + 3 * a1 * t;
    const derive = (a1, a2, t) => (3 * (1 - 3 * a2 + 3 * a1) * t + 2 * (3 * a2 - 6 * a1)) * t + 3 * a1;
    return x => {
      let t = x;
      for (let i = 0; i < 6; i += 1) {
        const err = sample(x1, x2, t) - x;
        const slope = derive(x1, x2, t);
        if (Math.abs(err) < 1e-4 || Math.abs(slope) < 1e-6) break;
        t -= err / slope;
      }
      return sample(y1, y2, Math.min(1, Math.max(0, t)));
    };
  };
  const easeArrive = bezier(getComputedStyle(root).getPropertyValue('--ease'));

  /* The card is what the reader looks at, so the card's own top is what the
     trigger line measures. */
  const scenes = [...document.querySelectorAll('.scrolly')].map(scene => {
    const steps = [...scene.querySelectorAll('.step')].map(step => ({
      data: step.dataset,
      box: step.querySelector('.step-card') || step,
    }));
    return {
      scene,
      steps,
      stage: makeStage(scene.querySelector('.ink-art')),
      caption: scene.querySelector('figcaption'),
      fill: scene.querySelector('.stage-progress i'),
      active: -1,
      near: true,
      /* The scrub's own bookkeeping: whether the scene blends, the segment it
         is in, its place as a share of the states, and the two line sets of
         the segment. */
      scrub: false,
      seg: -1,
      place: -1,
      layerFrom: null,
      layerTo: null,
    };
  });

  const setCaption = (item, caption) => {
    if (!item.caption) return;
    item.caption.textContent = caption;
    item.caption.style.animation = 'none';
    item.caption.getBoundingClientRect();
    item.caption.style.animation = '';
  };

  /* The paused path: one settled state per card, fired as the card crosses
     the cue line, with the transitions the no-motion gate then shortens to
     nothing. */
  const render = (item, index) => {
    const step = item.steps[index];
    if (!step) return;
    setState(item.stage, step.data.layout, readHighlight(step.data));
    setCaption(item, step.data.caption);
    if (item.fill) {
      const share = item.steps.length > 1 ? index / (item.steps.length - 1) : 1;
      item.fill.style.transform = `scaleX(${(.06 + share * .94).toFixed(3)})`;
    }
  };

  /* The two line sets of a segment. The leaving state's lines fade out over
     the first half of the segment and the arriving state's fade in over the
     second, so the drawing is never a tangle of two networks at once. The
     groups are rebuilt only when the segment changes; a scroll frame then
     writes two opacities and nothing else. */
  const setSegment = (item, from) => {
    const stage = item.stage;
    item.seg = from;
    if (!stage || !stage.lines) return;
    stage.lines.textContent = '';
    const make = name => {
      const group = document.createElementNS(NS, 'g');
      planFor(stage, name).lines.forEach(line => {
        const path = document.createElementNS(NS, 'path');
        path.setAttribute('d', line.d);
        group.append(path);
      });
      stage.lines.append(group);
      return group;
    };
    const next = item.steps[from + 1] || item.steps[from];
    item.layerFrom = make(item.steps[from].data.layout);
    item.layerTo = make(next.data.layout);
    item.layerTo.style.opacity = '0';
  };

  /* The scrub path: the scroll position is the state. f is the scene's place
     measured in states — 0 is the first card, one less than the count is the
     last. Every card after the first contributes one share, earned across
     three fifths of a viewport of scroll after its top crosses the cue line,
     so the drawing arrives as the card reaches the middle of the screen. The
     caption and the accent belong to whichever state is nearer, and the
     progress rule fills with the place itself instead of stepping. */
  const scrub = item => {
    const count = item.steps.length;
    const span = innerHeight * .6;
    const cue = innerHeight * .88;
    let f = 0;
    item.steps.forEach((step, i) => {
      if (!i) return;
      const t = (cue - step.box.getBoundingClientRect().top) / span;
      f += Math.min(1, Math.max(0, t));
    });
    if (f === item.place) return;
    item.place = f;
    const from = Math.min(Math.floor(f), Math.max(0, count - 2));
    const t = easeArrive(Math.min(1, f - from));
    if (item.seg !== from) setSegment(item, from);
    const next = item.steps[from + 1] || item.steps[from];
    const dominant = Math.round(f);
    blend(item.stage, item.steps[from].data.layout, next.data.layout, t,
      readHighlight(item.steps[dominant].data));
    if (item.layerFrom) item.layerFrom.style.opacity = (1 - Math.min(1, t / .45)).toFixed(3);
    if (item.layerTo) item.layerTo.style.opacity = Math.max(0, (t - .55) / .45).toFixed(3);
    if (dominant !== item.active) {
      item.active = dominant;
      setCaption(item, item.steps[dominant].data.caption);
      /* The color belongs to the nearer state, as the caption does. The marks
         keep their stroke transition in scrub mode, so the hue crosses on the
         same curve as the accent rather than tracking the scroll. */
      if (item.stage) item.stage.svg.dataset.state = item.steps[dominant].data.layout;
    }
    if (item.fill) {
      const share = count > 1 ? f / (count - 1) : 1;
      item.fill.style.transform = `scaleX(${(.06 + share * .94).toFixed(3)})`;
    }
  };

  const update = () => {
    /* Read the page, then write to it. A write between two reads makes the
       browser lay the page out again inside the same frame, and this runs on
       every frame the reader scrolls. One trigger line decides the state: the
       active card is the last one whose top has passed it. */
    const top = scrollY;
    const cue = innerHeight * .88;
    const actives = scenes.map(item => {
      if (!item.near) return -1;
      let active = 0;
      item.steps.forEach((step, i) => { if (step.box.getBoundingClientRect().top <= cue) active = i; });
      return active;
    });
    if (header) header.classList.toggle('is-scrolled', top > 40);
    scenes.forEach((item, i) => {
      if (actives[i] < 0) return;
      if (paused) {
        /* Motion off shares the reduced-motion path: one settled state per
           card. A scene that was blending settles on the card the reader is
           at, with the segment's line work cleared out of its way. */
        if (item.scrub) {
          item.scrub = false;
          item.scene.classList.remove('is-scrub');
          item.seg = -1;
          item.place = -1;
          item.active = -1;
          item.layerFrom = null;
          item.layerTo = null;
          if (item.stage) {
            clearTimeout(item.stage.timer);
            if (item.stage.lines) item.stage.lines.textContent = '';
            item.stage.leaving = [];
            item.stage.pending = null;
          }
        }
        if (actives[i] === item.active) return;
        item.active = actives[i];
        render(item, actives[i]);
        return;
      }
      if (!item.scrub) {
        item.scrub = true;
        item.scene.classList.add('is-scrub');
        item.seg = -1;
        item.place = -1;
        item.active = -1;
      }
      scrub(item);
    });
    /* Last, because it writes attributes. It runs on every frame whether the
       panel is open or not: it also names the section in the header and hands
       50-share.js the fragment Copy link writes. */
    if (syncContents) syncContents();
    kit.frame.forEach(work => work());
  };

  update();

  /* Paper cannot scroll, so print gets small multiples: one static copy of the
     stage for every step, laid out by the same function the screen uses. The
     copies are built once, here, before the live stage starts transitioning.
     Each copy renames its own gradient and mask so five drawings can share a
     page without sharing an id. */
  scenes.forEach(item => {
    const target = item.scene.querySelector('.print-figure');
    if (!target || !item.stage) return;
    const name = item.stage.svg.dataset.art;
    item.steps.forEach((step, index) => {
      const copy = item.stage.svg.cloneNode(true);
      const key = `${name}-p${index}`;
      copy.innerHTML = copy.innerHTML
        .split(`id="${name}--`).join(`id="${key}--`)
        .split(`(#${name}--`).join(`(#${key}--`);
      const figure = document.createElement('figure');
      const caption = document.createElement('figcaption');
      caption.textContent = step.data.caption;
      figure.append(copy, caption);
      target.append(figure);
      setState(makeStage(copy, item.stage), step.data.layout, readHighlight(step.data));
    });
    /* The print rules that hide the fallback stage and the static captions
       key on this: only once the small multiples exist does paper have
       anything to show in their place. Scripts off, or a scene that could
       not build its copies, leaves the fallback as the printed page. */
    item.scene.classList.add('print-ready');
  });

  scenes.forEach(item => goLive(item.stage));

  let pending = false;
  const schedule = () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => { update(); pending = false; });
  };
  addEventListener('scroll', schedule, { passive: true });
  addEventListener('pageshow', schedule);
  /* The observer only decides whether the listener does any work. It also has
     to ask for one pass of its own, or a jump that lands inside the section
     leaves the stage on the state the reader last scrolled past. */
  scenes.forEach(item => {
    if (!item.steps.length) return;
    new IntersectionObserver(entries => {
      entries.forEach(entry => {
        item.near = entry.isIntersecting;
        if (entry.isIntersecting) schedule();
      });
    }, { rootMargin: '25% 0px' }).observe(item.scene);
  });
  /* Turning motion off has to settle the stage at once, not on the next
     scroll frame, and turning it back on resumes the blend just as fast. */
  if (motion) motion.addEventListener('click', schedule);
  media.addEventListener('change', schedule);
  /* The stage height token tracks every resize, including a shorter window
     with the same width, so --stage-h-safe never goes stale. Height alone
     changing is also how a mobile browser hides its own chrome, though, and
     reacting to that with a state change is one the reader never asked for,
     so the layout recalculation stays gated on width. */
  let width = innerWidth;
  addEventListener('resize', () => {
    setStageHeight();
    if (innerWidth === width) return;
    width = innerWidth;
    schedule();
  });


  /* Copy link and Cite. Both controls are hidden in the markup and shown here,
     so a reader with no script never sees a control that cannot work. */
  const toast = document.querySelector('.toast');
  const canPopover = toast && typeof toast.showPopover === 'function';
  /* --dur-toast is in 00-tokens.css, so the hold is stated once. The
     2400ms the brief states holds until the token lands. */
  const TOAST_HOLD = kit.ms('--dur-toast');
  let toastTimer = 0;

  /* Where anchor positioning is not available, how much of the footer's control
     group is already on the screen is what lifts the message clear of the
     control that opened it. The group is measured rather than the whole footer,
     so the message lands over the buttons and not over the band above them. The
     stylesheet reads it and the anchor overrides it. */
  const controls = document.querySelector('.footer-controls')
    || document.querySelector('.site-footer');
  const lift = () => {
    if (!controls) return;
    const shown = innerHeight - controls.getBoundingClientRect().top;
    toast.style.setProperty('--toast-lift', `${Math.max(0, shown)}px`);
  };

  const say = message => {
    if (!toast) return;
    /* The text is written before the popover opens, so the status region
       carries its message the first time a screen reader reads it. */
    toast.textContent = message;
    toast.hidden = false;
    lift();
    clearTimeout(toastTimer);
    if (!canPopover) {
      /* Where the popover API is not there, the element is shown in the page
         and hidden again after the hold. It keeps role="status", so the
         reader is told what happened either way. */
      toastTimer = setTimeout(() => { toast.hidden = true; }, TOAST_HOLD);
      return;
    }
    if (!toast.matches(':popover-open')) toast.showPopover();
    toastTimer = setTimeout(() => toast.hidePopover(), TOAST_HOLD);
  };

  /* A page opened from disk is not a secure context, so the clipboard API is
     not always there. The selection path is the fallback that still works. */
  const copyBySelection = value => {
    const field = document.createElement('textarea');
    field.value = value;
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.opacity = '0';
    document.body.append(field);
    field.select();
    let done = false;
    try {
      done = document.execCommand('copy');
    } catch (error) {
      done = false;
    }
    field.remove();
    return done;
  };

  const report = (done, thing) => say(done
    ? `The ${thing} is on the clipboard.`
    : `The copy did not work. Select the ${thing} and copy it.`);

  const copy = (value, thing) => {
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      report(copyBySelection(value), thing);
      return;
    }
    navigator.clipboard.writeText(value).then(
      () => report(true, thing),
      () => report(copyBySelection(value), thing),
    );
  };

  /* The canonical address of the page, plus the section the reader is in, so a
     shared link opens where the reader was rather than at the cover. */
  const canonical = document.querySelector('link[rel="canonical"]');
  const address = () => {
    const base = canonical ? canonical.href : location.href.split('#')[0];
    return kit.section ? `${base}#${kit.section}` : base;
  };

  const copyLink = document.querySelector('.copy-link-button');
  if (copyLink && (navigator.clipboard || document.execCommand)) {
    copyLink.hidden = false;
    copyLink.addEventListener('click', () => copy(address(), 'link'));
  }

  const dialog = document.querySelector('.cite-dialog');
  const citeButton = document.querySelector('.cite-button');
  if (dialog && citeButton && typeof dialog.showModal === 'function') {
    citeButton.hidden = false;
    citeButton.addEventListener('click', () => dialog.showModal());
    dialog.querySelectorAll('.cite-close').forEach(
      button => button.addEventListener('click', () => dialog.close()),
    );
    /* <dialog> closes on Escape by itself. A click on the backdrop reports the
       dialog as the target, because the backdrop belongs to it, and so does a
       click on the padding of the dialog. The point decides between the two:
       the dialog closes only where the pointer is outside its own box. A
       button pressed from the keyboard reports the button as the target, so
       it never reaches this test. */
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      const outside = event.clientX < box.left || event.clientX > box.right
        || event.clientY < box.top || event.clientY > box.bottom;
      if (outside) dialog.close();
    });
    dialog.querySelectorAll('.cite-copy').forEach(button => {
      const source = document.getElementById(button.dataset.cite);
      if (!source) return;
      button.hidden = false;
      button.addEventListener('click', () => copy(source.textContent, 'citation'));
    });
  }


  /* A table sorts in place. The rows move, the focus stays on the button the
     reader pressed, aria-sort states the column and the direction, and one
     hidden status sentence states the new order for a reader who cannot see
     the rows move. Without this file the table is still a whole table. */
  const ORDERS = {
    'number-up': 'smallest first',
    'number-down': 'largest first',
    'text-up': 'A to Z',
    'text-down': 'Z to A',
  };

  const cellValue = (row, index, type) => {
    const cell = row.children[index];
    if (!cell) return type === 'number' ? 0 : '';
    if (type === 'number') return Number(cell.dataset.value);
    return cell.textContent.trim();
  };

  const sortTable = (button, table, status) => {
    const head = button.closest('th');
    const index = Number(button.dataset.column);
    const type = button.dataset.type;
    /* A first press on a column of numbers puts the largest at the top,
       which is the order a reader of a ranking wants. Text starts at A. */
    const up = head.getAttribute('aria-sort') === 'descending'
      || (head.getAttribute('aria-sort') === 'none' && type === 'text');
    const body = table.tBodies[0];
    const rows = [...body.rows];
    rows.sort((one, two) => {
      const first = cellValue(one, index, type);
      const second = cellValue(two, index, type);
      const order = type === 'number' ? first - second
        : String(first).localeCompare(String(second));
      return up ? order : -order;
    });
    rows.forEach(row => body.appendChild(row));
    [...table.tHead.rows[0].cells].forEach(cell => cell.setAttribute('aria-sort', 'none'));
    head.setAttribute('aria-sort', up ? 'ascending' : 'descending');
    if (status) {
      /* The name of the column and nothing else: the unit sits in a span
         beside it, and "Grants per year" is not the name of the column. */
      const name = button.querySelector('.column-name').textContent.trim();
      status.textContent = `Sorted by ${name}, ${ORDERS[`${type}-${up ? 'up' : 'down'}`]}.`;
    }
  };

  const initTables = () => {
    document.querySelectorAll('.column-sort').forEach(button => {
      const table = button.closest('table');
      const status = table.closest('.section') || document;
      button.addEventListener('click', () => {
        sortTable(button, table, status.querySelector('.table-status'));
      });
    });
  };
  kit.onReady(initTables);

  /* The ARIA tabs pattern with automatic activation: a tab shows its panel as
     soon as it takes focus, so the arrow keys walk the panels rather than
     walking a set of controls the reader then has to press. */
  const initTabs = group => {
    const tabs = [...group.querySelectorAll('[role="tab"]')];
    if (!tabs.length) return;
    /* The panel of a tab is found in the group the tab is in, not by id in
       the whole document, so a stray id somewhere else on the page is never
       hidden or shown. The kit writes these ids with a reserved "--", which
       no section id can hold, and this makes the pairing local as well. */
    const panelOf = tab => {
      const name = tab.getAttribute('aria-controls');
      const owner = tab.closest('.tabs') || group;
      return [...owner.querySelectorAll('[role="tabpanel"]')]
        .find(panel => panel.id === name) || null;
    };
    const panels = tabs.map(panelOf);
    const select = index => {
      tabs.forEach((tab, i) => {
        const on = i === index;
        tab.setAttribute('aria-selected', String(on));
        /* One stop in the page tab order for the whole list. Tab from the
           selected tab lands in the panel it opened. */
        tab.tabIndex = on ? 0 : -1;
        if (panels[i]) panels[i].hidden = !on;
      });
    };
    /* Home and End are jumps, the arrows are steps, and a step off either end
       wraps, which is what the pattern asks for. */
    const steps = {
      ArrowRight: index => index + 1,
      ArrowLeft: index => index - 1,
      Home: () => 0,
      End: () => tabs.length - 1,
    };
    const move = (event, index) => {
      const step = steps[event.key];
      if (!step) return;
      event.preventDefault();
      const next = (step(index) + tabs.length) % tabs.length;
      select(next);
      tabs[next].focus();
    };
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => select(index));
      tab.addEventListener('keydown', event => move(event, index));
    });
    select(0);
    /* The class is what shows the tab list and hides the headings the panels
       carry for a reader with no script, so it lands only once the list works. */
    group.classList.add('tabs-live');
  };
  kit.onReady(() => document.querySelectorAll('.tabs').forEach(initTabs));

  function initWaterfall(host) {
    const scope=host.attachShadow({mode:'open'});
    scope.appendChild(host.querySelector('template').content.cloneNode(true));
    let offset=0;
    const storyTop=()=>scope.getElementById('story').getBoundingClientRect().top+window.scrollY-offset;
    const fallbackMarkup=data=>'<h3>'+escapeHTML(data.title)+'</h3><p>'+escapeHTML(data.status)+'</p><table><thead><tr><th>Group</th><th>Value</th></tr></thead><tbody>'+data.groups.map(g=>'<tr><td>'+escapeHTML(g.label)+'</td><td>'+escapeHTML(g.value)+' '+escapeHTML(data.unit)+'</td></tr>').join('')+'</tbody></table><p>'+escapeHTML(data.source)+'</p><p>'+escapeHTML(data.caveat)+'</p>';

  /** A data-first unit-chart renderer. No libraries, network calls, or scroll hijacking. */
  const $ = id => scope.getElementById(id);
  const number = new Intl.NumberFormat('en-US',{maximumSignificantDigits:21});
  const clamp = (v, lo=0, hi=1) => Math.max(lo, Math.min(hi, v));
  const smoothstep = t => t*t*(3-2*t);
  const escapeHTML = text => String(text).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const clone = object => JSON.parse(JSON.stringify(object));
  const defaultData = JSON.parse($('scale-data').textContent);
  const reachData = {
    version:1,title:'Program reach, in perspective',unit:'people',totalSquares:2500,
    status:'Fictional example · not a measured population',
    source:'Entirely invented figures for demonstrating the storytelling template. These are not results from a real program, organization, or community.',
    caveat:'The four example groups are mutually exclusive and total 50,000 people. Replace all figures and narration with your own validated data before publication. “Not yet reached” should only be used when the full target population is known.',
    summaryHeadline:'The audience you know\nis not the whole audience.',
    groups:[
      {id:'regular',label:'Regular participants',shortLabel:'Regular',value:420,color:'#ec3864',headline:'The people\nyou know best.',description:'The regulars: {value} {unit}. They are highly visible, but occupy only {tiles} squares in this fictional population.'},
      {id:'occasional',label:'Occasional participants',shortLabel:'Occasional',value:1680,color:'#e7bb27',headline:'A wider\ncircle.',description:'Add the occasional participants. The picture grows, but the people actively involved are still a small group.'},
      {id:'aware',label:'Reached, not participating',shortLabel:'Reached',value:7900,color:'#00b982',headline:'Awareness\nis not engagement.',description:'These people have been reached by the fictional program but do not participate. A different relationship, and a bigger band.'},
      {id:'unreached',label:'Not yet reached',shortLabel:'Not reached',value:40000,color:'#3e4740',headline:'Beyond\nthe usual circle.',description:'The largest group: people the fictional program has not yet reached. This is what a participant-only view would leave out.'}
    ]
  };
  const dom = {track:$('story'),stage:$('stage'),box:$('chart-box'),canvas:$('unit-chart'),marker:$('boundary-marker'),hint:$('chart-hint'),nav:$('chapter-nav'),dialog:$('editor')};
  const ctx = dom.canvas.getContext('2d');
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  let reduceMotion = motionQuery.matches;
  let config, groups=[], total=0, tiles=2500, columns=50, rows=50, unitValue=0;
  let timeline=[], totalUnits=0, viewHeight=window.innerHeight, currentIndex=-1;
  let size={width:0,height:0,left:0,top:0,grid:0,pitch:0,dot:0};
  let frame=0, scrollPending=false, geometryPending=false, currentState=null, lastTally=-1;
  let lastWidth=0, lastHeight=0, draft, draftBaseline, opener, toastTimer, scrollAnimation=null;
  const hash = n => { const t=Math.sin(n*127.1+311.7)*43758.5453; return t-Math.floor(t); };

  function compact(value, digits=1) {
    const a=Math.abs(value);
    for(const [base,suffix] of [[1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']]) {
      if(a>=base) return (value/base).toFixed(digits).replace(/\.0+$/,'')+suffix;
    }
    if(a>0 && a<0.000001) return value.toExponential(digits);
    if(a>0 && a<1) return new Intl.NumberFormat('en-US',{maximumSignificantDigits:digits+1}).format(value);
    return number.format(Number(value.toFixed(digits)));
  }
  function words(value) {
    for(const [base,suffix] of [[1e12,'trillion'],[1e9,'billion'],[1e6,'million']]) {
      if(Math.abs(value)>=base) return (value/base).toFixed(2).replace(/\.?0+$/,'')+' '+suffix;
    }
    return number.format(value);
  }
  function percent(value) {
    if(value>0 && value<0.01) return '<0.01';
    return value.toFixed(value<1?2:1).replace(/\.0$/,'');
  }
  function contrastInk(hex) {
    // Darken category colors for small type on paper. The squares retain the data color.
    let rgb=hex.slice(1).match(/../g).map(x=>parseInt(x,16));
    const luminance = a => a.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
    while((.897+.05)/(luminance(rgb)+.05)<4.6 && Math.max(...rgb)>20) rgb=rgb.map(v=>Math.round(v*.91));
    return '#'+rgb.map(v=>v.toString(16).padStart(2,'0')).join('');
  }
  function validate(data) {
    if(!data || typeof data!=='object' || Array.isArray(data)) throw Error('The JSON must contain one dataset object.');
    if(typeof data.title!=='string' || !data.title.trim()) throw Error('Give the story a title.');
    if(typeof data.unit!=='string' || !data.unit.trim()) throw Error('Add a plural unit label, such as people or households.');
    if(![1000,2500,5000].includes(Number(data.totalSquares))) throw Error('Choose 1,000, 2,500, or 5,000 squares.');
    if(!Array.isArray(data.groups) || data.groups.length<2 || data.groups.length>8) throw Error('Use between two and eight groups.');
    const used=new Set();
    data.groups.forEach((g,i)=>{
      if(!g || typeof g.label!=='string' || !g.label.trim()) throw Error(`Give group ${i+1} a name.`);
      if(typeof g.value!=='number' || !Number.isFinite(g.value) || g.value<0) throw Error(`“${g.label}” needs a finite, non-negative number.`);
      if(!/^#[0-9a-f]{6}$/i.test(g.color||'')) throw Error(`Choose a six-digit color for “${g.label}”.`);
      if(g.value>Number.MAX_SAFE_INTEGER) throw Error(`“${g.label}” exceeds JavaScript's safe numeric range.`);
      if(typeof g.id!=='string' || !g.id || used.has(g.id)) g.id='group-'+i;
      used.add(g.id);
      g.shortLabel=typeof g.shortLabel==='string'&&g.shortLabel.trim()?g.shortLabel:g.label;
      g.headline=typeof g.headline==='string'&&g.headline.trim()?g.headline:g.label;
      g.description=typeof g.description==='string'?g.description:'{value} {unit}, or {share} of the total. Each square has the same weight.';
    });
    const sum=data.groups.reduce((s,g)=>s+g.value,0);
    if(!(sum>0) || !Number.isFinite(sum) || sum>Number.MAX_SAFE_INTEGER) throw Error('The combined value must be positive and within JavaScript’s safe numeric range.');
    data.totalSquares=Number(data.totalSquares);
    for(const key of ['status','source','caveat','summaryHeadline']) data[key]=typeof data[key]==='string'?data[key]:'';
    data.status=data.status.trim()||'Custom data · check source notes';
    return data;
  }
  function allocate() {
    total=config.groups.reduce((s,g)=>s+g.value,0);
    tiles=config.totalSquares;
    columns=tiles===1000?40:tiles===5000?50:50;
    rows=Math.ceil(tiles/columns);
    unitValue=total/tiles;
    groups=config.groups.map((g,i)=>({...g,index:i,share:g.value/total*100,exact:g.value/total*tiles,ink:contrastInk(g.color)}));
    groups.forEach(g=>g.count=Math.floor(g.exact));
    // Hamilton / largest-remainder apportionment keeps every square the same size
    // and makes the integer allocations sum to exactly totalSquares.
    const spare=tiles-groups.reduce((s,g)=>s+g.count,0);
    [...groups].sort((a,b)=>(b.exact-b.count)-(a.exact-a.count)||a.index-b.index).slice(0,spare).forEach(g=>g.count++);
    let cursor=0;
    groups.forEach(g=>{g.start=cursor;cursor+=g.count;g.end=cursor;});
    // The first, small group is already in place. Each later group gets its own
    // fill and hold interval. Share controls filling time, never tile area.
    let start=0;
    timeline=groups.map((g,i)=>{
      const fill=i===0?0:.82+(g.count/tiles)*2.65;
      const hold=i===0?.88:.64;
      const segment={start,fillEnd:start+fill,end:start+fill+hold,fill,hold};
      start=segment.end;return segment;
    });
    totalUnits=start+.22;
  }
  function replaceTokens(text,g) {
    const substitutions={value:words(g.value),unit:config.unit,tiles:number.format(g.count),totalSquares:number.format(tiles),share:percent(g.share)+'%'};
    return text.replace(/\{(value|unit|tiles|totalSquares|share)\}/g,(_,key)=>substitutions[key]);
  }
  function buildInterface() {
    $('story-title').textContent=config.title;

    $('data-note').textContent=config.status;
    $('chart-heading').textContent=`One whole. ${number.format(tiles)} squares.`;
    $('chart-total').textContent=`~${compact(total)} ${config.unit}`;
    $('square-key-text').textContent=`1 square ≈ ${compact(unitValue)} ${config.unit}`;
    $('total-tally').textContent=number.format(tiles);
    $('chart-description').textContent=`${config.status}. A unit chart of ${number.format(tiles)} equal squares, representing ${number.format(total)} ${config.unit}. `+groups.map(g=>`${g.label}: ${number.format(g.value)} ${config.unit}, ${percent(g.share)} percent, approximately ${g.count} squares.`).join(' ')+` The categories appear in this order as you scroll. The full values are in the data table below.`;
    dom.nav.innerHTML='';
    dom.nav.classList.toggle('many',groups.length>4);
    $('preset-select').options[0].textContent=defaultData.title+' · embedded dataset';
    groups.forEach((g,i)=>{
      const button=document.createElement('button');
      button.className='chapter-button';button.type='button';button.style.setProperty('--chapter-color',g.color);
      button.innerHTML=`<span class="nav-line"><span class="nav-num">${String(i+1)}</span><span class="nav-label">${escapeHTML(g.shortLabel)}</span></span>`;
      button.setAttribute('aria-label',`Jump to ${g.label}: ${percent(g.share)} percent`);
      button.addEventListener('click',()=>goToGroup(i));
      dom.nav.appendChild(button);
    });
    $('data-table-body').innerHTML='';
    groups.forEach(g=>{
      const row=document.createElement('tr');
      row.innerHTML=`<td><span class="table-swatch" style="background:${g.color}" aria-hidden="true"></span>${escapeHTML(g.label)}</td><td>${compact(g.value,2)}</td><td>${percent(g.share)}%</td><td>${number.format(g.count)}</td>`;
      $('data-table-body').appendChild(row);
    });
    $('value-column').textContent=config.unit.charAt(0).toUpperCase()+config.unit.slice(1);
    $('table-caption').textContent=config.title+' — '+config.status;
    $('data-table-foot').innerHTML=`<tr><td>Total</td><td>${compact(total,3)}</td><td>100%</td><td>${number.format(tiles)}</td></tr>`;
    const tiny=groups.filter(g=>g.value>0&&g.count===0);
    $('table-note').textContent=`Percentages use the sum of the input values (${number.format(total)} ${config.unit}). Displayed percentages and compact values are rounded. Squares are apportioned to the nearest whole-grid representation; labels report the input data.`+(tiny.length?` Below one square at this resolution: ${tiny.map(g=>g.label).join(', ')}. Increase the square count to improve visibility.`:'');
    const largest=groups.reduce((max,g)=>g.value>max.value?g:max,groups[0]);
    const rest=total-largest.value;
    $('summary-title').textContent=config.summaryHeadline||'Now compare\nthe whole picture.';
    $('summary-title').style.whiteSpace='pre-line';
    const comparison=rest>0 ? (largest.value/rest>=1?`<strong>${(largest.value/rest).toFixed(1)}× the size of all the other groups combined.</strong>`:`<strong>${percent(largest.share)}% of the whole.</strong>`) : '<strong>the entire population shown.</strong>';
    $('summary-text').innerHTML=`In this dataset, “${escapeHTML(largest.label)}” represents ${comparison} Same squares. Same scale. A very different picture when everyone is included.`;
    $('source-note').textContent=config.source||'No source has been entered. Add an attribution before sharing this story.';
    $('caveat-note').textContent=config.caveat||'No caveats have been entered. Validate the source, denominator, and category definitions before publication.';
    $('rounding-note').textContent=`There are exactly ${number.format(tiles)} squares. Each stands for ${number.format(unitValue)} ${config.unit}. The largest-remainder method assigns whole squares to each group so the total remains exact. This necessarily approximates small groups: for example, “${groups[0].label}” has ${number.format(groups[0].value)} ${config.unit} but is drawn as ${groups[0].count} squares, equivalent to ${number.format(groups[0].count*unitValue)} ${config.unit}. No group is given a larger square to make it more visible.`;
    currentIndex=-1;lastTally=-1;
  }
  function measure(keepProgress=false) {
    const oldHeight=viewHeight;
    const trackTop=dom.track.getBoundingClientRect().top+window.scrollY;
    const oldProgress=(window.scrollY+offset-trackTop)/oldHeight;
    // svh keeps geometry stable while mobile browser chrome expands/collapses.
    const probe=document.createElement('div');
    probe.style.cssText='position:absolute;width:0;height:100svh;pointer-events:none;visibility:hidden';
    scope.appendChild(probe);
    offset = document.querySelector('.site-header')?.getBoundingClientRect().height || 0;
    host.style.setProperty('--waterfall-offset',offset+'px');
    viewHeight=Math.max(200,(probe.getBoundingClientRect().height||window.innerHeight)-offset);
    probe.remove();
    host.style.setProperty('--vh',viewHeight+'px');
    dom.track.style.height=((totalUnits+1)*viewHeight)+'px';
    const box=dom.box.getBoundingClientRect();
    const dpr=Math.min(window.devicePixelRatio||1,2);
    dom.canvas.width=Math.round(box.width*dpr);dom.canvas.height=Math.round(box.height*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
    const gutter=box.width<430?79:99;
    const pad=5;
    const pitch=Math.max(1,Math.min((box.width-gutter-pad*2)/columns,(box.height-pad*2)/rows));
    const gridWidth=columns*pitch,gridHeight=rows*pitch;
    const left=pad+Math.max(0,(box.width-gutter-pad*2-gridWidth)/2);
    const top=pad+Math.max(0,(box.height-pad*2-gridHeight)/2);
    size={width:box.width,height:box.height,left,top,gridWidth,gridHeight,pitch,dot:Math.max(.7,pitch*.69)};
    dom.hint.style.left=left+'px';dom.hint.style.right=Math.max(0,box.width-left-gridWidth)+'px';
    if(keepProgress && oldHeight && Math.abs(oldHeight-viewHeight)>1 && oldProgress>=0 && oldProgress<=totalUnits) window.scrollTo(0,trackTop-offset+oldProgress*viewHeight);
    lastWidth=window.innerWidth;lastHeight=window.innerHeight;
    draw();
  }
  function stateAtScroll() {
    const rect=dom.track.getBoundingClientRect();
    const u=clamp((offset-rect.top)/viewHeight,0,totalUnits);
    let index=timeline.findIndex(segment=>u<segment.end);
    if(index<0) index=groups.length-1;
    const segment=timeline[index];
    const p=segment.fill?clamp((u-segment.start)/segment.fill):1;
    return {u,index,p,holding:p>=1,finished:u>=timeline[timeline.length-1].fillEnd};
  }
  function dotPosition(index) {
    const row=Math.floor(index/columns),col=index%columns;
    const inset=(size.pitch-size.dot)/2;
    return {x:size.left+col*size.pitch+inset,y:size.top+(rows-1-row)*size.pitch+inset};
  }
  function drawTile(x,y,color,alpha=1,stretch=1) {
    const d=size.dot;
    ctx.globalAlpha=alpha;ctx.fillStyle=color;
    ctx.fillRect(x,y,d,d*stretch);
    // A one-pixel lower face gives the field weight without glowing or gradients.
    if(stretch===1 && d>3) {ctx.fillStyle='rgba(0,0,0,.13)';ctx.fillRect(x,y+d-.65,d,.65);}
  }
  function updateNarrative(state) {
    const g=groups[state.index];
    if(currentIndex!==state.index) {
      currentIndex=state.index;
      host.style.setProperty('--accent',g.color);
      host.style.setProperty('--accent-ink',g.ink);
      $('chapter-index').textContent=String(state.index+1);
      $('chapter-label').textContent=g.label;
      $('chapter-headline').textContent=g.headline;
      $('metric-number').textContent=percent(g.share);
      $('group-value').textContent=`${words(g.value)} ${config.unit} · ${number.format(g.count)} squares`;
      $('chapter-description').textContent=replaceTokens(g.description,g);
      $('boundary-percent').textContent=percent(g.share)+'%';
      $('boundary-count').textContent=compact(g.value)+' '+config.unit;
      $('next-label').textContent=state.index===groups.length-1?'Read the full picture':'Scroll to add the next group';
      for(let i=0;i<dom.nav.children.length;i++) {
        if(i===state.index) dom.nav.children[i].setAttribute('aria-current','step');
        else dom.nav.children[i].removeAttribute('aria-current');
      }
      $('chapter-announcement').textContent=`Group ${state.index+1} of ${groups.length}. ${g.label}: ${words(g.value)} ${config.unit}, ${percent(g.share)} percent.`;
    }
    for(let i=0;i<dom.nav.children.length;i++) dom.nav.children[i].style.setProperty('--chapter-progress',i<state.index?'1':i===state.index?String(state.p):'0');
    dom.hint.style.opacity=state.index===0?'1':'0';
    $('scroll-status').textContent=state.holding?(state.index===groups.length-1?'The whole picture. Keep scrolling for the numbers.':'At the boundary. Keep scrolling for the next group.'):'Adding '+g.label.toLowerCase()+'…';
  }
  function draw() {
    if(!ctx || !groups.length || !size.width) return;
    const state=stateAtScroll();currentState=state;
    updateNarrative(state);
    ctx.clearRect(0,0,size.width,size.height);
    // Four quiet corner marks describe the total capacity, without pre-revealing
    // the large final group as a field of ghost squares.
    const l=size.left-.5,t=size.top-.5,r=l+size.gridWidth+1,b=t+size.gridHeight+1;
    ctx.globalAlpha=1;ctx.strokeStyle='#c9cec1';ctx.lineWidth=.75;
    const c=Math.max(5,Math.min(9,size.pitch));
    ctx.beginPath();
    ctx.moveTo(l,t+c);ctx.lineTo(l,t);ctx.lineTo(l+c,t);
    ctx.moveTo(r-c,t);ctx.lineTo(r,t);ctx.lineTo(r,t+c);
    ctx.moveTo(l,b-c);ctx.lineTo(l,b);ctx.lineTo(l+c,b);
    ctx.moveTo(r-c,b);ctx.lineTo(r,b);ctx.lineTo(r,b-c);ctx.stroke();
    let settled=0;
    for(let gi=0;gi<=state.index;gi++) {
      const g=groups[gi],p=gi<state.index?1:state.p;
      for(let j=0;j<g.count;j++) {
        const index=g.start+j,position=dotPosition(index);
        if(p>=1) {drawTile(position.x,position.y,g.color);settled++;continue;}
        if(reduceMotion) {
          if(j<Math.floor(g.count*p)) {drawTile(position.x,position.y,g.color);settled++;}
          continue;
        }
        // Scroll-linked waterfall: deterministic start times and trajectories,
        // so scrubbing backward unwinds the same motion instead of restarting it.
        const spread=g.count>1?j/(g.count-1):0;
        const delay=spread*.75;
        const duration=.17+hash(index+1)*.065;
        const local=(p-delay)/duration;
        if(local<=0) continue;
        if(local>=1) {drawTile(position.x,position.y,g.color);settled++;continue;}
        const progress=clamp(local);
        const fall=smoothstep(progress);
        const originY=size.top-size.dot*3-hash(index+90)*size.pitch*4;
        const y=originY+(position.y-originY)*fall;
        const drift=(hash(index+77)-.5)*size.pitch*2;
        const x=position.x+drift*(1-fall);
        const alpha=clamp(progress/.12);
        const stretch=1+(1-progress)*.55;
        // Clip each flight to the chart's own field; it never covers its caption.
        if(y>=size.top-size.dot && y<size.top+size.gridHeight) drawTile(x,y,g.color,alpha,stretch);
      }
    }
    ctx.globalAlpha=1;
    const g=groups[state.index];
    if(state.holding && g.count>0) {
      const end=dotPosition(g.end-1);
      const x1=end.x+size.dot+size.pitch*.35;
      const x2=size.left+size.gridWidth+9;
      const y=end.y+size.dot/2;
      ctx.strokeStyle=g.ink;ctx.globalAlpha=.58;ctx.lineWidth=.8;
      ctx.beginPath();ctx.moveTo(x1,y);ctx.lineTo(x2,y);ctx.stroke();ctx.globalAlpha=1;
      ctx.fillStyle=g.ink;ctx.fillRect(x2-1,y-1,2,2);
      const markerY=clamp(y-22,0,size.height-43);
      dom.marker.style.transform=`translate(${size.left+size.gridWidth+9}px,${markerY}px)`;
      dom.marker.style.opacity='1';
    } else dom.marker.style.opacity='0';
    if(settled!==lastTally) {$('visible-tally').textContent=number.format(settled);lastTally=settled;}
  }
  function scheduleDraw() {
    if(frame) return;
    frame=requestAnimationFrame(()=>{frame=0;draw();});
  }
  function cancelScrollAnimation() {
    if(scrollAnimation!==null) cancelAnimationFrame(scrollAnimation);
    scrollAnimation=null;
  }
  function scrollToY(target) {
    cancelScrollAnimation();
    if(reduceMotion) {window.scrollTo(0,target);scheduleDraw();return;}
    const start=window.scrollY,distance=target-start;
    const duration=clamp(Math.abs(distance)*.22,480,1350);
    const started=performance.now();
    function step(now) {
      const progress=clamp((now-started)/duration);
      window.scrollTo(0,start+distance*smoothstep(progress));
      if(progress<1) scrollAnimation=requestAnimationFrame(step);
      else scrollAnimation=null;
    }
    scrollAnimation=requestAnimationFrame(step);
  }
  function goToGroup(index) {
    const segment=timeline[clamp(index,0,groups.length-1)];
    const top=dom.track.getBoundingClientRect().top+window.scrollY;
    scrollToY(top-offset+(segment.fillEnd+segment.hold*.30)*viewHeight);
  }
  function showToast(message) {
    $('toast').textContent=message;$('toast').classList.add('show');clearTimeout(toastTimer);
    toastTimer=setTimeout(()=>$('toast').classList.remove('show'),3300);
  }
  function apply(data,{restart=true}={}) {
    config=validate(clone(data));allocate();buildInterface();measure();
    if(restart) {cancelScrollAnimation();window.scrollTo(0,storyTop());draw();}
  }

  // Editor utilities: user content only enters HTML through escapeHTML or textContent.
  function renderGroupEditor() {
    $('edit-groups').innerHTML='';
    draft.groups.forEach((g,i)=>{
      const box=document.createElement('div');box.className='edit-group';box.dataset.index=i;
      box.innerHTML=`<div class="edit-group-top"><label class="color-field"><span class="sr-only">Color for group ${i+1}</span><input type="color" data-field="color" value="${escapeHTML(g.color)}"></label><label class="field">Group ${i+1}<input data-field="label" required maxlength="100" value="${escapeHTML(g.label)}"></label><label class="field">Value<input data-field="value" required type="number" min="0" step="any" value="${g.value}"></label><button type="button" class="remove-group" data-remove="${i}" aria-label="Remove group ${i+1}" ${draft.groups.length<=2?'disabled':''}>×</button></div><details class="group-narration"><summary>Edit this group’s narration</summary><div class="form-grid"><label class="field">Short navigation label<input data-field="shortLabel" maxlength="40" value="${escapeHTML(g.shortLabel||g.label)}"></label><label class="field">Headline (use \\n for a line break)<input data-field="headline" maxlength="140" value="${escapeHTML((g.headline||g.label).replace(/\n/g,'\\n'))}"></label><label class="field wide">Description<textarea data-field="description" rows="2" maxlength="600">${escapeHTML(g.description||'')}</textarea><small>Optional tokens: {value}, {unit}, {tiles}, {totalSquares}, {share}.</small></label></div></details>`;
      $('edit-groups').appendChild(box);
    });
    $('add-group').disabled=draft.groups.length>=8;
  }
  function populateEditor(data) {
    draft=clone(data);draftBaseline=populationKey(data);
    $('edit-title').value=draft.title;$('edit-unit').value=draft.unit;$('edit-tiles').value=draft.totalSquares;
    $('edit-status').value=draft.status;$('edit-source').value=draft.source;$('edit-caveat').value=draft.caveat;
    $('editor-error').textContent='';renderGroupEditor();
  }
  const populationKey=data=>JSON.stringify([data.title,data.groups.map(g=>[g.label,g.value])]);
  function readDraft(validateNow=true) {
    const data={...draft,title:$('edit-title').value.trim(),unit:$('edit-unit').value.trim(),totalSquares:Number($('edit-tiles').value),status:$('edit-status').value.trim(),source:$('edit-source').value.trim(),caveat:$('edit-caveat').value.trim()};
    data.groups=[...$('edit-groups').children].map((node,i)=>{
      const group={...draft.groups[i]};
      node.querySelectorAll('[data-field]').forEach(input=>{
        group[input.dataset.field]=input.dataset.field==='value'?(input.value.trim()===''?NaN:Number(input.value)):input.value.trim();
        if(input.dataset.field==='headline') group.headline=group.headline.replace(/\\n/g,'\n');
      });
      return group;
    });
    // A bespoke default summary is no longer appropriate if the population changes.
    if(populationKey(data)!==draftBaseline) data.summaryHeadline='Now compare\nthe whole picture.';
    return validateNow?validate(data):data;
  }
  function openEditor(event) {
    opener=event?.currentTarget||scope.activeElement;
    populateEditor(config);$('preset-select').value='custom';
    dom.dialog.showModal();
  }
  function closeEditor() {dom.dialog.close();if(opener?.focus) opener.focus();}
  function download(content,name,type) {
    const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);
    const anchor=document.createElement('a');anchor.href=url;anchor.download=name;document.body.appendChild(anchor);anchor.click();anchor.remove();
    setTimeout(()=>URL.revokeObjectURL(url),10000);
  }
  function safeName(title) {return title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,70)||'scale-story';}
  function handleEditorAction(action) {
    try {const data=readDraft();$('editor-error').textContent='';action(data);} catch(error) {$('editor-error').textContent=error.message;}
  }
  scope.querySelectorAll('[data-open-editor]').forEach(button=>button.addEventListener('click',openEditor));
  scope.querySelector('.skip-link').addEventListener('click',event=>{event.preventDefault();$('numbers').scrollIntoView();$('summary-title').setAttribute('tabindex','-1');$('summary-title').focus({preventScroll:true});});
  $('close-editor').addEventListener('click',closeEditor);
  dom.dialog.addEventListener('click',event=>{if(event.target===dom.dialog){const r=dom.dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)closeEditor();}});
  dom.dialog.addEventListener('close',()=>{if(opener?.focus)opener.focus();});
  $('preset-select').addEventListener('change',event=>{if(event.target.value==='ai')populateEditor(defaultData);else if(event.target.value==='reach')populateEditor(reachData);else if(event.target.value==='custom')populateEditor(config);});
  $('edit-groups').addEventListener('click',event=>{const button=event.target.closest('[data-remove]');if(!button)return;draft=readDraft(false);draft.groups.splice(Number(button.dataset.remove),1);renderGroupEditor();});
  $('add-group').addEventListener('click',()=>{draft=readDraft(false);draft.groups.push({id:'group-'+Date.now(),label:'New group',shortLabel:'New group',value:0,color:'#526d91',headline:'Another part\nof the picture.',description:'{value} {unit}, or {share} of the total.'});renderGroupEditor();});
  $('sort-groups').addEventListener('click',()=>{draft=readDraft(false);draft.groups.sort((a,b)=>a.value-b.value);renderGroupEditor();});
  $('editor-form').addEventListener('submit',event=>{event.preventDefault();handleEditorAction(data=>{closeEditor();apply(data);showToast('Your data is in place. Scroll to rebuild the picture.');});});
  $('export-json').addEventListener('click',()=>handleEditorAction(data=>download(JSON.stringify(data,null,2),safeName(data.title)+'.json','application/json')));
  $('export-html').addEventListener('click',()=>handleEditorAction(data=>{
    const copy=host.cloneNode(true);
    copy.removeAttribute('style');
    const template=copy.querySelector('template');
    template.content.querySelector('#scale-data').textContent=JSON.stringify(data).replace(/</g,'\\u003c');
    const fallback=copy.querySelector('.waterfall-fallback');
    fallback.innerHTML=fallbackMarkup(data);
    const title=escapeHTML(data.title);
    // Publication URL and artwork belong to the exported chart's future host.
    const icon=document.head.querySelector('link[rel="icon"]')?.outerHTML||'';
    const description=escapeHTML(data.status+' '+data.source);
    const social=icon+'<meta name="description" content="'+description+'"><meta property="og:type" content="website"><meta property="og:title" content="'+title+'"><meta property="og:description" content="'+description+'"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="'+title+'"><meta name="twitter:description" content="'+description+'">';
    const script='('+initWaterfall.toString()+')(document.querySelector(".waterfall-host"));';
    download('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+title+'</title>'+social+'<style>body{margin:0}.waterfall-host{display:block}</style></head><body>'+copy.outerHTML+'<script>'+script.replace(/<\/script/gi,'<\\/script')+'<'+ '/script></body></html>',safeName(data.title)+'.html','text/html');
    showToast('Standalone HTML created with your edited data.');
  }));
  $('import-json').addEventListener('click',()=>$('json-file').click());
  $('json-file').addEventListener('change',async event=>{
    const input=event.target;
    const file=input.files[0];if(!file)return;
    try {if(file.size>500000)throw Error('Use a JSON dataset smaller than 500 KB.');const data=validate(JSON.parse(await file.text()));populateEditor(data);$('preset-select').value='custom';}catch(error){$('editor-error').textContent='Could not import: '+error.message;}finally{input.value='';}
  });
  $('show-all').addEventListener('click',()=>goToGroup(groups.length-1));
  $('replay').addEventListener('click',()=>scrollToY(storyTop()));
  $('brand-link').addEventListener('click',event=>{event.preventDefault();scrollToY(storyTop());});
  $('next-group').addEventListener('click',()=>{if(currentIndex>=groups.length-1)scrollToY($('numbers').getBoundingClientRect().top+window.scrollY);else goToGroup(currentIndex+1);});
  $('data-note').addEventListener('click',()=>{$('methodology').open=true;scrollToY($('methodology').getBoundingClientRect().top+window.scrollY-22);});
  let reportPaused=document.documentElement.classList.contains('no-motion');
  if(reportPaused) reduceMotion=true;
  new MutationObserver(()=>{
    const next=document.documentElement.classList.contains('no-motion');
    if(next===reportPaused)return;
    reportPaused=next;reduceMotion=next;
    $('reduce-motion').checked=next;cancelScrollAnimation();scheduleDraw();
  }).observe(document.documentElement,{attributes:true,attributeFilter:['class']});
  $('reduce-motion').checked=reduceMotion;
  $('reduce-motion').addEventListener('change',event=>{reduceMotion=event.target.checked;cancelScrollAnimation();scheduleDraw();});
  motionQuery.addEventListener?.('change',event=>{reduceMotion=event.matches;$('reduce-motion').checked=reduceMotion;cancelScrollAnimation();scheduleDraw();});
  window.addEventListener('scroll',scheduleDraw,{passive:true});
  // A user gesture always wins over a button-initiated guided scroll.
  for(const name of ['wheel','touchstart','pointerdown'])window.addEventListener(name,cancelScrollAnimation,{passive:true});
  window.addEventListener('keydown',event=>{if(['ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(event.key))cancelScrollAnimation();});
  window.addEventListener('resize',()=>{
    // Ignore height-only changes from mobile address bars. Width changes and
    // desktop window resizes get a new, proportional chart layout.
    const widthChanged=Math.abs(window.innerWidth-lastWidth)>1;
    if(!widthChanged&&window.innerWidth<761&&Math.abs(window.innerHeight-lastHeight)<170)return;
    if(geometryPending)return;geometryPending=true;
    requestAnimationFrame(()=>{geometryPending=false;measure(true);});
  });
  if('ResizeObserver' in window){let first=true;new ResizeObserver(()=>{if(first){first=false;return;}if(!geometryPending){geometryPending=true;requestAnimationFrame(()=>{geometryPending=false;measure();});}}).observe(dom.box);}
  window.addEventListener('beforeprint',()=>$('methodology').open=true);
  // Expose a read-only snapshot for embedding diagnostics and automated QA.
  host.ScaleStory=Object.freeze({getData:()=>clone(config),getState:()=>({...currentState,settled:lastTally,totalSquares:tiles,allocations:groups.map(g=>({label:g.label,squares:g.count,value:g.value,share:g.share}))}),goToGroup});
  try {apply(defaultData,{restart:false});requestAnimationFrame(()=>measure());} catch(error) {$('chapter-headline').textContent='Check the dataset.';$('chapter-description').textContent=error.message;console.error(error);}

  }
  kit.onReady(()=>document.querySelectorAll(".waterfall-host").forEach(initWaterfall));

  const print = document.querySelector('.print-button');
  if (print) {
    print.hidden = false;
    print.addEventListener('click', () => window.print());
  }


  /* Every partial has run and every stage is built and measured, so the page
     can take the layout that needs them. Anything that throws above this line
     leaves the reader the whole text in the order it is written. */
  kit.ready.forEach(work => work());
  root.classList.add('enhanced');

})();

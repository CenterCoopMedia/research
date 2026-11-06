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


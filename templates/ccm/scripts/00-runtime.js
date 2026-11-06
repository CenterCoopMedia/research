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

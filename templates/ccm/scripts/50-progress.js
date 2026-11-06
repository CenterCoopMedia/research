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

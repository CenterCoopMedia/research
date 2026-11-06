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

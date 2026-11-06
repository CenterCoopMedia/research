
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

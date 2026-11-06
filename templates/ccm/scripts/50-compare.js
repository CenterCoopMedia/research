
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

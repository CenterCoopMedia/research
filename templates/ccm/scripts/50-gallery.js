
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

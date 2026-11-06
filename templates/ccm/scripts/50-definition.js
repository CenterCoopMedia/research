
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

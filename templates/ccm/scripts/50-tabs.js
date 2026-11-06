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

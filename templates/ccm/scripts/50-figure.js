
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
